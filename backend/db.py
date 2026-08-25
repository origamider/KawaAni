import json
from pathlib import Path
import sqlite3
from datetime import datetime, timezone

DB_PATH = Path(__file__).parents[1] / "data/kawaani.db"


# ref:https://www.sqlite.org/lang_createtable.html
def init_users_table(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            anilist_username TEXT NOT NULL UNIQUE,
            user_vector TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()

def upsert_user_vector(conn: sqlite3.Connection, anilist_username, user_vector: list[float]) -> None:
    updated_at = datetime.now(timezone.utc).isoformat()
    conn.execute("""
        INSERT INTO users (anilist_username, user_vector, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(anilist_username)
        DO UPDATE SET
            user_vector = excluded.user_vector,
            updated_at = excluded.updated_at
    """, (anilist_username, json.dumps(user_vector), updated_at))
    conn.commit()

def get_user_vector(conn: sqlite3.Connection, anilist_username: str) -> list[float] | None:
    row = conn.execute(
        "Select user_vector From users where anilist_username = ?",
        (anilist_username,)
    ).fetchone()
    if row is None:
        return None
    return json.loads(row[0])

def init_user_ratings_table(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_ratings (
            anilist_username TEXT NOT NULL,
            mal_id INTEGER NOT NULL,
            score REAL NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (anilist_username, mal_id)
        )
    """)
    conn.commit()

def replace_user_ratings(conn: sqlite3.Connection, anilist_username: str,ratings: list[tuple[int, float]]) -> None:
    updated_at = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "DELETE FROM user_ratings WHERE anilist_username = ?",
        (anilist_username,))
    conn.executemany(
        "INSERT INTO user_ratings (anilist_username, mal_id, score, updated_at) VALUES (?, ?, ?, ?)",
        [(anilist_username, mal_id, score, updated_at) for mal_id, score in ratings],
    )
    conn.commit()

def get_watched_mal_ids(conn: sqlite3.Connection, anilist_username: str) -> set[int]:
    rows = conn.execute(
        "select mal_id from user_ratings where anilist_username = ?",
        (anilist_username,)
    ).fetchall()
    return {row[0] for row in rows}