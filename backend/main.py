from fastapi import FastAPI
import sqlite3
import pandas as pd

app = FastAPI()

@app.get("/recommend/next")
def get_recommend_top3():
    conn = sqlite3.connect('../data/kawaani.db')
    df = pd.read_sql("select title_japanese,image_url from anime order by score desc", conn)[:10]
    
    conn.close()
    return df.sample(n=3).to_dict("records") # 行番号は無視したいため。