from paths import POLICY_PATH
from tools.logger import log_event


def notify_manager(message: str, priority: int) -> str:
    """
    Invia una notifica di escalation immediata al manager di turno.
    USARE QUESTO TOOL se la richiesta è SALES con budget superiore a 10.000€,
    oppure se il sentiment rilevato è 'ARRABBIATO'.
    """
    print(
        f"\n🚨 [ESCALATION LIVE] Notifica inviata al Manager "
        f"(Priorità {priority}): {message}",
        flush=True,
    )
    log_event(
        "manager_escalation",
        {"message": message, "priority": priority},
    )
    return "Notifica di escalation inviata con successo al manager di turno."


def search_policy(query: str) -> str:
    """
    Effettua una ricerca all'interno delle policy aziendali e dei manuali interni di Impesud.
    USARE QUESTO TOOL quando il ticket richiede verifiche su sconti, rimborsi,
    termini di servizio o procedure.
    """
    if POLICY_PATH.exists():
        content = POLICY_PATH.read_text(encoding="utf-8")
        query_lower = query.lower()
        if any(
            term in query_lower
            for term in ("sentiment", "arrabbiato", "escalation", "critica", "insult")
        ):
            sentiment_lines = [
                line
                for line in content.split("\n")
                if any(
                    marker in line.lower()
                    for marker in ("sentiment", "arrabbiato", "notify_manager", "escalation")
                )
            ]
            if sentiment_lines:
                return "\n".join(sentiment_lines[:6])

        relevant_lines = [
            line
            for line in content.split("\n")
            if any(word in line.lower() for word in query_lower.split())
        ]
        if relevant_lines:
            return "\n".join(relevant_lines[:5])
        return (
            "Policy trovata ma nessun paragrafo specifico corrisponde alla query. "
            "Seguire gli standard generali Impesud."
        )

    query_lower = query.lower()
    if "sconto" in query_lower or "budget" in query_lower:
        return (
            "Policy Impesud: I progetti commerciali con budget superiore a 10k "
            "hanno diritto a uno sconto massimo del 5%."
        )
    if "rimborso" in query_lower:
        return (
            "Policy Impesud: I rimborsi tecnici possono essere approvati solo "
            "entro 14 giorni dall'attivazione del servizio."
        )

    return "Policy generale: Gestire la richiesta secondo gli standard di qualità Impesud."
