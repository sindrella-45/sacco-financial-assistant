"""
tests/test_loans.py
Tests for loan calculation helpers (monthly EMI, total interest).
"""

import pytest

from app.utils.helpers import monthly_repayment, total_interest


def test_monthly_repayment_standard():
    """UGX 2M at 15 % p.a. over 12 months ≈ UGX 180,517."""
    emi = monthly_repayment(2_000_000, 15.0, 12)
    assert 175_000 < emi < 186_000, f"Expected ~180,517, got {emi}"


def test_monthly_repayment_zero_rate():
    """Zero interest — should divide principal evenly across months."""
    emi = monthly_repayment(1_200_000, 0, 12)
    assert emi == 100_000.0


def test_monthly_repayment_zero_tenure():
    """Zero months tenure should return 0.0 without raising."""
    assert monthly_repayment(1_000_000, 15.0, 0) == 0.0


def test_monthly_repayment_longer_tenure_is_smaller():
    """Longer tenure → smaller monthly payment for the same principal."""
    emi_12 = monthly_repayment(2_000_000, 15.0, 12)
    emi_24 = monthly_repayment(2_000_000, 15.0, 24)
    assert emi_24 < emi_12


def test_monthly_repayment_higher_rate_is_larger():
    """Higher interest rate → larger monthly payment."""
    emi_15 = monthly_repayment(2_000_000, 15.0, 12)
    emi_24 = monthly_repayment(2_000_000, 24.0, 12)
    assert emi_24 > emi_15


def test_total_interest_is_positive():
    """Total interest must be positive for a non-zero rate loan."""
    emi = monthly_repayment(2_000_000, 15.0, 12)
    interest = total_interest(2_000_000, emi, 12)
    assert interest > 0


def test_total_interest_formula():
    """total_interest = (EMI × months) − principal."""
    emi = monthly_repayment(2_000_000, 15.0, 12)
    interest = total_interest(2_000_000, emi, 12)
    assert interest == round(emi * 12 - 2_000_000, 2)


def test_total_interest_zero_rate():
    """No interest charged when annual rate is 0."""
    emi = monthly_repayment(1_200_000, 0, 12)
    interest = total_interest(1_200_000, emi, 12)
    assert interest == 0.0
