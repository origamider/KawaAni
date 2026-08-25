import torch
import numpy as np
import db
from cf_model import predict

def recommend_top3(cpt, model, conn, anilist_username: str = "kawarin") -> list[dict]:
    user_vector = db.get_user_vector(conn, anilist_username)
    if user_vector is None:
        raise ValueError("user vectorが未学習です。先にcf_fold_in.pyを実行してください")
    user_vector = torch.tensor(user_vector, dtype=torch.float32)
    
    watched = db.get_watched_mal_ids(conn, anilist_username)
    all_ids = cpt["le_anime"].classes_.astype(np.int64) #label変換前
    candidate_ids = [int(i) for i in all_ids if int(i) not in watched] # 視聴していないアニメmal_id配列
    candidate_idx = torch.tensor(cpt["le_anime"].transform(candidate_ids),dtype=torch.long) # 候補mal_id配列をLabel変換。
    
    # 機械学習しない設定
    with torch.no_grad():
        scores = predict(user_vector, candidate_idx, model)
    
    # scoreの高い順に3つ取得。
    top = torch.topk(scores,3)
    top_mal_ids = [candidate_ids[i] for i in top.indices.tolist()]