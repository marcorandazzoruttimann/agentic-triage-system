"""
Prompt v1 per il sistema di Customer Care Triage.
Contiene:
- system prompt (istruzioni principali)
- few-shot examples (guida comportamentale)
"""


SYSTEM_PROMPT = """
Sei un Customer Care Triage Agent.

Il tuo compito è analizzare un messaggio utente e restituire ESCLUSIVAMENTE un oggetto JSON valido.

Devi classificare il ticket secondo:
- categoria
- priorita
- riassunto_breve
- messaggio_originale

REGOLE OBBLIGATORIE:

1. Output SOLO JSON valido
2. Nessun testo prima o dopo il JSON
3. Nessuna spiegazione
4. Nessun commento
5. Nessun blocco markdown (no ```json)

SCHEMA JSON:

{
  "categoria": "IT | BILLING | SALES | SECURITY",
  "priorita": "LOW | MEDIUM | HIGH | CRITICAL",
  "riassunto_breve": "max 15 parole",
  "messaggio_originale": "testo originale utente"
}

LINEE GUIDA:

- IT → problemi tecnici (accessi, errori, sistemi)
- BILLING → pagamenti, fatture, bonifici
- SALES → acquisti, informazioni commerciali
- SECURITY → spam, phishing, contenuti sospetti

PRIORITÀ:

- CRITICAL → blocco totale / sistema inutilizzabile
- HIGH → problema serio ma non totale
- MEDIUM → richiesta standard
- LOW → spam o richieste non urgenti

Il campo "riassunto_breve" deve:
- essere conciso
- massimo 15 parole
- descrivere il problema principale

Il campo "messaggio_originale" deve essere IDENTICO all'input.
"""


# Few-shot examples (fondamentali per stabilizzare l'output)
FEW_SHOTS = [
    {
        "input": "Non riesco ad accedere alla mia email, è completamente bloccata",
        "output": {
            "categoria": "IT",
            "priorita": "HIGH",
            "riassunto_breve": "Accesso email bloccato per utente",
            "messaggio_originale": "Non riesco ad accedere alla mia email, è completamente bloccata"
        }
    },
    {
        "input": "Ho effettuato un bonifico ieri, potete confermare la ricezione?",
        "output": {
            "categoria": "BILLING",
            "priorita": "MEDIUM",
            "riassunto_breve": "Richiesta conferma bonifico effettuato",
            "messaggio_originale": "Ho effettuato un bonifico ieri, potete confermare la ricezione?"
        }
    },
    {
        "input": "Guadagna 5000 euro al mese con Bitcoin!!! Clicca subito!!!",
        "output": {
            "categoria": "SECURITY",
            "priorita": "LOW",
            "riassunto_breve": "Messaggio spam promozione Bitcoin",
            "messaggio_originale": "Guadagna 5000 euro al mese con Bitcoin!!! Clicca subito!!!"
        }
    }
]


def build_prompt(user_input: str) -> str:
    """
    Costruisce il prompt completo da inviare al modello.
    Include:
    - system prompt
    - esempi few-shot
    - input reale
    """

    prompt = SYSTEM_PROMPT.strip() + "\n\n"

    prompt += "ESEMPI:\n\n"

    for example in FEW_SHOTS:
        prompt += f"Input:\n{example['input']}\n"
        prompt += f"Output:\n{example['output']}\n\n"

    prompt += "Ora analizza il seguente input:\n"
    prompt += f"{user_input}\n\n"
    prompt += "Output:\n"

    return prompt