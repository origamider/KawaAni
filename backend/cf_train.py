from typing import Any
import pandas as pd
from sklearn import preprocessing
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torch.optim as optim
from cf_model import CollaborativeFilteringModel
from pathlib import Path
from tqdm import tqdm

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

# GPU使用
if torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")
    
df = pd.read_csv(f'{Path(__file__).parents[1]}/data/ratings.csv')
users = torch.tensor(df['userID'].values, dtype=torch.long).to(device)
animes = torch.tensor(df['animeID'].values, dtype=torch.long).to(device)
scores = torch.tensor(df['rating'].values, dtype=torch.float32).to(device)

# hyperparameters
hidden_dim = 32
batch_size = 131072
num_epochs = 10
embedding_dim = 10
lr = 1e-3

train_dataset = CustomDataset(users, animes, scores)
train_loader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True,collate_fn=lambda batch: batch,)
model = CollaborativeFilteringModel(df['userID'].max() + 1, df['animeID'].max() + 1, embedding_dim, hidden_dim)
model.to(device)
optimizer = optim.Adam(model.parameters(), lr=lr)
criterion = nn.MSELoss() # Mean Squared Error

for epoch in tqdm(range(num_epochs)):
    current_loss = torch.tensor([0.0], device=device)
    ct = 0
    for batch_user_ids, batch_anime_ids, batch_scores in train_loader:
        ct += 1
        optimizer.zero_grad()
        predicted_output = model(batch_user_ids, batch_anime_ids)
        loss = criterion(predicted_output, batch_scores)
        loss.backward()
        optimizer.step()
        current_loss += loss.detach()
    print(f"loss = {current_loss.item() / ct} Epoch: {epoch}")

SAVE_PATH = '../model/model1.pt'
torch.save({
    "model_state_dict": model.state_dict(),
    "optimizer_state_dict": optimizer.state_dict(),
    "embedding_dim": embedding_dim,
    "hidden_dim": hidden_dim
},SAVE_PATH)


