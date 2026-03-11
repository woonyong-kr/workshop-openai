import secrets

from flask import Blueprint, current_app, flash, redirect, request, session, url_for

from ..extensions import get_oauth_service, get_user_repository

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.get("/google/start")
def google_start():
    oauth_service = get_oauth_service()

    if not oauth_service.is_configured():
        flash(oauth_service.configuration_message(), "error")
        return redirect(url_for("core.home"))

    if not get_user_repository().can_store_tokens:
        flash(
            "TOKEN_ENCRYPTION_KEY 설정이 없거나 형식이 올바르지 않아 로그인을 시작할 수 없습니다.",
            "error",
        )
        return redirect(url_for("core.home"))

    state = secrets.token_urlsafe(24)
    session["oauth_state"] = state

    authorization_url = oauth_service.authorization_url(state)
    return redirect(authorization_url)


@bp.get("/google/callback")
def google_callback():
    if request.args.get("error"):
        flash("Google 로그인이 취소되었거나 거부되었습니다.", "error")
        return redirect(url_for("core.home"))

    expected_state = session.get("oauth_state")
    received_state = request.args.get("state")

    if not expected_state or expected_state != received_state:
        flash("잘못된 OAuth state 입니다. 다시 로그인해주세요.", "error")
        return redirect(url_for("core.home"))

    oauth_service = get_oauth_service()
    user_repository = get_user_repository()

    try:
        authorization_response = current_app.config["GOOGLE_REDIRECT_URI"]
        if request.query_string:
            authorization_response = (
                f"{authorization_response}?{request.query_string.decode('utf-8')}"
            )

        token_payload = oauth_service.exchange_code(received_state, authorization_response)
        profile = oauth_service.fetch_userinfo(token_payload["access_token"])
        existing_user = user_repository.get_by_google_sub(profile["sub"])

        if existing_user and not token_payload.get("refresh_token"):
            existing_token = user_repository.get_token_payload(existing_user)
            token_payload["refresh_token"] = existing_token.get("refresh_token")

        user = user_repository.upsert_google_user(profile, token_payload)
    except Exception:  # pragma: no cover - exercised in integration
        current_app.logger.exception("Google OAuth callback failed")
        flash("Google 계정을 연결하지 못했습니다. 설정 또는 권한을 확인해주세요.", "error")
        return redirect(url_for("core.home"))

    session.pop("oauth_state", None)
    session["user_id"] = user["id"]
    session.permanent = True

    flash(f"{user['name']} 계정으로 로그인되었습니다.", "success")
    return redirect(url_for("mailbox.mailbox_home"))


@bp.post("/logout")
def logout():
    session.clear()
    flash("로그아웃되었습니다.", "success")
    return redirect(url_for("core.home"))
