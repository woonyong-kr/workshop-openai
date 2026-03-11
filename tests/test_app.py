from app import create_app


class FakeOAuthService:
    def __init__(self):
        self.last_authorization_response = None

    def is_configured(self):
        return True

    def configuration_message(self):
        return ""

    def exchange_code(self, state, authorization_response):
        self.last_authorization_response = authorization_response
        return {
            "access_token": "access-token",
            "refresh_token": "refresh-token",
            "scopes": ["openid", "email", "profile"],
            "expiry": "2030-01-01T00:00:00+00:00",
        }

    def fetch_userinfo(self, access_token):
        return {
            "sub": "google-user-1",
            "email": "user@example.com",
            "name": "테스트 사용자",
            "picture": "",
        }


class FakeGmailService:
    def list_message_page(self, user, cursor=None):
        if cursor:
            return {
                "messages": [
                    {
                        "id": "msg-2",
                        "thread_id": "thread-2",
                        "subject": "두 번째 메일",
                        "snippet": "다음 페이지 메일입니다.",
                        "sender_name": "Google",
                        "sender_email": "workspace-noreply@google.com",
                        "sender_initial": "G",
                        "display_date": "3월 11일",
                        "full_date": "2026년 03월 11일 오전 10:30",
                        "labels": ["INBOX"],
                        "unread": False,
                        "has_attachments": False,
                    }
                ],
                "next_cursor": None,
            }

        return {
            "messages": [
                {
                    "id": "msg-1",
                    "thread_id": "thread-1",
                    "subject": "첫 번째 메일",
                    "snippet": "메일 미리보기입니다.",
                    "sender_name": "OpenAI",
                    "sender_email": "team@openai.com",
                    "sender_initial": "O",
                    "display_date": "오전 9:42",
                    "full_date": "2026년 03월 11일 오전 9:42",
                    "labels": ["INBOX", "UNREAD"],
                    "unread": True,
                    "has_attachments": True,
                }
            ],
            "next_cursor": "cursor-2",
        }

    def get_message_detail(self, user, message_id):
        return {
            "id": message_id,
            "thread_id": "thread-1",
            "subject": "첫 번째 메일",
            "snippet": "메일 미리보기입니다.",
            "sender_name": "OpenAI",
            "sender_email": "team@openai.com",
            "sender_initial": "O",
            "to": "user@example.com",
            "cc": "",
            "labels": ["INBOX", "UNREAD"],
            "full_date": "2026년 03월 11일 오전 9:42",
            "display_date": "오전 9:42",
            "body_html": "<p>안녕하세요.</p>",
            "attachments": [
                {
                    "part_id": "1",
                    "filename": "image.png",
                    "mime_type": "image/png",
                    "size": "24.0 KB",
                    "is_image": True,
                }
            ],
            "image_attachments": [
                {
                    "part_id": "1",
                    "filename": "image.png",
                    "mime_type": "image/png",
                    "size": "24.0 KB",
                    "is_image": True,
                }
            ],
            "file_attachments": [],
            "unread": True,
        }

    def download_attachment(self, user, message_id, part_id):
        return {
            "filename": "image.png",
            "mime_type": "image/png",
            "bytes": b"fake-image-bytes",
        }


def create_test_client():
    app = create_app(
        {
            "TESTING": True,
            "USE_MOCK_DB": True,
            "MONGO_URI": "mongodb://localhost:27017/testdb",
            "MONGO_DB_NAME": "testdb",
            "FLASK_SECRET_KEY": "test-secret",
            "SECRET_KEY": "test-secret",
            "TOKEN_ENCRYPTION_KEY": "2mZiMlo9W2Mvo1FnvnDw0Javxk28M6DkPF-P9o_6toU=",
            "GOOGLE_CLIENT_ID": "client-id",
            "GOOGLE_CLIENT_SECRET": "client-secret",
            "GOOGLE_REDIRECT_URI": "http://localhost/auth/google/callback",
        }
    )
    app.extensions["oauth_service"] = FakeOAuthService()
    app.extensions["gmail_service"] = FakeGmailService()
    return app.test_client()


def login(client):
    with client.session_transaction() as session:
        session["oauth_state"] = "test-state"

    client.get("/auth/google/callback?state=test-state&code=test-code")


def test_home_page_renders():
    client = create_test_client()
    response = client.get("/")

    assert response.status_code == 200
    assert "Gmail을 더 차분하고 정돈된 흐름으로 읽는 뷰어".encode() in response.data


def test_mailbox_requires_login():
    client = create_test_client()
    response = client.get("/mailbox")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_google_callback_creates_session_and_mailbox_feed():
    client = create_test_client()
    login(client)

    mailbox_response = client.get("/mailbox")
    feed_response = client.get("/mailbox/feed?cursor=cursor-2")

    assert mailbox_response.status_code == 200
    assert "첫 번째 메일".encode() in mailbox_response.data
    assert feed_response.status_code == 200
    assert feed_response.json["next_cursor"] is None


def test_google_callback_honors_https_from_reverse_proxy():
    client = create_test_client()
    oauth_service = client.application.extensions["oauth_service"]

    with client.session_transaction() as session:
        session["oauth_state"] = "test-state"

    response = client.get(
        "/auth/google/callback?state=test-state&code=test-code",
        headers={"X-Forwarded-Proto": "https", "X-Forwarded-Host": "mail.woonyong.org"},
    )

    assert response.status_code == 302
    assert (
        oauth_service.last_authorization_response
        == "http://localhost/auth/google/callback?state=test-state&code=test-code"
    )


def test_google_callback_uses_configured_redirect_uri_for_token_exchange():
    app = create_app(
        {
            "TESTING": True,
            "USE_MOCK_DB": True,
            "MONGO_URI": "mongodb://localhost:27017/testdb",
            "MONGO_DB_NAME": "testdb",
            "FLASK_SECRET_KEY": "test-secret",
            "SECRET_KEY": "test-secret",
            "TOKEN_ENCRYPTION_KEY": "2mZiMlo9W2Mvo1FnvnDw0Javxk28M6DkPF-P9o_6toU=",
            "GOOGLE_CLIENT_ID": "client-id",
            "GOOGLE_CLIENT_SECRET": "client-secret",
            "GOOGLE_REDIRECT_URI": "https://mail.woonyong.org/auth/google/callback",
        }
    )
    app.extensions["oauth_service"] = FakeOAuthService()
    app.extensions["gmail_service"] = FakeGmailService()
    client = app.test_client()

    with client.session_transaction() as session:
        session["oauth_state"] = "test-state"

    response = client.get("/auth/google/callback?state=test-state&code=test-code")

    assert response.status_code == 302
    assert (
        app.extensions["oauth_service"].last_authorization_response
        == "https://mail.woonyong.org/auth/google/callback?state=test-state&code=test-code"
    )


def test_mail_detail_renders_after_login():
    client = create_test_client()
    login(client)

    response = client.get("/mail/msg-1")

    assert response.status_code == 200
    assert "Message Body".encode() in response.data
    assert "image.png".encode() in response.data
