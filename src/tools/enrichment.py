from schemas.ticket import Priority, Ticket

_PRIORITY_RANK: dict[Priority, int] = {
    "LOW": 0,
    "MEDIUM": 1,
    "HIGH": 2,
    "CRITICAL": 3,
}


def _max_priority(current: Priority, minimum: Priority) -> Priority:
    if _PRIORITY_RANK[current] >= _PRIORITY_RANK[minimum]:
        return current
    return minimum


def enrich_priority(ticket: Ticket) -> Ticket:
    """
    Enrichment deterministico sulla priorità (senza seconda chiamata LLM).
    - "urgente", "bloccato" → almeno HIGH
    - "subito", "non funziona" → almeno MEDIUM
    """
    if ticket.priorita is None:
        raise ValueError("Impossibile arricchire un ticket senza priorità")

    text = ticket.messaggio_originale.lower()
    priorita = ticket.priorita

    if "urgente" in text or "bloccato" in text:
        priorita = _max_priority(priorita, "HIGH")

    if "subito" in text or "non funziona" in text:
        priorita = _max_priority(priorita, "MEDIUM")

    return ticket.model_copy(update={"priorita": priorita})
