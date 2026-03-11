import os
from datetime import datetime, timezone

import requests

# Google이 콜백 시 요청보다 많은 스코프를 반환해도 예외 발생 방지
# (include_granted_scopes로 인해 이전에 허용된 스코프가 추가될 수 있음)
os.environ.setdefault("OAUTHLIB_RELAX_TOKEN_SCOPE", "1")
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow


class GoogleOAuthService:
    AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
    TOKEN_URI = "https://oauth2.googleapis.com/token"
    CERTS_URI = "https://www.googleapis.com/oauth2/v1/certs"
    USERINFO_URI = "https://openidconnect.googleapis.com/v1/userinfo"

    def __init__(self, config):
        self.client_id = config.get("GOOGLE_CLIENT_ID", "")
        self.client_secret = config.get("GOOGLE_CLIENT_SECRET", "")
        self.redirect_uri = config.get("GOOGLE_REDIRECT_URI", "")
        self.scopes = config.get("GOOGLE_SCOPES", [])

    def is_configured(self):
        return all([self.client_id, self.client_secret, self.redirect_uri])

    def configuration_message(self):
        if self.is_configured():
            return ""
        return (
            "Google OAuth 설정이 비어 있습니다. "
            ".env.secret에 GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI를 입력해주세요."
        )

    def authorization_url(self, state):
        self._assert_configured()
        flow = self._build_flow(state)
        authorization_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        return authorization_url

    def exchange_code(self, state, authorization_response):
        self._assert_configured()
        flow = self._build_flow(state)
        flow.fetch_token(authorization_response=authorization_response)
        return self.credentials_to_payload(flow.credentials)

    def fetch_userinfo(self, access_token):
        response = requests.get(
            self.USERINFO_URI,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def build_credentials(self, token_payload):
        self._assert_configured()
        credentials = Credentials(
            token=token_payload.get("access_token"),
            refresh_token=token_payload.get("refresh_token"),
            token_uri=self.TOKEN_URI,
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=token_payload.get("scopes") or self.scopes,
        )

        expiry = token_payload.get("expiry")
        if expiry:
            parsed_expiry = timezone_fix(expiry)
            credentials.expiry = parsed_expiry

        return credentials

    def ensure_valid_credentials(self, token_payload):
        credentials = self.build_credentials(token_payload)
        refreshed = False

        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            refreshed = True

        return credentials, self.credentials_to_payload(credentials), refreshed

    def credentials_to_payload(self, credentials):
        expiry = None
        if credentials.expiry:
            expiry = timezone_fix(credentials.expiry).isoformat()

        return {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "scopes": list(credentials.scopes or self.scopes),
            "expiry": expiry,
        }

    def _build_flow(self, state):
        flow = Flow.from_client_config(
            client_config={
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": self.AUTH_URI,
                    "token_uri": self.TOKEN_URI,
                    "auth_provider_x509_cert_url": self.CERTS_URI,
                    "redirect_uris": [self.redirect_uri],
                }
            },
            scopes=self.scopes,
            state=state,
        )
        flow.redirect_uri = self.redirect_uri
        return flow

    def _assert_configured(self):
        if not self.is_configured():
            raise RuntimeError(self.configuration_message())


def timezone_fix(expiry_value):
    if isinstance(expiry_value, datetime):
        parsed = expiry_value
    else:
        parsed = datetime.fromisoformat(expiry_value)

    if parsed.tzinfo is None:
        return parsed

    return parsed.astimezone(timezone.utc).replace(tzinfo=None)
