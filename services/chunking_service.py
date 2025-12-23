"""
Agentic Chunking Service
Intelligent semantic chunking using Claude (adopted from n8n RAG pattern)
"""
import os
import json
from typing import List
from anthropic import Anthropic


class AgenticChunker:
    """
    Intelligent semantic chunking using Claude
    Adopted from n8n's proven LangChain agentic chunking approach
    """

    def __init__(
        self,
        max_chunk_size: int = 1000,
        min_chunk_size: int = 400
    ):
        """
        Initialize agentic chunker

        Args:
            max_chunk_size: Maximum characters per chunk
            min_chunk_size: Minimum characters per chunk
        """
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.client = Anthropic(api_key=self.api_key)
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size

    async def chunk(self, text: str) -> List[str]:
        """
        Split text into semantically coherent chunks

        Same approach as n8n's LangChain agentic chunking:
        - AI determines natural split points
        - Respects semantic boundaries (headings, topics, paragraphs)
        - Enforces min/max chunk sizes
        - Merges undersized chunks

        Args:
            text: Text to chunk

        Returns:
            List of semantic chunks
        """
        # For very short text, return as single chunk
        if len(text) < self.min_chunk_size:
            return [text]

        try:
            response = self.client.messages.create(
                model='claude-sonnet-4-5-20250929',
                max_tokens=4096,
                temperature=0,  # Deterministic splitting
                messages=[{
                    'role': 'user',
                    'content': f"""Split the following text into semantic chunks.

RULES:
1. Each chunk should be a complete thought, topic, or section
2. Respect natural boundaries:
   - Section headings
   - Topic changes
   - Paragraph breaks
   - List boundaries
3. Minimum chunk size: {self.min_chunk_size} characters
4. Maximum chunk size: {self.max_chunk_size} characters
5. Merge chunks under {self.min_chunk_size} chars with adjacent chunks
6. Don't split mid-sentence or mid-thought
7. Preserve all original text (no summarization)

TEXT TO CHUNK:
{text}

OUTPUT FORMAT (JSON only, no markdown):
{{
  "chunks": [
    "First semantic chunk...",
    "Second semantic chunk...",
    ...
  ]
}}
"""
                }]
            )

            # Parse Claude's response
            result_text = response.content[0].text.strip()

            # Remove markdown code blocks if present
            if result_text.startswith('```'):
                lines = result_text.split('\n')
                result_text = '\n'.join(lines[1:-1])

            result = json.loads(result_text)
            chunks = result['chunks']

            # Post-process: merge undersized chunks
            chunks = self._merge_small_chunks(chunks)

            return chunks

        except (json.JSONDecodeError, KeyError) as e:
            # Fallback: simple splitting if AI response invalid
            print(f"Agentic chunking failed, using fallback: {e}")
            return self._fallback_chunk(text)

    def _merge_small_chunks(self, chunks: List[str]) -> List[str]:
        """
        Merge chunks that are too small (same logic as n8n)

        Args:
            chunks: List of chunks from AI

        Returns:
            List of merged chunks
        """
        merged = []
        buffer = ""

        for chunk in chunks:
            if len(buffer) + len(chunk) < self.min_chunk_size:
                # Accumulate small chunks
                buffer += " " + chunk if buffer else chunk
            else:
                if buffer:
                    merged.append(buffer)
                buffer = chunk

        if buffer:
            # Add remaining buffer
            if merged and len(buffer) < self.min_chunk_size:
                merged[-1] += " " + buffer
            else:
                merged.append(buffer)

        return merged

    def _fallback_chunk(self, text: str) -> List[str]:
        """
        Simple paragraph-based chunking as fallback

        Args:
            text: Text to chunk

        Returns:
            List of chunks
        """
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) > self.max_chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks


# Singleton instance
_chunker = None


def get_chunker(max_chunk_size: int = 1000, min_chunk_size: int = 400) -> AgenticChunker:
    """Get or create agentic chunker singleton"""
    global _chunker
    if _chunker is None or _chunker.max_chunk_size != max_chunk_size:
        _chunker = AgenticChunker(max_chunk_size, min_chunk_size)
    return _chunker


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[str]:
    """
    Simple text chunking without AI.

    Splits text into overlapping chunks for embedding.
    Falls back to basic character-based chunking.

    Args:
        text: Text to chunk
        chunk_size: Target characters per chunk
        chunk_overlap: Overlap between chunks

    Returns:
        List of text chunks
    """
    if not text or len(text) < chunk_size:
        return [text] if text else []

    chunks = []
    start = 0

    while start < len(text):
        # Find the end of this chunk
        end = start + chunk_size

        # If we're not at the end, try to find a good break point
        if end < len(text):
            # Try to break at paragraph
            para_break = text.rfind('\n\n', start, end)
            if para_break > start + chunk_size // 2:
                end = para_break + 2
            else:
                # Try to break at sentence
                for punct in ['. ', '! ', '? ']:
                    sent_break = text.rfind(punct, start, end)
                    if sent_break > start + chunk_size // 2:
                        end = sent_break + 2
                        break

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move start forward with overlap
        start = end - chunk_overlap if end < len(text) else len(text)

    return chunks
