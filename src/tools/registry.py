from tools.office_tools import notify_manager, search_policy

# Associazione tra stringa inviata dall'LLM e funzione Python reale
TOOL_MAP = {
    "notify_manager": notify_manager,
    "search_policy": search_policy
}

# Definizione delle Capabilities inviate all'API
TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "notify_manager",
            "description": (
                "Invia escalation immediata al manager di turno. Obbligatorio per "
                "richieste SALES con budget dichiarato superiore a 10.000€, o sentiment "
                "ARRABBIATO. Usare priority 3-4 per progetti VIP/Enterprise."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Il messaggio di sintesi del problema da inviare al manager."
                    },
                    "priority": {
                        "type": "integer",
                        "description": "Livello di urgenza da 1 (basso) a 4 (critico)."
                    }
                },
                "required": ["message", "priority"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_policy",
            "description": (
                "Cerca in data/policy.txt: sconti, budget, rimborsi, escalation, sentiment ARRABBIATO. "
                "Usare per dubbi commerciali o prima di notify_manager su casi critici."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "La chiave di ricerca (es. 'regole sconti', 'termini rimborso')."
                    }
                },
                "required": ["query"]
            }
        }
    }
]
