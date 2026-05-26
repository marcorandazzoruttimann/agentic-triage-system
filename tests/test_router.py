import pytest

from tools.router import assign_to_team


@pytest.mark.parametrize(
    ("categoria", "team"),
    [
        ("IT", "team_tecnico"),
        ("BILLING", "amministrazione"),
        ("SALES", "commerciale"),
        ("SECURITY", "sicurezza"),
    ],
)
def test_assign_to_team(triaged_ticket, categoria, team):
    routed = assign_to_team(triaged_ticket(categoria=categoria))
    assert routed.team == team
