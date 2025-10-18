from __future__ import annotations
from typing import List, Dict, Optional
from .connection import get_db

def add_message(sender_id: int, receiver_id: int, workout_id: int, content: str) -> None:
    db = get_db()
    db.execute("""
        INSERT INTO messages (sender_id, receiver_id, workout_id, content)
        VALUES (?, ?, ?, ?)
    """, (sender_id, receiver_id, workout_id, content))
    db.commit()

def list_messages(receiver_id: int) -> List[Dict]:
    db = get_db()
    rows = db.execute("""
        SELECT
            m.id,
            m.sender_id,
            m.receiver_id,
            m.content,
            m.created_at,
            s.username AS sender,
            r.username AS receiver,
            w.date AS workout_date,
            w.type AS workout_type
        FROM messages AS m
        JOIN users AS s ON s.id = m.sender_id
        JOIN users AS r ON r.id = m.receiver_id
        JOIN workouts AS w ON w.id = m.workout_id
        WHERE m.receiver_id = ?
        ORDER BY m.created_at DESC, m.id DESC
    """, (receiver_id,)).fetchall()
    return [dict(r) for r in rows]

def get_message_for_edit(message_id: int) -> Optional[dict]:
    db = get_db()
    row = db.execute("""
        SELECT id, sender_id, content
        FROM messages
        WHERE id = ?
    """, (message_id,)).fetchone()
    return dict(row) if row else None

def update_message_content(message_id: int, content: str) -> None:
    db = get_db()
    db.execute("""
        UPDATE messages
        SET content = ?
        WHERE id = ?
    """, (content, message_id))
    db.commit()
