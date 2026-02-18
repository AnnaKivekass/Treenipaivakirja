from __future__ import annotations
from typing import Dict, List, Optional
from .connection import get_db


def list_all_workouts():
    db = get_db()
    return db.execute(
        """SELECT w.id, w.date, w.type, w.duration, w.description, u.username
           FROM workouts w
           JOIN users u ON u.id = w.user_id
           ORDER BY w.date DESC, w.id DESC"""
    ).fetchall()


def add_workout(user_id: int, date: str, wtype: str, duration: int, description: Optional[str]) -> int:
    db = get_db()
    cur = db.execute(
        """
        INSERT INTO workouts (user_id, date, type, duration, description)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, date, wtype, duration, description),
    )
    db.commit()
    return int(cur.lastrowid)


def list_workouts(user_id: int) -> List[Dict]:
    db = get_db()
    rows = db.execute(
        """
        SELECT
            w.id,
            w.date,
            w.type,
            w.duration,
            w.description,
            u.username
        FROM workouts w
        JOIN users u ON u.id = w.user_id
        WHERE w.user_id = ?
        ORDER BY w.date DESC, w.id DESC
        """,
        (user_id,),
    ).fetchall()

    result: List[Dict] = []
    for row in rows:
        result.append(
            {
                "id": row["id"],
                "date": row["date"],
                "type": row["type"],
                "duration": row["duration"],
                "description": row["description"],
                "username": row["username"],
            }
        )
    return result


def get_workout(workout_id: int) -> Optional[dict]:
    db = get_db()
    row = db.execute(
        """
        SELECT id, user_id, date, type, duration, description
        FROM workouts
        WHERE id = ?
        """,
        (workout_id,),
    ).fetchone()
    return dict(row) if row else None

def search_workouts(user_id: int, query: str):
    db = get_db()
    return db.execute(
        """
        SELECT DISTINCT w.id, w.date, w.type, w.duration, w.description
        FROM workouts w
        LEFT JOIN workout_categories wc ON wc.workout_id = w.id
        LEFT JOIN categories c ON c.id = wc.category_id
        WHERE w.user_id = ?
          AND (
                w.type LIKE ?
                OR w.description LIKE ?
                OR w.date LIKE ?
                OR c.name LIKE ?
          )
        ORDER BY w.date DESC, w.id DESC
        """,
        (
            user_id,
            f"%{query}%",
            f"%{query}%",
            f"%{query}%",
            f"%{query}%",
        ),
    ).fetchall()

def update_workout(workout_id, user_id, date, wtype, duration, description):
    db = get_db()
    db.execute(
        """
        UPDATE workouts
        SET date = ?, type = ?, duration = ?, description = ?
        WHERE id = ? AND user_id = ?
        """,
        (date, wtype, duration, description, workout_id, user_id),
    )
    db.commit()

def delete_workout_by_id(workout_id: int, user_id: int):
    db = get_db()

    row = db.execute(
        "SELECT id FROM workouts WHERE id = ? AND user_id = ?",
        (workout_id, user_id),
    ).fetchone()

    if not row:
        return False

    db.execute("DELETE FROM workouts WHERE id = ?", (workout_id,))
    db.commit()
    return True
