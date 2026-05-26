"""Percorsi assoluti rispetto alla root del repository."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

MANUALE_IT_PATH = REPO_ROOT / "data" / "manuale_it.txt"
POLICY_PATH = REPO_ROOT / "data" / "policy.txt"
TICKETS_PATH = REPO_ROOT / "data" / "tickets.jsonl"
LOG_FILE_PATH = REPO_ROOT / "logs" / "activity.jsonl"
ENV_PATH = REPO_ROOT / ".env"
