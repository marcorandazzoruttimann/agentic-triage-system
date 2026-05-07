import json
import os
from datetime import datetime
from typing import Any, Dict


LOG_FILE_PATH = os.path.join("logs", "activity.jsonl")


def _ensure_log_dir():
    """
    Assicura che la cartella logs/ esista.
    """
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)


def _redact_sensitive_data(text: str) -> str:
    """
    Oscura informazioni sensibili nel testo.
    Esempi:
    - API keys (pattern base)
    - token lunghi
    """

    if not isinstance(text, str):
        return text

    # Redazione semplice per API key OpenAI (sk-...)
    text = text.replace("sk-", "sk-***")

    # Redazione generica per stringhe lunghe (token-like)
    # Es: abcdefghijklmnopqrstuvwxyz123456 → abc***456
    if len(text) > 20:
        text = text[:3] + "***" + text[-3:]

    return text


def _sanitize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Applica redaction a tutti i campi stringa del payload.
    """

    sanitized = {}

    for key, value in payload.items():
        if isinstance(value, str):
            sanitized[key] = _redact_sensitive_data(value)
        else:
            sanitized[key] = value

    return sanitized


def log_event(event_type: str, payload: Dict[str, Any]) -> None:
    """
    Scrive un evento nel file JSONL.

    Struttura:
    {
        "timestamp": "...",
        "event_type": "...",
        "payload": {...}
    }
    """

    _ensure_log_dir()

    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "payload": _sanitize_payload(payload),
    }

    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")