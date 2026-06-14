from flask import Blueprint, request
from werkzeug.security import check_password_hash, generate_password_hash

from backend.database import execute, fetch_one

auth_bp = Blueprint("auth", __name__)


def ensure_users_table():
    execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(120) NOT NULL,
            email VARCHAR(180) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


def _required_json(*fields):
    data = request.get_json(silent=True) or {}
    missing = [field for field in fields if not data.get(field)]
    if missing:
        return data, {"error": f"Missing required fields: {', '.join(missing)}"}
    return data, None


@auth_bp.post("/register")
def register():
    ensure_users_table()
    data, error = _required_json("name", "email", "password")
    if error:
        return error, 400

    existing = fetch_one("SELECT id FROM users WHERE email=%s", (data["email"],))
    if existing:
        return {"error": "Email is already registered"}, 409

    user_id = execute(
        """
        INSERT INTO users (name, email, password_hash)
        VALUES (%s, %s, %s)
        """,
        (
            data["name"],
            data["email"].lower(),
            generate_password_hash(data["password"]),
        ),
    )

    return {
        "message": "Registration successful",
        "user": {"id": user_id, "name": data["name"], "email": data["email"].lower()},
    }, 201


@auth_bp.post("/login")
def login():
    ensure_users_table()
    data, error = _required_json("email", "password")
    if error:
        return error, 400

    user = fetch_one(
        "SELECT id, name, email, password_hash FROM users WHERE email=%s",
        (data["email"].lower(),),
    )

    if not user or not check_password_hash(user["password_hash"], data["password"]):
        return {"error": "Invalid email or password"}, 401

    return {
        "message": "Login successful",
        "user": {"id": user["id"], "name": user["name"], "email": user["email"]},
    }
