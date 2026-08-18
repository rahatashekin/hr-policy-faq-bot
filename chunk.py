"""
Text chunking — split extracted text into overlapping chunks with metadata.

Mirrors cookbook knowledge/docling/2-chunking.py responsibility:
one file, one job — split text into searchable chunks.
"""

import logging

from config import CHUNK_SIZE

logger = logging.getLogger(__name__)


def chunk_text(text: str, filename: str, chunk_size: int | None = None) -> list[dict]:
    """Split text into chunks with metadata.

    Uses a recursive character splitter with paragraph-aware boundaries.
    Split priority: paragraph → newline → sentence → hard character limit.

    Args:
        text:       The full extracted text.
        filename:   Source filename (stored in metadata).
        chunk_size: Max characters per chunk. Defaults to config CHUNK_SIZE.

    Returns:
        List of dicts: [{"text": ..., "filename": ..., "chunk_index": ...}]
    """
    chunk_size = chunk_size or CHUNK_SIZE

    if not text.strip():
        return []

    raw_chunks = _recursive_split(text, chunk_size)
    chunks = []
    for idx, raw in enumerate(raw_chunks):
        cleaned = raw.strip()
        if cleaned:
            chunks.append({"text": cleaned, "filename": filename, "chunk_index": idx})

    logger.info("Chunked '%s' into %d chunks (size=%d)", filename, len(chunks), chunk_size)
    return chunks


def _recursive_split(text: str, max_len: int) -> list[str]:
    """Recursively split text by paragraph → newline → sentence → char limit."""
    if len(text) <= max_len:
        return [text]

    for sep in ["\n\n", "\n", ". ", " "]:
        parts = text.split(sep)
        if len(parts) > 1:
            result, current = [], ""
            for part in parts:
                candidate = f"{current}{sep}{part}" if current else part
                if len(candidate) <= max_len:
                    current = candidate
                else:
                    if current:
                        result.append(current)
                    current = part
            if current:
                result.append(current)

            final = []
            for chunk in result:
                if len(chunk) > max_len:
                    final.extend(_recursive_split(chunk, max_len))
                else:
                    final.append(chunk)
            return final

    return [text[i : i + max_len] for i in range(0, len(text), max_len)]
