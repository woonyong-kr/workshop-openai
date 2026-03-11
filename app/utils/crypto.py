import json
from datetime import datetime


def encrypt_payload(payload, fernet):
    if fernet is None:
        raise RuntimeError("TOKEN_ENCRYPTION_KEY is missing or invalid.")

    serialized = json.dumps(payload, default=_json_default).encode()
    return fernet.encrypt(serialized).decode()


def decrypt_payload(value, fernet):
    if not value or fernet is None:
        return {}

    decrypted = fernet.decrypt(value.encode())
    return json.loads(decrypted.decode())


def _json_default(value):
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"Unsupported type: {type(value)!r}")
