import torch
import numpy as np
import db
from cf_model import predict
import anilist

def recommend_top3_mal_id(model, conn, anilist_username: str = "kawarin") -> list[dict]:
    user_vector = db.get_user_vector(conn, anilist_username)
    if user_vector is None:
        raise ValueError("user vectorが未学習です。先にcf_fold_in.pyを実行してください")
    user_vector = torch.tensor(user_vector, dtype=torch.float32)
    
    watched = db.get_watched_mal_ids(conn, anilist_username) # mal_idのset
    mal_to_anime_id = db.get_mal_to_anime_id(conn) # mal_id,anime_idの辞書
    candidate_ids = [mal_id for mal_id in mal_to_anime_id if mal_id not in watched] # 視聴していないアニメmal_id配列
    candidate_idx = torch.tensor([mal_to_anime_id[mal_id] for mal_id in candidate_ids],dtype=torch.long) # 候補mal_id配列をLabel変換。
    
    # 機械学習しない設定
    with torch.no_grad():
        scores = predict(user_vector, candidate_idx, model)
    
    # scoreの高い順に3つ取得。
    top = torch.topk(scores,3)
    top_mal_ids = [candidate_ids[i] for i in top.indices.tolist()]
    
    info = db.get_anime_info_from_mal_ids(conn, top_mal_ids)
    
    for id_mal in top_mal_ids:
        title = info[id_mal]['japanese_title']
        if title is None:
            title = anilist.fetch_japanese_title_from_mal_id(id_mal)
            db.update_japanese_title(conn, id_mal, title)
            info[id_mal]['japanese_title'] = title
    
    return [info[id_mal] for id_mal in top_mal_ids]
    
    
    