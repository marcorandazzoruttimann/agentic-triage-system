"""
Nucleo del loop agentico (logic.py).

1. Riceve l'input utente e costruisce i messaggi chat (prompt + few-shot + manuale IT).
2. Passa le definizioni dei tool all'LLM (TOOLS_DEFINITION, tool_choice=auto).
3. Intercetta le tool_calls nella risposta ed esegue le funzioni localmente (TOOL_MAP).
4. Applica eventuali guardie policy (fallback VIP / sentiment ARRABBIATO) con observation in contesto.
5. Ri-sottomette il contesto aggiornato all'LLM per ottenere il JSON finale, poi valida con Pydantic.
"""

import json
import re
from typing import Any

from client import MODEL, get_client
from parsing.parser import parse_llm_output
from prompts.triage_v1 import build_chat_messages
from schemas.ticket import TriageResult
from tools.registry import TOOL_MAP, TOOLS_DEFINITION

# --- Policy guards (euristiche allineate a data/policy.txt) ---

_VIP_BUDGET_THRESHOLD = 10_000
_BUDGET_PATTERN = re.compile(
    r"(\d{1,3}(?:\.\d{3})+|\d+)\s*(?:€|euro)",
    re.IGNORECASE,
)

_ANGRY_LEGAL_TERMS = (
    "avvocato",
    "denuncio",
    "querela",
    "tribunale",
    "azione legale",
    "legali",
)
_ANGRY_INSULT_TERMS = (
    "inaccettabile",
    "furioso",
    "schifo",
    "vergogn",
    "incapaci",
    "deluso",
    "pessimo servizio",
)


def _parse_budget_amount(raw: str) -> int:
    return int(raw.replace(".", "").replace(",", ""))


def _extract_max_budget_eur(text: str) -> int | None:
    amounts = [_parse_budget_amount(m.group(1)) for m in _BUDGET_PATTERN.finditer(text)]
    return max(amounts) if amounts else None


def _requires_vip_escalation(text: str) -> bool:
    max_budget = _extract_max_budget_eur(text)
    return max_budget is not None and max_budget > _VIP_BUDGET_THRESHOLD


def _detects_angry_sentiment(text: str) -> bool:
    """Euristica allineata a policy.txt §3.1 (legali, caps, perdite finanziarie)."""
    lower = text.lower()
    legal = any(term in lower for term in _ANGRY_LEGAL_TERMS)
    insult = any(term in lower for term in _ANGRY_INSULT_TERMS)
    caps_words = sum(
        1 for word in text.split() if len(word) > 3 and word.isalpha() and word.isupper()
    )
    caps = caps_words >= 2
    financial = any(term in lower for term in ("perso", "perdita", "perdite", "fatturato", "danni"))
    financial = financial and bool(re.search(r"\d", text))
    return sum([legal, insult, caps, financial]) >= 2


def _policy_fallback_needed(user_input: str, tools_called: set[str]) -> bool:
    if "notify_manager" in tools_called:
        return False
    return _requires_vip_escalation(user_input) or _detects_angry_sentiment(user_input)


# --- Agent loop ---


def _call_llm_with_tools(client: Any, messages: list[dict[str, Any]]) -> Any:
    """Prima chiamata LLM con capabilities tool."""
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=messages,
        tools=TOOLS_DEFINITION,
        tool_choice="auto",
    )
    return response.choices[0].message


def _execute_tool_calls(conversation: list[Any], tool_calls: Any) -> set[str]:
    """Esegue tool_calls dell'LLM e appende messaggi role=tool alla conversazione."""
    tools_called: set[str] = set()
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        tools_called.add(function_name)
        function_args = json.loads(tool_call.function.arguments)
        tool_output = TOOL_MAP[function_name](**function_args)
        conversation.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": tool_output,
            }
        )
    return tools_called


def _apply_policy_fallback(
    user_input: str,
    conversation: list[Any],
    tools_called: set[str],
    *,
    first_assistant: Any | None = None,
) -> bool:
    """
    Fallback deterministico: esegue tool mancanti e appende observation alla conversazione.
    Ritorna True se sono stati invocati nuovi tool (serve seconda chiamata JSON).
    """
    if not _policy_fallback_needed(user_input, tools_called):
        return False

    needs_vip = _requires_vip_escalation(user_input)
    needs_angry = _detects_angry_sentiment(user_input)

    pending: list[tuple[str, dict[str, Any], str]] = []

    if needs_angry and "search_policy" not in tools_called:
        pending.append(
            (
                "search_policy",
                {"query": "sentiment ARRABBIATO escalation critica"},
                "fallback-sp-1",
            )
        )

    if "notify_manager" not in tools_called:
        if needs_vip:
            budget = _extract_max_budget_eur(user_input)
            message = (
                f"Escalation VIP automatica: budget {budget}€ (>10.000€). "
                f"Sintesi: {user_input[:250]}"
            )
            reason = "Escalation VIP applicata da policy (fallback deterministico)."
        else:
            message = (
                f"Escalation sentiment ARRABBIATO (policy §3.1). "
                f"Sintesi: {user_input[:250]}"
            )
            reason = (
                "Escalation sentiment ARRABBIATO applicata da policy (fallback deterministico)."
            )
        pending.append(
            ("notify_manager", {"message": message, "priority": 4}, "fallback-nm-1")
        )

    if not pending:
        return False

    if first_assistant is not None:
        conversation.append(first_assistant)

    conversation.append(
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": tool_id,
                    "type": "function",
                    "function": {
                        "name": name,
                        "arguments": json.dumps(args, ensure_ascii=False),
                    },
                }
                for name, args, tool_id in pending
            ],
        }
    )

    for name, args, tool_id in pending:
        tools_called.add(name)
        tool_output = TOOL_MAP[name](**args)
        conversation.append(
            {
                "role": "tool",
                "tool_call_id": tool_id,
                "name": name,
                "content": tool_output,
            }
        )
        if name == "search_policy":
            print(
                "[AGENTE] Policy consultata per sentiment ARRABBIATO (fallback deterministico).",
                flush=True,
            )

    print(f"[AGENTE] {reason}", flush=True)
    return True


def _request_final_json(client: Any, conversation: list[Any]) -> str:
    """Seconda chiamata LLM: contesto con observation → JSON strutturato."""
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=conversation,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content
    if not content:
        raise ValueError("Risposta vuota dal modello")
    return content.strip()


def _run_agent_loop(messages: list[dict[str, Any]], user_input: str) -> str:
    """
    Loop agentico: LLM + tool locali + fallback policy + ri-sottomissione per JSON finale.
    """
    client = get_client()
    response_message = _call_llm_with_tools(client, messages)
    tool_calls = response_message.tool_calls
    tools_called: set[str] = set()
    conversation: list[Any] = list(messages)

    if tool_calls:
        print("\n[AGENTE] Attivazione tool in corso...")
        conversation.append(response_message)
        tools_called = _execute_tool_calls(conversation, tool_calls)
        _apply_policy_fallback(user_input, conversation, tools_called)
        return _request_final_json(client, conversation)

    fallback_ran = _apply_policy_fallback(
        user_input,
        conversation,
        tools_called,
        first_assistant=response_message,
    )
    if fallback_ran:
        return _request_final_json(client, conversation)

    content = response_message.content
    if not content:
        raise ValueError("Risposta vuota dal modello")
    return content.strip()


def triage_message(user_input: str, manuale: str) -> TriageResult:
    """Entry point: build messaggi → loop agentico → parse TriageResult."""
    messages = build_chat_messages(user_input, manuale)
    raw_output = _run_agent_loop(messages, user_input)
    return parse_llm_output(raw_output)
