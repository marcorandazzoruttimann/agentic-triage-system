import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from schemas.ticket import Ticket
from tools.enrichment import enrich_priority


def _triaged(priorita: str, message: str) -> Ticket:
    return Ticket(
        id=1,
        status="TRIAGED",
        messaggio_originale=message,
        categoria="IT",
        priorita=priorita,
        riassunto_breve="test breve",
    )


def test_urgente_raises_to_high():
    ticket = _triaged("LOW", "È urgente, la mia email è bloccata")
    assert enrich_priority(ticket).priorita == "HIGH"


def test_bloccato_raises_to_high():
    ticket = _triaged("MEDIUM", "Account bloccato")
    assert enrich_priority(ticket).priorita == "HIGH"


def test_subito_raises_to_at_least_medium():
    ticket = _triaged("LOW", "Serve subito una risposta")
    assert enrich_priority(ticket).priorita == "MEDIUM"


def test_non_funziona_raises_to_at_least_medium():
    ticket = _triaged("LOW", "Il portale non funziona")
    assert enrich_priority(ticket).priorita == "MEDIUM"
