import os
import joblib
import pandas as pd


DATA_FILE = "data/wnba_games.csv"
MODEL_FILE = "models/wnba_totals_model_v1.joblib"


def safe_float(value, default=0):
    try:
        return float(value)
    except Exception:
        return default


def predict_wnba_total(
    home_team,
    away_team,
    bookmaker_total=165.5
):
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

    df["total_score"] = (
        pd.to_numeric(
            df["home_score"],
            errors="coerce"
        ).fillna(0)
        +
        pd.to_numeric(
            df["away_score"],
            errors="coerce"
        ).fillna(0)
    )

    home_games = df[
        (df["home_team_name"].astype(str) == str(home_team))
        |
        (df["away_team_name"].astype(str) == str(home_team))
    ]

    away_games = df[
        (df["home_team_name"].astype(str) == str(away_team))
        |
        (df["away_team_name"].astype(str) == str(away_team))
    ]

    home_avg = home_games["total_score"].tail(10).mean()
    away_avg = away_games["total_score"].tail(10).mean()

    if pd.isna(home_avg):
        home_avg = df["total_score"].mean()

    if pd.isna(away_avg):
        away_avg = df["total_score"].mean()

    avg_total_last_10 = round(
        (home_avg + away_avg) / 2,
        2
    )

    projected_total = avg_total_last_10
    model_used = False

    if os.path.exists(MODEL_FILE):
        try:
            model = joblib.load(MODEL_FILE)

            features = pd.DataFrame(
                [[avg_total_last_10]],
                columns=["avg_total_last_10"]
            )

            projected_total = round(
                float(model.predict(features)[0]),
                2
            )

            model_used = True

        except Exception:
            projected_total = avg_total_last_10
            model_used = False

    bookmaker_total = safe_float(
        bookmaker_total,
        165.5
    )

    edge = round(
        projected_total - bookmaker_total,
        2
    )

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
        "history_rows": len(df),
        "avg_total_last_10": avg_total_last_10,
        "model_used": model_used,
        "model_file": MODEL_FILE if model_used else "fallback_average",
        "debug_test": "WNBA_V2_RUNNING"
    }
