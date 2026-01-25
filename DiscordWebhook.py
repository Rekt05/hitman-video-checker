import json
import requests
import os

webhook = os.getenv('dcwebhook')
file = 'unavailable_yt_videos.json'

def send_message():
    with open(file, 'r') as f:
        data = json.load(f)
        count = len(data)

    if count > 0:
        message = {
            "embeds": [{
                "title": "New Unavailable Videos",
                "description": f"Found {count} new unavailable videos",
                "url": "https://rekt05.github.io/hitman-video-checker/"
            }]
        }
        requests.post(webhook, json=message)

if __name__ == "__main__":
    send_message()