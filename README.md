# SalesPilot AI — Autonomous AI Sales Voice Agent

> A browser-based AI sales assistant that qualifies leads, retrieves company knowledge, books appointments, and surfaces CRM insights.

![SalesPilot AI Screenshot](docs/screenshot.png)

---

## 🚀 Features

| Feature | Implementation |
|---|---|
| AI Conversation | Gemini 3.8 Flash — contextual, role-aware |
| Speech-to-Text | Browser Web Speech API |
| Text-to-Speech | Browser SpeechSynthesis API |
| Company Knowledge (RAG) | Sentence Transformers + FAISS |
| Lead Qualification | Gemini extraction + Hot/Warm/Cold rules |
| Sentiment Analysis | Positive / Neutral / Negative |
| Appointment Booking | Validated and stored in SQLite |
| CRM Dashboard | Chart.js charts, leads & appointments tables |
| Multilingual | 7 languages supported |

---

## 📋 Prerequisites

- Python 3.10+
- pip
- Google Gemini API key ([Get one free](https://aistudio.google.com/app/apikey))
- Chrome/Edge for best voice support

---

## ⚙️ Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/salespilot-ai.git
cd salespilot-ai

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

---

## 🏃 Running Locally

```bash
uvicorn backend.main:app --reload --port 8000
```

Then open **http://localhost:8000** in your browser.

> **Note:** First run will download the Sentence Transformer model (~90 MB). This is a one-time download.

---

## 📁 Project Structure

```
SalesPilot-AI/
├── backend/
│   ├── main.py               # FastAPI application & all endpoints
│   ├── agent.py              # Gemini conversation + RAG context
│   ├── rag.py                # Sentence Transformers + FAISS index
│   ├── lead_qualification.py # Lead extraction & classification
│   ├── booking.py            # Appointment validation & persistence
│   └── database.py           # SQLite CRUD operations
├── frontend/
│   ├── index.html            # Single-page app
│   ├── style.css             # Dark glassmorphism design system
│   └── script.js             # Chat, voice I/O, CRM dashboard
├── data/
│   └── company_knowledge.txt # TechVista Solutions knowledge base
├── docs/
│   └── architecture.png      # System architecture diagram
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── PROJECT_REPORT.md
```

---

## 🔑 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Serve frontend |
| `/chat` | POST | Process customer message |
| `/leads` | GET | Retrieve all leads |
| `/leads` | POST | Trigger lead extraction & save |
| `/appointments` | GET | Retrieve all appointments |
| `/appointments` | POST | Save appointment request |
| `/summary` | POST | Generate conversation summary |
| `/insights` | GET | Dashboard metrics |
| `/reset` | POST | Reset session history |

---

## 🎤 Using Voice

1. Click the **microphone button** (🎙) to start speaking.
2. The recognised text appears in the input box.
3. On silence, the message is automatically sent.
4. The AI response is spoken aloud via text-to-speech.
5. Use the language selector to switch languages.

> If the microphone is unavailable, use the text input as a fallback.

---

## 🔒 Security

- API keys are stored in `.env` — **never committed to Git**.
- `.gitignore` excludes `.env` and the SQLite database file.
- Input is validated before database writes.

---

## 🌐 Scalability Notes

The MVP runs locally with SQLite. For production at scale:
- Deploy multiple FastAPI instances behind a load balancer.
- Migrate to PostgreSQL with connection pooling.
- Use Redis for session state.
- Use a managed vector DB (Pinecone, Qdrant) for RAG.
- Integrate telephony (Twilio, Vapi) for real phone calls.

See `PROJECT_REPORT.md` for the full scalability discussion.

---

## 📄 License

MIT
