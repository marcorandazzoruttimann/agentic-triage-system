from main import (
    ANGRY_SENTIMENT_TICKET,
    DEMO_SCENARIOS,
    DISCOUNT_POLICY_TICKET,
    STANDARD_BUDGET_TICKET,
    VIP_ESCALATION_TICKET,
)


def test_demo_scenarios():
    assert len(DEMO_SCENARIOS) == 9
    labels = [label for label, _ in DEMO_SCENARIOS]
    assert any("F —" in label for label in labels)
    assert any("G —" in label for label in labels)
    assert any("H —" in label for label in labels)
    assert any("I —" in label for label in labels)
    messages = [msg for _, msg in DEMO_SCENARIOS]
    assert DISCOUNT_POLICY_TICKET in messages
    assert VIP_ESCALATION_TICKET in messages
    assert STANDARD_BUDGET_TICKET in messages
    assert "7.500" in STANDARD_BUDGET_TICKET
    assert ANGRY_SENTIMENT_TICKET in messages
    assert "AVVOCATO" in ANGRY_SENTIMENT_TICKET
