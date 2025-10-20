import requests
from bs4 import BeautifulSoup
import json
import os
import sys
import time

BLOG_URL = "https://kingshot.net/blog"
STORED_FILE = "latest_post.json"
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL",
    "https://discord.com/api/webhooks/1383153401168138280/21Z6FBxt4o2LVnf-h4dfn4gQDf0LsJn7kNwgXGACoCssbQjvhx_fEmDbBaw88xNztkdo")

if not DISCORD_WEBHOOK_URL:
    print("Error: Discord webhook URL is not set.")
    sys.exit(1)

def fetch_latest_post():
    resp = requests.get(BLOG_URL, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # You may need to adjust the selectors below depending on actual HTML structure
    # Example: find first blog‑item link
    article = soup.select_one("div.blog-content a")  # adjust this selector appropriately
    if not article:
        raise RuntimeError("Could not locate latest blog post link")

    title = article.get_text(strip=True)
    href = article.get('href')
    if href and href.startswith("/"):
        href = "https://kingshot.net" + href

    # If there is a date element, you can capture it; if not, we just use title+link.
    # For now, we will not capture date.
    return {
        "title": title,
        "link": href
    }

def read_stored():
    if not os.path.exists(STORED_FILE):
        return None
    with open(STORED_FILE, "r") as f:
        return json.load(f)

def write_stored(post):
    with open(STORED_FILE, "w") as f:
        json.dump(post, f)

def send_discord_notification(post):
    data = {
        "content": f"🆕 New blog post: **{post['title']}**\n{post['link']}"
    }
    resp = requests.post(DISCORD_WEBHOOK_URL, json=data)
    resp.raise_for_status()

def main():
    try:
        latest = fetch_latest_post()
    except Exception as e:
        print("Error fetching latest post:", e)
        sys.exit(1)

    stored = read_stored()

    if stored is None:
        # First run: store and don’t send notification
        write_stored(latest)
        print("First run — stored latest post:", latest)
    else:
        if latest['link'] != stored.get('link'):
            print("New post detected:", latest)
            send_discord_notification(latest)
            write_stored(latest)
        else:
            print("No new post. Latest link matches stored one.")

if __name__ == "__main__":
    main()
