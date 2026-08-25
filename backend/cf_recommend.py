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