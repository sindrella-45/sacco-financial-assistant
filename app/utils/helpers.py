"""
app/utils/helpers.py
======================
Shared formatting, parsing, and financial calculation utilities.
All functions are pure (no side effects) and safe to call from any module.
"""

from __future__ import annotations

from app.utils.constants import CURRENCY_SYMBOL


# ── Formatting ────────────────────────────────────────────────────────────────

def format_currency(amount: int | float) -> str:
    """Format a number as a UGX currency string.

    Examples:
        850000  → 'UGX 850,000'
        2000000 → 'UGX 2,000,000'
    """
    return f"{CURRENCY_SYMBOL}{int(round(amount)):,}"


def format_pct(value: float) -> str:
    """Format a fraction as a percentage string.

    Examples:
        0.50 → '50.0%'
        0.2  → '20.0%'
    """
    return f"{value * 100:.1f}%"


# ── Parsing ───────────────────────────────────────────────────────────────────

def parse_number(value: str | int | float) -> float:
    """Parse a value to float, stripping commas.  Returns 0.0 on failure.

    Examples:
        '850,000' → 850000.0
        '2000000' → 2000000.0
        ''        → 0.0
    """
    try:
        return float(str(value).replace(",", "").strip())
    except (ValueError, TypeError):
        return 0.0


# ── Percentage helpers ────────────────────────────────────────────────────────

def pct_of(amount: float, pct: float) -> float:
    """Return *pct* fraction of *amount*.

    Args:
        amount: The base value (e.g. monthly income).
        pct:    A fraction between 0 and 1 (e.g. 0.50 for 50 %).

    Returns:
        Rounded result to 2 decimal places.
    """
    return round(amount * pct, 2)


def pct_share(part: float, total: float) -> float:
    """Return what fraction *part* is of *total* (0–1 range).

    Returns 0.0 if *total* is zero.
    """
    if total == 0:
        return 0.0
    return round(part / total, 4)


# ── Loan / Financial calculations ────────────────────────────────────────────

def monthly_repayment(principal: float, annual_rate: float, months: int) -> float:
    """Calculate the monthly EMI using the reducing-balance method.

    Args:
        principal:   Loan amount in UGX.
        annual_rate: Interest rate as a percentage per annum (e.g. 15.0 for 15 %).
        months:      Loan tenure in months.

    Returns:
        Monthly payment (UGX), rounded to 2 decimal places.
        Returns 0.0 if months <= 0.
        Returns principal / months if annual_rate == 0.

    Example:
        >>> monthly_repayment(2_000_000, 15.0, 12)
        180516.9   # ≈ UGX 180,517
    """
    if months <= 0:
        return 0.0
    if annual_rate == 0:
        return round(principal / months, 2)

    r = annual_rate / 100 / 12          # monthly interest rate
    emi = principal * r * (1 + r) ** months / ((1 + r) ** months - 1)
    return round(emi, 2)


def total_interest(principal: float, monthly_payment: float, months: int) -> float:
    """Total interest paid over the full loan tenure.

    Returns:
        (monthly_payment × months) − principal, rounded to 2 dp.
    """
    return round(monthly_payment * months - principal, 2)
