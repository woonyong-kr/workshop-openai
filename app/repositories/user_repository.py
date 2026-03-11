from datetime import datetime, timezone

from bson import ObjectId
from pymongo import ReturnDocument

from ..utils.crypto import decrypt_payload, encrypt_payload


class UserRepository:
    DEFAULT_SETTINGS = {
        "mailbox_page_size": 20,
        "default_mail_view": "all",
        "review_threshold": 45,
        "quarantine_threshold": 80,
        "apply_hidden_rules": True,
        "allow_unsubscribe_actions": False,
        "confirm_unsubscribe_actions": True,
        "keep_unsubscribe_history": True,
        "show_html_preview": True,
        "allow_attachment_downloads": True,
        "sync_failure_alerts": True,
        "quarantine_alerts": True,
        "daily_summary_email": False,
    }

    def __init__(self, mongo_db, fernet):
        self.collection = mongo_db["users"]
        self.fernet = fernet
        self.can_store_tokens = fernet is not None

        self.collection.create_index("google_sub", unique=True)
        self.collection.create_index("email")

    def get_by_id(self, user_id):
        if not ObjectId.is_valid(user_id):
            return None

        user = self.collection.find_one({"_id": ObjectId(user_id)})
        return self._serialize(user)

    def get_by_google_sub(self, google_sub):
        user = self.collection.find_one({"google_sub": google_sub})
        return self._serialize(user)

    def get_token_payload(self, user):
        if user is None:
            return {}

        return decrypt_payload(user.get("token_encrypted"), self.fernet)

    def update_token_payload(self, user_id, token_payload):
        if not self.can_store_tokens:
            raise RuntimeError("Token encryption is not configured.")

        expiry = _parse_expiry(token_payload.get("expiry"))
        token_encrypted = encrypt_payload(token_payload, self.fernet)

        self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "token_encrypted": token_encrypted,
                    "token_scopes": token_payload.get("scopes", []),
                    "token_expiry": expiry,
                    "updated_at": _utcnow(),
                }
            },
        )

    def upsert_google_user(self, profile, token_payload):
        if not self.can_store_tokens:
            raise RuntimeError("Token encryption is not configured.")

        now = _utcnow()
        token_encrypted = encrypt_payload(token_payload, self.fernet)
        expiry = _parse_expiry(token_payload.get("expiry"))

        user = self.collection.find_one_and_update(
            {"google_sub": profile["sub"]},
            {
                "$set": {
                    "google_sub": profile["sub"],
                    "email": profile.get("email"),
                    "name": profile.get("name") or profile.get("email", "Google User"),
                    "picture": profile.get("picture"),
                    "token_encrypted": token_encrypted,
                    "token_scopes": token_payload.get("scopes", []),
                    "token_expiry": expiry,
                    "updated_at": now,
                    "last_login_at": now,
                },
                "$setOnInsert": {"created_at": now},
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

        return self._serialize(user)

    def get_hidden_keywords(self, user):
        if user is None:
            return []

        keywords = user.get("hidden_keywords", [])
        return [keyword for keyword in keywords if isinstance(keyword, str) and keyword.strip()]

    def add_hidden_keyword(self, user_id, keyword):
        keyword = (keyword or "").strip()
        if not keyword:
            raise ValueError("키워드를 입력해주세요.")

        user = self.collection.find_one({"_id": ObjectId(user_id)})
        if user is None:
            raise ValueError("사용자를 찾을 수 없습니다.")

        keywords = [
            item for item in user.get("hidden_keywords", []) if isinstance(item, str) and item.strip()
        ]
        if any(item.lower() == keyword.lower() for item in keywords):
            return keywords

        keywords.append(keyword)
        self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"hidden_keywords": keywords, "updated_at": _utcnow()}},
        )
        return keywords

    def remove_hidden_keyword(self, user_id, keyword):
        keyword = (keyword or "").strip()
        if not keyword:
            return []

        user = self.collection.find_one({"_id": ObjectId(user_id)})
        if user is None:
            return []

        keywords = [
            item
            for item in user.get("hidden_keywords", [])
            if isinstance(item, str) and item.strip() and item.lower() != keyword.lower()
        ]
        self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"hidden_keywords": keywords, "updated_at": _utcnow()}},
        )
        return keywords

    def get_settings(self, user):
        raw_settings = {}
        if user is not None:
            raw_settings = user.get("settings", {}) or {}
        return self._normalize_settings(raw_settings)

    def update_settings(self, user_id, settings):
        normalized = self._normalize_settings(settings)
        self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"settings": normalized, "updated_at": _utcnow()}},
        )
        user = self.collection.find_one({"_id": ObjectId(user_id)})
        return self._serialize(user)

    def _serialize(self, user):
        if user is None:
            return None

        data = dict(user)
        data["id"] = str(data.pop("_id"))
        return data

    def _normalize_settings(self, settings):
        merged = dict(self.DEFAULT_SETTINGS)
        if isinstance(settings, dict):
            merged.update(settings)

        mailbox_page_size = _coerce_int(
            merged.get("mailbox_page_size"),
            default=self.DEFAULT_SETTINGS["mailbox_page_size"],
            minimum=10,
            maximum=100,
        )
        review_threshold = _coerce_int(
            merged.get("review_threshold"),
            default=self.DEFAULT_SETTINGS["review_threshold"],
            minimum=10,
            maximum=95,
        )
        quarantine_threshold = _coerce_int(
            merged.get("quarantine_threshold"),
            default=self.DEFAULT_SETTINGS["quarantine_threshold"],
            minimum=review_threshold + 1,
            maximum=99,
        )
        default_view = merged.get("default_mail_view", self.DEFAULT_SETTINGS["default_mail_view"])
        if default_view not in {"all", "safe", "review", "quarantine"}:
            default_view = self.DEFAULT_SETTINGS["default_mail_view"]

        return {
            "mailbox_page_size": mailbox_page_size,
            "default_mail_view": default_view,
            "review_threshold": review_threshold,
            "quarantine_threshold": quarantine_threshold,
            "apply_hidden_rules": bool(merged.get("apply_hidden_rules")),
            "allow_unsubscribe_actions": bool(merged.get("allow_unsubscribe_actions")),
            "confirm_unsubscribe_actions": bool(merged.get("confirm_unsubscribe_actions")),
            "keep_unsubscribe_history": bool(merged.get("keep_unsubscribe_history")),
            "show_html_preview": bool(merged.get("show_html_preview")),
            "allow_attachment_downloads": bool(merged.get("allow_attachment_downloads")),
            "sync_failure_alerts": bool(merged.get("sync_failure_alerts")),
            "quarantine_alerts": bool(merged.get("quarantine_alerts")),
            "daily_summary_email": bool(merged.get("daily_summary_email")),
        }


def _utcnow():
    return datetime.now(timezone.utc)


def _parse_expiry(expiry_value):
    if not expiry_value:
        return None

    parsed = datetime.fromisoformat(expiry_value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _coerce_int(value, default, minimum, maximum):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default

    return max(minimum, min(maximum, parsed))
