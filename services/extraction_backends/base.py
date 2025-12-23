"""
Base Extraction Backend
Abstract interface for document extraction backends
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class ExtractionConfidence(Enum):
    """Confidence level of extraction"""
    HIGH = "high"       # Structured data, clear text
    MEDIUM = "medium"   # Some ambiguity, OCR required
    LOW = "low"         # Poor quality, uncertain


@dataclass
class ExtractedEntity:
    """An entity extracted from a document"""
    name: str
    entity_type: str  # e.g., "medication", "person", "date", "condition"
    value: Optional[str] = None
    confidence: ExtractionConfidence = ExtractionConfidence.MEDIUM
    source_text: Optional[str] = None  # Original text this was extracted from
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractedRelationship:
    """A relationship between entities"""
    source_entity: str
    target_entity: str
    relationship_type: str  # e.g., "PRESCRIBED", "STOPPED", "TREATS"
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractionResult:
    """Result of document extraction"""
    # Raw content
    raw_text: str
    markdown: Optional[str] = None

    # Structured data
    entities: List[ExtractedEntity] = field(default_factory=list)
    relationships: List[ExtractedRelationship] = field(default_factory=list)

    # Document metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Extraction info
    backend_name: str = "unknown"
    extraction_timestamp: datetime = field(default_factory=datetime.utcnow)
    confidence: ExtractionConfidence = ExtractionConfidence.MEDIUM

    # Validation
    validation_errors: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)

    def is_valid(self) -> bool:
        """Check if extraction passed validation"""
        return len(self.validation_errors) == 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "raw_text": self.raw_text,
            "markdown": self.markdown,
            "entities": [
                {
                    "name": e.name,
                    "type": e.entity_type,
                    "value": e.value,
                    "confidence": e.confidence.value,
                    "source_text": e.source_text,
                    "metadata": e.metadata
                }
                for e in self.entities
            ],
            "relationships": [
                {
                    "source": r.source_entity,
                    "target": r.target_entity,
                    "type": r.relationship_type,
                    "properties": r.properties
                }
                for r in self.relationships
            ],
            "metadata": self.metadata,
            "backend": self.backend_name,
            "timestamp": self.extraction_timestamp.isoformat(),
            "confidence": self.confidence.value,
            "validation": {
                "errors": self.validation_errors,
                "warnings": self.validation_warnings,
                "is_valid": self.is_valid()
            }
        }


class ExtractionBackend(ABC):
    """
    Abstract base class for extraction backends.

    Implementations can include:
    - ClaudeExtractionBackend (using Claude's native PDF reading)
    - DoclingExtractionBackend (using Docling API)
    - TesseractBackend (basic OCR fallback)
    - VisionBackend (for image-heavy documents)
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Backend identifier name"""
        pass

    @property
    @abstractmethod
    def supports_batch(self) -> bool:
        """Whether this backend supports batch processing"""
        pass

    @abstractmethod
    async def extract(
        self,
        file_path: str,
        extract_entities: bool = True,
        entity_types: Optional[List[str]] = None
    ) -> ExtractionResult:
        """
        Extract content from a document.

        Args:
            file_path: Path to the document
            extract_entities: Whether to extract structured entities
            entity_types: Optional list of entity types to extract
                         e.g., ["medication", "person", "date", "condition"]

        Returns:
            ExtractionResult with text, entities, and metadata
        """
        pass

    @abstractmethod
    async def extract_batch(
        self,
        file_paths: List[str],
        extract_entities: bool = True,
        entity_types: Optional[List[str]] = None
    ) -> List[ExtractionResult]:
        """
        Extract content from multiple documents.

        Args:
            file_paths: List of paths to documents
            extract_entities: Whether to extract structured entities
            entity_types: Optional list of entity types to extract

        Returns:
            List of ExtractionResults
        """
        pass

    @abstractmethod
    async def validate_extraction(
        self,
        result: ExtractionResult,
        original_file_path: str
    ) -> ExtractionResult:
        """
        Validate extraction results for accuracy.

        This should check for:
        - Hallucinated content (text not in original)
        - Missing critical sections
        - Malformed entities

        Args:
            result: The extraction result to validate
            original_file_path: Path to original document for comparison

        Returns:
            ExtractionResult with validation_errors/warnings populated
        """
        pass

    def get_supported_formats(self) -> List[str]:
        """Return list of supported file extensions"""
        return ['.pdf', '.docx', '.doc', '.txt', '.md']

    def is_format_supported(self, file_path: str) -> bool:
        """Check if file format is supported"""
        from pathlib import Path
        ext = Path(file_path).suffix.lower()
        return ext in self.get_supported_formats()
