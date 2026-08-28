import json
from pathlib import Path
import sqlite3
from datetime import datetime, timezone

DB_PATH = Path(__file__).parents[1] / "data/kawaani.db"

"""
ref:
conn.execute
https://docs.python.org/ja/3/library/sqlite3.html#sqlite3.Cursor.execute
"""
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

def init_anime_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS anime (
            mal_id INTEGER PRIMARY KEY,
            anime_id INTEGER NOT NULL UNIQUE,
            english_title TEXT,
            image_url TEXT NOT NULL,
            japanese_title TEXT
        )
        """
    )
    conn.commit()

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

def init_anilist_token_table(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS anilist_token (
            anilist_username TEXT PRIMARY KEY,
            access_token TEXT NOT NULL,
            obtained_at TEXT NOT NULL
        )
    """)
    conn.commit()

def init_all_tables(conn: sqlite3.Connection) -> None:
    init_users_table(conn)
    init_anime_table(conn)
    init_user_ratings_table(conn)
    init_anilist_token_table(conn)

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
        [anilist_username]
    ).fetchone()
    if row is None:
        return None
    return json.loads(row[0])

"""
一度全てを削除し、再度全てを追加する方式をとっている。
"""
def replace_user_ratings(conn: sqlite3.Connection, anilist_username: str,ratings: list[tuple[int, float]]) -> None:
    updated_at = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "DELETE FROM user_ratings WHERE anilist_username = ?",
        [anilist_username])
    conn.executemany(
        "INSERT INTO user_ratings (anilist_username, mal_id, score, updated_at) VALUES (?, ?, ?, ?)",
        [(anilist_username, mal_id, score, updated_at) for mal_id, score in ratings],
    )
    conn.commit()

"""
fetchall()をすると、[(111,), (123,)]のように、tupleのlistで返ってくる。
そのため、{123, 111}のようにしたい。
set型のオブジェクトは波括弧{}で生成できる。とのこと。
"""
def get_watched_mal_ids(conn: sqlite3.Connection, anilist_username: str) -> set[int]:
    rows = conn.execute(
        "select mal_id from user_ratings where anilist_username = ?",
        [anilist_username]
    ).fetchall()
    return {row[0] for row in rows}

def get_mal_to_anime_id(conn: sqlite3.Connection) -> dict[int, int]:
    return dict(conn.execute("SELECT mal_id, anime_id FROM anime").fetchall())

# ref:https://www.sqlite.org/lang_expr.html#the_in_and_not_in_operators
# mal_id配列からアニメ情報を取得する。
def get_anime_info_from_mal_ids(conn: sqlite3.Connection, mal_ids: list[int]) -> dict[int, dict]:
    rows = conn.execute(
        """
        SELECT mal_id, anime_id, english_title, image_url, japanese_title
        FROM anime
        WHERE mal_id IN (SELECT value FROM json_each(?))
        """,
        [json.dumps(mal_ids)]
    ).fetchall()
    
    return {
        row[0]: {
            "mal_id": row[0],
            "anime_id": row[1],
            "english_title": row[2],
            "image_url": row[3],
            "japanese_title": row[4],
        }
        for row in rows
    }

# AniListから取得したjapanese_titleをanimeテーブルに保存する。
def update_japanese_title(conn: sqlite3.Connection, mal_id: int, japanese_title: str) -> None:
    conn.execute(
        "UPDATE anime SET japanese_title = ? WHERE mal_id = ?",
        [japanese_title, mal_id]
    )
    conn.commit()

def save_anilist_token(conn: sqlite3.Connection, anilist_username: str, access_token: str) -> None:
    obtained_at = datetime.now(timezone.utc).isoformat()
    conn.execute("""
        INSERT INTO anilist_token (anilist_username, access_token, obtained_at)
        VALUES (?, ?, ?)
        ON CONFLICT(anilist_username)
        DO UPDATE SET
            access_token = excluded.access_token,
            obtained_at = excluded.obtained_at
    """, (anilist_username, access_token, obtained_at))
    conn.commit()

def get_anilist_token(conn: sqlite3.Connection, anilist_username: str) -> str | None:
    row = conn.execute(
        "SELECT access_token FROM anilist_token WHERE anilist_username = ?",
        [anilist_username]
    ).fetchone()
    return row[0] if row is not None else None