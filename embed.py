"""
Embedding + Pinecone vector storage.

Mirrors cookbook knowledge/docling/3-embedding.py responsibility:
one file, one job — turn text chunks into vectors and store them.
"""

import logging

from config import EMBEDDING_MODEL, PINECONE_INDEX, openai_client, pinecone_client

logger = logging.getLogger(__name__)


# --------------------------------------------------------------
# Embeddings — OpenAI batch embedding
# --------------------------------------------------------------


def embed_texts(texts: list[str], batch_size: int = 100) -> list[list[float]]:
    """Batch-embed texts using OpenAI.

    Args:
        texts:      List of text strings to embed.
        batch_size: Number of texts per API call.

    Returns:
        List of embedding vectors.
    """
    if openai_client is None:
        raise RuntimeError("OpenAI client not initialized.")

    sanitized = [t.strip() or "[empty]" for t in texts]
    all_embeddings: list[list[float]] = []

    for i in range(0, len(sanitized), batch_size):
        batch = sanitized[i : i + batch_size]
        logger.info("Embedding batch %d-%d of %d...", i, i + len(batch), len(sanitized))
        response = openai_client.embeddings.create(model=EMBEDDING_MODEL, input=batch)
        all_embeddings.extend([d.embedding for d in response.data])

    logger.info("Embedded %d texts.", len(all_embeddings))
    return all_embeddings


def embed_query(query: str) -> list[float]:
    """Embed a single query string. Returns embedding vector."""
    if openai_client is None:
        raise RuntimeError("OpenAI client not initialized.")

    response = openai_client.embeddings.create(model=EMBEDDING_MODEL, input=[query])
    return response.data[0].embedding


# --------------------------------------------------------------
# Pinecone — upsert and search
# --------------------------------------------------------------


def upsert_to_pinecone(
    chunks: list[dict], embeddings: list[list[float]], batch_size: int = 100
) -> None:
    """Batch upsert chunks and embeddings to Pinecone.

    Args:
        chunks:     List of chunk dicts with text, filename, chunk_index.
        embeddings: Corresponding embedding vectors.
        batch_size: Vectors per upsert call.
    """
    if pinecone_client is None:
        raise RuntimeError("Pinecone client not initialized.")

    index = pinecone_client.Index(PINECONE_INDEX)

    vectors = [
        {
            "id": f"{ch['filename']}_{ch['chunk_index']}",
            "values": emb,
            "metadata": {
                "text": ch["text"],
                "filename": ch["filename"],
                "chunk_index": ch["chunk_index"],
            },
        }
        for ch, emb in zip(chunks, embeddings)
    ]

    for i in range(0, len(vectors), batch_size):
        batch = vectors[i : i + batch_size]
        logger.info("Upserting batch %d-%d of %d...", i, i + len(batch), len(vectors))
        index.upsert(vectors=batch)

    logger.info("Upserted %d vectors to Pinecone.", len(vectors))


def search_pinecone(query: str, top_k: int = 5) -> list[dict]:
    """Embed query and search Pinecone.

    Args:
        query:  The search query string.
        top_k:  Number of results to return.

    Returns:
        List of dicts: [{"text": ..., "score": ..., "filename": ..., "chunk_index": ...}]
    """
    if pinecone_client is None:
        raise RuntimeError("Pinecone client not initialized.")

    query_vector = embed_query(query)
    index = pinecone_client.Index(PINECONE_INDEX)
    results = index.query(vector=query_vector, top_k=top_k, include_metadata=True)

    return [
        {
            "text": m.metadata.get("text", ""),
            "score": m.score,
            "filename": m.metadata.get("filename", ""),
            "chunk_index": m.metadata.get("chunk_index", 0),
        }
        for m in results.matches
    ]
