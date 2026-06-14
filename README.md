# AI-Enhanced Olympic Medal Analytics System

Full-stack Olympic analytics project with Flask, MySQL, Chart.js, Random Forest prediction, and optional Gemini-generated insights.

## Features

- User registration and login
- Olympic medal dashboard
- Country-wise medal standings
- Sport-wise medal statistics
- Historical year-wise trends
- Search and filter by country, sport, and year
- Random Forest medal prediction with probability output
- AI-generated country performance summaries
- Dark and light theme
- Printable PDF-style reports using the browser print dialog

## Project Structure

```text
Olympic-Medal-Analytics/
+-- backend/
|   +-- app.py
|   +-- database.py
|   +-- routes/
|   +-- services/
|   +-- predict.py
+-- dataset/
|   +-- athlete_events.csv
|   +-- noc_regions.csv
+-- frontend/
|   +-- index.html
|   +-- login.html
|   +-- dashboard.html
|   +-- standings.html
|   +-- analytics.html
|   +-- prediction.html
|   +-- ai-insights.html
|   +-- css/
|   +-- js/
+-- ml/
|   +-- preprocess.py
|   +-- train_model.py
|   +-- predict.py
|   +-- models/
+-- documentation/
|   +-- schema.sql
+-- requirements.txt
+-- README.md
```

## Setup

1. Create and activate a virtual environment.

```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Create the MySQL database and tables.

```bash
mysql -u root -p < documentation/schema.sql
```

4. Copy `.env.example` to `.env` and update database credentials if needed.

5. Import Olympic medal data.

```bash
python backend/import_data.py
```

6. Start the Flask API.

```bash
python backend/app.py
```

7. Open `frontend/index.html` in the browser.

## Machine Learning

The current backend uses the saved model files in `ml/models/` so the prediction page works immediately.

To train the enhanced model with `Gold`, `Silver`, `Bronze`, and `No Medal`:

```bash
python ml/preprocess.py
python ml/train_model.py
```

Enhanced model features:

- `country`
- `year`
- `sport`
- `athletes_count`
- `previous_medals`
- `participation_count`

## Generative AI

The AI module uses Gemini when `GEMINI_API_KEY` is configured. Without a key, the app returns a deterministic fallback summary, so the demo still works.

```text
GEMINI_API_KEY=your_api_key_here
```

## API Routes

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/medals`
- `GET /api/medals/countries`
- `GET /api/medals/sports`
- `GET /api/analytics/overview`
- `GET /api/analytics/top-countries`
- `GET /api/analytics/sport-distribution`
- `GET /api/analytics/medal-trends`
- `POST /api/analytics/predict`
- `GET /api/ai/country-summary`
- `GET /api/ai/trend-report`

## Evaluation Notes

This stack is intentionally practical for internship evaluation: HTML, CSS, JavaScript, Chart.js, Flask, MySQL, Scikit-learn, and optional Gemini API.
