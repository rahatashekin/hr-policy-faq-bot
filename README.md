# BRAC RSP Customer Support RAG FAQ Bot

AI-powered chatbot for BRAC Road Safety Programme employee policy queries — built with OpenAI, Pinecone, and Streamlit.

## Architecture

```
Google Drive (PDFs) → ingest.py → OpenAI Embeddings → Pinecone
                                                         ↓
User Question → chat.py (Streamlit) → GPT-4o-mini Agent → Pinecone Search → Answer
```

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env       # Edit with your API keys
```

## Usage

```bash
# Ingest documents from Google Drive → Pinecone
python ingest.py

# Launch chat interface
streamlit run chat.py
```

## Project Structure

```
brac-rsp-faq-bot/
├── config.py           # API clients & constants
├── ingest.py           # Drive → Extract → Chunk → Embed → Pinecone
├── chat.py             # RAG Agent + Streamlit Chat UI
├── requirements.txt
├── .env / .env.example
├── .gitignore
├── service_account.json   # Google Drive auth (gitignored)
├── scripts/               # Dev utilities
└── tests/
    └── test_pipeline.py
```

## Tech Stack

- **OpenAI** — GPT-4o-mini (chat) + text-embedding-3-small (embeddings)
- **Pinecone** — Vector database
- **Google Drive API** — Document source (service account auth)
- **Streamlit** — Chat interface
- **PyPDF2 / python-docx** — Text extraction
