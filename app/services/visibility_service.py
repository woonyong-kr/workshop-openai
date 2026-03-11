class VisibilityService:
    """Phase 2 placeholder for app-side hide and visibility rules."""

    def filter_summaries(self, messages, hidden_keywords=None, active_hidden_keyword=None):
        hidden_keywords = [keyword for keyword in (hidden_keywords or []) if keyword]

        if active_hidden_keyword:
            return [
                message
                for message in messages
                if self._matches_keyword(message, active_hidden_keyword)
            ]

        if not hidden_keywords:
            return messages

        return [
            message
            for message in messages
            if not any(self._matches_keyword(message, keyword) for keyword in hidden_keywords)
        ]

    def filter_detail(self, message, active_hidden_keyword=None):
        return message

    def _matches_keyword(self, message, keyword):
        needle = keyword.strip().lower()
        if not needle:
            return False

        haystack = " ".join(
            str(value)
            for value in [
                message.get("subject", ""),
                message.get("snippet", ""),
                message.get("sender_name", ""),
                message.get("sender_email", ""),
                message.get("classification_reason", ""),
            ]
        ).lower()
        return needle in haystack
