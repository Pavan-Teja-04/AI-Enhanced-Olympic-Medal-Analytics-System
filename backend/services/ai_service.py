import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


def _fallback_summary(stats):
    total = stats.get("total", 0)
    gold = stats.get("gold", 0)
    silver = stats.get("silver", 0)
    bronze = stats.get("bronze", 0)

    country = stats.get("country", "This country")
    first_year = stats.get("first_year", "early Olympic history")
    latest_year = stats.get("latest_year", "recent Olympic history")

    return (
        f"{country} has recorded {total} Olympic medals, "
        f"including {gold} Gold, {silver} Silver, and {bronze} Bronze medals. "
        f"The country's Olympic history spans from {first_year} to {latest_year}. "
        f"This demonstrates consistent participation and competitive performance "
        f"across multiple Olympic cycles."
    )


def generate_olympic_insight(stats):

    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key:
        return _fallback_summary(stats)

    prompt = f"""
You are an Olympic sports analyst.

Country: {stats.get('country')}
Gold Medals: {stats.get('gold')}
Silver Medals: {stats.get('silver')}
Bronze Medals: {stats.get('bronze')}
Total Medals: {stats.get('total')}
First Olympic Medal Year: {stats.get('first_year')}
Latest Olympic Medal Year: {stats.get('latest_year')}

Generate:

1. Performance Summary
2. Historical Trend Analysis
3. Strength Assessment
4. Future Outlook

Keep the response under 200 words.
"""

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)

        model = genai.GenerativeModel(
            os.getenv(
                "GEMINI_MODEL",
                "gemini-2.0-flash"
            )
        )

        response = model.generate_content(prompt)

        if response and hasattr(response, "text"):
            return response.text.strip()

        return _fallback_summary(stats)

    except Exception as exc:
        print("Gemini Error:", str(exc))
        return _fallback_summary(stats)
