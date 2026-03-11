import base64
import html
import re
from datetime import datetime
from email.utils import parseaddr, parsedate_to_datetime

import bleach
from googleapiclient.discovery import build


class GmailService:
    STATUS_STYLES = {"격리": "danger", "보류": "warning", "일반": "success"}
    RISK_STYLES = {"높음": "danger", "중간": "warning", "낮음": "success"}
    TRUSTED_DOMAINS = ["gmail.com", "google.com", "woonyong.org"]
    PHISHING_KEYWORDS = [
        "verify",
        "account",
        "urgent",
        "password",
        "security",
        "login",
        "invoice",
        "payment",
        "인증",
        "보안",
        "로그인",
        "비밀번호",
        "기한",
        "차단",
        "결제",
    ]
    MARKETING_KEYWORDS = [
        "unsubscribe",
        "promotion",
        "proposal",
        "campaign",
        "광고",
        "제안",
        "마케팅",
        "프로모션",
        "수신거부",
    ]
    RISKY_EXTENSIONS = [".html", ".htm", ".exe", ".js", ".scr", ".bat", ".cmd", ".docm", ".xlsm"]
    ALLOWED_TAGS = [
        "a", "b", "blockquote", "br", "code", "div", "em", "h1", "h2", "h3", "h4", "h5", "h6",
        "hr", "img", "li", "ol", "p", "pre", "span", "strong", "table", "tbody", "td", "th", "thead", "tr", "ul",
    ]
    ALLOWED_ATTRIBUTES = {
        "a": ["href", "title", "target", "rel"],
        "blockquote": ["cite"],
        "img": ["src", "alt", "title"],
    }

    def __init__(self, oauth_service, user_repository, page_size=20):
        self.oauth_service = oauth_service
        self.user_repository = user_repository
        self.page_size = page_size

    def list_message_page(self, user, cursor=None):
        service = self._build_service_for_user(user)
        page_size = self.user_repository.get_settings(user)["mailbox_page_size"]
        response = (
            service.users()
            .messages()
            .list(
                userId="me",
                maxResults=page_size,
                pageToken=cursor,
                includeSpamTrash=False,
            )
            .execute()
        )

        message_ids = [message_meta["id"] for message_meta in response.get("messages", [])]
        metadata_by_id = self._fetch_message_metadata_batch(service, message_ids)
        messages = [
            self._build_message_summary(user, metadata_by_id[message_id])
            for message_id in message_ids
            if message_id in metadata_by_id
        ]

        return {"messages": messages, "next_cursor": response.get("nextPageToken")}

    def get_message_detail(self, user, message_id):
        service = self._build_service_for_user(user)
        message = service.users().messages().get(userId="me", id=message_id, format="full").execute()
        return self._build_message_detail(user, message)

    def trash_messages(self, user, message_ids):
        service = self._build_service_for_user(user)
        for message_id in message_ids:
            service.users().messages().trash(userId="me", id=message_id).execute()

    def download_attachment(self, user, message_id, part_id):
        service = self._build_service_for_user(user)
        message = service.users().messages().get(userId="me", id=message_id, format="full").execute()

        part = self._find_part_by_id(message.get("payload", {}), part_id)
        if part is None:
            raise FileNotFoundError("Attachment not found.")

        body = part.get("body", {})
        if body.get("attachmentId"):
            attachment = (
                service.users()
                .messages()
                .attachments()
                .get(userId="me", messageId=message_id, id=body["attachmentId"])
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
        credentials, refreshed_payload, refreshed = self.oauth_service.ensure_valid_credentials(token_payload)

        if refreshed:
            self.user_repository.update_token_payload(user["id"], refreshed_payload)

        return build("gmail", "v1", credentials=credentials, cache_discovery=False)

    def _fetch_message_metadata_batch(self, service, message_ids):
        if not message_ids:
            return {}

        try:
            batch = service.new_batch_http_request()
        except AttributeError:
            batch = None

        if batch is None:
            return self._fetch_message_metadata_sequential(service, message_ids)

        responses = {}
        failed_ids = []

        def callback(request_id, response, exception):
            if exception is not None or response is None:
                failed_ids.append(request_id)
                return
            responses[request_id] = response

        try:
            for message_id in message_ids:
                batch.add(self._build_message_metadata_request(service, message_id), request_id=message_id, callback=callback)
            batch.execute()
        except Exception:
            return self._fetch_message_metadata_sequential(service, message_ids)

        missing_ids = [message_id for message_id in message_ids if message_id not in responses]
        if failed_ids or missing_ids:
            fallback_ids = list(dict.fromkeys([*failed_ids, *missing_ids]))
            responses.update(self._fetch_message_metadata_sequential(service, fallback_ids))

        return responses

    def _fetch_message_metadata_sequential(self, service, message_ids):
        return {
            message_id: self._build_message_metadata_request(service, message_id).execute()
            for message_id in message_ids
        }

    def _build_message_metadata_request(self, service, message_id):
        return service.users().messages().get(
            userId="me",
            id=message_id,
            format="metadata",
            metadataHeaders=["From", "Subject", "Date"],
        )

    def _build_message_summary(self, user, message):
        payload = message.get("payload", {})
        headers = payload.get("headers", [])
        from_header = self._extract_header(headers, "From")
        subject = self._extract_header(headers, "Subject") or "(제목 없음)"
        sender_name, sender_email = parseaddr(from_header)
        received_at = self._message_datetime(message, headers)
        labels = message.get("labelIds", [])
        classification = self._classify_message(
            user=user,
            subject=subject,
            sender_email=sender_email,
            content_text=f"{subject}\n{message.get('snippet', '')}",
            attachment_names=self._attachment_names(payload),
        )

        return {
            "id": message["id"],
            "thread_id": message.get("threadId"),
            "subject": subject,
            "snippet": message.get("snippet") or "본문 미리보기가 없습니다.",
            "sender_name": sender_name or sender_email or "이름 없는 발신자",
            "sender_email": sender_email or "unknown@example.com",
            "sender_initial": (sender_name or sender_email or "?")[:1].upper(),
            "display_date": self._format_list_date(received_at),
            "full_date": self._format_detail_date(received_at),
            "labels": labels[:3],
            "unread": "UNREAD" in labels,
            "has_attachments": self._has_attachment(payload),
            **classification,
        }

    def _build_message_detail(self, user, message):
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

        body_html = self._resolve_body_html(body_parts)
        body_text = body_parts["text"] or self._html_to_text(body_parts["html"])
        image_attachments = [item for item in attachments if item["is_image"]]
        file_attachments = [item for item in attachments if not item["is_image"]]
        classification = self._classify_message(
            user=user,
            subject=self._extract_header(headers, "Subject") or "(제목 없음)",
            sender_email=sender_email,
            content_text=f"{message.get('snippet', '')}\n{body_text}",
            attachment_names=[item["filename"] for item in attachments],
        )

        return {
            "id": message["id"],
            "thread_id": message.get("threadId"),
            "subject": self._extract_header(headers, "Subject") or "(제목 없음)",
            "snippet": message.get("snippet") or "",
            "sender_name": sender_name or sender_email or "이름 없는 발신자",
            "sender_email": sender_email or "unknown@example.com",
            "sender_initial": (sender_name or sender_email or "?")[:1].upper(),
            "to": to_header or "수신자 정보 없음",
            "cc": cc_header,
            "labels": message.get("labelIds", []),
            "full_date": self._format_detail_date(received_at),
            "display_date": self._format_list_date(received_at),
            "body_html": body_html,
            "body_text": body_text,
            "attachments": attachments,
            "image_attachments": image_attachments,
            "file_attachments": file_attachments,
            "unread": "UNREAD" in message.get("labelIds", []),
            **classification,
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

    def _resolve_body_html(self, body_parts):
        html_body = body_parts["html"]
        if html_body and self._html_to_text(html_body):
            return html_body
        return self._text_to_html(body_parts["text"])

    def _text_to_html(self, text):
        if not text:
            return "<p>표시할 본문이 없습니다.</p>"

        escaped = html.escape(text)
        paragraphs = [f"<p>{paragraph.replace(chr(10), '<br>')}</p>" for paragraph in escaped.split("\n\n")]
        return "".join(paragraphs)

    def _html_to_text(self, value):
        if not value:
            return ""

        text = re.sub(r"(?is)<(script|style).*?>.*?</\\1>", " ", value)
        text = re.sub(r"(?s)<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        return html.unescape(text).strip()

    def _attachment_names(self, payload):
        names = []
        self._collect_attachment_names(payload, names)
        return names

    def _collect_attachment_names(self, part, names):
        filename = part.get("filename")
        if filename:
            names.append(filename)

        for child in part.get("parts", []):
            self._collect_attachment_names(child, names)

    def _classify_message(self, user, subject, sender_email, content_text, attachment_names):
        settings = self.user_repository.get_settings(user)
        review_threshold = settings["review_threshold"]
        quarantine_threshold = max(review_threshold + 1, settings["quarantine_threshold"])

        text = f"{subject}\n{content_text}".lower()
        score = 15
        evidence = []
        reason_flags = set()

        if any(keyword in text for keyword in self.PHISHING_KEYWORDS):
            score += 35
            evidence.append("본문에 계정 확인, 로그인, 결제, 보안 관련 표현이 포함되어 있습니다.")
            reason_flags.add("본문 내용")

        if any(keyword in text for keyword in self.MARKETING_KEYWORDS):
            score += 18
            evidence.append("광고 또는 반복 제안으로 보이는 문구가 감지되었습니다.")
            reason_flags.add("본문 내용")

        sender_domain = sender_email.split("@")[-1].lower() if "@" in sender_email else ""
        if sender_domain and all(not sender_domain.endswith(domain) for domain in self.TRUSTED_DOMAINS):
            score += 12
            evidence.append("발신 도메인이 신뢰 도메인 목록과 일치하지 않습니다.")

        risky_attachment = next(
            (
                filename
                for filename in attachment_names
                if any(filename.lower().endswith(ext) for ext in self.RISKY_EXTENSIONS)
            ),
            None,
        )
        if risky_attachment:
            score += 30
            evidence.append(f"위험 가능성이 있는 첨부파일이 있습니다: {risky_attachment}")
            reason_flags.add("첨부파일")

        score = min(score, 99)
        if score >= quarantine_threshold:
            status = "격리"
            classification = "격리 권장"
            risk_level = "높음"
        elif score >= review_threshold:
            status = "보류"
            classification = "보류 필요"
            risk_level = "중간"
        else:
            status = "일반"
            classification = "일반 메일"
            risk_level = "낮음"

        if not evidence:
            evidence.append("위험 키워드나 첨부파일 이상 징후가 뚜렷하게 감지되지 않았습니다.")

        classification_reason = " + ".join(sorted(reason_flags)) if reason_flags else "본문 내용"
        return {
            "classification": classification,
            "classification_reason": classification_reason,
            "status": status,
            "status_style": self.STATUS_STYLES[status],
            "risk_score": score,
            "risk_level": risk_level,
            "risk_style": self.RISK_STYLES[risk_level],
            "evidence": evidence,
        }

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
        return value.strftime("%Y년 %m월 %d일 %p %I:%M").replace("AM", "오전").replace("PM", "오후")

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
