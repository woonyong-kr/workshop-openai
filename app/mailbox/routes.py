import io

from flask import (
    Blueprint,
    current_app,
    g,
    jsonify,
    render_template,
    request,
    send_file,
)

from ..extensions import get_gmail_service, get_visibility_service
from ..utils.auth import api_login_required, login_required

bp = Blueprint("mailbox", __name__)


@bp.get("/mailbox")
@login_required
def mailbox_home():
    gmail_service = get_gmail_service()
    error_message = None
    messages = []
    next_cursor = None

    try:
        page = gmail_service.list_message_page(g.current_user)
        messages = get_visibility_service().filter_summaries(page["messages"])
        next_cursor = page["next_cursor"]
    except Exception:  # pragma: no cover - depends on external API
        current_app.logger.exception("Failed to load mailbox")
        error_message = "메일 목록을 가져오지 못했습니다. Google 권한과 설정을 확인해주세요."

    return render_template(
        "mailbox.html",
        messages=messages,
        next_cursor=next_cursor,
        error_message=error_message,
    )


@bp.get("/mailbox/feed")
@api_login_required
def mailbox_feed():
    cursor = request.args.get("cursor")

    try:
        page = get_gmail_service().list_message_page(g.current_user, cursor=cursor)
        messages = get_visibility_service().filter_summaries(page["messages"])
        html = render_template("partials/mail_rows.html", messages=messages)
        return jsonify({"html": html, "next_cursor": page["next_cursor"]})
    except Exception:  # pragma: no cover - depends on external API
        current_app.logger.exception("Failed to extend mailbox feed")
        return (
            jsonify(
                {
                    "error": "메일을 더 불러오지 못했습니다. 잠시 후 다시 시도해주세요.",
                }
            ),
            502,
        )


@bp.get("/mail/<message_id>")
@login_required
def mail_detail(message_id):
    error_message = None
    message = None

    try:
        message = get_visibility_service().filter_detail(
            get_gmail_service().get_message_detail(g.current_user, message_id)
        )
    except Exception:  # pragma: no cover - depends on external API
        current_app.logger.exception("Failed to load message detail")
        error_message = "메일 상세를 가져오지 못했습니다. 잠시 후 다시 시도해주세요."

    return render_template(
        "mail_detail.html",
        message=message,
        error_message=error_message,
    )


@bp.get("/mail/<message_id>/attachments/<part_id>")
@login_required
def mail_attachment(message_id, part_id):
    attachment = get_gmail_service().download_attachment(g.current_user, message_id, part_id)
    as_attachment = request.args.get("download") == "1"

    return send_file(
        io.BytesIO(attachment["bytes"]),
        mimetype=attachment["mime_type"],
        as_attachment=as_attachment,
        download_name=attachment["filename"],
    )
