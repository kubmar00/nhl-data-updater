import requests
import pandas as pd
import time

OUTPUT_FILE = "nhl_players.csv"

def safe_div(a, b):
    return round(a / b, 3) if b > 0 else 0

def main():
    print("Stahuji NHL data + formu hráčů...")

    all_players = []

    teams = requests.get(
        "https://statsapi.web.nhl.com/api/v1/teams",
        timeout=20
    ).json()["teams"]

    for team in teams:
        team_id = team["id"]
        team_name = team["name"]
        print(f"→ {team_name}")

        roster = requests.get(
            f"https://statsapi.web.nhl.com/api/v1/teams/{team_id}/roster",
            timeout=20
        ).json()["roster"]

        for r in roster:
            player_id = r["person"]["id"]
            player_name = r["person"]["fullName"]

            # sezónní statistiky
            stats = requests.get(
                f"https://statsapi.web.nhl.com/api/v1/people/"
                f"{player_id}/stats?stats=statsSingleSeason",
                timeout=20
            ).json()["stats"][0]["splits"]

            if not stats:
                continue

            stat = stats[0]["stat"]
            games = stat.get("games", 0)
            goals = stat.get("goals", 0)
            points = stat.get("points", 0)

            if games == 0:
                continue

            # forma – poslední zápasy
            logs = requests.get(
                f"https://statsapi.web.nhl.com/api/v1/people/"
                f"{player_id}/stats?stats=gameLog",
                timeout=20
            ).json()["stats"][0]["splits"]

            last5 = logs[:5]
            last10 = logs[:10]

            g5 = sum(g["stat"].get("goals", 0) for g in last5)
            p5 = sum(g["stat"].get("points", 0) for g in last5)

            g10 = sum(g["stat"].get("goals", 0) for g in last10)
            p10 = sum(g["stat"].get("points", 0) for g in last10)

            all_players.append({
                "team": team_name,
                "player": player_name,
                "games": games,
                "goals": goals,
                "points": points,
                "gpg_last5": safe_div(g5, len(last5)),
                "ppg_last5": safe_div(p5, len(last5)),
                "gpg_last10": safe_div(g10, len(last10)),
                "ppg_last10": safe_div(p10, len(last10)),
            })

            time.sleep(0.05)

    df = pd.DataFrame(all_players)
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    print("HOTOVO")
    print(f"Hráčů: {len(df)}")
    print(f"Soubor uložen: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
