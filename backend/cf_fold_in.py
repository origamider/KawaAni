from pathlib import Path
import pandas as pd
from sklearn import preprocessing
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torch.optim as optim
from cf_model import CollaborativeFilteringModel, predict, load_frozen_model
from anilist import fetch_ratings
import numpy as np
import sqlite3
import db

MODEL_PATH = Path(__file__).parents[1] / "model/model.pt";
cpt, model = load_frozen_model(MODEL_PATH)
entries = fetch_ratings("kawarin")

# kaggle datasetのアニメid集合
known_ids = set(cpt["le_anime"].classes_.astype(np.int64))
matched = [(id_mal, score) for (id_mal, score) in entries if id_mal in known_ids]
print(f"{len(matched)}/{len(entries)} 件が学習済アニメリストに存在しています")

# LabelEocode済の配列に変換
anime_ids = torch.tensor(cpt["le_anime"].transform([id_mal for id_mal,tmp in matched]),dtype=torch.long)
target_scores = torch.tensor([score for _, score in matched], dtype=torch.float32)

# ユーザー専用の埋め込みベクトル作成。(embedding_dim,)。N(0,1)
embedding_dim = cpt["embedding_dim"]
user_vector = nn.Parameter(torch.randn(embedding_dim) * 0.1)

optimizer = optim.Adam([user_vector],lr=1e-2)
criterion = nn.MSELoss()

num_epochs = 10000
for epoch in range(num_epochs):
    optimizer.zero_grad()
    predicted_output = predict(user_vector, anime_ids, model)
    loss = criterion(predicted_output, target_scores)
    loss.backward()
    optimizer.step()
    if(epoch % 50 == 0):
        print(f"epoch:{epoch} loss:{loss.item()}")


conn = sqlite3.connect(db.DB_PATH)
db.init_users_table(conn)
db.upsert_user_vector(conn, "kawarin", user_vector.detach().tolist())
conn.close()
print("user_vectorをDBに保存しました。")