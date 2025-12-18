from business.budgets import check_budget


def test_budget():
    assert check_budget(1200, 1000) is True