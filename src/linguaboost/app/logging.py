import logging
import re
from typing import Any


_TOKEN_LIKE = re.compile(r"(bot\d+:[A-Za-z0-9_-]{20,})", re.IGNORECASE)


def _redact(msg: str) -> str:
    return _TOKEN_LIKE.sub("[REDACTED_BOT_TOKEN]", msg)


class RedactingFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        record.msg = _redact(str(record.msg))
        if record.args:
            record.args = tuple(_redact(str(a)) if isinstance(a, str) else a for a in record.args)
        return super().format(record)


def setup_logging(level: str = "INFO") -> None:
    root = logging.getLogger()
    root.setLevel(level)
    if not root.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            RedactingFormatter("%(asctime)s %(levelname)s %(name)s %(message)s"),
        )
        root.addHandler(handler)


def user_message_preview(text: str | None, max_len: int = 80) -> str | None:
    if text is None:
        return None
    text = text.strip()
    if len(text) > max_len:
        return text[:max_len] + "…"
    return text


def safe_log_extra(**kwargs: Any) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in kwargs.items():
        if k in {"message_text", "user_text", "raw_text"} and isinstance(v, str):
            out[k] = user_message_preview(v)
        else:
            out[k] = v
    return out
