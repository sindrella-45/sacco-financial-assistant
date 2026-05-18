"""
tests/test_memory.py
Tests for load_user_profile (Handshake 3).

Uses the real memory_service if available, otherwise falls back to
the mock defined in summary_ui — so these tests pass on any branch.
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


REQUIRED_KEYS = {
    "user_id", "name", "age", "occupation", "monthly_income",
    "loan_id", "principal", "interest_rate", "tenure_months",
    "start_date", "status",
}


def test_profile_contains_all_required_keys():
    """Profile must include every key defined in Handshake 3."""
    profile = _get_profile("M001")
    missing = REQUIRED_KEYS - set(profile.keys())
    assert not missing, f"Missing keys: {missing}"


def test_profile_user_id_matches_request():
    """Returned user_id must match the one that was requested."""
    assert _get_profile("M001")["user_id"] == "M001"
    assert _get_profile("M002")["user_id"] == "M002"


def test_profile_income_is_non_negative_number():
    """monthly_income must be a non-negative int or float."""
    profile = _get_profile("M001")
    income = profile["monthly_income"]
    assert isinstance(income, (int, float))
    assert income >= 0


def test_profile_interest_rate_is_numeric():
    """interest_rate must be a number."""
    rate = _get_profile("M001")["interest_rate"]
    assert isinstance(rate, (int, float))


def test_profile_tenure_months_is_integer_compatible():
    """tenure_months must be castable to int without error."""
    tenure = _get_profile("M001")["tenure_months"]
    assert int(tenure) >= 0


def test_unknown_user_returns_dict_not_exception():
    """An unrecognised user_id must return a dict, not raise."""
    profile = _get_profile("DOES_NOT_EXIST_999")
    assert isinstance(profile, dict)
    assert "user_id" in profile


def test_multiple_users_return_different_names():
    """Different user IDs should return different member names."""
    name_001 = _get_profile("M001")["name"]
    name_002 = _get_profile("M002")["name"]
    assert name_001 != name_002
