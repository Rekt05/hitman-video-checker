import json
import sys
from pathlib import Path
from speedruncompy.api import *
from speedruncompy.endpoints import *

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

class Run:
    def __init__(self, run_data):
        self.data = {
            "weblink": f"https://www.speedrun.com/run/{run_data.get('id')}",
            "video": run_data.get("video")
        }

    def to_dict(self):
        return self.data

#https://github.com/ManicJamie/speedruncompy/blob/7af7d67659f73b5122263dbab66aa5e93663ac77/src/speedruncompy/endpoints.py#L16
def process_page(gameId, categoryId, page):
    try:
        res = GetGameLeaderboard2(
            gameId, categoryId, obsolete=1, video=1, verified=1, page=page
        ).perform()
        
        runs = res.get("runList", [])

        for r in runs:
            run_item = Run(r).to_dict()
            current_list.append(run_item)
            all_list.append(run_item)

        return res["pagination"]["pages"]
    except Exception:
        return 0

def process_category(gameId, categoryId):
    total_pages = process_page(gameId, categoryId, 1)
    for p in range(2, total_pages + 1):
        process_page(gameId, categoryId, p)

def process_game(gameId):
    data = GetGameData(gameId).perform()
    if not data: 
        return

    for c in data["categories"]:
        process_category(gameId, c["id"])

def main():
    global current_list
    
    for gid, info in games.items():
        print(f"Scraping {info['name']}")
        
        current_list = [] 
        process_game(gid)
        
        with open(info["path"], "w", encoding="utf-8") as f:
            json.dump(current_list, f, indent=2)
            
        print(f"{info['name']} completed with {len(current_list)} runs\n")

    with open(combined, "w", encoding="utf-8") as f:
        json.dump(all_list, f, indent=2)
    
    print(f"Done, combined total of {len(all_list)} runs")

if __name__ == "__main__":
    main()