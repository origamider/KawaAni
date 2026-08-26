from pathlib import Path
import torch
import torch.nn as nn
import torch.optim as optim
from cf_model import predict, load_frozen_model, MODEL_PATH
from anilist import fetch_ratings
import sqlite3
import db

cpt, model = load_frozen_model(MODEL_PATH)
entries = fetch_ratings("kawarin")
conn = sqlite3.connect(db.DB_PATH)

# GPU使用
if torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")

model.to(device)

# kaggle datasetから、mal_id->anime_idへの辞書作成
mal_to_anime_id = db.get_mal_to_anime_id(conn)
# in演算子で辞書のkey存在チェックで対応
matched = [(id_mal, score) for (id_mal, score) in entries if id_mal in mal_to_anime_id]
print(f"{len(matched)}/{len(entries)} 件が学習済アニメリストに存在しています")

# anime_idに変換する。(機械学習するため)
anime_ids = torch.tensor([mal_to_anime_id[id_mal] for id_mal, _ in matched],dtype=torch.long).to(device)
target_scores = torch.tensor([score for _, score in matched], dtype=torch.float32).to(device)

# ユーザー専用の埋め込みベクトル作成。(embedding_dim,)。N(0,1)
embedding_dim = cpt["embedding_dim"]
user_vector = nn.Parameter(torch.randn(embedding_dim).to(device))

optimizer = optim.Adam([user_vector],lr=1e-2)
criterion = nn.MSELoss()

num_epochs = 10000
total_loss = torch.tensor([0.0],device=device)
for epoch in range(num_epochs):
    optimizer.zero_grad()
    predicted_output = predict(user_vector, anime_ids, model)
    loss = criterion(predicted_output, target_scores)
    loss.backward()
    optimizer.step()
    total_loss += loss.detach()
    if(epoch % 50 == 0):
        print(f"epoch:{epoch} loss:{total_loss.item()/50}")
        total_loss = 0.0

db.init_users_table(conn)
db.init_user_ratings_table(conn)
db.replace_user_ratings(conn, "kawarin", entries)
db.upsert_user_vector(conn, "kawarin", user_vector.detach().tolist())
conn.close()
print("user_vectorをDBに保存しました。")