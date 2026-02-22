from fastapi import FastAPI, File, UploadFile, HTTPException
import json
from typing import List, Set

app = FastAPI(
    title="Instagram Unfollower Detector",
    description="Upload your Instagram data files to find out who doesn't follow you back.",
    version="1.1"
)


def extract_usernames(json_data: list) -> Set[str]:
    """
    Parses the specific JSON structure provided by Instagram/Meta exports.
    Handles differences between 'followers' and 'following' file structures.
    """
    usernames = set()

    # 1. Drill down if the root is a dictionary (common in 'following.json')
    if isinstance(json_data, dict):
        if "relationships_following" in json_data:
            json_data = json_data["relationships_following"]
        elif "relationships_followers" in json_data:
            json_data = json_data["relationships_followers"]

    # If it's still not a list, we can't parse it
    if not isinstance(json_data, list):
        return set()

    for entry in json_data:
        username = None

        # STRATEGY A: Try to find username in 'string_list_data' (Standard for Followers)
        try:
            if "string_list_data" in entry and len(entry["string_list_data"]) > 0:
                item = entry["string_list_data"][0]
                if "value" in item:
                    username = item["value"]
        except (KeyError, IndexError):
            pass

        # STRATEGY B: If A failed, try to find username in 'title' (Standard for Following)
        if not username:
            if "title" in entry and entry["title"]:
                username = entry["title"]

        # If we found a username, add it to the set
        if username:
            usernames.add(username)

    return usernames


@app.post("/check-unfollowers")
async def check_unfollowers(
        followers_file: UploadFile = File(..., description="Upload followers_1.json"),
        following_file: UploadFile = File(..., description="Upload following.json")
):
    try:
        # 1. Read and parse the Followers file
        followers_content = await followers_file.read()
        followers_json = json.loads(followers_content)
        followers_set = extract_usernames(followers_json)

        # 2. Read and parse the Following file
        following_content = await following_file.read()
        following_json = json.loads(following_content)
        following_set = extract_usernames(following_json)

        # 3. Validation
        if not followers_set and not following_set:
            return {
                "error": "No data found. Please check if you uploaded the correct JSON files.",
                "followers_found": 0,
                "following_found": 0
            }

        # 4. Logic: (Following) - (Followers) = People I follow who don't follow me
        not_following_back = list(following_set - followers_set)
        not_following_back.sort()

        return {
            "stats": {
                "total_following": len(following_set),
                "total_followers": len(followers_set),
                "not_following_back_count": len(not_following_back)
            },
            "users_not_following_back": not_following_back
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file uploaded.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)