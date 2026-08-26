import requests
import json

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
    url = 'https://graphql.anilist.co'
    response = requests.post(url, json={'query': query, 'variables': {'userName': username}})
    return response.json()

# return: (id_mal, score)
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