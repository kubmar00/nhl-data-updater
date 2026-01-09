import requests
import pandas as pd

OUTPUT_FILE = "nhl_players.csv"
HEADERS = {"User-Agent": "Mozilla/5.0"}

SEASON = "20242025"

def get_teams():
    url = "https://api-web.nhle.com/v1/standings/now"
    data = requests.get(url, headers=HEADERS, timeout=30).json()

    teams = {}
    for t in data["standings"]:
        abbr = t["teamAbbrev"]["default"]
        name = t["teamName"]["default"]
        teams[abbr] = name

    return teams

def get_roster(team_abbr):
    url = f"https://api-web.nhle.com/v1/roster/{team_abbr}/current"
    data = requests.get(url, headers=HEADERS, timeout=30).json()

    players = []
    for group in ["forwards", "defensemen"]:
        for p in data.get(group, []):
            players.append({
                "id": p["id"],
                "name": f"{p['firstName']['default']} {p['lastName']['default']}"
            })
    return players

def get_player_stats(player_id):
    url = f"https://api-web.nhle.com/v1/player/{player_id}/landing"
    r = requests.get(url, headers=HEADERS, timeout=30)

    if r.status_code != 200:
        return None

    data = r.json()

    stats = data.get("featuredStats", {}).get("regularSeason", {})
    if not stats:
        return None

    return {
        "games": stats.get("gamesPlayed", 0),
        "goals": stats.get("goals", 0),
        "points": stats.get("points", 0)
    }

def main():
    print("Stahuji NHL data – FINÁLNÍ VERZE")

    teams = get_teams()
    rows = []

    for abbr, team_name in teams.items():
        print(f"→ {team_name}")
        roster = get_roster(abbr)

        for player in roster:
            stats = get_player_stats(player["id"])
            if not stats:
                continue

            if stats["games"] == 0:
                continue

            rows.append({
                "team": team_name,
                "player": player["name"],
                "games": stats["games"],
                "goals": stats["goals"],
                "points": stats["points"]
            })

    df = pd.DataFrame(rows)

    if df.empty:
        raise RuntimeError("CSV by bylo prázdné – NHL API změna!")

    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    print(f"HOTOVO – hráčů: {len(df)}")
    print(f"Uloženo do {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
