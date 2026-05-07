from client import call_llm
from prompts.triage_v1 import build_prompt
from parsing.parser import parse_llm_output
from tools.logger import log_event


def process_ticket(user_input: str):
    """
    Pipeline completa di gestione ticket (Parte 1):

    1. Log input
    2. Costruzione prompt
    3. Chiamata LLM
    4. Parsing output
    5. Validazione schema (Pydantic)
    6. Log risultato
    """

    try:
        # 1. Log input
        log_event("ticket_received", {"input": user_input})

        # 2. Costruzione prompt
        prompt = build_prompt(user_input)

        # 3. Chiamata LLM
        raw_output = call_llm(prompt)

        log_event("llm_raw_response", {"response": raw_output})

        # 4. Parsing + validazione
        ticket = parse_llm_output(raw_output)

        # 5. Log risultato strutturato
        log_event("ticket_processed", {"ticket": ticket.model_dump()})

        # 6. Output finale
        print("\n=== TICKET PROCESSATO ===")
        print(ticket.model_dump())

    except Exception as e:
        log_event("error", {"message": str(e), "input": user_input})
        print("\n[ERRORE]", str(e))


def run_tests():
    """
    Esegue i 4 scenari obbligatori del progetto.
    """

    test_cases = [
        # Scenario A — IT (Urgente)
        "Non riesco ad accedere alla mia email, è bloccata",

        # Scenario B — Business
        "Ho effettuato un bonifico, potete confermare?",

        # Scenario C — Security
        "Guadagna 5000 euro al mese con Bitcoin!!!",

        # Scenario D — Ambiguo
        "Vorrei comprare il corso ma il sito non carica la pagina di pagamento"
    ]

    for i, test in enumerate(test_cases, start=1):
        print(f"\n\n--- SCENARIO {i} ---")
        process_ticket(test)


if __name__ == "__main__":
    run_tests()