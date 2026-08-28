from fastapi import FastAPI
import sqlite3
import pandas as pd
from pathlib import Path
from cf_recommend import recommend_top3_mal_id
from cf_model import load_frozen_model
import db
import requests
import os
from anilist import get_access_token
from dotenv import load_dotenv
load_dotenv()

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
    result = recommend_top3_mal_id(model, conn)
    conn.close()
    return [
        {
            "title_japanese": anime["japanese_title"],
            "image_url": anime["image_url"]
        }
        for anime in result
    ]

"""
ref:
1.POST形式
https://coddy.tech/docs/ja/python/http-requests
2.AniList Token取得
https://docs.anilist.co/guide/auth/authorization-code
"""
@app.get("/auth/anilist/callback")
def anilist_callback(code: str):
    access_token = get_access_token(code)
    # 次の段階でDBに保存する
    return {"access_token": access_token}  # 動作確認用の一時的な戻り値
    
