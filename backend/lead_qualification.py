"""
lead_qualification.py — Extract lead details and classify using Gemini.
"""

import json
import re
from typing import Optional

import google.generativeai as genai


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
    prompt = EXTRACTION_PROMPT.format(conversation=conversation_text)
    try:
        model = genai.GenerativeModel("gemini-3.8-flash")
        response = model.generate_content(prompt)
        raw = response.text.strip()

        # Strip markdown code fences if present
        raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("```").strip()

        data = json.loads(raw)
        # Ensure all expected keys exist
        defaults = {
            "customer_name": None,
            "business_type": None,
            "requirement": None,
            "budget": None,
            "contact": None,
            "lead_category": "Cold",
            "sentiment": "Neutral",
        }
        defaults.update(data)
        return defaults
    except Exception as exc:
        print(f"[LeadQualification] Error: {exc}")
        return {
            "customer_name": None,
            "business_type": None,
            "requirement": None,
            "budget": None,
            "contact": None,
            "lead_category": "Cold",
            "sentiment": "Neutral",
        }
