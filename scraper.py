import requests
import json
import os
import hashlib
from bs4 import BeautifulSoup

SEEN_FILE = "seen_events.json"

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

def scrape_events():
    url = "https://www.serebii.net/index2.shtml"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    events = []
    # Grab all bold/header text as news headlines
    for tag in soup.find_all(["b", "h2", "h3"]):
        text = tag.get_text(strip=True)
        if len(text) > 15:
            events.append(text)
    return events

def send_to_discord(message):
    webhook_url = os.environ["DISCORD_WEBHOOK_URL"]
    data = {"content": f"🎮 **New Serebii Event!**\n{message}"}
    requests.post(webhook_url, json=data)

def main():
    seen = load_seen()
    events = scrape_events()
    new_found = False

    for event in events:
        event_id = hashlib.md5(event.encode()).hexdigest()
        if event_id not in seen:
            send_to_discord(event)
            seen.add(event_id)
            new_found = True

    if new_found:
        save_seen(seen)
    else:
        print("No new events.")

if __name__ == "__main__":
    main()
