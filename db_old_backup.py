import sqlite3
import hashlib
from flask import g, current_app
from pathlib import Path

def get_db():
    if "db" not in g:
        db_path = current_app.config.get("DATABASE")
        if not db_path:
            instance = Path(current_app.instance_path)
            instance.mkdir(parents=True, exist_ok=True)
            db_path = instance / "app.sqlite3"
            current_app.config["DATABASE"] = str(db_path)
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(schema_path: str = "schema.sql"):
    db = get_db()
    with open(schema_path, "r", encoding="utf-8") as f:
        db.executescript(f.read())
    db.commit()

def _hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()


def verify_password(user_row, password: str) -> bool:
    if not user_row:
        return False
    return user_row["password_hash"] == _hash_password(password)


def add_user(username: str, password: str):
    db = get_db()
    db.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, _hash_password(password)),
    )
    db.commit()


def get_user(username: str):
    db = get_db()
    return db.execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?",
        (username,),
    ).fetchone()


def get_user_by_id(user_id: int):
    db = get_db()
    return db.execute(
        "SELECT id, username FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()

def add_workout(user_id: int, date: str, wtype: str, duration: int, description: str | None):
    db = get_db()
    cur = db.execute(
        "INSERT INTO workouts (user_id, date, type, duration, description) VALUES (?, ?, ?, ?, ?)",
        (user_id, date, wtype, duration, description),
    )
    db.commit()
    return cur.lastrowid


def list_workouts(user_id: int):
    db = get_db()
    return db.execute(
        "SELECT id, date, type, duration, description FROM workouts WHERE user_id = ? ORDER BY date DESC, id DESC",
        (user_id,),
    ).fetchall()


def get_workout(workout_id: int):
    db = get_db()
    return db.execute(
        "SELECT id, user_id, date, type, duration, description FROM workouts WHERE id = ?",
        (workout_id,),
    ).fetchone()

def list_categories():
    db = get_db()
    return db.execute(
        "SELECT id, name FROM categories ORDER BY name",
    ).fetchall()


def assign_categories_to_workout(workout_id: int, category_ids: list[int]):
    db = get_db()
    for cid in category_ids:
        db.execute(
            "INSERT OR IGNORE INTO workout_categories (workout_id, category_id) VALUES (?, ?)",
            (workout_id, cid),
        )
    db.commit()


def list_workout_categories(workout_id: int):
    db = get_db()
    return db.execute(
        """SELECT c.id, c.name
           FROM categories c
           JOIN workout_categories wc ON wc.category_id = c.id
           WHERE wc.workout_id = ?
           ORDER BY c.name""",
        (workout_id,),
    ).fetchall()

def add_message(sender_id: int, receiver_id: int, workout_id: int, content: str):
    db = get_db()
    db.execute(
        "INSERT INTO messages (sender_id, receiver_id, workout_id, content) VALUES (?, ?, ?, ?)",
        (sender_id, receiver_id, workout_id, content),
    )
    db.commit()


def list_messages(receiver_id: int):
    db = get_db()
    return db.execute(
        """SELECT m.id, m.sender_id, m.receiver_id, m.content, m.created_at,
                  s.username, w.date, w.type
           FROM messages m
           JOIN users s ON s.id = m.sender_id
           JOIN workouts w ON w.id = m.workout_id
           WHERE m.receiver_id = ?
           ORDER BY m.created_at DESC, m.id DESC""",
        (receiver_id,),
    ).fetchall()
