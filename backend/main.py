from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import sqlite3
import pandas as pd
from pathlib import Path
from cf_recommend import recommend_top3_mal_id
from cf_model import load_frozen_model
import db
import requests
import os
from anilist import get_access_token, search_anime, get_anilist_username, save_score
from dotenv import load_dotenv
from utils import normalize_title
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()
from pydantic import BaseModel

class ScoreRequest(BaseModel):
    mediaId: int
    score: float

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# table作成(最初のみ)
conn = sqlite3.connect(db.DB_PATH)
db.init_all_tables(conn)
conn.close()

cpt, model = load_frozen_model()

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
    anilist_username = get_anilist_username(access_token)
    conn = sqlite3.connect(db.DB_PATH)
    db.init_anilist_token_table(conn)
    db.save_anilist_token(conn, anilist_username, access_token)
    conn.close()

    return RedirectResponse("http://localhost:3000/dashboard")

@app.get("/anilist/search")
def anilist_search(title: str):
    cleaned_title = normalize_title(title)
    candidate_animes = search_anime(cleaned_title)
    if not candidate_animes:
        return {"cleaned_title": cleaned_title, "anime": None}
    return {"cleaned_title": cleaned_title, "anime": candidate_animes[0]}

@app.post("/anilist/save")
def anilist_save(body: ScoreRequest):
    conn = sqlite3.connect(db.DB_PATH)
    anilist_username = "kawarin"
    access_token = db.get_anilist_token(conn, anilist_username)
    conn.close()

    if access_token is None:
        return {"ok": False, "error": "AniList未連携です"}

    result = save_score(access_token, body.mediaId, body.score)
    if "errors" in result:
        return {"ok": False, "error": result["errors"][0]["message"]}
    return {"ok": True, "result": result}

# AniList連携チェック
@app.get("/auth/anilist/status")
def anilist_status():
    conn = sqlite3.connect(db.DB_PATH)
    token = db.get_anilist_token(conn, "kawarin")
    conn.close()
    return {"connected": token is not None}