"""
app/utils/constants.py
========================
Shared constants used across the UI layer.
Import from here rather than hardcoding values in UI files.
"""

# ── Budget Framework (50 / 20 / 20 / 10) ─────────────────────────────────────
BUDGET_NEEDS_PCT    = 0.50   # rent, food, transport, school fees
BUDGET_LOAN_PCT     = 0.20   # loan repayment
BUDGET_SAVINGS_PCT  = 0.20   # savings
BUDGET_PERSONAL_PCT = 0.10   # personal / other

# Warn the user if their loan repayment exceeds this share of income
LOAN_REPAYMENT_WARNING_PCT = 0.20

# ── Currency ──────────────────────────────────────────────────────────────────
CURRENCY        = "UGX"
CURRENCY_SYMBOL = "UGX "

# ── App Info ──────────────────────────────────────────────────────────────────
APP_TITLE = "SACCO Financial Assistant"

# ── Demo Member IDs (used in UI dropdowns before CSV is loaded) ───────────────
DEMO_USER_IDS = ["M001", "M002", "M003", "M004", "M005"]
