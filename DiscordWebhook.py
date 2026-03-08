import json
import requests
import os

webhook = os.getenv('dcwebhook')
file = 'unavailable_yt_videos.json'
txt = 'unavailable_vid_count.txt'

def send_message():
    with open(file, 'r') as f:
        data = json.load(f)
        count = len(data)

    last_count = 0
    with open(txt, 'r') as f:
        content = f.read().strip()
        last_count = int(content) if content else 0

    if count != last_count:
        diff = count - last_count
        if diff > 0:
            desc = f"Found {diff} new unavailable video(s) - Total {count}"
        else:
            desc = f"{abs(diff)} less unavailable video(s) - Total {count}"
        message = {
            "embeds": [{
                "title": "Unavailable Videos Update",
                "description": desc,
                "url": "https://rekt05.github.io/hitman-video-checker/"
            }]
        }
        response = requests.post(webhook, json=message)

        if response.status_code < 300:
            with open(txt, 'w') as f:
                f.write(str(count))

if __name__ == "__main__":
    send_message()