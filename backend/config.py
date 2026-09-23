"""
TalentIQ configuration.

Handles the MySQL -> SQLite graceful fallback described in the implementation
plan: if MySQL environment variables are absent, or a MySQL connection cannot
be established at boot, the app transparently switches to a local SQLite
database file (talentiq.db) so the whole platform still runs with a single
command and zero external setup.
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _mysql_uri():
    host = os.getenv("MYSQL_HOST")
    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    database = os.getenv("MYSQL_DATABASE")
    port = os.getenv("MYSQL_PORT", "3306")
    if not all([host, user, database]):
        return None
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"


def _sqlite_uri():
    path = os.path.join(BASE_DIR, "talentiq.db")
    return f"sqlite:///{path}"


def resolve_database_uri():
    """
    Returns (uri, engine_name). Tries MySQL first if DB_ENGINE=mysql and
    credentials are present + reachable, otherwise falls back to SQLite.
    """
    engine_pref = os.getenv("DB_ENGINE", "mysql").lower()

    if engine_pref == "mysql":
        uri = _mysql_uri()
        if uri:
            try:
                import pymysql
                pymysql.install_as_MySQLdb()
                conn = pymysql.connect(
                    host=os.getenv("MYSQL_HOST"),
                    user=os.getenv("MYSQL_USER"),
                    password=os.getenv("MYSQL_PASSWORD") or "",
                    port=int(os.getenv("MYSQL_PORT", "3306")),
                    connect_timeout=2,
                )
                conn.close()
                return uri, "mysql"
            except Exception as exc:  # noqa: BLE001
                print(f"[TalentIQ] MySQL unreachable ({exc}); falling back to SQLite.")
        else:
            print("[TalentIQ] MySQL credentials incomplete; falling back to SQLite.")

    return _sqlite_uri(), "sqlite"


class Config:
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
    JWT_SECRET_KEY = SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MIN", "120"))
    )

    SQLALCHEMY_DATABASE_URI, DB_ENGINE_NAME = resolve_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = (
        {"pool_pre_ping": True} if DB_ENGINE_NAME == "mysql" else {}
    )

    UPLOAD_FOLDER = os.path.join(BASE_DIR, os.getenv("UPLOAD_FOLDER", "uploads/resumes"))
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_UPLOAD_MB", "10")) * 1024 * 1024

    MODEL_DIR = os.path.join(BASE_DIR, "ml", "saved_models")

    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
