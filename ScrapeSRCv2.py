import json
import logging
import sys
import time
from pathlib import Path

from pydantic import ValidationError

from speedruncompy.endpoints import GetGameData, GetGameLeaderboard2

logging.getLogger("speedruncompy").setLevel(logging.ERROR)

games = {
    "j1ne5891": {"name": "Main Board", "path": Path("MainBoard.json")},
    "v1ponx76": {"name": "Category Extensions", "path": Path("CategoryExtensions.json")},
    "4d7nxqn6": {"name": "Elusive Targets", "path": Path("ElusiveTargets.json")},
    "kdkmjxg1": {"name": "Escalations", "path": Path("Escalations.json")},
    "76r35zv6": {"name": "Freelancer", "path": Path("Freelancer.json")}
}

combined = Path("CombinedBoards.json")

sys.stdout.reconfigure(encoding="utf-8")

current_list = []
all_list = []
incomplete = False
_warned_raw = False

def _as_dict(result):
    if isinstance(result, dict):
        return result
    dump = getattr(result, "model_dump", None)
    if callable(dump):
        return dump()
    return result

def _raw_json(request):
    global _warned_raw
    raw = getattr(request, "response", None)
    if not raw:
        raise RuntimeError("src response model rejected payload")
    content = raw[0]
    if isinstance(content, bytes):
        content = content.decode()
    if not _warned_raw:
        print("src response model stale", flush=True)
        _warned_raw = True
    return json.loads(content)

def _once(request):
    try:
        return request.perform_sync()
    except ValidationError:
        return _raw_json(request)

def perform(request):
    result = _once(request)
    time.sleep(2)
    return _as_dict(result)

class Run:
    def __init__(self, run_data):
        self.data = {
            "weblink": f"https://www.speedrun.com/run/{run_data.get('id')}",
            "video": run_data.get("video")
        }

    def to_dict(self):
        return self.data

def process_page(gameId, categoryId, page):
    global incomplete
    try:
        res = perform(GetGameLeaderboard2(
            gameId, categoryId, obsolete=1, video=1, verified=1, page=page
        ))
        
        runs = res.get("runList") or []

        for r in runs:
            run_item = Run(r).to_dict()
            current_list.append(run_item)
            all_list.append(run_item)

        return int(res["pagination"]["pages"])
    except Exception as e:
        incomplete = True
        print(f"page failed game={gameId} category={categoryId} page={page}: {e}")
        return 0

def process_category(gameId, categoryId):
    total_pages = process_page(gameId, categoryId, 1)
    for p in range(2, total_pages + 1):
        process_page(gameId, categoryId, p)

def process_game(gameId):
    global incomplete
    try:
        data = perform(GetGameData(gameId))
    except Exception as e:
        incomplete = True
        print(f"game data failed game={gameId}: {e}")
        return
    if not data: 
        return

    for c in data["categories"]:
        process_category(gameId, c["id"])

def main():
    global current_list, incomplete
    ok = True
    
    for gid, info in games.items():
        print(f"Scraping {info['name']}")
        
        current_list = []
        incomplete = False
        process_game(gid)

        if incomplete:
            ok = False
            print(f"{info['name']} incomplete, file left unchanged\n")
            continue
        
        with open(info["path"], "w", encoding="utf-8") as f:
            json.dump(current_list, f, indent=2)
            
        print(f"{info['name']} completed with {len(current_list)} runs\n")

    if not ok:
        print("combined file left unchanged")
        sys.exit(1)

    with open(combined, "w", encoding="utf-8") as f:
        json.dump(all_list, f, indent=2)
    
    print(f"Done, combined total of {len(all_list)} runs")

if __name__ == "__main__":
    main()