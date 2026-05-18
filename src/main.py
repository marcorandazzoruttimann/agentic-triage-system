from client import call_llm
from parsing.parser import parse_llm_output
from prompts.triage_v1 import build_prompt
from schemas.ticket import Ticket
from storage.store import next_ticket_id, save_ticket
from tools.enrichment import enrich_priority
from tools.logger import log_event
from tools.router import assign_to_team


def process_ticket(user_input: str) -> Ticket | None:
    """
    Pipeline Parte 1 + Parte 2:

    1. Ricezione ticket
    2. Assegnazione ID + save OPEN
    3. Chiamata LLM + parsing/validazione
    4. Enrichment deterministico
    5. Stato TRIAGED + save
    6. Routing team
    7. Logging
    """

    try:
        log_event("ticket_received", {"input": user_input})

        # 2. ID + OPEN
        ticket = Ticket(
            id=next_ticket_id(),
            status="OPEN",
            messaggio_originale=user_input,
        )
        save_ticket(ticket)
        log_event("ticket_saved", {"ticket": ticket.model_dump(), "phase": "open"})

        # 3. LLM + parsing
        prompt = build_prompt(user_input)
        raw_output = call_llm(prompt)
        log_event("llm_raw_response", {"response": raw_output})

        triage = parse_llm_output(raw_output)
        ticket = ticket.model_copy(
            update={
                "categoria": triage.categoria,
                "priorita": triage.priorita,
                "riassunto_breve": triage.riassunto_breve,
                "messaggio_originale": triage.messaggio_originale,
            }
        )

        # 4. Enrichment
        ticket = enrich_priority(ticket)
        log_event("ticket_enriched", {"ticket": ticket.model_dump()})

        # 5. TRIAGED + save
        ticket = ticket.model_copy(update={"status": "TRIAGED"})
        save_ticket(ticket)
        log_event("ticket_saved", {"ticket": ticket.model_dump(), "phase": "triaged"})

        # 6. Routing
        ticket = assign_to_team(ticket)
        log_event("ticket_routed", {"ticket": ticket.model_dump()})

        log_event("ticket_processed", {"ticket": ticket.model_dump()})

        print("\n=== TICKET PROCESSATO ===")
        print(ticket.model_dump())
        return ticket

    except Exception as e:
        log_event("error", {"message": str(e), "input": user_input})
        print("\n[ERRORE]", str(e))
        return None


def run_tests():
    """Esegue i 4 scenari obbligatori del progetto."""
    test_cases = [
        # Scenario A — IT (Urgente)
        "Non riesco ad accedere alla mia email, è bloccata",

        # Scenario B — Business
        "Ho effettuato un bonifico, potete confermare?",

        # Scenario C — Security
        "Guadagna 5000 euro al mese con Bitcoin!!!",

        # Scenario D — Ambiguo
        "Vorrei comprare il corso ma il sito non carica la pagina di pagamento",
    ]

    for i, test in enumerate(test_cases, start=1):
        print(f"\n\n--- SCENARIO {i} ---")
        process_ticket(test)


if __name__ == "__main__":
    run_tests()
