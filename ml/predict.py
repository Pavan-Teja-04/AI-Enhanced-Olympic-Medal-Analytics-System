from pathlib import Path

import joblib
import pandas as pd


MODEL_PATH = Path(__file__).resolve().parent / "random_forest_model.pkl"


def predict_medal(country, sport, year, athletes_count=1, previous_medals=0, participation_count=1):
    model = joblib.load(MODEL_PATH)
    row = pd.DataFrame(
        [
            {
                "country": country,
                "year": int(year),
                "sport": sport,
                "athletes_count": int(athletes_count),
                "previous_medals": int(previous_medals),
                "participation_count": int(participation_count),
            }
        ]
    )

    medal = model.predict(row)[0]
    probabilities = {}
    if hasattr(model, "predict_proba"):
        probabilities = {
            label: round(float(probability) * 100, 2)
            for label, probability in zip(model.classes_, model.predict_proba(row)[0])
        }

    return {"predicted_medal": medal, "probabilities": probabilities}


if __name__ == "__main__":
    print(predict_medal("China", "Judo", 2028, 4, 2, 3))
