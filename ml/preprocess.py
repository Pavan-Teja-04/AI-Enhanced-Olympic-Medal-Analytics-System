from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT_DIR / "dataset" / "athlete_events.csv"
OUTPUT_PATH = Path(__file__).resolve().parent / "olympic_medals.csv"


def build_training_dataset():
    df = pd.read_csv(DATASET_PATH)
    df["Medal"] = df["Medal"].fillna("No Medal")

    grouped = (
        df.groupby(["Team", "Year", "Sport"], as_index=False)
        .agg(
            athletes_count=("ID", "nunique"),
            participation_count=("Event", "nunique"),
            medal=("Medal", lambda values: _best_medal(values)),
        )
    )

    grouped = grouped.sort_values(["Team", "Sport", "Year"])
    grouped["previous_medals"] = (
        grouped.assign(won_medal=grouped["medal"].ne("No Medal").astype(int))
        .groupby(["Team", "Sport"])["won_medal"]
        .cumsum()
        .sub(grouped["medal"].ne("No Medal").astype(int))
    )

    grouped = grouped.rename(columns={"Team": "country", "Sport": "sport", "Year": "year"})
    grouped = grouped[
        [
            "country",
            "year",
            "sport",
            "athletes_count",
            "previous_medals",
            "participation_count",
            "medal",
        ]
    ]
    grouped.to_csv(OUTPUT_PATH, index=False)
    return grouped


def _best_medal(values):
    priority = {"Gold": 1, "Silver": 2, "Bronze": 3, "No Medal": 4}
    return min(values, key=lambda medal: priority.get(medal, 4))


if __name__ == "__main__":
    result = build_training_dataset()
    print(f"Saved {len(result)} rows to {OUTPUT_PATH}")
