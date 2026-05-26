import pytest

from schemas.ticket import Ticket
from tools.enrichment import enrich_priority


def test_urgente_raises_to_high(triaged_ticket):
    ticket = triaged_ticket(priorita="LOW", messaggio="È urgente, email bloccata")
    assert enrich_priority(ticket).priorita == "HIGH"


def test_enrich_without_priorita_raises():
    ticket = Ticket(id=1, status="OPEN", messaggio_originale="x", categoria="IT")
    with pytest.raises(ValueError, match="priorità"):
        enrich_priority(ticket)
