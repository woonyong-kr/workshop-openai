import io

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)

from ..extensions import get_gmail_service, get_user_repository, get_visibility_service
from ..utils.auth import api_login_required, login_required

bp = Blueprint("mailbox", __name__)
STATUS_FILTERS = {
    "all": None,
    "safe": "일반",
    "review": "보류",
    "quarantine": "격리",
}


def _user_settings():
    return get_user_repository().get_settings(g.current_user)


def _active_status_key():
    default_key = _user_settings()["default_mail_view"]
    key = request.args.get("status", default_key)
    return key if key in STATUS_FILTERS else "all"


def _active_hidden_keyword():
    return request.args.get("hidden_keyword", "").strip()


def _filter_messages(messages, status_key, hidden_keywords, active_hidden_keyword, apply_hidden_rules):
    target_status = STATUS_FILTERS.get(status_key)
    filtered = messages if target_status is None else [
        message for message in messages if message.get("status") == target_status
    ]
    effective_hidden_keywords = hidden_keywords if apply_hidden_rules else []
    return get_visibility_service().filter_summaries(
        filtered,
        hidden_keywords=effective_hidden_keywords,
        active_hidden_keyword=active_hidden_keyword,
    )


def _mailbox_url(status_key, hidden_keyword=""):
    params = {}
    if status_key and status_key != "all":
        params["status"] = status_key
    if hidden_keyword:
        params["hidden_keyword"] = hidden_keyword
    return url_for("mailbox.mailbox_home", **params)


def _load_mailbox_page(status_key, hidden_keywords, active_hidden_keyword, apply_hidden_rules, cursor=None):
    current_cursor = cursor

    while True:
        page = get_gmail_service().list_message_page(g.current_user, cursor=current_cursor)
        filtered = _filter_messages(
            page["messages"],
            status_key,
            hidden_keywords,
            active_hidden_keyword,
            apply_hidden_rules,
        )

        if filtered or not page["next_cursor"] or (
            status_key == "all" and (not hidden_keywords or not apply_hidden_rules) and not active_hidden_keyword
        ):
            return {"messages": filtered, "next_cursor": page["next_cursor"]}

        current_cursor = page["next_cursor"]


@bp.get("/mailbox")
@login_required
def mailbox_home():
    error_message = None
    messages = []
    next_cursor = None
    active_filter = _active_status_key()
    active_hidden_keyword = _active_hidden_keyword()
    hidden_keywords = get_user_repository().get_hidden_keywords(g.current_user)
    settings = _user_settings()

    try:
        page = _load_mailbox_page(
            active_filter,
            hidden_keywords,
            active_hidden_keyword,
            settings["apply_hidden_rules"],
        )
        messages = page["messages"]
        next_cursor = page["next_cursor"]
    except Exception:
        current_app.logger.exception("Failed to load mailbox")
        error_message = "메일 목록을 불러오지 못했습니다. Google 권한과 설정을 확인해주세요."

    return render_template(
        "mailbox.html",
        messages=messages,
        next_cursor=next_cursor,
        error_message=error_message,
        active_filter=active_filter,
        active_hidden_keyword=active_hidden_keyword,
        settings=settings,
        hidden_keywords=hidden_keywords,
    )


@bp.get("/mailbox/feed")
@api_login_required
def mailbox_feed():
    cursor = request.args.get("cursor")
    active_filter = _active_status_key()
    active_hidden_keyword = _active_hidden_keyword()
    hidden_keywords = get_user_repository().get_hidden_keywords(g.current_user)
    settings = _user_settings()

    try:
        page = _load_mailbox_page(
            active_filter,
            hidden_keywords,
            active_hidden_keyword,
            settings["apply_hidden_rules"],
            cursor=cursor,
        )
        html = render_template(
            "partials/mail_rows.html",
            messages=page["messages"],
            active_filter=active_filter,
            active_hidden_keyword=active_hidden_keyword,
        )
        return jsonify({"html": html, "next_cursor": page["next_cursor"]})
    except Exception:
        current_app.logger.exception("Failed to extend mailbox feed")
        return jsonify({"error": "메일을 더 불러오지 못했습니다. 잠시 후 다시 시도해주세요."}), 502


@bp.post("/mail/bulk-trash")
@login_required
def bulk_trash_messages():
    message_ids = request.form.getlist("message_ids")
    active_filter = _active_status_key()
    active_hidden_keyword = request.form.get("hidden_keyword", "").strip()
    if not message_ids:
        flash("이동할 메일을 먼저 선택해주세요.", "error")
        return redirect(_mailbox_url(active_filter, active_hidden_keyword))

    try:
        get_gmail_service().trash_messages(g.current_user, message_ids)
        flash(f"{len(message_ids)}개 메일을 Gmail 휴지통으로 이동했습니다.", "success")
    except Exception:
        current_app.logger.exception("Failed to trash selected messages")
        flash("메일을 휴지통으로 이동하지 못했습니다. 잠시 후 다시 시도해주세요.", "error")

    return redirect(_mailbox_url(active_filter, active_hidden_keyword))


@bp.post("/mailbox/hidden-rules")
@login_required
def add_hidden_rule():
    keyword = request.form.get("keyword", "").strip()
    active_filter = request.form.get("status", "all")

    if not keyword:
        flash("숨길 키워드를 입력해주세요.", "error")
        return redirect(_mailbox_url(active_filter))

    try:
        get_user_repository().add_hidden_keyword(g.current_user["id"], keyword)
        flash(f"'{keyword}' 키워드를 숨김 규칙에 추가했습니다.", "success")
    except ValueError as exc:
        flash(str(exc), "error")

    return redirect(_mailbox_url(active_filter))


@bp.post("/mailbox/hidden-rules/remove")
@login_required
def remove_hidden_rule():
    keyword = request.form.get("keyword", "").strip()
    active_filter = request.form.get("status", "all")
    active_hidden_keyword = request.form.get("active_hidden_keyword", "").strip()

    get_user_repository().remove_hidden_keyword(g.current_user["id"], keyword)
    flash(f"'{keyword}' 키워드를 숨김 규칙에서 제거했습니다.", "success")

    next_hidden_keyword = "" if active_hidden_keyword.lower() == keyword.lower() else active_hidden_keyword
    return redirect(_mailbox_url(active_filter, next_hidden_keyword))


@bp.get("/mail/<message_id>")
@login_required
def mail_detail(message_id):
    error_message = None
    message = None
    active_filter = _active_status_key()
    active_hidden_keyword = _active_hidden_keyword()
    settings = _user_settings()

    try:
        message = get_visibility_service().filter_detail(
            get_gmail_service().get_message_detail(g.current_user, message_id)
        )
    except Exception:
        current_app.logger.exception("Failed to load message detail")
        error_message = "메일 상세를 불러오지 못했습니다. 잠시 후 다시 시도해주세요."

    return render_template(
        "mail_detail.html",
        message=message,
        error_message=error_message,
        active_filter=active_filter,
        active_hidden_keyword=active_hidden_keyword,
        settings=settings,
    )



@bp.get("/mail/<message_id>/viewer")
@login_required
def mail_viewer(message_id):
    settings = _user_settings()

    try:
        message = get_visibility_service().filter_detail(
            get_gmail_service().get_message_detail(g.current_user, message_id)
        )
    except Exception:
        current_app.logger.exception("Failed to load message viewer")
        return render_template(
            "mail_viewer.html",
            message=None,
            error_message="메일 본문을 표시하지 못했습니다. 잠시 후 다시 시도해주세요.",
            settings=settings,
        )

    return render_template(
        "mail_viewer.html",
        message=message,
        error_message=None,
        settings=settings,
    )

@bp.get("/mail/<message_id>/attachments/<part_id>")
@login_required
def mail_attachment(message_id, part_id):
    if not _user_settings()["allow_attachment_downloads"]:
        abort(403)

    attachment = get_gmail_service().download_attachment(g.current_user, message_id, part_id)
    as_attachment = request.args.get("download") == "1"

    return send_file(
        io.BytesIO(attachment["bytes"]),
        mimetype=attachment["mime_type"],
        as_attachment=as_attachment,
        download_name=attachment["filename"],
    )


@bp.post("/mail/<message_id>/trash")
@login_required
def trash_single_message(message_id):
    active_filter = _active_status_key()
    active_hidden_keyword = _active_hidden_keyword()
    try:
        get_gmail_service().trash_messages(g.current_user, [message_id])
        flash("메일을 Gmail 휴지통으로 이동했습니다.", "success")
    except Exception:
        current_app.logger.exception("Failed to trash message")
        flash("메일을 휴지통으로 이동하지 못했습니다. 잠시 후 다시 시도해주세요.", "error")
        if active_filter == "all":
            if active_hidden_keyword:
                return redirect(url_for("mailbox.mail_detail", message_id=message_id, hidden_keyword=active_hidden_keyword))
            return redirect(url_for("mailbox.mail_detail", message_id=message_id))
        return redirect(
            url_for(
                "mailbox.mail_detail",
                message_id=message_id,
                status=active_filter,
                hidden_keyword=active_hidden_keyword or None,
            )
        )

    return redirect(_mailbox_url(active_filter, active_hidden_keyword))
