from pathlib import Path

import pandas as pd

from database import db_cursor


ROOT_DIR = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT_DIR / "dataset" / "athlete_events.csv"


def import_medal_data():
    df = pd.read_csv(DATASET_PATH)
    df = df[df["Medal"].notna()]
    df = df[["Year", "Team", "Sport", "Event", "Medal"]]
    df = df.drop_duplicates()

    data = [
        (
            int(row["Year"]),
            str(row["Team"]),
            str(row["Sport"]),
            str(row["Event"]),
            str(row["Medal"]),
        )
        for _, row in df.iterrows()
    ]

    with db_cursor(dictionary=False) as cursor:
        cursor.execute("TRUNCATE TABLE olympic_medals")
        cursor.executemany(
            """
            INSERT INTO olympic_medals (year, country, sport, event_name, medal)
            VALUES (%s, %s, %s, %s, %s)
            """,
            data,
        )

    return len(data)


if __name__ == "__main__":
    print("Imported:", import_medal_data(), "records")
