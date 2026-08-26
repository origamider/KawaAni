import pandas as pd
import sqlite3
from pathlib import Path
import re

# dataset:https://www.kaggle.com/datasets/ramazanturann/user-animelist-dataset?select=animes.csv
df = pd.read_csv(f'{Path(__file__).parents[1]}/data/animes.csv')
dbname = f"{Path(__file__).parents[1]}/data/kawaani.db"

# mal_urlからmal_idを正規表現で取得する。
def extract_mal_id(target: str) -> int|None:
    match = re.search(r"/anime/(\d+)",target)
    return int(match.group(1)) if match else None

#  mal_id追加
df["mal_id"] = df["mal_url"].apply(extract_mal_id)

conn = sqlite3.connect(dbname)

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

rows = []
for r in df.itertuples():
    rows.append((r.mal_id, r.animeID, r.title, r.image_url, None))

conn.executemany(
    """
    INSERT INTO anime (mal_id, anime_id, english_title, image_url, japanese_title)
    VALUES (?, ?, ?, ?, ?)
    """
    ,rows
)
conn.commit()
print("anime table is created in kawaani.db")
conn.close()