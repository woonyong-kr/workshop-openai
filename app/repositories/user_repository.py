from datetime import datetime, timezone

from bson import ObjectId
from pymongo import ReturnDocument

from ..utils.crypto import decrypt_payload, encrypt_payload


class UserRepository:
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

    def _serialize(self, user):
        if user is None:
            return None

        data = dict(user)
        data["id"] = str(data.pop("_id"))
        return data


def _utcnow():
    return datetime.now(timezone.utc)


def _parse_expiry(expiry_value):
    if not expiry_value:
        return None

    parsed = datetime.fromisoformat(expiry_value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
