import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from schemas.ticket import Ticket
from storage import store


@pytest.fixture(autouse=True)
def isolated_tickets_file(tmp_path, monkeypatch):
    tickets_file = tmp_path / "tickets.jsonl"
    monkeypatch.setattr(store, "TICKETS_PATH", tickets_file)
    yield tickets_file


def test_next_ticket_id_starts_at_one():
    assert store.next_ticket_id() == 1


def test_save_ticket_append_jsonl():
    ticket = Ticket(id=1, status="OPEN", messaggio_originale="ciao")
    store.save_ticket(ticket)

    lines = store.TICKETS_PATH.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["status"] == "OPEN"


def test_current_state_is_last_snapshot():
    open_ticket = Ticket(id=1, status="OPEN", messaggio_originale="help")
    triaged_ticket = Ticket(
        id=1,
        status="TRIAGED",
        messaggio_originale="help",
        categoria="IT",
        priorita="HIGH",
        riassunto_breve="Email bloccata",
    )
    store.save_ticket(open_ticket)
    store.save_ticket(triaged_ticket)

    current = store.get_current_ticket(1)
    assert current["status"] == "TRIAGED"
