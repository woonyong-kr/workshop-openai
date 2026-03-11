import base64
import html
from datetime import datetime
from email.utils import parseaddr, parsedate_to_datetime

import bleach
from googleapiclient.discovery import build


class GmailService:
    ALLOWED_TAGS = [
        "a",
        "b",
        "blockquote",
        "br",
        "code",
        "div",
        "em",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "hr",
        "li",
        "ol",
        "p",
        "pre",
        "span",
        "strong",
        "table",
        "tbody",
        "td",
        "th",
        "thead",
        "tr",
        "ul",
    ]
    ALLOWED_ATTRIBUTES = {
        "a": ["href", "title", "target", "rel"],
        "blockquote": ["cite"],
    }

    def __init__(self, oauth_service, user_repository, page_size=20):
        self.oauth_service = oauth_service
        self.user_repository = user_repository
        self.page_size = page_size

    def list_message_page(self, user, cursor=None):
        service = self._build_service_for_user(user)
        response = (
            service.users()
            .messages()
            .list(
                userId="me",
                maxResults=self.page_size,
                pageToken=cursor,
                includeSpamTrash=False,
            )
            .execute()
        )

        messages = []
        for message_meta in response.get("messages", []):
            metadata = (
                service.users()
                .messages()
                .get(
                    userId="me",
                    id=message_meta["id"],
                    format="metadata",
                    metadataHeaders=["From", "Subject", "Date"],
                )
                .execute()
            )
            messages.append(self._build_message_summary(metadata))

        return {
            "messages": messages,
            "next_cursor": response.get("nextPageToken"),
        }

    def get_message_detail(self, user, message_id):
        service = self._build_service_for_user(user)
        message = (
            service.users()
            .messages()
            .get(userId="me", id=message_id, format="full")
            .execute()
        )
        return self._build_message_detail(message)

    def download_attachment(self, user, message_id, part_id):
        service = self._build_service_for_user(user)
        message = (
            service.users()
            .messages()
            .get(userId="me", id=message_id, format="full")
            .execute()
        )

        part = self._find_part_by_id(message.get("payload", {}), part_id)
        if part is None:
            raise FileNotFoundError("Attachment not found.")

        body = part.get("body", {})
        if body.get("attachmentId"):
            attachment = (
                service.users()
                .messages()
                .attachments()
                .get(
                    userId="me",
                    messageId=message_id,
                    id=body["attachmentId"],
                )
                .execute()
            )
            data = attachment.get("data", "")
        else:
            data = body.get("data", "")

        return {
            "filename": part.get("filename") or f"attachment-{part_id}",
            "mime_type": part.get("mimeType") or "application/octet-stream",
            "bytes": self._decode_base64(data),
        }

    def _build_service_for_user(self, user):
        token_payload = self.user_repository.get_token_payload(user)
        credentials, refreshed_payload, refreshed = self.oauth_service.ensure_valid_credentials(
            token_payload
        )

        if refreshed:
            self.user_repository.update_token_payload(user["id"], refreshed_payload)

        return build("gmail", "v1", credentials=credentials, cache_discovery=False)

    def _build_message_summary(self, message):
        payload = message.get("payload", {})
        headers = payload.get("headers", [])
        from_header = self._extract_header(headers, "From")
        subject = self._extract_header(headers, "Subject") or "(제목 없음)"
        sender_name, sender_email = parseaddr(from_header)
        received_at = self._message_datetime(message, headers)
        labels = message.get("labelIds", [])

        return {
            "id": message["id"],
            "thread_id": message.get("threadId"),
            "subject": subject,
            "snippet": message.get("snippet") or "본문 미리보기가 없습니다.",
            "sender_name": sender_name or sender_email or "알 수 없는 발신자",
            "sender_email": sender_email or "unknown@example.com",
            "sender_initial": (sender_name or sender_email or "?")[:1].upper(),
            "display_date": self._format_list_date(received_at),
            "full_date": self._format_detail_date(received_at),
            "labels": labels[:3],
            "unread": "UNREAD" in labels,
            "has_attachments": self._has_attachment(payload),
        }

    def _build_message_detail(self, message):
        payload = message.get("payload", {})
        headers = payload.get("headers", [])
        from_header = self._extract_header(headers, "From")
        sender_name, sender_email = parseaddr(from_header)
        to_header = self._extract_header(headers, "To")
        cc_header = self._extract_header(headers, "Cc")
        received_at = self._message_datetime(message, headers)

        body_parts = {"html": None, "text": None}
        attachments = []
        self._walk_parts(payload, body_parts, attachments)

        body_html = body_parts["html"] or self._text_to_html(body_parts["text"])
        image_attachments = [item for item in attachments if item["is_image"]]
        file_attachments = [item for item in attachments if not item["is_image"]]

        return {
            "id": message["id"],
            "thread_id": message.get("threadId"),
            "subject": self._extract_header(headers, "Subject") or "(제목 없음)",
            "snippet": message.get("snippet") or "",
            "sender_name": sender_name or sender_email or "알 수 없는 발신자",
            "sender_email": sender_email or "unknown@example.com",
            "sender_initial": (sender_name or sender_email or "?")[:1].upper(),
            "to": to_header or "수신자 정보 없음",
            "cc": cc_header,
            "labels": message.get("labelIds", []),
            "full_date": self._format_detail_date(received_at),
            "display_date": self._format_list_date(received_at),
            "body_html": body_html,
            "attachments": attachments,
            "image_attachments": image_attachments,
            "file_attachments": file_attachments,
            "unread": "UNREAD" in message.get("labelIds", []),
        }

    def _walk_parts(self, part, body_parts, attachments):
        mime_type = part.get("mimeType", "")
        filename = part.get("filename")
        body = part.get("body", {})
        data = body.get("data")

        if filename:
            attachments.append(
                {
                    "part_id": part.get("partId", "root"),
                    "filename": filename,
                    "mime_type": mime_type or "application/octet-stream",
                    "size": self._format_size(body.get("size", 0)),
                    "is_image": mime_type.startswith("image/"),
                }
            )

        if mime_type == "text/html" and data and not body_parts["html"]:
            raw_html = self._decode_base64(data).decode("utf-8", errors="replace")
            body_parts["html"] = self._sanitize_html(raw_html)
        elif mime_type == "text/plain" and data and not body_parts["text"]:
            body_parts["text"] = self._decode_base64(data).decode("utf-8", errors="replace")

        for child in part.get("parts", []):
            self._walk_parts(child, body_parts, attachments)

    def _sanitize_html(self, raw_html):
        cleaned = bleach.clean(
            raw_html,
            tags=self.ALLOWED_TAGS,
            attributes=self.ALLOWED_ATTRIBUTES,
            protocols=["http", "https", "mailto"],
            strip=True,
        )
        return bleach.linkify(cleaned)

    def _text_to_html(self, text):
        if not text:
            return "<p>표시할 본문이 없습니다.</p>"

        escaped = html.escape(text)
        paragraphs = [
            f"<p>{paragraph.replace(chr(10), '<br>')}</p>"
            for paragraph in escaped.split("\n\n")
        ]
        return "".join(paragraphs)

    def _message_datetime(self, message, headers):
        internal_date = message.get("internalDate")
        if internal_date:
            return datetime.fromtimestamp(int(internal_date) / 1000).astimezone()

        date_header = self._extract_header(headers, "Date")
        if date_header:
            try:
                parsed = parsedate_to_datetime(date_header)
                return parsed.astimezone()
            except Exception:
                pass

        return datetime.now().astimezone()

    def _format_list_date(self, value):
        now = datetime.now().astimezone()
        if value.date() == now.date():
            label = value.strftime("%p %I:%M")
            return label.replace("AM", "오전").replace("PM", "오후")
        if value.year == now.year:
            return f"{value.month}월 {value.day}일"
        return value.strftime("%Y.%m.%d")

    def _format_detail_date(self, value):
        return value.strftime("%Y년 %m월 %d일 %p %I:%M").replace("AM", "오전").replace(
            "PM", "오후"
        )

    def _extract_header(self, headers, name):
        name = name.lower()
        for header in headers:
            if header.get("name", "").lower() == name:
                return header.get("value", "")
        return ""

    def _has_attachment(self, part):
        if part.get("filename"):
            return True
        return any(self._has_attachment(child) for child in part.get("parts", []))

    def _find_part_by_id(self, part, part_id):
        if part.get("partId", "root") == part_id:
            return part
        for child in part.get("parts", []):
            found = self._find_part_by_id(child, part_id)
            if found:
                return found
        return None

    def _format_size(self, size_in_bytes):
        if size_in_bytes >= 1024 * 1024:
            return f"{size_in_bytes / (1024 * 1024):.1f} MB"
        if size_in_bytes >= 1024:
            return f"{size_in_bytes / 1024:.1f} KB"
        return f"{size_in_bytes} B"

    def _decode_base64(self, value):
        if not value:
            return b""
        padding = "=" * (-len(value) % 4)
        return base64.urlsafe_b64decode(f"{value}{padding}".encode())
