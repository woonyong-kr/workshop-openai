from datetime import datetime, timezone

from app.services.google_oauth import timezone_fix


def test_timezone_fix_converts_aware_expiry_to_naive_utc():
    value = "2030-01-01T09:00:00+09:00"

    normalized = timezone_fix(value)

    assert normalized == datetime(2030, 1, 1, 0, 0)
    assert normalized.tzinfo is None


def test_timezone_fix_keeps_naive_expiry_naive():
    value = datetime(2030, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

    normalized = timezone_fix(value)

    assert normalized == datetime(2030, 1, 1, 0, 0)
    assert normalized.tzinfo is None
