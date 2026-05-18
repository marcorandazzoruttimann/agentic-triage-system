import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from parsing.parser import parse_llm_output


def test_parse_llm_output_valid():
    raw = (
        '{"categoria":"BILLING","priorita":"MEDIUM",'
        '"riassunto_breve":"Conferma bonifico",'
        '"messaggio_originale":"Ho effettuato un bonifico"}'
    )
    result = parse_llm_output(raw)
    assert result.categoria == "BILLING"
