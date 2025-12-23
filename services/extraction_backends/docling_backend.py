"""
Docling Extraction Backend
Uses Docling API for batch document extraction
"""

import os
import logging
import httpx
from typing import List, Optional, Dict, Any
from pathlib import Path

from .base import (
    ExtractionBackend,
    ExtractionResult,
    ExtractedEntity,
    ExtractedRelationship,
    ExtractionConfidence
)

logger = logging.getLogger(__name__)


class DoclingExtractionBackend(ExtractionBackend):
    """
    Extraction backend using Docling API.

    Advantages:
    - Free (self-hosted)
    - Good for batch processing
    - Fast for simple documents
    - No token costs

    Disadvantages:
    - May miss styled/formatted content (as seen with medication boxes)
    - Less accurate for complex layouts
    - Requires separate service running

    Best for:
    - Batch processing many documents
    - Simple text-heavy PDFs
    - When cost is a concern
    """

    def __init__(
        self,
        api_url: Optional[str] = None,
        timeout: int = 180
    ):
        """
        Initialize Docling backend.

        Args:
            api_url: Docling API URL (defaults to DOCLING_API_URL env var)
            timeout: Request timeout in seconds
        """
        self.api_url = api_url or os.getenv(
            "DOCLING_API_URL",
            "https://docling.leadingai.info"
        )
        self.timeout = timeout

    @property
    def name(self) -> str:
        return "docling"

    @property
    def supports_batch(self) -> bool:
        return True

    async def extract(
        self,
        file_path: str,
        extract_entities: bool = True,
        entity_types: Optional[List[str]] = None
    ) -> ExtractionResult:
        """
        Extract content using Docling API.

        Note: Docling returns raw text/markdown. Entity extraction
        would need a secondary LLM pass if required.

        Args:
            file_path: Path to the document
            extract_entities: If True, would need secondary LLM processing
            entity_types: Types of entities to extract

        Returns:
            ExtractionResult with text content
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        endpoint = f"{self.api_url}/v1/convert/file"

        async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
            with open(file_path, 'rb') as f:
                files = {'files': (Path(file_path).name, f)}

                try:
                    response = await client.post(endpoint, files=files)
                    response.raise_for_status()

                    data = response.json()

                except httpx.HTTPStatusError as e:
                    logger.error(f"Docling API error: {e}")
                    raise
                except Exception as e:
                    logger.error(f"Docling request failed: {e}")
                    raise

        # Parse Docling response
        document = data.get("document", {})
        markdown = document.get("md_content", "")

        result = ExtractionResult(
            raw_text=markdown,
            markdown=markdown,
            backend_name=self.name,
            confidence=ExtractionConfidence.MEDIUM,
            metadata={
                "file_path": file_path,
                "file_name": document.get("filename", Path(file_path).name),
                "docling_metadata": document.get("metadata", {})
            }
        )

        # Add warning about limitations
        result.validation_warnings.append(
            "Docling may miss styled/formatted content boxes. "
            "Consider using Claude backend for critical documents."
        )

        # If entity extraction requested, we'd need a secondary pass
        if extract_entities:
            result.validation_warnings.append(
                "Entity extraction with Docling requires secondary LLM processing. "
                "Entities not extracted - use Claude backend for structured extraction."
            )

        return result

    async def extract_batch(
        self,
        file_paths: List[str],
        extract_entities: bool = True,
        entity_types: Optional[List[str]] = None
    ) -> List[ExtractionResult]:
        """
        Extract from multiple documents.

        Docling can handle multiple files more efficiently than Claude
        for pure text extraction.
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
        Validate Docling extraction.

        Since Docling doesn't extract entities, validation is limited.
        We mainly check that we got some content.
        """
        if not result.raw_text or len(result.raw_text.strip()) < 50:
            result.validation_errors.append(
                "Extraction returned minimal content - document may not have been read correctly"
            )
            result.confidence = ExtractionConfidence.LOW

        # Check for truncation indicators
        if "[truncated]" in result.raw_text.lower():
            result.validation_warnings.append(
                "Content appears to be truncated"
            )

        return result

    async def health_check(self) -> bool:
        """Check if Docling API is available"""
        try:
            async with httpx.AsyncClient(timeout=10, verify=False) as client:
                response = await client.get(f"{self.api_url}/health")
                return response.status_code == 200
        except Exception:
            return False

    def get_supported_formats(self) -> List[str]:
        """Docling supports various document formats"""
        return ['.pdf', '.docx', '.doc', '.pptx', '.html', '.md', '.txt']
