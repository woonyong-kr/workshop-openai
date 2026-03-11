from app.services.gmail_service import GmailService


class DummyOAuthService:
    def ensure_valid_credentials(self, token_payload):  # pragma: no cover - not used here
        raise NotImplementedError


class DummyUserRepository:
    def get_token_payload(self, user):  # pragma: no cover - not used here
        raise NotImplementedError


def build_service():
    return GmailService(DummyOAuthService(), DummyUserRepository(), page_size=10)


def test_text_body_is_wrapped_into_paragraphs():
    service = build_service()
    body_html = service._text_to_html("line 1\nline 2\n\nline 3")

    assert "<p>line 1<br>line 2</p>" in body_html
    assert "<p>line 3</p>" in body_html


def test_html_is_sanitized():
    service = build_service()
    cleaned = service._sanitize_html("<script>alert(1)</script><p>Hello</p>")

    assert "script" not in cleaned
    assert "<p>Hello</p>" in cleaned
