"""
Text extraction — Google Drive file download + PDF/DOCX/text parsing.

Mirrors cookbook knowledge/docling/1-extraction.py responsibility:
one file, one job — get text out of documents.
"""

import io
import logging

import PyPDF2
import docx

from config import DRIVE_FOLDER_ID, get_drive_service

logger = logging.getLogger(__name__)


# --------------------------------------------------------------
# Google Drive — list and download files
# --------------------------------------------------------------


def list_drive_files(folder_id: str | None = None) -> list[dict]:
    """List all files in a Google Drive folder.

    Returns list of dicts: [{"id": ..., "name": ..., "mimeType": ...}]
    """
    folder_id = folder_id or DRIVE_FOLDER_ID
    service = get_drive_service()
    if service is None:
        return []

    query = f"'{folder_id}' in parents and trashed=false"
    response = (
        service.files()
        .list(q=query, fields="files(id,name,mimeType)", pageSize=100)
        .execute()
    )
    files = response.get("files", [])
    logger.info("Listed %d files from folder %s", len(files), folder_id)
    return files


def download_file(file_id: str, file_name: str, mime_type: str = "") -> bytes:
    """Download a file's binary content from Google Drive."""
    service = get_drive_service()
    if service is None:
        raise RuntimeError("Google Drive service unavailable.")

    if mime_type.startswith("application/vnd.google-apps."):
        logger.info("Exporting Google Doc '%s' as PDF", file_name)
        content = (
            service.files()
            .export_media(fileId=file_id, mimeType="application/pdf")
            .execute()
        )
    else:
        logger.info("Downloading file '%s'", file_name)
        content = service.files().get_media(fileId=file_id).execute()

    logger.info("Downloaded %d bytes for '%s'", len(content), file_name)
    return content


# --------------------------------------------------------------
# Text extraction — PDF, DOCX, plain text
# --------------------------------------------------------------


def extract_text(file_bytes: bytes, mime_type: str, filename: str = "") -> str:
    """Extract plain text from a file's binary content.

    Supports PDF (PyPDF2), DOCX (python-docx), and plain text (UTF-8).
    """
    label = filename or mime_type

    try:
        if mime_type == "application/pdf" or filename.lower().endswith(".pdf"):
            reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
            logger.info("Extracted %d chars from PDF '%s'", len(text), label)
            return text

        elif filename.lower().endswith(".docx") or "wordprocessingml" in mime_type:
            doc = docx.Document(io.BytesIO(file_bytes))
            text = "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
            logger.info("Extracted %d chars from DOCX '%s'", len(text), label)
            return text

        else:
            text = file_bytes.decode("utf-8", errors="replace")
            logger.info("Extracted %d chars from text file '%s'", len(text), label)
            return text

    except Exception as exc:
        logger.error("Extraction failed for '%s': %s", label, exc)
        return ""
