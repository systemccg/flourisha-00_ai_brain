"""
Extraction Backends
Pluggable document extraction backends for the AI Brain
"""

from .base import ExtractionBackend, ExtractionResult
from .claude_backend import ClaudeExtractionBackend
from .docling_backend import DoclingExtractionBackend

__all__ = [
    'ExtractionBackend',
    'ExtractionResult',
    'ClaudeExtractionBackend',
    'DoclingExtractionBackend'
]
