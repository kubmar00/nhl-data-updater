import requests
import pandas as pd
from datetime import datetime

OUTPUT_FILE = "nhl_players.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_teams():
    url = "https://api-web.nhle.com/v1/standings/now"
    data = requests.get(url, headers=HEADERS, timeout=20).json()
    teams = []
    for t in data["standings"]:
        teams.append({
            "id": t["teamAbbrev"]["default"],
            "name": t["teamName"]["default"]
        })
    return teams

def get_roster(team_abbrev):
    url = f"https://api-web.nhle.com/v1/roster/{team_abbrev}/current"
    data = requests.get(url, headers=HEADERS, timeout=20).json()
    players = []

    for group in ["forwards", "defensemen", "goalies"]:
        for p in data.get(group, []):
            players.append(p)

    return players

def get_player_stats(player_id):
    season = "20242025"
    url = f"https://api-web.nhle.com/v1/player/{player_id}/stats?season={season}"
    r = requests.get(url, headers=HEADERS, timeout=20)
    if r.status_code != 200:
        return None

    data = r.json()
    if "splits" not in data or not data["splits"]:
        return None

    return data["splits"][0]["stat"]

def main():
    print("Stahuji NHL data (nové API)...")

    rows = []
    teams = get_teams()

    for team in teams:
        print(f"→ {team['name']}")
        roster = get_roster(team["id"])

        for p in roster:
            stats = get_player_stats(p["id"])
            if not stats:
                continue

            games = stats.get("gamesPlayed", 0)
            goals = stats.get("goals", 0)
            points = stats.get("points", 0)

            if games == 0:
                continue

            rows.append({
                "team": team["name"],
                "player": f"{p['firstName']['default']} {p['lastName']['default']}",
                "games": games,
                "goals": goals,
                "points": points
            })

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    print(f"HOTOVO – hráčů: {len(df)}")
    print(f"Uloženo do {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
