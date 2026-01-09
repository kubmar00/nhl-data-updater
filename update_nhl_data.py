import requests
import pandas as pd

OUTPUT_FILE = "nhl_players.csv"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_teams():
    url = "https://api-web.nhle.com/v1/standings/now"
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()

    teams = {}
    for t in data.get("standings", []):
        try:
            abbr = t["teamAbbrev"]["default"]
            name = t["teamName"]["default"]
            teams[abbr] = name
        except Exception:
            continue
    return teams

def get_roster(team_abbr):
    try:
        url = f"https://api-web.nhle.com/v1/roster/{team_abbr}/current"
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code != 200:
            return []
        data = r.json()

        players = []
        for group in ["forwards", "defensemen"]:
            for p in data.get(group, []):
                try:
                    players.append({
                        "id": p["id"],
                        "name": f"{p['firstName']['default']} {p['lastName']['default']}"
                    })
                except Exception:
                    continue
        return players
    except Exception:
        return []

def get_player_stats(player_id):
    try:
        url = f"https://api-web.nhle.com/v1/player/{player_id}/landing"
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code != 200:
            return None

        data = r.json()
        stats = data.get("featuredStats", {}).get("regularSeason", {})

        games = stats.get("gamesPlayed", 0)
        goals = stats.get("goals", 0)
        points = stats.get("points", 0)

        if not games or games == 0:
            return None

        return {
            "games": games,
            "goals": goals,
            "points": points
        }
    except Exception:
        return None

def main():
    print("Stahuji NHL data – BULLETPROOF VE
