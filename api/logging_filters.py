"""
Logging filters untuk MIRU Bank Sampah.

Fungsi:
- Redact PII (password, token, NIK, KTP) dari log messages
- Menyediakan JSON formatter untuk structured logging
"""

import logging
import re

# Pola untuk mendeteksi dan meredact data sensitif
SENSITIVE_PATTERNS: list[tuple[re.Pattern, str]] = [
    # Password di JSON body
    (re.compile(r'("password")\s*:\s*"[^"]+"', re.IGNORECASE), r'\1: "***REDACTED***"'),
    # Token JWT di header Authorization
    (re.compile(r'(Authorization:\s*Bearer\s+)[A-Za-z0-9\-._~+/]+={0,2}', re.IGNORECASE), r'\1***REDACTED***'),
    # Token di JSON body (refresh, access)
    (re.compile(r'"(access|refresh|token)"\s*:\s*"[A-Za-z0-9\-._~+/]+={0,2}"', re.IGNORECASE), r'"\1": "***REDACTED***"'),
    # NIK (16 digit)
    (re.compile(r'\b(\d{16})\b'), r'***NIK-REDACTED***'),
    # No HP
    (re.compile(r'("no_hp")\s*:\s*"\d{10,15}"', re.IGNORECASE), r'\1: "***REDACTED***"'),
]


def redact_sensitive(text: str) -> str:
    """Redact all sensitive data from a log string."""
    if not isinstance(text, str):
        return text
    for pattern, replacement in SENSITIVE_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


class PIIRedactFilter(logging.Filter):
    """Logging filter yang meredact PII dari log messages.

    Gunakan di LOGGING.handlers.filters di settings.py.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            record.msg = redact_sensitive(record.msg)
        if hasattr(record, 'args') and record.args:
            cleaned_args = tuple(
                redact_sensitive(str(arg)) if isinstance(arg, str) else arg
                for arg in record.args
            )
            record.args = cleaned_args
        return True


class JSONFormatter(logging.Formatter):
    """JSON log formatter untuk structured logging.

    Output: satu baris JSON per log entry, cocok untuk log aggregation
    (ELK, Datadog, Grafana Loki, dll.)
    """

    def format(self, record: logging.LogRecord) -> str:
        from datetime import timezone

        log_entry = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
        }

        # Sertakan request_id jika ada di thread-local
        from .middleware import get_current_request
        _req = get_current_request()
        if _req is not None:
            log_entry['request_id'] = getattr(_req, 'request_id', None)

        # Sertakan exception traceback jika ada
        if record.exc_info and record.exc_info[0]:
            log_entry['exception'] = self.formatException(record.exc_info)

        # Extra fields dari logging extra={}
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)

        import json
        return json.dumps(log_entry, ensure_ascii=False, default=str)
