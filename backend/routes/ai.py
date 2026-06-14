from flask import Blueprint, request

from database import fetch_all
from services.ai_service import generate_olympic_insight

ai_bp = Blueprint("ai", __name__)


@ai_bp.get("/country-summary")
def country_summary():
    country = request.args.get("country", "").strip()
    if not country:
        return {"error": "country query parameter is required"}, 400

    rows = fetch_all(
        """
        SELECT
            country,
            SUM(medal = 'Gold') AS gold,
            SUM(medal = 'Silver') AS silver,
            SUM(medal = 'Bronze') AS bronze,
            COUNT(*) AS total,
            MIN(year) AS first_year,
            MAX(year) AS latest_year
        FROM (
            SELECT year, country, sport, event_name, medal
            FROM olympic_medals
            GROUP BY year, country, sport, event_name, medal
        ) AS medal_events
        WHERE country LIKE %s
        GROUP BY country
        ORDER BY total DESC
        LIMIT 1
        """,
        (f"%{country}%",),
    )
    if not rows:
        return {"error": "No medal records found for that country"}, 404

    return {"country": rows[0], "insight": generate_olympic_insight(rows[0])}


@ai_bp.get("/trend-report")
def trend_report():
    country = request.args.get("country", "").strip()
    rows = fetch_all(
        """
        SELECT year, COUNT(*) AS medals
        FROM (
            SELECT year, country, sport, event_name, medal
            FROM olympic_medals
            GROUP BY year, country, sport, event_name, medal
        ) AS medal_events
        WHERE (%s = '' OR country LIKE %s)
        GROUP BY year
        ORDER BY year
        """,
        (country, f"%{country}%"),
    )
    if not rows:
        return {"error": "No trend records found"}, 404

    best_year = max(rows, key=lambda item: item["medals"])
    subject = country or "All countries"
    return {
        "subject": subject,
        "best_year": best_year,
        "insight": (
            f"{subject} shows its strongest medal count in {best_year['year']} "
            f"with {best_year['medals']} medals. The year-wise trend chart can be "
            "used to compare growth, dips, and repeat performance cycles."
        ),
    }
