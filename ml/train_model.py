from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "olympic_medals.csv"
MODEL_PATH = BASE_DIR / "random_forest_model.pkl"


def train():
    if not DATA_PATH.exists():
        raise FileNotFoundError("Run `python ml/preprocess.py` before training.")

    df = pd.read_csv(DATA_PATH)
    features = [
        "country",
        "year",
        "sport",
        "athletes_count",
        "previous_medals",
        "participation_count",
    ]
    target = "medal"

    X = df[features]
    y = df[target]

    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical", OneHotEncoder(handle_unknown="ignore"), ["country", "sport"]),
            (
                "numeric",
                "passthrough",
                ["year", "athletes_count", "previous_medals", "participation_count"],
            ),
        ]
    )

    model = RandomForestClassifier(n_estimators=200, random_state=42)
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)

    print(f"Accuracy: {accuracy_score(y_test, predictions):.4f}")
    print(classification_report(y_test, predictions))

    joblib.dump(pipeline, MODEL_PATH)
    print(f"Saved model to {MODEL_PATH}")


if __name__ == "__main__":
    train()
