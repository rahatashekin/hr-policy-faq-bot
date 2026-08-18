# HR Policy FAQ Bot

AI-powered RAG chatbot for employee policy queries — built with OpenAI, Pinecone, and Streamlit.

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
├── config.py           # API clients & constants
├── extract.py          # Google Drive + PDF/DOCX extraction
├── chunk.py            # Text chunking
├── embed.py            # Embedding + Pinecone store/search
├── chat.py             # RAG Agent + Streamlit Chat UI
├── ingest.py           # Pipeline orchestrator
├── requirements.txt
├── .env.example
└── tests/
```

## Tech Stack

- **OpenAI** — GPT-4o-mini (chat) + text-embedding-3-small (embeddings)
- **Pinecone** — Vector database
- **Google Drive API** — Document source (service account)
- **Streamlit** — Chat interface
- **PyPDF2 / python-docx** — Text extraction
