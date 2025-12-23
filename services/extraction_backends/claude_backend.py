"""
Claude PDF Extraction Backend
Uses Claude's native PDF reading for accurate document extraction
"""

import os
import base64
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

from anthropic import Anthropic

from .base import (
    ExtractionBackend,
    ExtractionResult,
    ExtractedEntity,
    ExtractedRelationship,
    ExtractionConfidence
)

logger = logging.getLogger(__name__)


# Entity extraction prompt template
ENTITY_EXTRACTION_PROMPT = """Analyze this document and extract the following information in a structured format.

CRITICAL INSTRUCTIONS:
1. ONLY extract information that is EXPLICITLY stated in the document
2. DO NOT infer, guess, or hallucinate any information
3. If something is unclear, mark confidence as "low"
4. Include the exact source text for each entity when possible

Extract the following entity types: {entity_types}

For each entity found, provide:
- name: The entity name/value
- type: The entity type (from the list above)
- value: Any associated value (e.g., dosage for medication)
- source_text: The exact text from the document where this was found
- confidence: "high", "medium", or "low"

For relationships between entities, provide:
- source: The source entity name
- target: The target entity name
- type: The relationship type (e.g., "PRESCRIBED", "STOPPED", "TREATS", "DIAGNOSED_WITH")

Also provide:
- A clean markdown version of the document content
- Any warnings about unclear or ambiguous content

Respond in JSON format:
{{
    "markdown": "...",
    "entities": [...],
    "relationships": [...],
    "warnings": [...]
}}"""


class ClaudeExtractionBackend(ExtractionBackend):
    """
    Extraction backend using Claude's native document reading.

    Advantages:
    - High accuracy for complex layouts
    - Understands context and can extract semantic relationships
    - Handles images, tables, and styled content well

    Disadvantages:
    - Costs tokens (included in Claude Max subscription)
    - Slower than pure OCR for simple documents
    - Requires API access
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"):
        """
        Initialize Claude backend.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Claude model to use
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found")

        self.model = model
        self.client = Anthropic(api_key=self.api_key)

    @property
    def name(self) -> str:
        return "claude"

    @property
    def supports_batch(self) -> bool:
        return True  # Can process multiple, but sequentially

    def _read_file_as_base64(self, file_path: str) -> tuple[str, str]:
        """Read file and return base64 content with media type"""
        ext = Path(file_path).suffix.lower()

        media_types = {
            '.pdf': 'application/pdf',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }

        media_type = media_types.get(ext, 'application/octet-stream')

        with open(file_path, 'rb') as f:
            content = base64.standard_b64encode(f.read()).decode('utf-8')

        return content, media_type

    async def extract(
        self,
        file_path: str,
        extract_entities: bool = True,
        entity_types: Optional[List[str]] = None
    ) -> ExtractionResult:
        """
        Extract content using Claude's native document reading.

        Args:
            file_path: Path to the document
            extract_entities: Whether to extract structured entities
            entity_types: Types of entities to extract

        Returns:
            ExtractionResult with full content and entities
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Default entity types for medical documents
        if entity_types is None:
            entity_types = [
                "medication", "person", "date", "condition",
                "vital_sign", "procedure", "instruction", "allergy"
            ]

        # Read file
        file_content, media_type = self._read_file_as_base64(file_path)

        # Build messages
        if extract_entities:
            prompt = ENTITY_EXTRACTION_PROMPT.format(
                entity_types=", ".join(entity_types)
            )
        else:
            prompt = """Extract all text content from this document.
Provide a clean markdown version preserving structure (headings, lists, tables).
Respond with just the markdown content."""

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": file_content
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]

        # Call Claude
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=16000,
                messages=messages
            )

            response_text = response.content[0].text

            # Parse response
            if extract_entities:
                result = self._parse_entity_response(response_text, file_path)
            else:
                result = ExtractionResult(
                    raw_text=response_text,
                    markdown=response_text,
                    backend_name=self.name,
                    confidence=ExtractionConfidence.HIGH
                )

            # Add file metadata
            result.metadata["file_path"] = file_path
            result.metadata["file_name"] = Path(file_path).name
            result.metadata["file_size"] = os.path.getsize(file_path)
            result.metadata["model"] = self.model

            return result

        except Exception as e:
            logger.error(f"Claude extraction failed: {e}")
            raise

    def _parse_entity_response(
        self,
        response_text: str,
        file_path: str
    ) -> ExtractionResult:
        """Parse Claude's JSON response into ExtractionResult"""
        import json

        # Try to extract JSON from response
        try:
            # Handle potential markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            data = json.loads(response_text)

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            # Return raw text if JSON parsing fails
            return ExtractionResult(
                raw_text=response_text,
                markdown=response_text,
                backend_name=self.name,
                confidence=ExtractionConfidence.LOW,
                validation_warnings=["Failed to parse structured response"]
            )

        # Build entities
        entities = []
        for e in data.get("entities", []):
            confidence = ExtractionConfidence.MEDIUM
            if e.get("confidence") == "high":
                confidence = ExtractionConfidence.HIGH
            elif e.get("confidence") == "low":
                confidence = ExtractionConfidence.LOW

            entities.append(ExtractedEntity(
                name=e.get("name", ""),
                entity_type=e.get("type", "unknown"),
                value=e.get("value"),
                confidence=confidence,
                source_text=e.get("source_text"),
                metadata=e.get("metadata", {})
            ))

        # Build relationships
        relationships = []
        for r in data.get("relationships", []):
            relationships.append(ExtractedRelationship(
                source_entity=r.get("source", ""),
                target_entity=r.get("target", ""),
                relationship_type=r.get("type", "RELATED_TO"),
                properties=r.get("properties", {})
            ))

        return ExtractionResult(
            raw_text=data.get("markdown", ""),
            markdown=data.get("markdown"),
            entities=entities,
            relationships=relationships,
            backend_name=self.name,
            confidence=ExtractionConfidence.HIGH,
            validation_warnings=data.get("warnings", [])
        )

    async def extract_batch(
        self,
        file_paths: List[str],
        extract_entities: bool = True,
        entity_types: Optional[List[str]] = None
    ) -> List[ExtractionResult]:
        """
        Extract from multiple documents sequentially.

        For true parallel processing, consider using Docling backend.
        """
        results = []
        for file_path in file_paths:
            try:
                result = await self.extract(file_path, extract_entities, entity_types)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to extract {file_path}: {e}")
                results.append(ExtractionResult(
                    raw_text="",
                    backend_name=self.name,
                    confidence=ExtractionConfidence.LOW,
                    validation_errors=[f"Extraction failed: {str(e)}"]
                ))

        return results

    async def validate_extraction(
        self,
        result: ExtractionResult,
        original_file_path: str
    ) -> ExtractionResult:
        """
        Validate extraction by checking entities against source text.

        Claude's extractions are generally reliable, but we still check
        that entity names appear in the raw text.
        """
        for entity in result.entities:
            # Check if entity name appears in raw text
            if entity.name and entity.name.lower() not in result.raw_text.lower():
                # Could be a hallucination or abbreviation
                if entity.source_text:
                    # Check source text instead
                    if entity.name.lower() not in entity.source_text.lower():
                        result.validation_warnings.append(
                            f"Entity '{entity.name}' not found in source text"
                        )
                        entity.confidence = ExtractionConfidence.LOW
                else:
                    result.validation_warnings.append(
                        f"Entity '{entity.name}' may be inferred (not found in raw text)"
                    )

        return result

    def get_supported_formats(self) -> List[str]:
        """Claude supports PDFs and images natively"""
        return ['.pdf', '.png', '.jpg', '.jpeg', '.gif', '.webp']
