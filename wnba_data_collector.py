import os
import pandas as pd
import requests


DATA_DIR = "data"
OUTPUT_FILE = "data/wnba_games.csv"


def collect_wnba_games(season=2025):
    os.makedirs(DATA_DIR, exist_ok=True)

    url = "https://site.api.espn.com/apis/site/v2/sports/basketball/wnba/scoreboard"

    rows = []

    # WNBA regular season usually runs May to September.
    dates = pd.date_range(
        start=f"{season}-05-01",
        end=f"{season}-10-31",
        freq="D"
    )

    for game_date in dates:
        date_str = game_date.strftime("%Y%m%d")

        try:
            response = requests.get(
                url,
                params={"dates": date_str},
                timeout=20
            )

            if response.status_code != 200:
                continue

            data = response.json()
            events = data.get("events", [])

            for event in events:
                competitions = event.get("competitions", [])

                if not competitions:
                    continue

                competition = competitions[0]
                status = competition.get("status", {}).get("type", {})
                completed = status.get("completed", False)

                if not completed:
                    continue

                competitors = competition.get("competitors", [])

                home = None
                away = None

                for team in competitors:
                    if team.get("homeAway") == "home":
                        home = team
                    elif team.get("homeAway") == "away":
                        away = team

                if home is None or away is None:
                    continue

                rows.append({
                    "date": game_date.strftime("%Y-%m-%d"),
                    "season": str(season),
                    "home_team_id": home.get("team", {}).get("id"),
                    "away_team_id": away.get("team", {}).get("id"),
                    "home_team_name": home.get("team", {}).get("displayName"),
                    "away_team_name": away.get("team", {}).get("displayName"),
                    "home_score": int(home.get("score", 0)),
                    "away_score": int(away.get("score", 0))
                })

        except Exception:
            continue

    df = pd.DataFrame(rows)

    df = df.drop_duplicates(
        subset=[
            "date",
            "home_team_name",
            "away_team_name"
        ]
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    return {
        "status": "success",
        "season": season,
        "rows": len(df),
        "file": OUTPUT_FILE
    }


if __name__ == "__main__":
    print(collect_wnba_games(2025))
