# Agentic Customer Care Triage System

Sistema agentico per il triage e il processamento ticket customer care.

## Parte 1 — Triage Agent

Classificazione LLM con output JSON strutturato (`categoria`, `priorita`, `riassunto_breve`, `messaggio_originale`).

## Parte 2 — Smart Data Processing Agent

Pipeline stateful con:

- **Persistenza** — `data/tickets.jsonl` (append, ultima riga per ID = stato corrente)
- **Workflow** — `OPEN` → `TRIAGED`
- **Enrichment** — regole deterministiche sulla priorità
- **Routing** — assegnazione team per categoria

## Struttura

```
agentic-triage-system/
├── pyproject.toml
├── .env
├── data/tickets.jsonl
├── logs/activity.jsonl
└── src/
    ├── main.py
    ├── client.py
    ├── schemas/ticket.py
    ├── prompts/triage_v1.py
    ├── parsing/parser.py
    ├── tools/logger.py
    ├── tools/router.py
    ├── tools/enrichment.py
    └── storage/store.py
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
```

Imposta `OPENAI_API_KEY` in `.env`.

## Esecuzione

```bash
PYTHONPATH=src python src/main.py
```

## Test

```bash
PYTHONPATH=src pytest tests/ -q
```
