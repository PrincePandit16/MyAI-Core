import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# Patterns to redact: JWTs, API Keys, Passwords, Emails
REDACTION_PATTERNS = {
    "jwt": r"eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*",
    "api_key": r"(?i)(api[_-]?key|secret|token|password)[\s]*=[\s]*['\"]?([A-Za-z0-9_\-]{16,})['\"]?",
    "email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
}


def redact_sensitive_info(message: Any) -> str:
    """
    Redacts sensitive information from a string using predefined patterns.
    """
    if not isinstance(message, str):
        message = str(message)

    redacted_text = message
    for label, pattern in REDACTION_PATTERNS.items():
        redacted_text = re.sub(pattern, f"<{label.upper()}_REDACTED>", redacted_text)

    return redacted_text


class RedactingFormatter(logging.Formatter):
    """
    Custom logging formatter that redacts sensitive information from all logs.
    """

    def format(self, record: logging.LogRecord) -> str:
        original_msg = super().format(record)
        return redact_sensitive_info(original_msg)
