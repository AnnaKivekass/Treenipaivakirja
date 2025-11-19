import sqlite3
from pathlib import Path

from flask import g, current_app


def get_db():
    """Hae tietokantayhteys nykyiseen Flask-sovellukseen."""
    if "db" not in g:
        db_path = current_app.config.get("DATABASE")
        if not db_path:
            instance = Path(current_app.instance_path)
            instance.mkdir(parents=True, exist_ok=True)
            db_path = instance / "app.sqlite3"
            current_app.config["DATABASE"] = str(db_path)

        conn = sqlite3.connect(current_app.config["DATABASE"])
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        g.db = conn

    return g.db


def close_db(e=None):
    """Sulje tietokantayhteys sovelluskontekstin lopussa."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(schema_path: str = "schema.sql"):
    """Alustaa tietokannan ajamalla schema.sql-tiedoston."""
    db = get_db()
    with open(schema_path, "r", encoding="utf-8") as f:
        db.executescript(f.read())
    db.commit()
