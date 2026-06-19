import os
import pandas as pd


DATA_FILE = "data/wnba_games.csv"


def predict_wnba_total(home_team, away_team, bookmaker_total=165.5):
    if not os.path.exists(DATA_FILE):
        return {
            "status": "error",
            "message": "data/wnba_games.csv not found"
        }

    df = pd.read_csv(DATA_FILE)

    if df.empty:
        return {
            "status": "error",
            "message": "WNBA historical data is empty"
        }

    df["total_score"] = df["home_score"] + df["away_score"]

    home_games = df[
        (df["home_team_name"] == home_team) |
        (df["away_team_name"] == home_team)
    ]

    away_games = df[
        (df["home_team_name"] == away_team) |
        (df["away_team_name"] == away_team)
    ]

    home_avg = home_games["total_score"].tail(10).mean()
    away_avg = away_games["total_score"].tail(10).mean()

    if pd.isna(home_avg):
        home_avg = df["total_score"].mean()

    if pd.isna(away_avg):
        away_avg = df["total_score"].mean()

    projected_total = round((home_avg + away_avg) / 2, 2)
    edge = round(projected_total - float(bookmaker_total), 2)

    if edge >= 6:
        recommendation = "Strong Over"
    elif edge >= 3:
        recommendation = "Lean Over"
    elif edge <= -6:
        recommendation = "Strong Under"
    elif edge <= -3:
        recommendation = "Lean Under"
    else:
        recommendation = "No Bet"

    return {
        "status": "success",
        "home_team": home_team,
        "away_team": away_team,
        "projected_total": projected_total,
        "bookmaker_total": bookmaker_total,
        "edge": edge,
        "recommendation": recommendation,
        "history_rows": len(df)
    }
