import requests
import json
import os
ANILIST_ENDPOINT = 'https://graphql.anilist.co'

def fetch_anime_list(username: str) -> list[dict]:
    query = """
    query ($userName: String) {
        MediaListCollection(userName: $userName, type: ANIME) {
            lists {
                name
                entries {
                    status
                    score
                    progress
                    updatedAt
                    media {
                        id
                        idMal
                        title {
                            romaji
                            english
                            native
                        }
                        coverImage {
                            large
                        }
                        episodes
                        genres
                    }
                }
            }   
        }
    }
    """
    response = requests.post(ANILIST_ENDPOINT, json={'query': query, 'variables': {'userName': username}})
    return response.json()

def fetch_ratings(username: str) -> list[tuple[int, float]]:
    # (mal_id, score) のリストを返す。未評価(score=0)とidMal無しは除外。
    anime_list = fetch_anime_list(username)
    entries = []
    for lst in anime_list["data"]["MediaListCollection"]["lists"]:
        for entry in lst["entries"]:
            id_mal = entry["media"]["idMal"]
            score = entry["score"]
            if id_mal is not None and score > 0:  # 未評価(score=0)・idMal無しは除外
                entries.append((id_mal, score))
    return entries

def fetch_japanese_title_from_mal_id(mal_id: int) -> str:
    query = """
    query ($idMal: Int) {
        Media(idMal: $idMal) {
            title {
                native
            }
        }
    }
    """
    response = requests.post(ANILIST_ENDPOINT, json={'query': query, 'variables': {'idMal': mal_id}})
    title = response.json()['data']['Media']['title']['native']
    return title

"""
ref:
1.POST形式
https://coddy.tech/docs/ja/python/http-requests
2.AniList Token取得
https://docs.anilist.co/guide/auth/authorization-code
"""
def get_access_token(code: str) -> str:
    response = requests.post(
        "https://anilist.co/api/v2/oauth/token",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        json={
            "grant_type": "authorization_code",
            "client_id": os.environ['ANILIST_CLIENT_ID'],
            "client_secret": os.environ['ANILIST_CLIENT_SECRET'],
            "redirect_uri": os.environ['ANILIST_REDIRECT_URI'],
            "code": code
        }
    )
    return response.json()["access_token"]

def get_anilist_username(access_token: str) -> str:
    query = """
        query{
            Viewer{
                name
            }
        }
    """
    response = requests.post(
        ANILIST_ENDPOINT,
        headers={
            "Authorization": f"Bearer {access_token}",
            'Content-Type': 'application/json',
			'Accept': 'application/json',
        },
        json={'query': query}
    )
    return response.json()['data']['Viewer']['name']

def get_anilist_media_id(mal_id: int) -> int:
    query = """
        query ($idMal: Int)
        { 
            Media(idMal: $idMal){
                id
            } 
        }
    """
    response = requests.post(
        ANILIST_ENDPOINT,
        json={
            'query': query,
            'variables': {'idMal': mal_id}
        }
    )
    return response.json()['data']['Media']['id']

def save_score(access_token: str, media_id: int, score: float) -> dict:
    mutation = """
    mutation ($mediaId: Int, $score: Float) {
        SaveMediaListEntry(mediaId: $mediaId, status: COMPLETED, score: $score) {
            id
            status
            score
        }
    }
    """
    response = requests.post(
        ANILIST_ENDPOINT,
        json={
            'query': mutation,
            'variables':{
                'mediaId': media_id,
                'score': score
            }
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    return response.json()

def search_anime(title: str, per_page: int = 5) -> list[dict]:
    query = """
        query ($search: String, $perPage: Int)
        {
            Page(perPage: $perPage) {
                media(search: $search, type: ANIME) {
                    id
                    idMal
                    title {
                        romaji
                        english
                        native
                    }
                    coverImage {
                        medium
                    }
                }
            }
        }
    """
    response = requests.post(
        ANILIST_ENDPOINT,
        json={
            'query': query,
            'variables': {'search': title, 'perPage': per_page}
        }
    )
    return response.json()['data']['Page']['media']