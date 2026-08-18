"""Configuration — environment variables, API clients, and constants."""

import logging
import os

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from openai import OpenAI
from pinecone import Pinecone

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
load_dotenv()

OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
DRIVE_FOLDER_ID: str = os.getenv(
    "DRIVE_FOLDER_ID", "1JyaRSZUKGLghqNi7oZX0zFb3eoW99RPZ"
)
GOOGLE_SERVICE_ACCOUNT_FILE: str = os.getenv(
    "GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json"
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
EMBEDDING_MODEL: str = "text-embedding-3-small"
CHAT_MODEL: str = "gpt-4o-mini"
PINECONE_INDEX: str = "niloy"
CHUNK_SIZE: int = 500
CHUNK_OVERLAP: int = 50

# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------

openai_client: OpenAI | None = None
if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    logger.info("OpenAI client initialized.")
else:
    logger.warning("OPENAI_API_KEY not set.")

pinecone_client: Pinecone | None = None
if PINECONE_API_KEY:
    pinecone_client = Pinecone(api_key=PINECONE_API_KEY)
    logger.info("Pinecone client initialized.")
else:
    logger.warning("PINECONE_API_KEY not set.")


def get_drive_service():
    """Build and return the Google Drive API v3 service."""
    if not os.path.exists(GOOGLE_SERVICE_ACCOUNT_FILE):
        logger.warning("Service account file not found: %s", GOOGLE_SERVICE_ACCOUNT_FILE)
        return None
    try:
        credentials = service_account.Credentials.from_service_account_file(
            GOOGLE_SERVICE_ACCOUNT_FILE,
            scopes=["https://www.googleapis.com/auth/drive.readonly"],
        )
        service = build("drive", "v3", credentials=credentials)
        logger.info("Google Drive service initialized.")
        return service
    except Exception as exc:
        logger.error("Failed to initialize Google Drive service: %s", exc)
        return None
