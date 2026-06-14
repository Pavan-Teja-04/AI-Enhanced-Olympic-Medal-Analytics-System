import os
from contextlib import contextmanager

import mysql.connector

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "connection_timeout": int(os.getenv("DB_CONNECTION_TIMEOUT", "10")),
}


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


@contextmanager
def db_cursor(dictionary=True):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=dictionary)
    try:
        yield cursor
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def fetch_all(query, params=None):
    with db_cursor(dictionary=True) as cursor:
        cursor.execute(query, params or ())
        return cursor.fetchall()


def fetch_one(query, params=None):
    with db_cursor(dictionary=True) as cursor:
        cursor.execute(query, params or ())
        return cursor.fetchone()


def execute(query, params=None):
    with db_cursor(dictionary=True) as cursor:
        cursor.execute(query, params or ())
        return cursor.lastrowid
