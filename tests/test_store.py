from schemas.ticket import Ticket
from storage import store


def test_next_ticket_id_starts_at_one():
    assert store.next_ticket_id() == 1


def test_last_snapshot_wins():
    store.save_ticket(Ticket(id=1, status="OPEN", messaggio_originale="help"))
    store.save_ticket(
        Ticket(
            id=1,
            status="TRIAGED",
            messaggio_originale="help",
            analisi_problema="1. P. 2. C. 3. IT. 4. HIGH.",
            categoria="IT",
            priorita="HIGH",
            riassunto_breve="Email bloccata",
            team="team_tecnico",
        )
    )
    current = store.get_current_ticket(1)
    assert current["status"] == "TRIAGED"
    assert current["team"] == "team_tecnico"
