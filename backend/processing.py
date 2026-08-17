import pandas as pd
import sqlite3
from pathlib import Path

df = pd.read_csv(f'{Path(__file__).parents[1]}/data/anime_dataset.csv')
dbname = f"{Path(__file__).parents[1]}/data/kawaani.db"
conn = sqlite3.connect(dbname)
cur = conn.cursor()
df.to_sql('anime', conn, if_exists='replace')
cur.close()
conn.close()
print("kawaani.db created!")