from typing import Any
import pandas as pd
from sklearn import preprocessing
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torch.optim as optim

class CustomDataset(Dataset):
    def __init__(self, users, animes, scores):
        self.users = users
        self.animes = animes
        self.scores = scores
    
    def __len__(self):
        return len(self.scores)
    
    def __getitem__(self, index):
        return self.users[index], self.animes[index], self.scores[index]

# user_idとanime_idからscoreを予測するモデル。
class CollaborativeFilteringModel(nn.Module):
    def __init__(self, n_users, n_animes, embedding_dim, hidden_dim):
        super().__init__()
        self.user_embed_layer = nn.Embedding(n_users, embedding_dim)
        self.anime_embed_layer = nn.Embedding(n_animes, embedding_dim)
        self.linear_layer1 = nn.Linear(embedding_dim*2, hidden_dim)
        self.linear_layer2 = nn.Linear(hidden_dim, 1)
        self.relu = nn.ReLU()
    
    # batch化するか。
    def forward(self, users, animes):
        users_vector = self.user_embed_layer(users)
        animes_vector = self.anime_embed_layer(animes)
        inputs = torch.concat([users_vector, animes_vector], dim=1)
        predicted_score = self.linear_layer2(self.relu(self.linear_layer1(inputs)))
        
        return predicted_score

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
train_loader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)
model = CollaborativeFilteringModel(len(le_user.classes_), len(le_anime.classes_), embedding_dim, hidden_dim)
optimizer = optim.Adam(model.parameters(), lr=lr)
criterion = nn.MSELoss() # Mean Squared Error

for epoch in range(num_epochs):
    for batch_user_ids, batch_anime_ids, batch_scores in train_loader:
        optimizer.zero_grad()
        
        predicted_output = model(batch_user_ids, batch_anime_ids)
        loss = criterion(predicted_output, batch_scores)
        loss.backward()
        optimizer.step()
    print(f"loss = {loss.item()} Epoch: {epoch}")

SAVE_PATH = '../model/model.pt'
torch.save({
    "model_state_dict": model.state_dict(),
    "optimizer_state_dict": optimizer.state_dict(),
    "le_user": le_user,
    "le_anime": le_anime,
    "embedding_dim": embedding_dim,
    "hidden_dim": hidden_dim
},SAVE_PATH)
