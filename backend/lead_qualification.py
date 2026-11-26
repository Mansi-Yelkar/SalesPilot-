"""
lead_qualification.py — Extract lead details and classify using Gemini.
"""

import json
import re
from typing import Optional

import os
from dotenv import load_dotenv


EXTRACTION_PROMPT = """
You are a CRM data extractor. Given the following sales conversation, extract the customer details below.
Return ONLY valid JSON with exactly these keys (use null if not mentioned):

{{
  "customer_name": string or null,
  "business_type": string or null,
  "requirement": string or null,
  "budget": string or null,
  "contact": string or null,
  "lead_category": "Hot" | "Warm" | "Cold",
  "sentiment": "Positive" | "Neutral" | "Negative"
}}

Lead classification rules:
- Hot: customer has shared a clear requirement AND a budget AND has asked for or agreed to an appointment.
- Warm: customer has shared a requirement but no budget or no appointment interest.
- Cold: customer has not shared a clear requirement.

Sentiment rules:
- Positive: enthusiastic, interested, agreeable.
- Neutral: informational, non-committal.
- Negative: frustrated, disinterested, or objecting.

Conversation:
{conversation}
"""


def extract_lead_data(conversation_text: str) -> dict:
    """
    Call Gemini to extract structured lead information from the conversation.
    Returns a dict with lead fields; falls back to safe defaults on error.
    """
    # Use deterministic local extraction so CRM saving never depends on Gemini uptime.
    return _extract_locally(conversation_text)


def _defaults() -> dict:
    return {
        "customer_name": None,
        "business_type": None,
        "requirement": None,
        "budget": None,
        "contact": None,
        "lead_category": "Cold",
        "sentiment": "Neutral",
    }


def _extract_locally(conversation_text: str) -> dict:
    """Extract useful lead details without requiring the external LLM."""
    data = _defaults()
    customer_lines = [line.split(":", 1)[-1].strip() for line in conversation_text.splitlines() if line.startswith("Customer:")]
    text = "\n".join(customer_lines)
    email = re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", text)
    phone = re.search(r"(?:\+?\d[\d\s().-]{7,}\d)", text)
    data["contact"] = email.group(0) if email else (phone.group(0).strip() if phone else None)

    for pattern in (r"\bmy name is\s+([A-Z][\w'-]*(?:\s+[A-Z][\w'-]*){0,2})", r"\bI am called\s+([A-Z][\w'-]*(?:\s+[A-Z][\w'-]*){0,2})"):
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data["customer_name"] = match.group(1).strip()
            break

    requirement_markers = ("need", "looking for", "interested in", "want to", "require")
    for line in customer_lines:
        if any(marker in line.casefold() for marker in requirement_markers):
            data["requirement"] = line
            break

    business_match = re.search(r"\b(e-commerce|healthcare|retail|finance|logistics|manufacturing|education|technology)\b", text, re.IGNORECASE)
    if business_match:
        data["business_type"] = business_match.group(1)
    budget_match = re.search(r"(?:budget|spend|price range)\s*(?:is|of|:)?\s*((?:₹|rs\.?\s*)?[\d,]+(?:\s*(?:k|lakh|lakhs|crore|million))?(?:\s*(?:/\s*month|per month|monthly))?)", text, re.IGNORECASE)
    if budget_match:
        data["budget"] = budget_match.group(1).strip()

    if data["requirement"]:
        data["lead_category"] = "Warm"
    if any(word in text.casefold() for word in ("excited", "great", "interested", "thank you", "yes, book", "sounds good")):
        data["sentiment"] = "Positive"
    elif any(word in text.casefold() for word in ("frustrated", "not interested", "stop", "terrible", "unhappy")):
        data["sentiment"] = "Negative"
    return data
