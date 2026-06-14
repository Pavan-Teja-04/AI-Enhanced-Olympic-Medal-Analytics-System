from pathlib import Path

import joblib
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT_DIR / "ml" / "models"

model = joblib.load(MODELS_DIR / "model.pkl")
country_encoder = joblib.load(MODELS_DIR / "country_encoder.pkl")
sport_encoder = joblib.load(MODELS_DIR / "sport_encoder.pkl")
medal_encoder = joblib.load(MODELS_DIR / "medal_encoder.pkl")


def normalize_text(value):
    if not value:
        return ""

    value = str(value).strip()

    # Convert:
    # india -> India
    # INDIA -> India
    # badminton -> Badminton
    return value.title()


def _encode_value(encoder, value, label):

    value = normalize_text(value)

    # Case-insensitive lookup
    classes_map = {
        str(item).lower(): item
        for item in encoder.classes_
    }

    if value.lower() not in classes_map:

        examples = ", ".join(
            map(str, encoder.classes_[:8])
        )

        raise ValueError(
            f"Unknown {label}: {value}. "
            f"Try one of these examples: {examples}"
        )

    actual_value = classes_map[value.lower()]

    return encoder.transform(
        [actual_value]
    )[0]


def predict_medal(
    country,
    sport,
    year,
    athletes_count=1
):

    country = normalize_text(country)
    sport = normalize_text(sport)

    country_encoded = _encode_value(
        country_encoder,
        country,
        "country"
    )

    sport_encoded = _encode_value(
        sport_encoder,
        sport,
        "sport"
    )

    input_data = pd.DataFrame(
        [[country_encoded, sport_encoded, year]],
        columns=[
            "Team",
            "Sport",
            "Year"
        ],
    )

    prediction = model.predict(
        input_data
    )

    medal = medal_encoder.inverse_transform(
        prediction
    )[0]

    probabilities = {}

    if hasattr(model, "predict_proba"):

        probability_values = model.predict_proba(
            input_data
        )[0]

        labels = medal_encoder.inverse_transform(
            model.classes_
        )

        probabilities = {
            str(label): round(
                float(probability) * 100,
                2
            )
            for label, probability
            in zip(labels, probability_values)
        }

    return {
        "country": country,
        "sport": sport,
        "year": year,
        "athletes_count": athletes_count,
        "predicted_medal": medal,
        "probability_percent": probabilities.get(
            medal,
            0
        ),
        "probabilities": probabilities,
        "model_note": (
            "Current saved model predicts medal category "
            "among historical medal winners."
        ),
    }