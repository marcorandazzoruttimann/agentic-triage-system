import json
from unittest.mock import MagicMock, patch

import pytest

from logic import (
    _detects_angry_sentiment,
    _extract_max_budget_eur,
    _requires_vip_escalation,
    triage_message,
)


def _completion(content=None, tool_calls=None):
    msg = MagicMock(tool_calls=tool_calls, content=content)
    resp = MagicMock()
    resp.choices = [MagicMock(message=msg)]
    return resp


def _tool_call(name: str, args: dict, call_id: str = "c1"):
    tc = MagicMock(id=call_id)
    tc.function.name = name
    tc.function.arguments = json.dumps(args)
    return tc


@patch("logic.get_client")
def test_triage_message_without_tools(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    json_out = (
        '{"analisi_problema":"1. P. 2. C. 3. IT. 4. LOW.",'
        '"categoria":"IT","priorita":"LOW","riassunto_breve":"test ok",'
        '"messaggio_originale":"help"}'
    )
    mock_client.chat.completions.create.return_value = _completion(content=json_out)

    result = triage_message("help", manuale="Manuale IT")

    assert result.categoria == "IT"
    mock_client.chat.completions.create.assert_called_once()


@patch("logic.get_client")
def test_triage_message_with_tool(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    tc = _tool_call("search_policy", {"query": "sconto"})
    final = (
        '{"analisi_problema":"1. P. 2. POLICY. 3. SALES. 4. MEDIUM.",'
        '"categoria":"SALES","priorita":"MEDIUM","riassunto_breve":"sconto",'
        '"messaggio_originale":"sconto?"}'
    )
    mock_client.chat.completions.create.side_effect = [
        _completion(tool_calls=[tc]),
        _completion(content=final),
    ]

    result = triage_message("sconto?", manuale="")

    assert result.categoria == "SALES"
    assert mock_client.chat.completions.create.call_count == 2


@patch("logic.get_client")
def test_triage_message_empty_response_raises(mock_get_client):
    mock_get_client.return_value = MagicMock(
        chat=MagicMock(
            completions=MagicMock(
                create=MagicMock(return_value=_completion(content=None))
            )
        )
    )
    with pytest.raises(ValueError, match="Risposta vuota"):
        triage_message("x", manuale="")


def test_extract_max_budget_eur():
    assert _extract_max_budget_eur("budget di 15.000€ per il progetto") == 15000
    assert _extract_max_budget_eur("budget di 8.000 euro") == 8000
    assert _extract_max_budget_eur("nessun importo") is None


def test_detects_angry_sentiment():
    angry = (
        "SONO FURIOSO! Ho perso 20.000 euro. INACCETTABILE! Vi denuncio e chiamo l'avvocato!"
    )
    calm = "Buongiorno, vorrei informazioni sul corso base."
    assert _detects_angry_sentiment(angry) is True
    assert _detects_angry_sentiment(calm) is False


def test_requires_vip_escalation_threshold():
    assert _requires_vip_escalation("abbiamo 15.000€ approvati") is True
    assert _requires_vip_escalation("budget di 8.000 euro") is False
    assert _requires_vip_escalation("budget esatto 10.000€") is False


@patch("logic.get_client")
def test_vip_escalation_fallback_when_llm_skips_tool(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    first_json = (
        '{"analisi_problema":"1. P. 2. C. 3. SALES. 4. HIGH.",'
        '"categoria":"SALES","priorita":"HIGH","riassunto_breve":"VIP",'
        '"messaggio_originale":"15k"}'
    )
    final_json = (
        '{"analisi_problema":"1. P. 2. VIP notify. 3. SALES. 4. HIGH.",'
        '"categoria":"SALES","priorita":"HIGH","riassunto_breve":"VIP",'
        '"messaggio_originale":"15k"}'
    )
    mock_client.chat.completions.create.side_effect = [
        _completion(content=first_json),
        _completion(content=final_json),
    ]

    vip_input = (
        "Buon giorno, budget approvato di 15.000€ per integrazione AI, "
        "vorremmo parlare urgentemente con un responsabile commerciale."
    )
    mock_notify = MagicMock(return_value="ok")
    with patch.dict("logic.TOOL_MAP", {"notify_manager": mock_notify}, clear=False):
        result = triage_message(vip_input, manuale="")

    assert result.categoria == "SALES"
    mock_notify.assert_called_once()
    assert mock_notify.call_args.kwargs["priority"] == 4
    assert mock_client.chat.completions.create.call_count == 2


@patch("logic.get_client")
def test_no_vip_fallback_under_threshold(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    json_out = (
        '{"analisi_problema":"1. P. 2. C. 3. SALES. 4. MEDIUM.",'
        '"categoria":"SALES","priorita":"MEDIUM","riassunto_breve":"std",'
        '"messaggio_originale":"8k"}'
    )
    mock_client.chat.completions.create.return_value = _completion(content=json_out)

    standard_input = "Abbiamo un budget di 8.000 euro per formazione Agile."
    mock_notify = MagicMock(return_value="ok")
    with patch.dict("logic.TOOL_MAP", {"notify_manager": mock_notify}, clear=False):
        triage_message(standard_input, manuale="")

    mock_notify.assert_not_called()


@patch("logic.get_client")
def test_angry_sentiment_fallback_policy_then_notify(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    first_json = (
        '{"analisi_problema":"1. P. 2. C. 3. IT. 4. CRITICAL.",'
        '"categoria":"IT","priorita":"CRITICAL","riassunto_breve":"arrabbiato",'
        '"messaggio_originale":"down"}'
    )
    final_json = (
        '{"analisi_problema":"1. P. 2. POLICY+notify. 3. IT. 4. CRITICAL.",'
        '"categoria":"IT","priorita":"CRITICAL","riassunto_breve":"arrabbiato",'
        '"messaggio_originale":"down"}'
    )
    mock_client.chat.completions.create.side_effect = [
        _completion(content=first_json),
        _completion(content=final_json),
    ]

    angry_input = (
        "SONO DELUSO! Portale IN DOWN, perso 20.000 euro. INACCETTABILE! "
        "Chiamo l'avvocato e vi denuncio!"
    )
    mock_notify = MagicMock(return_value="ok")
    mock_policy = MagicMock(return_value="Policy: sentiment ARRABBIATO → notify_manager")
    with patch.dict(
        "logic.TOOL_MAP",
        {"notify_manager": mock_notify, "search_policy": mock_policy},
        clear=False,
    ):
        triage_message(angry_input, manuale="")

    mock_policy.assert_called_once()
    mock_notify.assert_called_once()
    assert mock_client.chat.completions.create.call_count == 2


@patch("logic.get_client")
def test_fallback_appends_tool_messages_to_conversation(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_client.chat.completions.create.side_effect = [
        _completion(content='{"analisi_problema":"x","categoria":"SALES",'
        '"priorita":"HIGH","riassunto_breve":"v","messaggio_originale":"15k"}'),
        _completion(
            content='{"analisi_problema":"y","categoria":"SALES",'
            '"priorita":"HIGH","riassunto_breve":"v","messaggio_originale":"15k"}'
        ),
    ]

    vip_input = "Budget approvato di 15.000€ per progetto enterprise."
    with patch.dict(
        "logic.TOOL_MAP",
        {"notify_manager": MagicMock(return_value="ok")},
        clear=False,
    ):
        triage_message(vip_input, manuale="")

    second_call_messages = mock_client.chat.completions.create.call_args_list[1].kwargs["messages"]
    tool_messages = [m for m in second_call_messages if isinstance(m, dict) and m.get("role") == "tool"]
    assert any(m.get("name") == "notify_manager" for m in tool_messages)
    assert any(m.get("tool_call_id") == "fallback-nm-1" for m in tool_messages)
