from typing import Any
import pandas as pd
from sklearn import preprocessing
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torch.optim as optim
from cf_model import CollaborativeFilteringModel

class CustomDataset(Dataset):
    def __init__(self, users, animes, scores):
        self.users = users
        self.animes = animes
        self.scores = scores
    
    def __len__(self):
        return len(self.scores)
    
    def __getitem__(self, index):
        return self.users[index], self.animes[index], self.scores[index]

    """
    まとめて取得。これ何気に重要。
    __getitem__だと、要素のアクセスを１つずつ行なってしまう。
    __getitems__を用意すれば、欲しいindex集合をまとめてアクセスしてできる。
    https://docs.pytorch.org/tutorials/intermediate/intermediate_data_loading_tutorial.html
    """
    
    def __getitems__(self, indices):
        idx = torch.tensor(indices)
        return self.users[idx], self.animes[idx], self.scores[idx]

# preprocessing

le_user = preprocessing.LabelEncoder()
le_anime = preprocessing.LabelEncoder()
df = pd.read_csv('../data/rating_complete.csv')
df['user_id'] = le_user.fit_transform(df['user_id'].values) # user_idはすでに連番対応済
df['anime_id'] = le_anime.fit_transform(df['anime_id'].values) # anime_idは連番対応でないため、対応させる。48456->16871
users = torch.tensor(df['user_id'].values, dtype=torch.long)
animes = torch.tensor(df['anime_id'].values, dtype=torch.long)
scores = torch.tensor(df['rating'].values, dtype=torch.float32)

# hyperparameters
hidden_dim = 32
batch_size = 1024
num_epochs = 10
embedding_dim = 5
lr = 1e-3

train_dataset = CustomDataset(users, animes, scores)
train_loader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True,collate_fn=lambda batch: batch,)
model = CollaborativeFilteringModel(len(le_user.classes_), len(le_anime.classes_), embedding_dim, hidden_dim)
optimizer = optim.Adam(model.parameters(), lr=lr)
criterion = nn.MSELoss() # Mean Squared Error

for epoch in range(num_epochs):
    total_loss = 0
    ct = 0
    for batch_user_ids, batch_anime_ids, batch_scores in train_loader:
        ct += 1
        optimizer.zero_grad()
        predicted_output = model(batch_user_ids, batch_anime_ids)
        loss = criterion(predicted_output, batch_scores)
        total_loss += loss.item()
        loss.backward()
        optimizer.step()
    print(f"loss = {total_loss / ct} Epoch: {epoch}")

SAVE_PATH = '../model/model1.pt'
torch.save({
    "model_state_dict": model.state_dict(),
    "optimizer_state_dict": optimizer.state_dict(),
    "le_user": le_user,
    "le_anime": le_anime,
    "embedding_dim": embedding_dim,
    "hidden_dim": hidden_dim
},SAVE_PATH)


