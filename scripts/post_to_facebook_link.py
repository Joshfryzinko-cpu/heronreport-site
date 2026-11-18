"""Post a news article link to The Heron Report Facebook Page feed.
Reuses the Page token already configured for heron-broadcast's .env
(same Facebook Page, same credential — no need to duplicate it)."""
import os
import sys
import requests

# Load the existing Facebook Page credentials from heron-broadcast/.env
BROADCAST_ENV = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "..", "heron-broadcast", ".env"
)
BROADCAST_ENV = os.path.normpath(BROADCAST_ENV)


def load_env(path):
    env = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def post_article_link(article_url: str, message: str) -> dict:
    env = load_env(BROADCAST_ENV)
    page_id = env.get("FACEBOOK_PAGE_ID")
    page_token = env.get("FACEBOOK_PAGE_TOKEN")
    if not page_id or not page_token:
        raise RuntimeError(f"FACEBOOK_PAGE_ID/FACEBOOK_PAGE_TOKEN missing in {BROADCAST_ENV}")

    url = f"https://graph.facebook.com/v21.0/{page_id}/feed"
    resp = requests.post(url, data={
        "access_token": page_token,
        "message": message,
        "link": article_url,
    }, timeout=60)
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    article_url = sys.argv[1]
    message = sys.argv[2]
    result = post_article_link(article_url, message)
    print("RESULT:", result)
