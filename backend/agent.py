"""
agent.py — Core AI agent using Gemini with conversation memory and RAG.
"""

import os
from typing import List, Dict, Any

import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from dotenv import load_dotenv

from backend.rag import rag_engine

load_dotenv(override=True)

SYSTEM_PROMPT = """You are SalesPilot, a friendly, persuasive, and professional AI sales assistant for Fortivex AI — an industry-leading AI automation company.

Your role:
1. Greet customers warmly and ask about their business needs.
2. Understand their business type, operational challenges, requirements, and budget.
3. Answer questions about Fortivex AI services accurately using the company knowledge provided.
4. Qualify the lead naturally by gathering: Customer Name, Business Type, Specific Requirement, Budget, and Contact (phone/email).
5. Recommend relevant Fortivex AI solutions and highlight tangible ROI (e.g. 30-60% ticket reduction, 24/7 availability).
6. Actively offer to schedule a live product demonstration or sales appointment.
7. If the customer indicates interest in a demo/appointment, ask for their preferred date and time.
8. CRITICAL LANGUAGE RULE: Always reply in the EXACT language specified. If Hindi is selected, reply in fluent Hindi (Devanagari script). If Spanish, reply in Spanish. If Marathi, reply in Marathi. Never switch to English when another language is selected.
9. Be concise, engaging, and professional. Keep replies under 120 words unless technical detail is explicitly requested.
10. Never promise confirmed appointments — say the request has been recorded and a Fortivex AI specialist will confirm shortly."""


# In-memory session store: { session_id: [ {"role": ..., "parts": [...]} ] }
_sessions: Dict[str, List[Dict[str, Any]]] = {}


def _get_api_key() -> str:
    """Return the Gemini API key, re-reading .env on every call so hot-reload works."""
    load_dotenv(override=True)
    return os.getenv("GEMINI_API_KEY", "").strip()


def _fallback_reply(language: str = "English") -> str:
    """Return a friendly error when the Gemini API key is missing or invalid."""
    if language and language.strip().lower() not in ("english", "en", ""):
        return (
            "⚠️ AI assistant is not configured. Please add your GEMINI_API_KEY "
            "to the .env file and restart the server."
        )
    return (
        "⚠️ AI assistant is not configured. Please open the .env file and set "
        "GEMINI_API_KEY=<your key from https://aistudio.google.com/app/apikey>, "
        "then save the file — the server will auto-restart."
    )


def _get_history(session_id: str) -> List[Dict[str, Any]]:
    if session_id not in _sessions:
        _sessions[session_id] = []
    return _sessions[session_id]


def reset_session(session_id: str) -> None:
    _sessions.pop(session_id, None)


def get_conversation_text(session_id: str) -> str:
    """Return the conversation as a plain text string for analysis."""
    history = _get_history(session_id)
    lines = []
    for turn in history:
        role = "Customer" if turn["role"] == "user" else "SalesPilot"
        content = turn["parts"][0] if turn["parts"] else ""
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


def chat(session_id: str, user_message: str, language: str = "English") -> str:
    """
    Process a customer message:
    1. Check API key is valid.
    2. Retrieve relevant RAG context.
    3. Inject context + language instruction into the conversation.
    4. Call Gemini with full history.
    5. Store turn and return response.
    """
    api_key = _get_api_key()
    if not api_key or api_key == "your_gemini_api_key_here":
        return _fallback_reply(language)

    history = _get_history(session_id)

    # Retrieve relevant company knowledge
    rag_context = rag_engine.retrieve(user_message, k=3)

    # Build the user turn — include RAG context if found
    if rag_context:
        augmented_message = (
            f"[Company Knowledge Reference — use only if relevant]:\n"
            f"{rag_context}\n\n"
            f"Customer message: {user_message}"
        )
    else:
        augmented_message = user_message

    # Language instruction — force language in model's terms
    lang = (language or "English").strip()
    if lang.lower() not in ("english", "en", ""):
        language_note = (
            f"\n\n[MANDATORY: Your ENTIRE reply MUST be written in {lang}. "
            f"Do NOT use English. Write naturally as a fluent {lang} speaker.]"
        )
    else:
        language_note = ""

    full_user_msg = augmented_message + language_note
    history.append({"role": "user", "parts": [full_user_msg]})

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-3.8-flash",
            system_instruction=SYSTEM_PROMPT,
        )
        gemini_chat = model.start_chat(history=history[:-1])
        response = gemini_chat.send_message(full_user_msg)
        ai_reply = response.text.strip()
    except ResourceExhausted:
        print("[Agent] Gemini usage quota exceeded.")
        history.pop()
        return (
            "Google Gemini's usage limit has been reached for this API key. "
            "Check your Google AI Studio quota or billing, or retry after the limit resets."
        )
    except Exception as exc:
        print(f"[Agent] Gemini error: {exc}")
        history.pop()   # Remove the failed user turn so session stays clean
        return f"I encountered an issue: {str(exc)[:120]}. Please check your API key or try again."

    history.append({"role": "model", "parts": [ai_reply]})
    return ai_reply


def generate_summary(session_id: str) -> str:
    """Generate a concise conversation summary using Gemini."""
    api_key = _get_api_key()
    if not api_key or api_key == "your_gemini_api_key_here":
        return "Summary unavailable — please configure your GEMINI_API_KEY."

    conversation = get_conversation_text(session_id)
    if not conversation.strip():
        return "No conversation to summarise yet."

    prompt = (
        "Summarise the following sales conversation in 3–5 bullet points covering: "
        "customer needs, budget, lead potential, and recommended next steps.\n\n"
        f"{conversation}"
    )
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-3.8-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as exc:
        print(f"[Agent] Summary error: {exc}")
        return "Could not generate summary at this time."
