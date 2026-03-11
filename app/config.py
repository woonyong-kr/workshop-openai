import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env.public")
load_dotenv(BASE_DIR / ".env.secret", override=True)


class Config:
    APP_NAME = os.getenv("APP_NAME", "Mail Flow")
    APP_TAGLINE = os.getenv(
        "APP_TAGLINE",
        "Google 메일을 더 선명한 흐름으로 보여주는 개인 메일 워크스페이스",
    )
    APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:5001")

    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-only-change-me")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    PORT = int(os.getenv("PORT", "5001"))

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    PERMANENT_SESSION_LIFETIME = timedelta(
        days=int(os.getenv("SESSION_LIFETIME_DAYS", "14"))
    )

    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/gmail_viewer")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "gmail_viewer")
    USE_MOCK_DB = os.getenv("USE_MOCK_DB", "false").lower() == "true"

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI = os.getenv(
        "GOOGLE_REDIRECT_URI",
        f"{APP_BASE_URL.rstrip('/')}/auth/google/callback",
    )
    GOOGLE_SCOPES = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/gmail.modify",
    ]
    TOKEN_ENCRYPTION_KEY = os.getenv("TOKEN_ENCRYPTION_KEY", "")

    MAILBOX_PAGE_SIZE = int(os.getenv("MAILBOX_PAGE_SIZE", "20"))
