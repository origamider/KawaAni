from fastapi import FastAPI
import sqlite3
import pandas as pd

app = FastAPI()

@app.get("/recommend/next")
def get_recommend_top3():
    conn = sqlite3.connect('../data/test.db')
    df = pd.read_sql("select title_japanese from anime_cleaned order by score desc", conn)[:10]
    
    conn.close()
    return df.sample(n=3)