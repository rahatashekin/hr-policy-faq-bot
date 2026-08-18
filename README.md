# 🏢 HR Policy FAQ Bot

An AI-powered RAG (Retrieval-Augmented Generation) chatbot that answers employee policy questions using your company's HR documents. Built with **OpenAI**, **Pinecone**, **Google Drive**, and **Streamlit**.

## How It Works

```
                         INGESTION PIPELINE
Google Drive (PDFs) ──→ extract.py ──→ chunk.py ──→ embed.py ──→ Pinecone
                                                                    │
                              CHAT INTERFACE                        │
User Question ──→ chat.py (Streamlit) ──→ GPT-4o-mini Agent ──→ Search ──→ Answer
```

1. **Ingest**: PDFs are downloaded from Google Drive, text is extracted, split into chunks, embedded via OpenAI, and stored in Pinecone.
2. **Chat**: User asks a question → the AI agent searches Pinecone for relevant policy chunks → generates an answer with source citations.

## Sample Data

The `data/` folder contains 5 sample HR policy PDFs you can use to test the system:

- `01_HR_Leave_and_Attendance_Policy.pdf`
- `02_Road_Safety_and_Fleet_Operations_Manual.pdf`
- `03_Field_Travel_Allowance_and_Expense_Policy.pdf`
- `04_Emergency_Accident_Response_and_Health_Benefits.pdf`
- `05_Employee_Code_of_Conduct_and_Whistleblowing.pdf`

You can replace these with your own company's HR documents.

---

## Prerequisites

- Python 3.10+
- An [OpenAI](https://platform.openai.com/) account (for GPT-4o-mini and embeddings)
- A [Pinecone](https://www.pinecone.io/) account (for vector storage)
- A [Google Cloud](https://console.cloud.google.com/) project (for Drive API)

---

## Setup Guide

### Step 1: Clone & Install

```bash
git clone https://github.com/rahatashekin/hr-policy-faq-bot.git
cd hr-policy-faq-bot
pip install -r requirements.txt
```

### Step 2: Get OpenAI API Key

1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Click **"Create new secret key"**
3. Copy the key (starts with `sk-`)

### Step 3: Get Pinecone API Key

1. Go to [app.pinecone.io](https://app.pinecone.io/)
2. Create a free account
3. Go to **API Keys** → copy your key
4. Create an index:
   - Name: `hr-policy` (or any name you prefer)
   - Dimensions: `1536`
   - Metric: `cosine`
   - Cloud: any free tier option

### Step 4: Set Up Google Drive API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable the **Google Drive API**:
   - Go to **APIs & Services** → **Library**
   - Search "Google Drive API" → **Enable**
4. Create a **Service Account**:
   - Go to **APIs & Services** → **Credentials**
   - Click **"Create Credentials"** → **"Service Account"**
   - Give it a name → **Create**
   - Skip optional steps → **Done**
5. Create a **JSON key**:
   - Click on the service account you just created
   - Go to **Keys** tab → **Add Key** → **Create new key** → **JSON**
   - Save the downloaded file as `service_account.json` in the project root
6. **Share your Google Drive folder** with the service account:
   - Copy the service account email (looks like `name@project.iam.gserviceaccount.com`)
   - Go to Google Drive → right-click your folder → **Share**
   - Paste the service account email → **Viewer** access → **Send**
   - Copy the folder ID from the URL: `drive.google.com/drive/folders/` **`<THIS_IS_YOUR_FOLDER_ID>`**

### Step 5: Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your keys:

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
PINECONE_API_KEY=your-pinecone-api-key-here
DRIVE_FOLDER_ID=your-google-drive-folder-id
GOOGLE_SERVICE_ACCOUNT_FILE=service_account.json
```

### Step 6: Update Pinecone Index Name

In `config.py`, change the index name to match yours:

```python
PINECONE_INDEX: str = "hr-policy"   # Change to your index name
```

---

## Usage

### Ingest Documents

Upload your PDFs to the Google Drive folder, then run:

```bash
python ingest.py
```

This will: download PDFs → extract text → chunk → embed → store in Pinecone.

### Launch Chat Interface

```bash
streamlit run chat.py
```

Open `http://localhost:8501` in your browser and start asking questions about your HR policies.

---

## Project Structure

```
hr-policy-faq-bot/
├── config.py           # API clients & constants
├── extract.py          # Google Drive download + PDF/DOCX text extraction
├── chunk.py            # Text chunking (recursive character splitter)
├── embed.py            # OpenAI embeddings + Pinecone store/search
├── chat.py             # RAG Agent + Streamlit Chat UI
├── ingest.py           # Pipeline orchestrator (extract → chunk → embed)
├── data/               # Sample HR policy PDFs
├── tests/              # Unit tests
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
└── .gitignore          # Secrets excluded from git
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | OpenAI GPT-4o-mini |
| Embeddings | OpenAI text-embedding-3-small (1536 dims) |
| Vector DB | Pinecone |
| Document Source | Google Drive API (Service Account) |
| Text Extraction | PyPDF2, python-docx |
| Chat UI | Streamlit |

## License

MIT
