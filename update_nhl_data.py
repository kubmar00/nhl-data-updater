import pandas as pd
import time

OUTPUT_FILE = "nhl_players.csv"
SEASON = 2024

TEAMS = {
    "ANA": "Anaheim Ducks",
    "BOS": "Boston Bruins",
    "BUF": "Buffalo Sabres",
    "CGY": "Calgary Flames",
    "CAR": "Carolina Hurricanes",
    "CHI": "Chicago Blackhawks",
    "COL": "Colorado Avalanche",
    "CBJ": "Columbus Blue Jackets",
    "DAL": "Dallas Stars",
    "DET": "Detroit Red Wings",
    "EDM": "Edmonton Oilers",
    "FLA": "Florida Panthers",
    "LAK": "Los Angeles Kings",
    "MIN": "Minnesota Wild",
    "MTL": "Montreal Canadiens",
    "NSH": "Nashville Predators",
    "NJD": "New Jersey Devils",
    "NYI": "New York Islanders",
    "NYR": "New York Rangers",
    "OTT": "Ottawa Senators",
    "PHI": "Philadelphia Flyers",
    "PIT": "Pittsburgh Penguins",
    "SJS": "San Jose Sharks",
    "SEA": "Seattle Kraken",
    "STL": "St. Louis Blues",
    "TBL": "Tampa Bay Lightning",
    "TOR": "Toronto Maple Leafs",
    "VAN": "Vancouver Canucks",
    "VGK": "Vegas Golden Knights",
    "WSH": "Washington Capitals",
    "WPG": "Winnipeg Jets"
}

def main():
    print("Stahuji NHL data z hockey-reference.com")
    rows = []

    for abbr, team_name in TEAMS.items():
        url = f"https://www.hockey-reference.com/teams/{abbr}/{SEASON}.html"
        print(f"→ {team_name}")

        try:
            tables = pd.read_html(url, attrs={"id": "skaters"})
            df = tables[0]

            df.columns = df.columns.droplevel(0)
            df = df.dropna(subset=["Player"])

            df = df.rename(columns={
                "Player": "player",
                "GP": "games",
                "G": "goals",
                "PTS": "points"
            })

            df["team"] = team_name
            df = df[["team", "player", "games", "goals", "points"]]

            for col in ["games", "goals", "points"]:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            df = df.dropna()
            rows.append(df)

            time.sleep(1)  # proti 429

        except Exception as e:
            print(f"⚠️ Přeskočeno ({team_name}): {e}")
            continue

    if rows:
        final_df = pd.concat(rows, ignore_index=True)
    else:
        final_df = pd.DataFrame(columns=["team", "player", "games", "goals", "points"])

    final_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    print(f"HOTOVO – hráčů: {len(final_df)}")
    print(f"Uloženo do {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
