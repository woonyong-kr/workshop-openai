from flask import Blueprint, g, jsonify, redirect, render_template, url_for

from ..extensions import get_mongo_client, get_oauth_service, get_user_repository

bp = Blueprint("core", __name__)


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


@bp.get("/privacy")
def privacy():
    return render_template("privacy.html")


@bp.get("/health")
def health():
    try:
        get_mongo_client().admin.command("ping")
        db_status = "connected"
    except Exception as exc:  # pragma: no cover - depends on runtime infra
        db_status = f"error: {exc}"

    return jsonify(
        {
            "status": "ok",
            "db": db_status,
            "oauth_configured": get_oauth_service().is_configured(),
            "token_storage_ready": get_user_repository().can_store_tokens,
        }
    )
