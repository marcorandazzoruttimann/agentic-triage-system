import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from schemas.ticket import Ticket
from tools.router import assign_to_team


def test_assign_to_team_it():
    ticket = Ticket(
        id=1,
        status="TRIAGED",
        messaggio_originale="x",
        categoria="IT",
        priorita="HIGH",
        riassunto_breve="test",
    )
    routed = assign_to_team(ticket)
    assert routed.team == "team_tecnico"


def test_assign_to_team_billing():
    ticket = Ticket(
        id=2,
        status="TRIAGED",
        messaggio_originale="x",
        categoria="BILLING",
        priorita="MEDIUM",
        riassunto_breve="test",
    )
    assert assign_to_team(ticket).team == "amministrazione"
