from datetime import datetime, timezone

from flask import Blueprint, current_app, flash, g, jsonify, redirect, render_template, request, url_for

from ..extensions import get_mongo_client, get_oauth_service, get_user_repository

bp = Blueprint("core", __name__)


def _format_timestamp(value):
    if not value:
        return "기록 없음"

    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value

    if value.tzinfo is not None:
        value = value.astimezone(timezone.utc).replace(tzinfo=None)

    return value.strftime("%Y-%m-%d %H:%M")


def _scope_label(scopes):
    if not scopes:
        return "기본 scope"

    labels = []
    for scope in scopes[:3]:
        if scope.startswith("https://www.googleapis.com/auth/"):
            labels.append(scope.rsplit("/", 1)[-1])
        elif scope.startswith("https://www.googleapis.com/auth/userinfo."):
            labels.append(scope.rsplit(".", 1)[-1])
        else:
            labels.append(scope)

    suffix = " +" if len(scopes) > 3 else ""
    return ", ".join(labels) + suffix


def _checked(form, name):
    return form.get(name) == "on"


@bp.get("/")
def home():
    if g.get("current_user"):
        return redirect(url_for("mailbox.mailbox_home"))

    oauth_service = get_oauth_service()
    token_storage_ready = get_user_repository().can_store_tokens
    return render_template(
        "home.html",
        oauth_ready=oauth_service.is_configured(),
        token_storage_ready=token_storage_ready,
        setup_ready=oauth_service.is_configured() and token_storage_ready,
        oauth_warning=oauth_service.configuration_message(),
    )


@bp.route("/settings", methods=["GET", "POST"])
def settings_page():
    user_repository = get_user_repository()
    user = g.current_user or {}

    if request.method == "POST":
        if not user:
            flash("설정을 저장하려면 먼저 로그인해주세요.", "error")
            return redirect(url_for("core.settings_page"))
        current_settings = user_repository.get_settings(user)
        submitted = {
            "mailbox_page_size": request.form.get("mailbox_page_size"),
            "default_mail_view": request.form.get("default_mail_view", "all"),
            "review_threshold": request.form.get("review_threshold"),
            "quarantine_threshold": request.form.get("quarantine_threshold"),
            "apply_hidden_rules": _checked(request.form, "apply_hidden_rules"),
            "allow_unsubscribe_actions": _checked(request.form, "allow_unsubscribe_actions"),
            "confirm_unsubscribe_actions": _checked(request.form, "confirm_unsubscribe_actions"),
            "keep_unsubscribe_history": _checked(request.form, "keep_unsubscribe_history"),
            "show_html_preview": _checked(request.form, "show_html_preview"),
            "allow_attachment_downloads": _checked(request.form, "allow_attachment_downloads"),
            "sync_failure_alerts": _checked(request.form, "sync_failure_alerts"),
            "quarantine_alerts": _checked(request.form, "quarantine_alerts"),
            "daily_summary_email": _checked(request.form, "daily_summary_email"),
        }
        current_settings.update(submitted)
        user_repository.update_settings(user["id"], current_settings)
        flash("설정을 저장했습니다.", "success")
        return redirect(url_for("core.settings_page"))

    settings = user_repository.get_settings(user)
    token_scopes = user.get("token_scopes") or current_app.config.get("GOOGLE_SCOPES", [])
    last_synced = user.get("updated_at") or user.get("last_login_at")

    return render_template(
        "settings.html",
        browser_title=f"설정 | {current_app.config['APP_NAME']}",
        settings=settings,
        is_connected=bool(user),
        connected_email=user.get("email"),
        connected_name=user.get("name"),
        last_synced_label=_format_timestamp(last_synced),
        google_configured=get_oauth_service().is_configured(),
        gmail_scope_label=_scope_label(token_scopes),
        hidden_keywords=user_repository.get_hidden_keywords(user),
    )


@bp.get("/privacy")
def privacy():
    return render_template("privacy.html")


@bp.get("/health")
def health():
    try:
        get_mongo_client().admin.command("ping")
        db_status = "connected"
    except Exception as exc:  # pragma: no cover
        db_status = f"error: {exc}"

    return jsonify(
        {
            "status": "ok",
            "db": db_status,
            "oauth_configured": get_oauth_service().is_configured(),
            "token_storage_ready": get_user_repository().can_store_tokens,
        }
    )
