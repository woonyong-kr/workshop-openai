from cryptography.fernet import Fernet
from flask import current_app
from pymongo import MongoClient
from pymongo.errors import ConfigurationError

from .repositories.user_repository import UserRepository
from .services.gmail_service import GmailService
from .services.google_oauth import GoogleOAuthService
from .services.visibility_service import VisibilityService

try:
    import mongomock
except ImportError:  # pragma: no cover - installed for tests only
    mongomock = None


def init_extensions(app):
    mongo_client = _build_mongo_client(app)

    try:
        mongo_db = mongo_client.get_default_database()
    except ConfigurationError:
        mongo_db = mongo_client[app.config["MONGO_DB_NAME"]]

    fernet = _build_fernet(app.config.get("TOKEN_ENCRYPTION_KEY"))
    user_repository = UserRepository(mongo_db, fernet)
    oauth_service = GoogleOAuthService(app.config)
    gmail_service = GmailService(
        oauth_service=oauth_service,
        user_repository=user_repository,
        page_size=app.config["MAILBOX_PAGE_SIZE"],
    )
    visibility_service = VisibilityService()

    app.extensions["mongo_client"] = mongo_client
    app.extensions["mongo_db"] = mongo_db
    app.extensions["fernet"] = fernet
    app.extensions["user_repository"] = user_repository
    app.extensions["oauth_service"] = oauth_service
    app.extensions["gmail_service"] = gmail_service
    app.extensions["visibility_service"] = visibility_service


def _build_mongo_client(app):
    client_factory = MongoClient

    if app.config.get("USE_MOCK_DB"):
        if mongomock is None:
            raise RuntimeError("mongomock is required when USE_MOCK_DB is enabled.")
        client_factory = mongomock.MongoClient

    return client_factory(app.config["MONGO_URI"])


def _build_fernet(token_encryption_key):
    if not token_encryption_key:
        return None

    try:
        return Fernet(token_encryption_key.encode())
    except (TypeError, ValueError):
        return None


def get_mongo_client():
    return current_app.extensions["mongo_client"]


def get_mongo_db():
    return current_app.extensions["mongo_db"]


def get_user_repository():
    return current_app.extensions["user_repository"]


def get_oauth_service():
    return current_app.extensions["oauth_service"]


def get_gmail_service():
    return current_app.extensions["gmail_service"]


def get_visibility_service():
    return current_app.extensions["visibility_service"]
