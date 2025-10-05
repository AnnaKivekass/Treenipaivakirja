import sqlite3
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

def add_user(username: str, password: str):
    db = get_db()
    db.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, password),
    )
    db.commit()

def get_user(username: str):
    db = get_db()
    return db.execute(
        "SELECT id, username, password_hash AS password FROM users WHERE username = ?",
        (username,),
    ).fetchone()

def add_workout(user_id: int, date: str, wtype: str, duration: int, description: str | None):
    db = get_db()
    db.execute(
        "INSERT INTO workouts (user_id, date, type, duration, description) VALUES (?, ?, ?, ?, ?)",
        (user_id, date, wtype, duration, description),
    )
    db.commit()

def list_workouts(user_id: int):
    db = get_db()
    return db.execute(
        "SELECT id, date, type, duration, description FROM workouts WHERE user_id = ? ORDER BY date DESC, id DESC",
        (user_id,),
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
        """SELECT m.id, m.content, m.created_at,
                  s.username AS sender, w.id AS workout_id, w.type AS workout_type, w.date AS workout_date
           FROM messages m
           JOIN users s ON s.id = m.sender_id
           JOIN workouts w ON w.id = m.workout_id
           WHERE m.receiver_id = ?
           ORDER BY m.created_at DESC, m.id DESC""",
        (receiver_id,),
    ).fetchall()
