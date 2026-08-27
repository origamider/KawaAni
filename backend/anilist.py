import requests
import json
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
