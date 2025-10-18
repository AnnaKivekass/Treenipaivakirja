from __future__ import annotations
import hashlib
from typing import Optional
from .connection import get_db

def _hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def add_user(username: str, password: str) -> None:
    db = get_db()
    db.execute("""
        INSERT INTO users (username, password_hash)
        VALUES (?, ?)
    """, (username, _hash_password(password)))
    db.commit()

def get_user(username: str) -> Optional[dict]:
    db = get_db()
    row = db.execute("""
        SELECT id, username, password_hash
        FROM users
        WHERE username = ?
    """, (username,)).fetchone()
    return dict(row) if row else None

def get_user_by_id(user_id: int) -> Optional[dict]:
    db = get_db()
    row = db.execute("""
        SELECT id, username
        FROM users
        WHERE id = ?
    """, (user_id,)).fetchone()
    return dict(row) if row else None

def verify_password(user_row: Optional[dict], password: str) -> bool:
    return bool(user_row) and user_row["password_hash"] == _hash_password(password)
