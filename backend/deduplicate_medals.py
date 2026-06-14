from database import db_cursor, fetch_one


def deduplicate_medals():
    before = fetch_one("SELECT COUNT(*) AS count FROM olympic_medals")["count"]

    with db_cursor(dictionary=False) as cursor:
        cursor.execute("DROP TABLE IF EXISTS olympic_medals_dedup")
        cursor.execute(
            """
            CREATE TABLE olympic_medals_dedup (
                id INT AUTO_INCREMENT PRIMARY KEY,
                year INT NOT NULL,
                country VARCHAR(150) NOT NULL,
                sport VARCHAR(150) NOT NULL,
                event_name VARCHAR(255) NOT NULL,
                medal ENUM('Gold', 'Silver', 'Bronze') NOT NULL,
                INDEX idx_country (country),
                INDEX idx_sport (sport),
                INDEX idx_year (year),
                UNIQUE KEY unique_medal_event
                    (year, country, sport, event_name, medal)
            )
            """
        )
        cursor.execute(
            """
            INSERT INTO olympic_medals_dedup
                (year, country, sport, event_name, medal)
            SELECT DISTINCT year, country, sport, event_name, medal
            FROM olympic_medals
            """
        )
        cursor.execute("DROP TABLE IF EXISTS olympic_medals_with_duplicates")
        cursor.execute(
            """
            RENAME TABLE
                olympic_medals TO olympic_medals_with_duplicates,
                olympic_medals_dedup TO olympic_medals
            """
        )
        cursor.execute("DROP TABLE olympic_medals_with_duplicates")

        try:
            cursor.execute(
                """
                ALTER TABLE olympic_medals
                ADD UNIQUE KEY unique_medal_event
                    (year, country, sport, event_name, medal)
                """
            )
        except Exception as exc:
            if "Duplicate key name" not in str(exc):
                raise

    after = fetch_one("SELECT COUNT(*) AS count FROM olympic_medals")["count"]
    return before, after


if __name__ == "__main__":
    before_count, after_count = deduplicate_medals()
    print(f"Rows before: {before_count}")
    print(f"Rows after: {after_count}")
    print(f"Removed duplicates: {before_count - after_count}")
