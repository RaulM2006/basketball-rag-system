---
title: CourtVision AI
emoji: 🏀
colorFrom: yellow
colorTo: red
sdk: docker
app_port: 7860
pinned: false
---

# CourtVision AI 🏀

CourtVision AI is an end-to-end **Multimodal RAG (Retrieval-Augmented Generation)** basketball coaching system. It analyzes a user's uploaded jump shot video frame-by-frame, identifies biomechanical form errors, and queries a local vector database to provide verified coaching corrections and timestamped YouTube drill tutorials.

---

## 🚀 Key Features

*   **Multimodal Biomechanical Analysis**: Uploads raw jump shot videos directly to Gemini 2.5 Flash to evaluate anatomical markers:
    *   *Base & Knee Load* (stance width and balance)
    *   *Elbow Alignment* (chicken wing detection)
    *   *Release & Guide Hand* (interference and wrist flick)
*   **Local Vector Knowledge Base**: ChromaDB database populated with transcript chunks scraped from YouTube coaching videos (e.g., shooting expert Coach Mike Dunn).
*   **API Throttling & Idempotency**: Safe ingestion script featuring document batching (size 20) and throttling sleep (10 seconds) to respect Google Free Tier API rate limits. Uses deterministic chunk IDs to avoid duplicate data entries on reruns.
*   **FastAPI Backend**: Clean Rest API router featuring CORS, video file-type validation, and streaming file-size checks (Max 10MB limit) to protect memory allocation.
*   **Interactive Glassmorphic Dashboard**: A self-contained, responsive dark-mode dashboard served directly by the FastAPI app. Includes drag-and-drop uploads, visual status logs, and markdown link rendering.

---

## 🛠️ Technology Stack

*   **Framework**: FastAPI (Python 3.14+)
*   **LLM & Embeddings**: Google GenAI SDK (`gemini-2.5-flash` & `gemini-embedding-2`)
*   **Vector Database**: ChromaDB (integrated via LangChain)
*   **Data Prep**: yt-dlp (audio extraction) & OpenAI Whisper (transcription)
*   **Frontend**: HTML5, Vanilla CSS3 (tactical dark theme), JavaScript (Fetch & marked.js)

---

## 📦 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/RaulM2006/basketball-rag-system.git
cd basketball-rag-system
```

### 2. Install Dependencies
Ensure you are in your Python environment and run:
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy the template configuration file:
```bash
cp .env.example .env
```
Open `.env` and fill in your actual Gemini API key:
```env
MULTIMODAL_LLM_API_KEY=your_actual_gemini_api_key_here
CHROMA_DB_DIRECTORY=./db
MAX_VIDEO_UPLOAD_SIZE_MB=10
```

### 4. Populate the Vector Database
Ingest the pre-chunked transcription JSON files from `data/transcriptions/` into your local ChromaDB collection:
```bash
python ingest.py
```
*(On completion, the script will automatically run a test query to verify documents are successfully stored.)*

---

## 🏃 Running the Application

Start the FastAPI backend server:
```bash
uvicorn main:app --reload
```

Once the server is running:
1.  Open your browser and navigate to: **`http://127.0.0.1:8000/`**
2.  Drag and drop a short (5-10 second) basketball shooting video (Max 10MB, support for `.mp4`, `.mov`).
3.  Click **Analyze Shooting Form**.
4.  Review your personalized, interactive biomechanical coaching report with direct timestamp links to corrective drills on YouTube!

---

## 📁 Project Directory Structure

```
├── api/
│   └── routes.py             # FastAPI REST upload & size validation endpoints
├── core/
│   ├── extractor.py          # Uploads video to Gemini File API and waits for processing
│   ├── generator.py          # Orchestrates full visual analysis + RAG retrieval
│   └── retriever.py          # Queries ChromaDB vectors and returns clean dictionaries
├── data/
│   ├── transcriptions/       # Chunked coaching JSON transcripts
│   ├── yt_links.txt          # Scraped source YouTube coaching reference videos
│   └── README.md             # Transcription metadata documentation
├── static/
│   ├── index.html            # Main dashboard HTML template
│   ├── style.css             # Glassmorphic tactical dark theme styles
│   └── app.js                # Frontend drag-and-drop controller & API fetch caller
├── ingest.py                 # Ingestion script to embed and save transcripts
├── main.py                   # FastAPI entrypoint and static file mount
├── requirements.txt          # Python package requirements
└── .gitignore                # Standard repository gitignore config
```

---

## 🤝 Contributing
Feel free to fork this repository, submit issues, or create pull requests to enhance the biomechanical model, add support for more models, or expand the database!
