from flask import Blueprint, request

from database import fetch_all
from predict import predict_medal

analytics_bp = Blueprint("analytics", __name__)


def _int_arg(name, default, minimum=None, maximum=None):
    raw_value = request.args.get(name, default)
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be a number")

    if minimum is not None:
        value = max(value, minimum)
    if maximum is not None:
        value = min(value, maximum)
    return value


@analytics_bp.get("/overview")
def overview():
    totals = fetch_all(
        """
        SELECT
            COUNT(*) AS total_medals,
            COUNT(DISTINCT country) AS total_countries,
            COUNT(DISTINCT sport) AS total_sports,
            MIN(year) AS first_year,
            MAX(year) AS latest_year
        FROM (
            SELECT year, country, sport, event_name, medal
            FROM olympic_medals
            GROUP BY year, country, sport, event_name, medal
        ) AS medal_events
        """
    )[0]
    return totals


@analytics_bp.get("/top-countries")
def top_countries():
    try:
        limit = _int_arg("limit", 10, minimum=1, maximum=50)
    except ValueError as exc:
        return {"error": str(exc)}, 400

    return fetch_all(
        """
        SELECT country, COUNT(*) AS medals
        FROM (
            SELECT year, country, sport, event_name, medal
            FROM olympic_medals
            GROUP BY year, country, sport, event_name, medal
        ) AS medal_events
        GROUP BY country
        ORDER BY medals DESC
        LIMIT %s
        """,
        (limit,),
    )


@analytics_bp.get("/sport-distribution")
def sport_distribution():
    try:
        limit = _int_arg("limit", 10, minimum=1, maximum=50)
    except ValueError as exc:
        return {"error": str(exc)}, 400

    return fetch_all(
        """
        SELECT sport, COUNT(*) AS medals
        FROM (
            SELECT year, country, sport, event_name, medal
            FROM olympic_medals
            GROUP BY year, country, sport, event_name, medal
        ) AS medal_events
        GROUP BY sport
        ORDER BY medals DESC
        LIMIT %s
        """,
        (limit,),
    )


@analytics_bp.get("/medal-trends")
def medal_trends():
    country = request.args.get("country", "").strip()
    sport = request.args.get("sport", "").strip()
    return fetch_all(
        """
        SELECT year, COUNT(*) AS medals
        FROM (
            SELECT year, country, sport, event_name, medal
            FROM olympic_medals
            GROUP BY year, country, sport, event_name, medal
        ) AS medal_events
        WHERE (%s = '' OR country LIKE %s)
          AND (%s = '' OR sport LIKE %s)
        GROUP BY year
        ORDER BY year
        """,
        (country, f"%{country}%", sport, f"%{sport}%"),
    )


@analytics_bp.get("/medal-breakdown")
def medal_breakdown():
    country = request.args.get("country", "").strip()
    return fetch_all(
        """
        SELECT medal, COUNT(*) AS count
        FROM (
            SELECT year, country, sport, event_name, medal
            FROM olympic_medals
            GROUP BY year, country, sport, event_name, medal
        ) AS medal_events
        WHERE (%s = '' OR country LIKE %s)
        GROUP BY medal
        ORDER BY FIELD(medal, 'Gold', 'Silver', 'Bronze')
        """,
        (country, f"%{country}%"),
    )


@analytics_bp.post("/predict")
def predict():
    data = request.get_json(silent=True) or {}
    required = ["country", "sport", "year"]
    missing = [field for field in required if not data.get(field)]
    if missing:
        return {"error": f"Missing required fields: {', '.join(missing)}"}, 400

    try:
        result = predict_medal(
            country=data["country"],
            sport=data["sport"],
            year=int(data["year"]),
            athletes_count=int(data.get("athletes_count", 1)),
        )
    except ValueError as exc:
        return {"error": str(exc)}, 400

    return result
