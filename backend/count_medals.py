from pathlib import Path

import pandas as pd


DATASET_PATH = Path(__file__).resolve().parents[1] / "dataset" / "athlete_events.csv"


if __name__ == "__main__":
    df = pd.read_csv(DATASET_PATH)
    print("Medal Records:", df["Medal"].notna().sum())
