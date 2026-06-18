"""
tests/test_budget.py
Tests for budget framework calculations and warning thresholds.
"""

import pytest

from app.utils.helpers import pct_of, pct_share
from app.utils.constants import (
    BUDGET_NEEDS_PCT,
    BUDGET_LOAN_PCT,
    BUDGET_SAVINGS_PCT,
    BUDGET_PERSONAL_PCT,
    LOAN_REPAYMENT_WARNING_PCT,
)


def test_budget_framework_sums_to_one():
    """50 + 20 + 20 + 10 must equal 100 %."""
    total = BUDGET_NEEDS_PCT + BUDGET_LOAN_PCT + BUDGET_SAVINGS_PCT + BUDGET_PERSONAL_PCT
    assert abs(total - 1.0) < 1e-9


def test_pct_of_needs_target():
    """50 % of UGX 850,000 = UGX 425,000."""
    assert pct_of(850_000, BUDGET_NEEDS_PCT) == 425_000.0


def test_pct_of_loan_target():
    """20 % of UGX 850,000 = UGX 170,000."""
    assert pct_of(850_000, BUDGET_LOAN_PCT) == 170_000.0


def test_pct_of_savings_target():
    """20 % of UGX 850,000 = UGX 170,000."""
    assert pct_of(850_000, BUDGET_SAVINGS_PCT) == 170_000.0


def test_pct_of_personal_target():
    """10 % of UGX 850,000 = UGX 85,000."""
    assert pct_of(850_000, BUDGET_PERSONAL_PCT) == 85_000.0


def test_pct_of_zero_income():
    """Any percentage of 0 income returns 0."""
    for pct in [BUDGET_NEEDS_PCT, BUDGET_LOAN_PCT, BUDGET_SAVINGS_PCT, BUDGET_PERSONAL_PCT]:
        assert pct_of(0, pct) == 0.0


def test_pct_share_exact_20_percent():
    """UGX 170,000 repayment on UGX 850,000 income = exactly 20 %."""
    assert pct_share(170_000, 850_000) == 0.2


def test_pct_share_zero_total():
    """Division by zero total returns 0.0 safely."""
    assert pct_share(100_000, 0) == 0.0


def test_loan_repayment_triggers_warning():
    """Repayment > 20 % of income should exceed the warning threshold."""
    income = 850_000
    high_repayment = 200_000          # ≈ 23.5 %
    assert pct_share(high_repayment, income) > LOAN_REPAYMENT_WARNING_PCT


def test_loan_repayment_within_safe_limit():
    """Repayment exactly at 20 % should NOT exceed the warning threshold."""
    income = 850_000
    safe_repayment = 170_000          # exactly 20 %
    assert pct_share(safe_repayment, income) <= LOAN_REPAYMENT_WARNING_PCT
