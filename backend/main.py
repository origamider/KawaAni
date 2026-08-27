from fastapi import FastAPI
import sqlite3
import pandas as pd
from pathlib import Path
from cf_recommend import recommend_top3_mal_id
from cf_model import load_frozen_model
import db

app = FastAPI()
cpt, model = load_frozen_model()

# @app.get("/recommend/next")
# def get_recommend_top3():
#     conn = sqlite3.connect('../data/kawaani.db')
#     df = pd.read_sql("select title_japanese,image_url from anime order by score desc", conn)[:10]
    
#     conn.close()
#     return df.sample(n=3).to_dict("records") # 行番号は無視したいため。

@app.get("/recommend/next")
def get_recommend_top3():
    conn = sqlite3.connect(db.DB_PATH)
    recommend_top3_mal_id(model, conn)
    result = recommend_top3_mal_id(model, conn)
    conn.close()
    return [
        {
            "title_japanese": anime["japanese_title"],
            "image_url": anime["image_url"]
        }
        for anime in result
    ]
