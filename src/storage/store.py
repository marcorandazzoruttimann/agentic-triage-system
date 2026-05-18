import json
from pathlib import Path

from schemas.ticket import Ticket

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TICKETS_PATH = _REPO_ROOT / "data" / "tickets.jsonl"


def _ensure_data_dir() -> None:
    TICKETS_PATH.parent.mkdir(parents=True, exist_ok=True)


def next_ticket_id() -> int:
    """Restituisce il prossimo ID univoco (max esistente + 1)."""
    if not TICKETS_PATH.exists():
        return 1

    max_id = 0
    with open(TICKETS_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            max_id = max(max_id, int(record["id"]))

    return max_id + 1


def save_ticket(ticket: Ticket) -> None:
    """
    Append di uno snapshot ticket su JSONL.
    Ogni cambio di stato aggiunge una riga; l'ultima riga per ID è lo stato corrente.
    """
    _ensure_data_dir()
    with open(TICKETS_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(ticket.model_dump(), ensure_ascii=False) + "\n")


def load_ticket_snapshots() -> list[dict]:
    """Carica tutte le righe JSONL (utilità per test e debug)."""
    if not TICKETS_PATH.exists():
        return []

    snapshots = []
    with open(TICKETS_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                snapshots.append(json.loads(line))
    return snapshots


def get_current_ticket(ticket_id: int) -> dict | None:
    """Ultimo snapshot per ID (stato corrente)."""
    current = None
    for row in load_ticket_snapshots():
        if row["id"] == ticket_id:
            current = row
    return current
