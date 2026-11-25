"""
database.py — SQLite persistence for leads, appointments, and summaries.
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "salespilot.db")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables if they do not exist."""
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id      TEXT NOT NULL,
                customer_name   TEXT,
                business_type   TEXT,
                requirement     TEXT,
                budget          TEXT,
                contact         TEXT,
                lead_category   TEXT,
                sentiment       TEXT,
                summary         TEXT,
                created_at      TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS appointments (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id      TEXT NOT NULL,
                customer_name   TEXT,
                preferred_date  TEXT,
                preferred_time  TEXT,
                requirement     TEXT,
                status          TEXT DEFAULT 'Requested',
                created_at      TEXT NOT NULL
            );
            """
        )


def save_lead(
    session_id: str,
    customer_name: Optional[str],
    business_type: Optional[str],
    requirement: Optional[str],
    budget: Optional[str],
    contact: Optional[str],
    lead_category: Optional[str],
    sentiment: Optional[str],
    summary: Optional[str],
) -> int:
    """Insert or replace lead for a session. Returns row id."""
    now = datetime.utcnow().isoformat()
    with _connect() as conn:
        # Check if a lead for this session already exists
        existing = conn.execute(
            "SELECT id FROM leads WHERE session_id = ?", (session_id,)
        ).fetchone()
        if existing:
            conn.execute(
                """
                UPDATE leads
                SET customer_name=?, business_type=?, requirement=?,
                    budget=?, contact=?, lead_category=?, sentiment=?,
                    summary=?, created_at=?
                WHERE session_id=?
                """,
                (
                    customer_name,
                    business_type,
                    requirement,
                    budget,
                    contact,
                    lead_category,
                    sentiment,
                    summary,
                    now,
                    session_id,
                ),
            )
            return existing["id"]
        else:
            cursor = conn.execute(
                """
                INSERT INTO leads
                    (session_id, customer_name, business_type, requirement,
                     budget, contact, lead_category, sentiment, summary, created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    session_id,
                    customer_name,
                    business_type,
                    requirement,
                    budget,
                    contact,
                    lead_category,
                    sentiment,
                    summary,
                    now,
                ),
            )
            return cursor.lastrowid


def get_all_leads() -> List[Dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM leads ORDER BY created_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def save_appointment(
    session_id: str,
    customer_name: Optional[str],
    preferred_date: Optional[str],
    preferred_time: Optional[str],
    requirement: Optional[str],
) -> int:
    now = datetime.utcnow().isoformat()
    with _connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO appointments
                (session_id, customer_name, preferred_date,
                 preferred_time, requirement, status, created_at)
            VALUES (?,?,?,?,?,'Requested',?)
            """,
            (session_id, customer_name, preferred_date, preferred_time, requirement, now),
        )
        return cursor.lastrowid


def get_all_appointments() -> List[Dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM appointments ORDER BY created_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def get_insights() -> Dict[str, Any]:
    with _connect() as conn:
        total_leads = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        hot = conn.execute(
            "SELECT COUNT(*) FROM leads WHERE lead_category='Hot'"
        ).fetchone()[0]
        warm = conn.execute(
            "SELECT COUNT(*) FROM leads WHERE lead_category='Warm'"
        ).fetchone()[0]
        cold = conn.execute(
            "SELECT COUNT(*) FROM leads WHERE lead_category='Cold'"
        ).fetchone()[0]
        positive = conn.execute(
            "SELECT COUNT(*) FROM leads WHERE sentiment='Positive'"
        ).fetchone()[0]
        neutral = conn.execute(
            "SELECT COUNT(*) FROM leads WHERE sentiment='Neutral'"
        ).fetchone()[0]
        negative = conn.execute(
            "SELECT COUNT(*) FROM leads WHERE sentiment='Negative'"
        ).fetchone()[0]
        total_appointments = conn.execute(
            "SELECT COUNT(*) FROM appointments"
        ).fetchone()[0]
    return {
        "total_leads": total_leads,
        "lead_categories": {"Hot": hot, "Warm": warm, "Cold": cold},
        "sentiments": {
            "Positive": positive,
            "Neutral": neutral,
            "Negative": negative,
        },
        "total_appointments": total_appointments,
    }
