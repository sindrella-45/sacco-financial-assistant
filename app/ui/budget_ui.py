"""
app/ui/budget_ui.py — Budget Planner tab (Person 3)
=====================================================
Gradio interface for the 50 / 20 / 20 / 10 budget framework.

  50 % → Needs (rent, food, transport, school fees)
  20 % → Loan repayment
  20 % → Savings
  10 % → Personal / other

Flags a warning if loan repayment exceeds 20 % of income.
No AI or external service calls — pure local calculation.
"""

import gradio as gr

from app.utils.helpers import format_currency, pct_of, pct_share, format_pct
from app.utils.constants import (
    CURRENCY,
    BUDGET_NEEDS_PCT,
    BUDGET_LOAN_PCT,
    BUDGET_SAVINGS_PCT,
    BUDGET_PERSONAL_PCT,
    LOAN_REPAYMENT_WARNING_PCT,
)


def build_budget_ui() -> gr.Blocks:
    """Return a gr.Blocks component for the Budget Planner tab."""

    with gr.Blocks() as budget_tab:
        gr.Markdown("## Budget Planner")
        gr.Markdown(
            "Enter your **monthly income** and actual spending. "
            "The **50 / 20 / 20 / 10** framework shows you where you stand."
        )

        with gr.Row():
            with gr.Column(scale=1):
                income_input      = gr.Number(label=f"Monthly Income ({CURRENCY})",        value=850_000, step=10_000,  minimum=0)
                rent_input        = gr.Number(label=f"Rent ({CURRENCY})",                  value=0,       step=5_000,   minimum=0)
                food_input        = gr.Number(label=f"Food ({CURRENCY})",                  value=0,       step=5_000,   minimum=0)
                transport_input   = gr.Number(label=f"Transport ({CURRENCY})",             value=0,       step=5_000,   minimum=0)
                school_fees_input = gr.Number(label=f"School Fees ({CURRENCY})",           value=0,       step=5_000,   minimum=0)
                loan_input        = gr.Number(label=f"Loan Repayment ({CURRENCY})",        value=0,       step=5_000,   minimum=0)
                savings_input     = gr.Number(label=f"Savings ({CURRENCY})",               value=0,       step=5_000,   minimum=0)
                other_input       = gr.Number(label=f"Personal / Other ({CURRENCY})",      value=0,       step=5_000,   minimum=0)
                calc_btn          = gr.Button("Analyse My Budget", variant="primary")

            with gr.Column(scale=1):
                result_md  = gr.Markdown("*Fill in your details and click Analyse.*")
                warning_md = gr.Markdown(visible=False)

        def _analyse(income, rent, food, transport, school_fees, loan, savings, other):
            income = float(income or 0)
            if income <= 0:
                return "*Please enter a valid monthly income.*", gr.update(visible=False)

            needs   = sum(float(v or 0) for v in [rent, food, transport, school_fees])
            loan    = float(loan or 0)
            savings = float(savings or 0)
            other   = float(other or 0)
            total_spent = needs + loan + savings + other

            # Targets
            t_needs   = pct_of(income, BUDGET_NEEDS_PCT)
            t_loan    = pct_of(income, BUDGET_LOAN_PCT)
            t_savings = pct_of(income, BUDGET_SAVINGS_PCT)
            t_other   = pct_of(income, BUDGET_PERSONAL_PCT)

            def _status(actual: float, target: float, under_is_bad: bool = False) -> str:
                if under_is_bad:
                    return "✅" if actual >= target else "⚠️ Under target"
                return "✅" if actual <= target else "⚠️ Over target"

            result = f"""
### Budget Analysis — {format_currency(income)} / month

| Category | Your Amount | Target ({{}}) | Target Amount | Status |
|---|---|---|---|---|
| Needs (rent + food + transport + fees) | {format_currency(needs)} | 50 % | {format_currency(t_needs)} | {_status(needs, t_needs)} |
| Loan Repayment | {format_currency(loan)} | 20 % | {format_currency(t_loan)} | {_status(loan, t_loan)} |
| Savings | {format_currency(savings)} | 20 % | {format_currency(t_savings)} | {_status(savings, t_savings, under_is_bad=True)} |
| Personal / Other | {format_currency(other)} | 10 % | {format_currency(t_other)} | {_status(other, t_other)} |

**Total spending:** {format_currency(total_spent)} &nbsp;|&nbsp; **Unaccounted:** {format_currency(max(0, income - total_spent))}
"""

            warning = gr.update(visible=False)
            if pct_share(loan, income) > LOAN_REPAYMENT_WARNING_PCT:
                warning = gr.update(
                    value=(
                        f"> **Warning:** Your loan repayment is "
                        f"**{format_pct(pct_share(loan, income))}** of your income, "
                        "which exceeds the recommended 20 %. "
                        "Consider speaking to your SACCO officer about restructuring your loan."
                    ),
                    visible=True,
                )

            return result, warning

        calc_btn.click(
            fn=_analyse,
            inputs=[
                income_input, rent_input, food_input, transport_input,
                school_fees_input, loan_input, savings_input, other_input,
            ],
            outputs=[result_md, warning_md],
        )

    return budget_tab
