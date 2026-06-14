from flask import Blueprint, request

from backend.database import fetch_all
medals_bp = Blueprint("medals", __name__)


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


@medals_bp.get("")
def medals():
    country = request.args.get("country", "").strip()
    sport = request.args.get("sport", "").strip()
    year = request.args.get("year", "").strip()

    try:
        limit = _int_arg("limit", 100, minimum=1, maximum=500)
        year_value = int(year) if year else 0
    except ValueError as exc:
        return {"error": str(exc)}, 400

    query = """
        SELECT
            MIN(id) AS id,
            year,
            country,
            sport,
            event_name,
            medal
        FROM olympic_medals
        WHERE (%s = '' OR country LIKE %s)
          AND (%s = '' OR sport LIKE %s)
          AND (%s = '' OR year = %s)
        GROUP BY year, country, sport, event_name, medal
        ORDER BY year DESC, country, sport
        LIMIT %s
    """
    like_country = f"%{country}%"
    like_sport = f"%{sport}%"

    return fetch_all(
        query,
        (country, like_country, sport, like_sport, year, year_value, limit),
    )


@medals_bp.get("/countries")
def countries():
    return fetch_all(
        """
        SELECT country, COUNT(*) AS medals
        FROM (
            SELECT country
            FROM olympic_medals
            GROUP BY year, country, sport, event_name, medal
        ) AS medal_events
        GROUP BY country
        ORDER BY medals DESC, country
        """
    )


@medals_bp.get("/sports")
def sports():
    return fetch_all(
        """
        SELECT sport, COUNT(*) AS medals
        FROM (
            SELECT sport
            FROM olympic_medals
            GROUP BY year, country, sport, event_name, medal
        ) AS medal_events
        GROUP BY sport
        ORDER BY medals DESC, sport
        """
    )
