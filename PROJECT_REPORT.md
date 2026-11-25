# SalesPilot AI — Project Report

**Student / Developer:** [Your Name]  
**Submission Date:** November 2026  
**Category:** AI / Autonomous Agents

---

## 1. Project Title and Objective

**SalesPilot AI** — An Autonomous AI Sales Voice Agent that conducts intelligent sales conversations, qualifies leads, books appointments, and presents business insights through a CRM dashboard.

**Objective:** Build a browser-based AI sales assistant that can replace or augment the initial stage of the sales funnel, reducing manual effort while consistently capturing lead data.

---

## 2. Business Problem

Businesses that receive high volumes of sales enquiries face several challenges:

- Repetitive first-contact calls or chats that consume sales agent time.
- Inconsistent capture of lead details (name, requirement, budget).
- Delayed follow-up due to disorganised records.
- Difficulty operating outside business hours without additional cost.

Manual handling of these activities is time-consuming, error-prone, and difficult to scale.

---

## 3. Proposed Solution

SalesPilot AI is a browser-based prototype that simulates an intelligent AI sales agent:

- Accepts voice or text input from a customer.
- Maintains conversation context using Gemini 3.8 Flash.
- Answers company-specific questions using Retrieval-Augmented Generation (RAG).
- Extracts structured lead details and classifies the lead as Hot, Warm, or Cold.
- Identifies customer sentiment (Positive / Neutral / Negative).
- Books appointment requests and stores them in a local database.
- Generates conversation summaries and surfaces insights in a CRM dashboard.

---

## 4. Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| Frontend | HTML, CSS, JavaScript | Lightweight, universal, no build step |
| Backend | Python + FastAPI | Fast async API, easy Python integrations |
| AI Model | Gemini 3.8 Flash | Free tier, strong instruction-following |
| STT | Web Speech API | Browser-native, no external API cost |
| TTS | SpeechSynthesis API | Browser-native, multilingual support |
| RAG | Sentence Transformers + FAISS | Open-source, local, no external vector DB |
| Database | SQLite | Zero-config, file-based, sufficient for MVP |
| Charts | Chart.js | Lightweight, CDN-available |

---

## 5. Architecture and End-to-End Workflow

```
Customer (voice/text)
        │
        ▼
  Frontend (HTML/JS)
  - Web Speech API (STT)
  - SpeechSynthesis (TTS)
        │ POST /chat
        ▼
  FastAPI Backend
        │
        ├─► RAG Engine (FAISS) ──► company_knowledge.txt
        ├─► Gemini 3.8 Flash  ──► AI response
        └─► Lead Qualification ──► Hot/Warm/Cold + Sentiment
                │
                ▼
         SQLite Database
         (leads + appointments)
                │
                ▼
         CRM Dashboard
         (Chart.js + tables)
```

The customer's message is augmented with relevant company knowledge before being sent to Gemini, enabling accurate, grounded answers without hallucination.

---

## 6. Implemented Features

- ✅ Text-based AI sales conversation with context memory
- ✅ Browser voice input (Web Speech API) with text fallback
- ✅ Text-to-speech AI response playback
- ✅ Multilingual support (7 languages)
- ✅ RAG-based company knowledge retrieval (Sentence Transformers + FAISS)
- ✅ Lead qualification — Hot / Warm / Cold
- ✅ Sentiment detection — Positive / Neutral / Negative
- ✅ Appointment request booking and validation
- ✅ SQLite persistence for leads and appointments
- ✅ Conversation summary generation
- ✅ CRM dashboard with KPI cards and Chart.js doughnut charts
- ✅ Dark glassmorphism premium UI

---

## 7. Scalability and Security Approach

**Scalability (for 1,00,000 users):**
1. Deploy multiple FastAPI instances behind a load balancer (e.g., nginx, AWS ALB).
2. Replace SQLite with PostgreSQL and use connection pooling (asyncpg / pgBouncer).
3. Use Redis for in-memory session/conversation state.
4. Use a managed vector database (Pinecone, Qdrant) for RAG at scale.
5. Apply rate limiting, retries, and circuit breakers on Gemini API calls.
6. Integrate telephony (Twilio, Vapi, Retell) for real inbound/outbound calls.
7. Use APM tools (Datadog, New Relic) for observability.

**Security:**
- API keys stored in `.env` — excluded from Git via `.gitignore`.
- Input validated before database writes.
- No unnecessary personal data collected.
- HTTPS required for any deployed instance.

---

## 8. Commercial Feasibility and Future Enhancements

**Business value:**
- Reduces first-level enquiry handling effort.
- Captures consistent, structured lead data automatically.
- Helps sales teams prioritise hot leads.
- Enables 24/7 coverage without additional staffing.

**Potential revenue model:**
- SaaS subscription: ₹2,000–₹10,000/month per business depending on conversations handled.
- Usage-based: charged per qualified lead or per conversation minute.

**Future enhancements:**
1. Real telephony integration (Twilio / Vapi).
2. CRM integrations (Salesforce, HubSpot, Zoho).
3. Email/WhatsApp channel support.
4. Advanced lead scoring with ML models.
5. Admin panel with authentication and role-based access.
6. Production-grade deployment with Docker and CI/CD.
