import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor


DATA_FILE = "data/wnba_games.csv"
MODEL_FILE = "models/wnba_totals_model_v1.joblib"


def train_wnba_totals_model():

    df = pd.read_csv(DATA_FILE)

    df["total_score"] = (
        df["home_score"] +
        df["away_score"]
    )

    features = []
    targets = []

    for i in range(10, len(df)):

        recent_games = df.iloc[i-10:i]

        avg_total = recent_games[
            "total_score"
        ].mean()

        features.append([
            avg_total
        ])

        targets.append(
            df.iloc[i]["total_score"]
        )

    X = pd.DataFrame(
        features,
        columns=["avg_total_last_10"]
    )

    y = targets

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42
    )

    model.fit(X, y)

    joblib.dump(
        model,
        MODEL_FILE
    )

    return {
        "status": "success",
        "rows": len(df),
        "model_file": MODEL_FILE
    }


if __name__ == "__main__":
    print(
        train_wnba_totals_model()
    )
