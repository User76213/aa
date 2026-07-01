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
    for link in soup.find_all("a", href=True):
        href = link["href"]
        text = link.get_text(strip=True)
        if any(str(year) in href for year in range(2020, 2027)) and text:
            full_url = "https://www.serebii.net" + href if href.startswith("/") else href
            events.append(f"{text} — {full_url}")
    return events

def send_to_discord(message):
    webhook_url = os.environ["DISCORD_WEBHOOK_URL"]
    data = {"content": message}
    requests.post(webhook_url, json=data)

def main():
    seen = load_seen()
    events = scrape_events()
    new_found = False

    for event in events:
        url_part = event.split(" — ")[-1].strip()
        event_id = hashlib.md5(url_part.encode()).hexdigest()
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
