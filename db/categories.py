from __future__ import annotations

from typing import Dict, List

from .connection import get_db


def list_categories() -> List[Dict]:
    db = get_db()
    rows = db.execute(
        """
        SELECT id, name
        FROM categories
        ORDER BY name
    """
    ).fetchall()
    return [dict(r) for r in rows]


def assign_categories_to_workout(workout_id: int, category_ids: list[int]) -> None:
    db = get_db()
    for cid in category_ids:
        db.execute(
            """
            INSERT OR IGNORE INTO workout_categories (workout_id, category_id)
            VALUES (?, ?)
        """,
            (workout_id, cid),
        )
    db.commit()


def list_workout_categories(workout_id: int) -> List[Dict]:
    db = get_db()
    rows = db.execute(
        """
        SELECT c.id, c.name
        FROM categories AS c
        JOIN workout_categories AS wc ON wc.category_id = c.id
        WHERE wc.workout_id = ?
        ORDER BY c.name
    """,
        (workout_id,),
    ).fetchall()
    return [dict(r) for r in rows]
