"""
agent.py — Core AI agent using Gemini with conversation memory and RAG.
"""

import os
import re
from typing import List, Dict, Any

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


def _company_faq_reply(question: str) -> str | None:
    """Answer common company questions locally from the maintained knowledge file."""
    path = os.path.join(os.path.dirname(__file__), "..", "data", "company_knowledge.txt")
    try:
        with open(path, "r", encoding="utf-8") as knowledge_file:
            text = knowledge_file.read()
    except OSError:
        return None

    q = question.casefold()
    normalized = re.sub(r"[^a-z0-9]+", " ", q).strip()
    sections = {
        "services": ["OUR SERVICES", "FREQUENTLY ASKED QUESTIONS"],
        "about": ["ABOUT FORTIVEX AI", "OUR SERVICES"],
        "pricing": ["OUR SERVICES", "FREQUENTLY ASKED QUESTIONS"],
        "implementation": ["FREQUENTLY ASKED QUESTIONS", "CONTACT INFORMATION"],
        "support": ["FREQUENTLY ASKED QUESTIONS", "CONTACT INFORMATION"],
        "integration": ["FREQUENTLY ASKED QUESTIONS", "CONTACT INFORMATION"],
        "security": ["FREQUENTLY ASKED QUESTIONS", "CONTACT INFORMATION"],
        "data": ["FREQUENTLY ASKED QUESTIONS", "CONTACT INFORMATION"],
        "demo": ["FREQUENTLY ASKED QUESTIONS", "CONTACT INFORMATION"],
        "contact": ["CONTACT INFORMATION", "CURRENT PROMOTIONS"],
        "roi": ["FREQUENTLY ASKED QUESTIONS", "CONTACT INFORMATION"],
        "promotion": ["CURRENT PROMOTIONS", "CASE STUDIES"],
        "case study": ["CASE STUDIES (Brief)", None],
    }
    topic_keys = {
        "services": ("service", "provide", "solution", "product"),
        "about": ("fortivex", "company", "who are you", "founded", "headquarter", "mission"),
        "pricing": ("price", "pricing", "cost", "how much", "rate", "fee"),
        "implementation": ("implementation", "how long", "timeline", "deployment"),
        "support": ("support", "warranty", "after deployment", "maintenance"),
        "integration": ("integrat", "software", "salesforce", "zoho", "sap", "hubspot", "connector"),
        "security": ("secure", "security", "privacy", "data safe", "nda"),
        "data": ("data need", "get started", "dataset", "documents"),
        "demo": ("demo", "demonstration", "try"),
        "contact": ("contact", "email", "phone", "address", "office", "website"),
        "roi": ("roi", "results", "improvement", "savings", "reduction", "conversion"),
        "promotion": ("promotion", "discount", "offer", "free setup"),
        "case study": ("case study", "customer example", "client example", "success story"),
    }
    topic_order = (
        "case study", "integration", "implementation", "support", "security", "data",
        "demo", "contact", "roi", "promotion", "pricing", "services", "about",
    )
    promotion_terms = ("discount", "promotion", "free setup", "free audit")
    if "service" in normalized or ("offer" in normalized and not any(term in normalized for term in promotion_terms)):
        topic = "services"
    else:
        topic = next(
            (name for name in topic_order if any(term in normalized for term in topic_keys[name])),
            None,
        )
    if topic is None:
        return None

    start_marker, end_marker = sections[topic]
    start = text.find(start_marker)
    if start < 0:
        return None
    end = text.find(end_marker, start + len(start_marker)) if end_marker else len(text)
    section = text[start + len(start_marker):end if end >= 0 else len(text)].strip()
    section = re.sub(r"(?m)^[-=]{3,}\s*$", "", section).strip()

    if topic in ("services", "pricing"):
        lines = [line.strip() for line in section.splitlines() if line.strip()]
        if topic == "services":
            items = []
            for line in lines:
                if re.match(r"\d+\. ", line):
                    items.append(line)
            answer = "Fortivex AI provides " + "; ".join(re.sub(r"^\d+\. ", "", item) for item in items[:6]) + "."
        else:
            items = []
            current = ""
            service_aliases = (
                (("chatbot", "chatbots", "conversational ai"), "AI Chatbot & Conversational AI"),
                (("process automation", "ipa", "workflow automation"), "Intelligent Process Automation (IPA)"),
                (("analytics", "business intelligence", "forecasting"), "Predictive Analytics & Business Intelligence"),
                (("salespilot", "sales assistant"), "AI-Powered Sales Assistant (SalesPilot)"),
                (("computer vision", "vision", "defect detection"), "Computer Vision Solutions"),
                (("custom ai", "custom development", "machine learning"), "Custom AI Development"),
            )
            requested_service = next((service for aliases, service in service_aliases if any(alias in normalized for alias in aliases)), None)
            for line in lines:
                if re.match(r"\d+\. ", line):
                    current = re.sub(r"^\d+\. ", "", line)
                elif line.lower().strip().startswith("- pricing:") and current:
                    items.append(f"{current}: {line.split(':', 1)[1].strip()}")
            if requested_service:
                selected = next((item for item in items if item.startswith(requested_service)), None)
                answer = f"{selected}." if selected else "Pricing depends on the solution; contact sales@fortivex.ai for a quote."
            else:
                answer = "Pricing depends on the solution: " + "; ".join(items[:6]) + "."
    else:
        relevant = [line.strip() for line in section.splitlines() if line.strip() and not set(line.strip()) <= set("-=")]
        if topic == "about":
            answer = " ".join(relevant[:4])
        elif topic == "contact":
            answer = " ".join(line for line in relevant if any(label in line.casefold() for label in ("sales team:", "support:", "phone:", "office:", "website:")))
        else:
            # Include the matching FAQ item and its answer, plus a neighboring line when useful.
            terms = topic_keys[topic]
            faq_terms = {
                "demo": ("demo", "demonstration"),
                "integration": ("integrat", "software", "connector"),
                "support": ("support", "warranty"),
                "security": ("secure", "security", "privacy"),
                "data": ("data", "get started"),
                "implementation": ("implementation", "how long", "timeline"),
                "roi": ("roi", "results", "improvement", "savings", "reduction", "conversion"),
            }.get(topic, terms)
            match = next((i for i, line in enumerate(relevant) if line.casefold().startswith("q:") and any(term in line.casefold() for term in faq_terms)), None)
            if match is not None:
                answer = " ".join(relevant[match:match + 2])
            else:
                answer = " ".join(relevant[:5])

    answer = re.sub(r"\s+", " ", answer).strip()
    answer = answer.replace("Q: ", "").replace("A: ", "")
    answer = re.sub(r"^\([^)]*\)\s*", "", answer)
    return answer or None


def _gemini():
    """Load and configure the optional Gemini client only when requested."""
    try:
        import google.generativeai as genai

        api_key = _get_api_key()
        if not api_key or api_key == "your_gemini_api_key_here":
            return None
        genai.configure(api_key=api_key)
        return genai
    except Exception as exc:
        print(f"[Agent] Gemini client unavailable: {type(exc).__name__}")
        return None


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


def has_customer_message(session_id: str) -> bool:
    return any(turn.get("role") == "user" for turn in _get_history(session_id))


def _local_reply(message: str, language: str = "English") -> str:
    """Return a useful local answer if the external language model is unavailable."""
    normalized = re.sub(r"[^a-z]+", " ", message.casefold()).strip()
    greetings = {"hi", "hii", "hiii", "hello", "hey", "good morning", "good afternoon", "good evening"}
    if normalized in greetings:
        replies = {
            "German": "Hallo! Willkommen bei Fortivex AI. Wobei kann ich Ihnen helfen: Kundenservice, Workflow-Automatisierung, Analysen, Vertrieb oder eine Produktdemo?",
            "Spanish": "¡Hola! Bienvenido a Fortivex AI. ¿En qué puedo ayudarte: atención al cliente, automatización de flujos, análisis, ventas o una demostración?",
            "French": "Bonjour ! Bienvenue chez Fortivex AI. Comment puis-je vous aider : support client, automatisation, analyses, ventes ou démonstration ?",
            "Hindi": "नमस्ते! Fortivex AI में आपका स्वागत है। मैं ग्राहक सहायता, वर्कफ़्लो ऑटोमेशन, एनालिटिक्स, बिक्री या डेमो में कैसे मदद करूँ?",
            "Marathi": "नमस्कार! Fortivex AI मध्ये आपले स्वागत आहे. ग्राहक सहाय्य, वर्कफ्लो ऑटोमेशन, विश्लेषण, विक्री किंवा डेमो यापैकी कशात मदत करू?",
            "Tamil": "வணக்கம்! Fortivex AI-க்கு வரவேற்கிறோம். வாடிக்கையாளர் ஆதரவு, பணிச்சுற்று தானியக்கம், பகுப்பாய்வு, விற்பனை அல்லது டெமோ—எதில் உதவலாம்?",
        }
        return replies.get(language, "Hello! Welcome to Fortivex AI. What would you like help with: customer support, workflow automation, analytics, sales, or a product demo?")

    if any(word in normalized.split() for word in ("thanks", "thank", "great")):
        return "You're welcome! Tell me a little about your business and what you'd like to improve, and I can suggest a relevant Fortivex AI solution."

    return "I can help with Fortivex AI services, pricing, integrations, support, demos, and contact details. What would you like to know, or what would you like to improve in your business?"


def _record_exchange(history: List[Dict[str, Any]], user_message: str, reply: str) -> str:
    history.extend([
        {"role": "user", "parts": [user_message]},
        {"role": "model", "parts": [reply]},
    ])
    return reply


def chat(session_id: str, user_message: str, language: str = "English") -> str:
    """
    Process a customer message:
    1. Check API key is valid.
    2. Retrieve relevant RAG context.
    3. Inject context + language instruction into the conversation.
    4. Call Gemini with full history.
    5. Store turn and return response.
    """
    history = _get_history(session_id)

    # Company FAQs are answered from the local knowledge base without external API calls.
    faq_reply = _company_faq_reply(user_message)
    if faq_reply:
        return _record_exchange(history, user_message, faq_reply)

    normalized = re.sub(r"[^a-z]+", " ", user_message.casefold()).strip()
    if normalized in {"hi", "hii", "hiii", "hello", "hey", "good morning", "good afternoon", "good evening"}:
        return _record_exchange(history, user_message, _local_reply(user_message, language))

    genai = _gemini()
    if genai is None:
        return _record_exchange(history, user_message, _local_reply(user_message, language))

    # Load semantic search only when a configured Gemini chat actually needs it.
    from backend.rag import rag_engine
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
        model = genai.GenerativeModel(
            model_name=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
            system_instruction=SYSTEM_PROMPT,
        )
        gemini_chat = model.start_chat(history=history[:-1])
        response = gemini_chat.send_message(full_user_msg, request_options={"timeout": 8})
        ai_reply = response.text.strip() if response.text else "I couldn't generate a reply just now. Please try again."
    except Exception as exc:
        if "ResourceExhausted" in type(exc).__name__ or "quota" in str(exc).lower():
            fallback = _local_reply(user_message, language)
            return _record_exchange(history[:-1], user_message, fallback)
        print(f"[Agent] Gemini request failed: {exc}")
        fallback = _local_reply(user_message, language)
        return _record_exchange(history[:-1], user_message, fallback)

    history.append({"role": "model", "parts": [ai_reply]})
    return ai_reply


def generate_summary(session_id: str) -> str:
    """Summarise the conversation locally so CRM never depends on Gemini uptime."""
    conversation = get_conversation_text(session_id)
    if not conversation.strip():
        return "No conversation to summarise yet."
    return _local_summary(conversation)


def _local_summary(conversation: str) -> str:
    customer_lines = [line.removeprefix("Customer: ") for line in conversation.splitlines() if line.startswith("Customer: ")]
    if not customer_lines:
        return "No customer messages were recorded."
    return "\n".join(f"• {line}" for line in customer_lines[-5:])
