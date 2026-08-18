"""
Ingestion pipeline orchestrator — calls extract → chunk → embed in sequence.

Run: python ingest.py
"""

import logging

from extract import download_file, extract_text, list_drive_files
from chunk import chunk_text
from embed import embed_texts, upsert_to_pinecone

logger = logging.getLogger(__name__)


def run_ingestion(folder_id: str | None = None) -> None:
    """Run the full pipeline: Drive → Extract → Chunk → Embed → Pinecone."""
    logger.info("=" * 60)
    logger.info("Starting BRAC RSP Knowledge Ingestion Pipeline")
    logger.info("=" * 60)

    files = list_drive_files(folder_id)
    if not files:
        logger.warning("No files found. Exiting.")
        return

    success = 0
    for idx, f in enumerate(files, 1):
        logger.info("[%d/%d] Processing: %s", idx, len(files), f["name"])
        try:
            file_bytes = download_file(f["id"], f["name"], f.get("mimeType", ""))
            text = extract_text(file_bytes, f.get("mimeType", ""), f["name"])
            if not text.strip():
                logger.warning("No text from '%s'. Skipping.", f["name"])
                continue

            chunks = chunk_text(text, f["name"])
            if not chunks:
                continue

            embeddings = embed_texts([ch["text"] for ch in chunks])
            upsert_to_pinecone(chunks, embeddings)

            logger.info("Done: '%s' (%d chunks)", f["name"], len(chunks))
            success += 1
        except Exception as exc:
            logger.error("Failed '%s': %s", f["name"], exc, exc_info=True)

    logger.info("=" * 60)
    logger.info("Ingestion complete: %d/%d files.", success, len(files))
    logger.info("=" * 60)


if __name__ == "__main__":
    run_ingestion()
