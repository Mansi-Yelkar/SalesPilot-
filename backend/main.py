"""
main.py — FastAPI application entry point for SalesPilot AI.
"""

import uuid
import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from backend import database, agent
from backend.lead_qualification import extract_lead_data
from backend.booking import book_appointment
from backend.rag import rag_engine

# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------
database.init_db()
rag_engine.build()

app = FastAPI(title="SalesPilot AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", response_class=FileResponse)
async def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    language: Optional[str] = "English"


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    turn_count: int


class LeadIn(BaseModel):
    session_id: str


class AppointmentIn(BaseModel):
    session_id: str
    customer_name: Optional[str] = None
    preferred_date: Optional[str] = None
    preferred_time: Optional[str] = None
    requirement: Optional[str] = None


class SummaryRequest(BaseModel):
    session_id: str


class ResetRequest(BaseModel):
    session_id: str


# ---------------------------------------------------------------------------
# Track turn counts per session (in-memory)
# ---------------------------------------------------------------------------
_turn_counts: dict = {}


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    reply = agent.chat(session_id, req.message, req.language or "English")

    # Increment turn counter
    _turn_counts[session_id] = _turn_counts.get(session_id, 0) + 1
    turn_count = _turn_counts[session_id]

    # Auto-extract and save lead every 5 turns and at end
    if turn_count >= 3 and turn_count % 5 == 3:
        _auto_save_lead(session_id)

    return ChatResponse(session_id=session_id, reply=reply, turn_count=turn_count)


def _auto_save_lead(session_id: str) -> None:
    """Extract lead data from conversation and persist to DB."""
    try:
        convo = agent.get_conversation_text(session_id)
        summary = agent.generate_summary(session_id)
        lead_data = extract_lead_data(convo)
        database.save_lead(
            session_id=session_id,
            customer_name=lead_data.get("customer_name"),
            business_type=lead_data.get("business_type"),
            requirement=lead_data.get("requirement"),
            budget=lead_data.get("budget"),
            contact=lead_data.get("contact"),
            lead_category=lead_data.get("lead_category", "Cold"),
            sentiment=lead_data.get("sentiment", "Neutral"),
            summary=summary,
        )
    except Exception as exc:
        print(f"[main] Auto-save lead error: {exc}")


@app.get("/leads")
async def get_leads():
    return database.get_all_leads()


@app.post("/leads")
async def save_lead_endpoint(req: LeadIn):
    """Manually trigger lead extraction and save for a session."""
    convo = agent.get_conversation_text(req.session_id)
    if not convo.strip():
        raise HTTPException(status_code=400, detail="No conversation found for this session.")
    summary = agent.generate_summary(req.session_id)
    lead_data = extract_lead_data(convo)
    lead_id = database.save_lead(
        session_id=req.session_id,
        customer_name=lead_data.get("customer_name"),
        business_type=lead_data.get("business_type"),
        requirement=lead_data.get("requirement"),
        budget=lead_data.get("budget"),
        contact=lead_data.get("contact"),
        lead_category=lead_data.get("lead_category", "Cold"),
        sentiment=lead_data.get("sentiment", "Neutral"),
        summary=summary,
    )
    return {"lead_id": lead_id, "lead_data": lead_data, "summary": summary}


@app.get("/appointments")
async def get_appointments():
    return database.get_all_appointments()


@app.post("/appointments")
async def create_appointment(req: AppointmentIn):
    success, message = book_appointment(
        session_id=req.session_id,
        customer_name=req.customer_name,
        preferred_date=req.preferred_date,
        preferred_time=req.preferred_time,
        requirement=req.requirement,
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}


@app.post("/summary")
async def get_summary(req: SummaryRequest):
    convo = agent.get_conversation_text(req.session_id)
    if not convo.strip():
        raise HTTPException(status_code=400, detail="No conversation found.")
    summary = agent.generate_summary(req.session_id)
    return {"summary": summary}


@app.get("/insights")
async def get_insights():
    return database.get_insights()


@app.post("/reset")
async def reset_session(req: ResetRequest):
    agent.reset_session(req.session_id)
    _turn_counts.pop(req.session_id, None)
    return {"message": f"Session {req.session_id} reset."}


@app.get("/health")
async def health():
    return {"status": "ok"}
