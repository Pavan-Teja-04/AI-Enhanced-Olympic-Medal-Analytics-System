from pathlib import Path

from flask import Flask, send_from_directory
from flask_cors import CORS

from backend.routes.ai import ai_bp
from backend.routes.analytics import analytics_bp
from backend.routes.auth import auth_bp
from backend.routes.medals import medals_bp


ROOT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT_DIR / "frontend"


def create_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(medals_bp, url_prefix="/api/medals")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")

    @app.get("/")
    def home():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.get("/api/status")
    def status():
        return {"status": "running", "api": "Olympic Medal Analytics"}

    @app.get("/<path:filename>")
    def frontend(filename):
        requested = FRONTEND_DIR / filename
        if requested.is_file():
            return send_from_directory(FRONTEND_DIR, filename)
        return send_from_directory(FRONTEND_DIR, "index.html")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False, threaded=False)
