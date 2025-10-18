from __future__ import annotations
from typing import Optional, List, Dict
from .connection import get_db

def add_workout(user_id: int, date: str, wtype: str, duration: int, description: Optional[str]) -> int:
    db = get_db()
    cur = db.execute("""
        INSERT INTO workouts (user_id, date, type, duration, description)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, date, wtype, duration, description))
    db.commit()
    return int(cur.lastrowid)

def list_workouts(user_id: int) -> List[Dict]:
    db = get_db()
    rows = db.execute("""
        SELECT id, date, type, duration, description
        FROM workouts
        WHERE user_id = ?
        ORDER BY date DESC, id DESC
    """, (user_id,)).fetchall()
    return [dict(r) for r in rows]

def get_workout(workout_id: int) -> Optional[dict]:
    db = get_db()
    row = db.execute("""
        SELECT id, user_id, date, type, duration, description
        FROM workouts
        WHERE id = ?
    """, (workout_id,)).fetchone()
    return dict(row) if row else None
