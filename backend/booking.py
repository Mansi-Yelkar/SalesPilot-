"""
booking.py — Validate and save appointment requests.
"""

from typing import Optional, Tuple

from backend import database  # noqa: E402


def book_appointment(
    session_id: str,
    customer_name: Optional[str],
    preferred_date: Optional[str],
    preferred_time: Optional[str],
    requirement: Optional[str],
) -> Tuple[bool, str]:
    """
    Validate fields and persist an appointment request.
    Returns (success, message).
    """
    missing = []
    if not preferred_date:
        missing.append("preferred date")
    if not preferred_time:
        missing.append("preferred time")

    if missing:
        return (
            False,
            f"Could not save appointment — missing: {', '.join(missing)}.",
        )

    try:
        appt_id = database.save_appointment(
            session_id=session_id,
            customer_name=customer_name,
            preferred_date=preferred_date,
            preferred_time=preferred_time,
            requirement=requirement,
        )
        return (
            True,
            f"Appointment request #{appt_id} saved for {preferred_date} at {preferred_time}.",
        )
    except Exception as exc:
        return (False, f"Database error while saving appointment: {exc}")
