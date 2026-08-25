from pathlib import Path

import torch
import torch.nn as nn

MODEL_PATH = Path(__file__).parents[1] / "model" / "model.pt"

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
        
        """
        (N,1)->(N)。これをしないと、MSELossの計算の際、broadcastされ、おかしくなる。
        ex:
        a = torch.tensor([1,2,3],dtype=torch.float32)
        b = torch.tensor([[1],[2],[3]],dtype=torch.float32)
        criterion = nn.MSELoss()
        loss = criterion(a,b)
        loss.item()
        ->1.3333333730697632
        """
        return predicted_score.squeeze(1)

# 推測関数
def predict(user_vector, anime_idx_tensor, model):
    u = user_vector.unsqueeze(0).expand(len(anime_idx_tensor),-1)
    a = model.anime_embed_layer(anime_idx_tensor)
    x = torch.cat([u, a], dim=1)
    # squeeze(1)で(N,1)=>(N,)
    return model.linear_layer2(model.relu(model.linear_layer1(x))).squeeze(1)

# model読み込み
def load_frozen_model(path: Path = MODEL_PATH):
    cpt = torch.load(MODEL_PATH,weights_only=False)# checkpoint
    model = CollaborativeFilteringModel(
        n_users=len(cpt["le_user"].classes_),
        n_animes=len(cpt["le_anime"].classes_),
        embedding_dim=cpt["embedding_dim"],
        hidden_dim=cpt["hidden_dim"])
    model.load_state_dict(cpt["model_state_dict"])
    model.eval()
    model.anime_embed_layer.requires_grad_(False)
    model.linear_layer1.requires_grad_(False)
    model.linear_layer2.requires_grad_(False)
    return cpt, model