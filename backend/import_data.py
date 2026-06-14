from pathlib import Path

import pandas as pd

from database import db_cursor


ROOT_DIR = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT_DIR / "dataset" / "athlete_events.csv"


def import_medal_data():
    print("Loading dataset...")

    df = pd.read_csv(DATASET_PATH)

    # Keep only medal winners
    df = df[df["Medal"].notna()]

    # Required columns
    df = df[["Year", "Team", "Sport", "Event", "Medal"]]

    # Remove duplicates
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

        print("Creating table if not exists...")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS olympic_medals (
            id INT AUTO_INCREMENT PRIMARY KEY,
            year INT NOT NULL,
            country VARCHAR(150) NOT NULL,
            sport VARCHAR(150) NOT NULL,
            event_name VARCHAR(255) NOT NULL,
            medal ENUM('Gold','Silver','Bronze') NOT NULL,
            INDEX idx_country (country),
            INDEX idx_sport (sport),
            INDEX idx_year (year)
        )
        """)

        print("Clearing existing data...")
        cursor.execute("DELETE FROM olympic_medals")

        print("Importing records...")
        cursor.executemany(
            """
            INSERT INTO olympic_medals
            (year, country, sport, event_name, medal)
            VALUES (%s, %s, %s, %s, %s)
            """,
            data,
        )

    return len(data)


if __name__ == "__main__":
    try:
        total = import_medal_data()
        print(f"\n✅ Imported {total} records successfully!")
    except Exception as e:
        print("\n❌ Import failed:")
        print(e)