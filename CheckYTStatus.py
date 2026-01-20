import json
import os
import re
from googleapiclient.discovery import build
from urllib.parse import urlparse

#if you want to run this locally need to put your own api key here or use a .env
#https://developers.google.com/youtube/v3/getting-started
api_key = os.getenv("ytapikey") or "here"
input = "CombinedBoards.json"

output_unavail = "unavailable_yt_videos.json"
output_non_yt = "non_yt_videos.json"

batch_size = 50

yt_regex = re.compile(r"[A-Za-z0-9_-]{11}")

def get_video_id(url):
    if not url or not isinstance(url, str):
        return None

    parsed = urlparse(url)
    netloc = parsed.netloc.lower()

    if not any(x in netloc for x in ("youtube.com", "youtu.be", "m.youtube.com")):
        return None

    spots = " ".join([
        parsed.path or "",
        parsed.query or "",
        parsed.fragment or ""
    ])

    match = yt_regex.search(spots)
    if match:
        return match.group(0)

    return None

def main():

    with open(input, "r", encoding="utf-8") as f:
        data = json.load(f)

    yt_id_groups = {}
    non_yt_entries = []

    for run in data:
        vid_url = run.get("video", "")
        vid_id = get_video_id(vid_url)

        if not vid_id:
            non_yt_entries.append({
                "weblink": run.get("weblink"),
                "video": vid_url
            })
            continue

        if vid_id not in yt_id_groups:
            yt_id_groups[vid_id] = []
        yt_id_groups[vid_id].append(run)

    with open(output_non_yt, "w", encoding="utf-8") as f:
        json.dump(non_yt_entries, f, indent=2, ensure_ascii=False)

    video_ids = list(yt_id_groups.keys())
    total = len(video_ids)

    print(f"Checking {total} unique yt videos")

    youtube = build("youtube", "v3", developerKey=api_key)

    unavailable_vids = []

    for i in range(0, total, batch_size):
        batch = video_ids[i : i + batch_size]

        response = youtube.videos().list(
            part="status",
            id=",".join(batch),
        ).execute()

        found_ids = set()
        private_ids = set()

        for item in response.get("items", []):
            vid_id = item["id"]
            found_ids.add(vid_id)

            if item["status"].get("privacyStatus") == "private":
                private_ids.add(vid_id)

        missing_ids = set(batch) - found_ids
        unavailable_ids = private_ids | missing_ids

        for vid_id in unavailable_ids:
            runs_sharing_video = yt_id_groups[vid_id]
            for run in runs_sharing_video:
                unavailable_vids.append({
                    "weblink": run.get("weblink"),
                    "video": run.get("video")
                })

        print(f"Progress: {min(i + batch_size, total)}/{total}")

        with open(output_unavail, "w", encoding="utf-8") as f:
            json.dump(unavailable_vids, f, indent=2, ensure_ascii=False)

    print("Done")

if __name__ == "__main__":
    main()