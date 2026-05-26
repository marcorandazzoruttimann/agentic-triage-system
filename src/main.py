from paths import MANUALE_IT_PATH
from logic import triage_message
from schemas.ticket import Ticket
from storage.store import next_ticket_id, save_ticket
from tools.enrichment import enrich_priority
from tools.logger import log_event
from tools.router import assign_to_team


def load_it_manual() -> str:
    """Carica il manuale IT; solleva FileNotFoundError se assente."""
    return MANUALE_IT_PATH.read_text(encoding="utf-8")


def process_ticket(user_input: str) -> Ticket | None:
    """
    Orchestrazione ticket: persistenza, triage agentico, enrichment, routing.
    """
    try:
        log_event("ticket_received", {"input": user_input})

        ticket = Ticket(
            id=next_ticket_id(),
            status="OPEN",
            messaggio_originale=user_input,
        )
        save_ticket(ticket)
        log_event("ticket_saved", {"ticket": ticket.model_dump(), "phase": "open"})

        manuale = load_it_manual()
        triage = triage_message(user_input, manuale)
        log_event("triage_cot", {"analisi_problema": triage.analisi_problema})

        ticket = ticket.model_copy(
            update={
                "analisi_problema": triage.analisi_problema,
                "categoria": triage.categoria,
                "priorita": triage.priorita,
                "riassunto_breve": triage.riassunto_breve,
            }
        )

        ticket = enrich_priority(ticket)
        log_event("ticket_enriched", {"ticket": ticket.model_dump()})

        ticket = ticket.model_copy(update={"status": "TRIAGED"})
        save_ticket(ticket)
        log_event("ticket_saved", {"ticket": ticket.model_dump(), "phase": "triaged"})

        ticket = assign_to_team(ticket)
        save_ticket(ticket)
        log_event("ticket_saved", {"ticket": ticket.model_dump(), "phase": "routed"})
        log_event("ticket_processed", {"ticket": ticket.model_dump()})

        print("\n=== TICKET PROCESSATO ===")
        print(ticket.model_dump())
        return ticket

    except (FileNotFoundError, ValueError, OSError) as e:
        log_event("error", {"message": str(e), "input": user_input})
        print("\n[ERRORE]", str(e))
        return None


VPN_STUDENT_TICKET = (
    "Ciao, non riesco a collegarmi da casa alla rete aziendale, "
    "mi dà errore di connessione."
)

AMBIGUOUS_RAG_TICKET = (
    "Vorrei acquistare il corso online ma il sito non carica "
    "la pagina di pagamento, potete aiutarmi?"
)

DISCOUNT_POLICY_TICKET = (
    "Salve, sono Marco. Volevo sapere se per l'acquisto di un corso aziendale "
    "è previsto uno sconto sul budget."
)

VIP_ESCALATION_TICKET = (
    "Salve, sono l'Ing. Rossi di ACME Srl. Il consiglio ha approvato 15.500€ "
    "per il rollout della piattaforma cloud e chiediamo un incontro entro 48 ore "
    "con un referente commerciale senior."
)

# Scenario H: budget standard sotto 10k (no escalation manager)
STANDARD_BUDGET_TICKET = (
    "Buongiorno, siamo la società Verdi & Partners. Disponiamo di 7.500 euro per un "
    "corso Scrum Master certificato e vorremmo un preventivo entro la settimana."
)

# Scenario I: sentiment ARRABBIATO (policy §3.1) → search_policy + notify_manager
ANGRY_SENTIMENT_TICKET = (
    "SONO ESTREMAMENTE DELUSO! Il vostro portale è IN DOWN da 3 settimane e ho perso "
    "oltre 20.000 euro di fatturato per colpa vostra. È INACCETTABILE! "
    "Se non risolvete entro oggi contatterò il mio AVVOCATO e vi denuncio!"
)

DEMO_SCENARIOS: list[tuple[str, str]] = [
    (
        "A — IT (accesso email)",
        "Non riesco più ad accedere alla casella aziendale, risulta bloccata",
    ),
    (
        "B — BILLING (pagamento)",
        "Ho fatto un bonifico la settimana scorsa, avete ricevuto il pagamento?",
    ),
    (
        "C — SECURITY (spam)",
        "Investi in crypto e guadagni migliaia di euro! Clicca subito per info!!!",
    ),
    ("D — IT / VPN (ticket studente)", VPN_STUDENT_TICKET),
    ("E — Ambiguo (SALES vs IT, RAG)", AMBIGUOUS_RAG_TICKET),
    ("F — SALES / policy RAG (sconto)", DISCOUNT_POLICY_TICKET),
    ("G — SALES VIP / escalation (>10k)", VIP_ESCALATION_TICKET),
    ("H — SALES standard (budget <10k)", STANDARD_BUDGET_TICKET),
    ("I — Sentiment ARRABBIATO (policy + escalation)", ANGRY_SENTIMENT_TICKET),
]


def run_demo_scenarios() -> None:
    """Esegue i 9 scenari di valutazione (RAG, policy, escalation o meno)."""
    for label, message in DEMO_SCENARIOS:
        print(f"\n\n--- SCENARIO {label} ---")
        process_ticket(message)


if __name__ == "__main__":
    run_demo_scenarios()
