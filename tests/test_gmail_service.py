from app.services.gmail_service import GmailService


class DummyOAuthService:
    def ensure_valid_credentials(self, token_payload):  # pragma: no cover - not used here
        raise NotImplementedError


class DummyUserRepository:
    def get_token_payload(self, user):  # pragma: no cover - not used here
        raise NotImplementedError


def build_service():
    return GmailService(DummyOAuthService(), DummyUserRepository(), page_size=10)


class FakeRequest:
    def __init__(self, payload, on_execute=None):
        self.payload = payload
        self.on_execute = on_execute

    def execute(self):
        if self.on_execute:
            self.on_execute()
        return self.payload


class FakeBatchRequest:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.items = []

    def add(self, request, request_id=None, callback=None):
        self.items.append((request, request_id, callback))

    def execute(self):
        if self.should_fail:
            raise RuntimeError("batch failed")

        for request, request_id, callback in self.items:
            callback(request_id, request.execute(), None)


class FakeMessagesApi:
    def __init__(self, should_fail_batch=False):
        self.should_fail_batch = should_fail_batch
        self.get_calls = []

    def list(self, **kwargs):
        return FakeRequest(
            {
                "messages": [{"id": "msg-1"}, {"id": "msg-2"}],
                "nextPageToken": "next-cursor",
            }
        )

    def get(self, **kwargs):
        message_id = kwargs["id"]
        return FakeRequest(
            {
                "id": message_id,
                "threadId": f"thread-{message_id}",
                "payload": {"headers": []},
                "labelIds": [],
                "snippet": f"snippet-{message_id}",
                "internalDate": "0",
            },
            on_execute=lambda: self.get_calls.append(message_id),
        )


class FakeUsersApi:
    def __init__(self, messages_api):
        self._messages_api = messages_api

    def messages(self):
        return self._messages_api


class FakeGmailApi:
    def __init__(self, should_fail_batch=False):
        self.messages_api = FakeMessagesApi(should_fail_batch=should_fail_batch)
        self.batch = FakeBatchRequest(should_fail=should_fail_batch)

    def users(self):
        return FakeUsersApi(self.messages_api)

    def new_batch_http_request(self):
        return self.batch


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


def test_list_message_page_uses_batch_fetch_and_keeps_order():
    service = build_service()
    fake_api = FakeGmailApi()
    service._build_service_for_user = lambda user: fake_api
    service._build_message_summary = lambda message: {"id": message["id"]}

    page = service.list_message_page({"id": "user-1"})

    assert page["messages"] == [{"id": "msg-1"}, {"id": "msg-2"}]
    assert page["next_cursor"] == "next-cursor"
    assert fake_api.messages_api.get_calls == ["msg-1", "msg-2"]


def test_list_message_page_falls_back_to_sequential_when_batch_fails():
    service = build_service()
    fake_api = FakeGmailApi(should_fail_batch=True)
    service._build_service_for_user = lambda user: fake_api
    service._build_message_summary = lambda message: {"id": message["id"]}

    page = service.list_message_page({"id": "user-1"})

    assert page["messages"] == [{"id": "msg-1"}, {"id": "msg-2"}]
    assert page["next_cursor"] == "next-cursor"
    assert fake_api.messages_api.get_calls == ["msg-1", "msg-2"]
