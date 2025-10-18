from __future__ import annotations

from typing import Dict, List, Optional

from .connection import get_db


def add_message(sender_id: int, receiver_id: int, workout_id: int, content: str) -> None:
    db = get_db()
    db.execute(
        """
        INSERT INTO messages (sender_id, receiver_id, workout_id, content)
        VALUES (?, ?, ?, ?)
    """,
        (sender_id, receiver_id, workout_id, content),
    )
    db.commit()


def list_messages(receiver_id: int) -> List[Dict]:
    db = get_db()
    rows = db.execute(
        """
        SELECT
            m.id,
            m.sender_id,
            m.receiver_id,
            m.content,
            m.created_at,
            s.username,
            r.username,
            w.date,
            w.type
        FROM messages m
        JOIN users s ON s.id = m.sender_id
        JOIN users r ON r.id = m.receiver_id
        JOIN workouts w ON w.id = m.workout_id
        WHERE m.receiver_id = ?
        ORDER BY m.created_at DESC, m.id DESC
    """,
        (receiver_id,),
    ).fetchall()

    result: List[Dict] = []
    for row in rows:
        result.append(
            {
                "id": row["id"],
                "sender_id": row["sender_id"],
                "receiver_id": row["receiver_id"],
                "content": row["content"],
                "created_at": row["created_at"],
                "sender": row[5],
                "receiver": row[6],
                "workout_date": row[7],
                "workout_type": row[8],
            }
        )
    return result


def get_message_for_edit(message_id: int) -> Optional[dict]:
    db = get_db()
    row = db.execute(
        """
        SELECT id, sender_id, content
        FROM messages
        WHERE id = ?
    """,
        (message_id,),
    ).fetchone()
    return dict(row) if row else None


def update_message_content(message_id: int, content: str) -> None:
    db = get_db()
    db.execute(
        """
        UPDATE messages
        SET content = ?
        WHERE id = ?
    """,
        (content, message_id),
    )
    db.commit()
