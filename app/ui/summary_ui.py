"""
app/ui/summary_ui.py — Financial Summary tab (Person 3)
=========================================================
Loads a member profile and displays a combined financial overview:
  • Member details (name, income, occupation)
  • Loan status (principal, rate, EMI, total interest)
  • Budget targets (50/20/20/10 framework)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 HANDSHAKE 3  —  Person 2 → Person 3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 This file imports:
     from app.services.memory_service import load_user_profile

 Expected signature:
     load_user_profile(user_id: str) -> dict

 Required dict keys:
     user_id, name, age, occupation, monthly_income,
     loan_id, principal, interest_rate, tenure_months,
     start_date, status

 Until Person 2 delivers memory_service, _mock_load_user_profile()
 is used as a transparent fallback.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import gradio as gr

from app.utils.helpers import (
    format_currency,
    format_pct,
    monthly_repayment,
    total_interest,
    pct_share,
    pct_of,
)
from app.utils.constants import DEMO_USER_IDS, LOAN_REPAYMENT_WARNING_PCT

# ── Handshake 3: try real service, fall back to mock ──────────────────────────
try:
    from app.services.memory_service import load_user_profile as _load_profile
    _PROFILE_READY = True
except ImportError:
    _PROFILE_READY = False

# ── Demo profiles used until memory_service is available ─────────────────────
_DEMO_PROFILES = {
    "M001": {
        "user_id": "M001", "name": "Nakamya Grace",  "age": 34,
        "occupation": "Teacher",    "monthly_income": 850_000,
        "loan_id": "L001", "principal": 2_000_000, "interest_rate": 15.0,
        "tenure_months": 12, "start_date": "2024-01-15", "status": "active",
    },
    "M002": {
        "user_id": "M002", "name": "Ssemakula John", "age": 42,
        "occupation": "Farmer",     "monthly_income": 620_000,
        "loan_id": "L002", "principal": 1_500_000, "interest_rate": 18.0,
        "tenure_months": 24, "start_date": "2024-03-01", "status": "active",
    },
    "M003": {
        "user_id": "M003", "name": "Auma Patricia",  "age": 29,
        "occupation": "Shopkeeper", "monthly_income": 1_100_000,
        "loan_id": "L003", "principal": 3_000_000, "interest_rate": 15.0,
        "tenure_months": 18, "start_date": "2023-11-01", "status": "active",
    },
    "M004": {
        "user_id": "M004", "name": "Ochieng Moses",  "age": 38,
        "occupation": "Boda driver", "monthly_income": 480_000,
        "loan_id": "L004", "principal": 800_000, "interest_rate": 24.0,
        "tenure_months": 12, "start_date": "2024-06-01", "status": "active",
    },
    "M005": {
        "user_id": "M005", "name": "Nantongo Rita",  "age": 31,
        "occupation": "Tailor",     "monthly_income": 730_000,
        "loan_id": None,   "principal": 0,         "interest_rate": 0.0,
        "tenure_months": 0, "start_date": "—", "status": "none",
    },
}


def _mock_load_user_profile(user_id: str) -> dict:
    """Demo profile — used until memory_service is available."""
    return _DEMO_PROFILES.get(
        user_id,
        {
            "user_id": user_id, "name": "Unknown Member", "age": 0,
            "occupation": "—", "monthly_income": 0,
            "loan_id": "—", "principal": 0, "interest_rate": 0.0,
            "tenure_months": 0, "start_date": "—", "status": "—",
        },
    )


def _dispatch_load_profile(user_id: str) -> dict:
    if _PROFILE_READY:
        return _load_profile(user_id)
    return _mock_load_user_profile(user_id)


def build_summary_ui() -> gr.Blocks:
    """Return a gr.Blocks component for the Financial Summary tab."""

    with gr.Blocks() as summary_tab:
        gr.Markdown("## Financial Summary")
        gr.Markdown(
            "Select a member ID to view their **loan status**, "
            "**budget targets**, and overall financial health snapshot."
        )

        if not _PROFILE_READY:
            gr.Markdown(
                "> 🟡 **Demo mode** — showing sample profiles. "
                "Live profiles will load once `memory_service` is connected."
            )

        with gr.Row():
            user_id_input = gr.Dropdown(
                choices=DEMO_USER_IDS,
                value=DEMO_USER_IDS[0],
                label="Member ID",
                scale=2,
            )
            load_btn = gr.Button("Load Profile", variant="primary", scale=1)

        summary_md = gr.Markdown("*Select a Member ID and click Load Profile.*")

        def _load_summary(user_id: str) -> str:
            p = _dispatch_load_profile(user_id)

            name       = p.get("name", "—")
            age        = p.get("age", "—")
            occupation = p.get("occupation", "—")
            income     = float(p.get("monthly_income", 0) or 0)
            # Support both real service keys and mock keys
            principal  = float(p.get("loan_amount") or p.get("principal") or 0)
            rate       = float(p.get("interest_rate", 0) or 0)
            tenure     = int(p.get("loan_term_months") or p.get("tenure_months") or 0)
            start      = p.get("start_date", "—")
            status     = (p.get("status") or "—").upper()

            monthly   = monthly_repayment(principal, rate, tenure) if (principal and rate and tenure) else 0.0
            interest  = total_interest(principal, monthly, tenure) if monthly else 0.0
            repay_pct = pct_share(monthly, income) if income > 0 else 0.0

            warning_line = ""
            if income > 0 and repay_pct > LOAN_REPAYMENT_WARNING_PCT:
                warning_line = (
                    f"\n> ⚠️ **Warning:** Monthly repayment is "
                    f"**{format_pct(repay_pct)}** of income — "
                    "exceeds the recommended 20 %. Please discuss loan restructuring "
                    "with your SACCO officer.\n"
                )

            no_loan_line = ""
            if not principal:
                no_loan_line = "\n*This member has no active loan.*\n"

            md = f"""
### Member Profile

| Field | Value |
|---|---|
| Member ID | {p.get("user_id", "—")} |
| Name | {name} |
| Age | {age} |
| Occupation | {occupation} |
| Monthly Income | **{format_currency(income)}** |

### Loan Details
{no_loan_line}
| Field | Value |
|---|---|
| Loan ID | {p.get("loan_id") or "—"} |
| Principal | {format_currency(principal)} |
| Interest Rate | {rate} % p.a. |
| Tenure | {tenure} months |
| Start Date | {start} |
| Status | **{status}** |
| Monthly Repayment | **{format_currency(monthly)}** |
| Total Interest | {format_currency(interest)} |
| Total Repayable | {format_currency(monthly * tenure)} |
| Repayment / Income | {format_pct(repay_pct)} |
{warning_line}
### Budget Targets (50 / 20 / 20 / 10)

| Category | Target % | Target Amount |
|---|---|---|
| Needs (rent, food, transport, fees) | 50 % | {format_currency(pct_of(income, 0.50))} |
| Loan Repayment | 20 % | {format_currency(pct_of(income, 0.20))} |
| Savings | 20 % | {format_currency(pct_of(income, 0.20))} |
| Personal / Other | 10 % | {format_currency(pct_of(income, 0.10))} |
"""
            return md

        load_btn.click(fn=_load_summary, inputs=[user_id_input], outputs=[summary_md])

    return summary_tab
