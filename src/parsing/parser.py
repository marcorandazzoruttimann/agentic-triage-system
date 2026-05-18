import json
import re
from typing import Any, Dict

from schemas.ticket import TriageResult


def _extract_json_block(text: str) -> str:
    """
    Estrae il primo blocco JSON valido da una stringa.
    Gestisce:
    - testo extra prima/dopo
    - blocchi markdown ```json
    """

    # Rimuove eventuali blocchi markdown ```json ... ```
    text = re.sub(r"```json|```", "", text, flags=re.IGNORECASE).strip()

    # Cerca il primo blocco JSON (da { a })
    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        raise ValueError("Nessun JSON trovato nella risposta del modello")

    return match.group(0)


def _safe_json_load(json_str: str) -> Dict[str, Any]:
    """
    Converte una stringa JSON in dict con gestione errori.
    """

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON non valido: {e}")


def parse_llm_output(raw_output: str) -> TriageResult:
    """
    Pipeline completa di parsing:

    1. Estrazione JSON
    2. Parsing stringa → dict
    3. Validazione con Pydantic

    Restituisce:
    - oggetto TriageResult valido

    Solleva errore se:
    - JSON non trovato
    - JSON invalido
    - schema non rispettato
    """

    # 1. Estrai JSON
    json_str = _extract_json_block(raw_output)

    # 2. Converti in dict
    data = _safe_json_load(json_str)

    # 3. Validazione schema
    try:
        result = TriageResult(**data)
    except Exception as e:
        raise ValueError(f"Errore validazione TriageResult: {e}")

    return result