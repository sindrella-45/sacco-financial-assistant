"""
tests/test_memory.py
Tests for load_user_profile (Handshake 3).

Uses the real memory_service (now available after merge).
Real service returns {} for unknown users and reads from users.csv.
Column names follow Person 2's schema:
  user_id, name, monthly_income, loan_amount, loan_term_months,
  interest_rate, savings_goal, occupation
"""

import pytest


def _get_profile(user_id: str) -> dict:
    """Import the real service or the mock transparently."""
    try:
        from app.services.memory_service import load_user_profile
        return load_user_profile(user_id)
    except ImportError:
        from app.ui.summary_ui import _mock_load_user_profile
        return _mock_load_user_profile(user_id)


# Real service keys (Person 2's schema)
REAL_SERVICE_KEYS = {
    "user_id", "name", "monthly_income", "loan_amount",
    "loan_term_months", "interest_rate", "savings_goal", "occupation",
}


def test_load_profile_returns_dict():
    """load_user_profile() must always return a dict, never raise."""
    result = _get_profile("M001")
    assert isinstance(result, dict)


def test_unknown_user_returns_dict_not_exception():
    """An unrecognised user_id must return a dict (may be empty), not raise."""
    result = _get_profile("DOES_NOT_EXIST_999")
    assert isinstance(result, dict)


def test_profile_with_data_has_expected_keys():
    """If a profile has data, it must contain the real service's column names."""
    profile = _get_profile("M001")
    if not profile:
        pytest.skip("M001 not in users.csv yet — seed data not loaded")
    missing = REAL_SERVICE_KEYS - set(profile.keys())
    assert not missing, f"Missing keys: {missing}"


def test_profile_user_id_matches_request():
    """Returned user_id must match the one requested."""
    profile = _get_profile("M001")
    if not profile:
        pytest.skip("M001 not in users.csv yet — seed data not loaded")
    assert profile["user_id"] == "M001"


def test_profile_income_is_non_negative_number():
    """monthly_income must be a non-negative number when present."""
    profile = _get_profile("M001")
    if not profile:
        pytest.skip("M001 not in users.csv yet — seed data not loaded")
    income = profile.get("monthly_income")
    if income is not None:
        assert isinstance(float(income), float)
        assert float(income) >= 0


def test_profile_interest_rate_is_numeric():
    """interest_rate must be castable to float when present."""
    profile = _get_profile("M001")
    if not profile:
        pytest.skip("M001 not in users.csv yet — seed data not loaded")
    rate = profile.get("interest_rate")
    if rate is not None:
        assert isinstance(float(rate), float)


def test_profile_tenure_months_is_integer_compatible():
    """loan_term_months must be castable to int when present."""
    profile = _get_profile("M001")
    if not profile:
        pytest.skip("M001 not in users.csv yet — seed data not loaded")
    tenure = profile.get("loan_term_months")
    if tenure is not None:
        assert int(tenure) >= 0

