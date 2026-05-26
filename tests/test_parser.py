import pytest

from parsing.parser import parse_llm_output


def test_parse_llm_output_valid():
    raw = (
        '{"analisi_problema":"1. Problema: bonifico. 2. C. 3. BILLING. 4. MEDIUM.",'
        '"categoria":"BILLING","priorita":"MEDIUM",'
        '"riassunto_breve":"Conferma bonifico",'
        '"messaggio_originale":"Ho effettuato un bonifico"}'
    )
    result = parse_llm_output(raw)
    assert result.categoria == "BILLING"


def test_parse_llm_output_missing_json_raises():
    with pytest.raises(ValueError, match="Nessun JSON"):
        parse_llm_output("risposta senza json")
