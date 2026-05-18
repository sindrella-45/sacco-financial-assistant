"""
app/ui/loan_ui.py — Loan Calculator tab (Person 3)
====================================================
Gradio interface for calculating monthly EMI and total interest
using the reducing-balance method.

No AI or RAG calls — pure local math via helpers.py.
"""

import gradio as gr

from app.utils.helpers import format_currency, monthly_repayment, total_interest
from app.utils.constants import CURRENCY


def build_loan_ui() -> gr.Blocks:
    """Return a gr.Blocks component for the Loan Calculator tab."""

    with gr.Blocks() as loan_tab:
        gr.Markdown("## Loan Calculator")
        gr.Markdown(
            "Calculate your **monthly repayment** and **total interest** "
            "using the reducing-balance (EMI) method used by most SACCOs."
        )

        with gr.Row():
            with gr.Column(scale=1):
                principal_input = gr.Number(
                    label=f"Loan Principal ({CURRENCY})",
                    value=2_000_000,
                    minimum=100_000,
                    step=100_000,
                )
                rate_input = gr.Number(
                    label="Annual Interest Rate (%)",
                    value=15.0,
                    minimum=1.0,
                    maximum=50.0,
                    step=0.5,
                )
                tenure_input = gr.Number(
                    label="Loan Tenure (months)",
                    value=12,
                    minimum=1,
                    maximum=120,
                    step=1,
                    precision=0,
                )
                calc_btn = gr.Button("Calculate", variant="primary")

            with gr.Column(scale=1):
                monthly_out  = gr.Textbox(label="Monthly Repayment",    interactive=False)
                total_out    = gr.Textbox(label="Total Amount Repayable", interactive=False)
                interest_out = gr.Textbox(label="Total Interest Paid",   interactive=False)
                warning_md   = gr.Markdown(visible=False)

        def _calculate(principal, rate, tenure):
            principal = float(principal or 0)
            rate      = float(rate or 0)
            tenure    = int(tenure or 0)

            if principal <= 0 or rate <= 0 or tenure <= 0:
                return "—", "—", "—", gr.update(visible=False)

            monthly  = monthly_repayment(principal, rate, tenure)
            interest = total_interest(principal, monthly, tenure)
            total    = round(monthly * tenure, 2)

            # Warn if total interest exceeds 25 % of principal
            warning = gr.update(visible=False)
            if interest > 0 and interest / principal > 0.25:
                pct = interest / principal * 100
                warning = gr.update(
                    value=(
                        f"> **Note:** You will pay **{pct:.1f}%** of your principal "
                        "in interest. Consider a shorter tenure or extra repayments "
                        "to reduce the total cost."
                    ),
                    visible=True,
                )

            return (
                format_currency(monthly),
                format_currency(total),
                format_currency(interest),
                warning,
            )

        calc_btn.click(
            fn=_calculate,
            inputs=[principal_input, rate_input, tenure_input],
            outputs=[monthly_out, total_out, interest_out, warning_md],
        )

    return loan_tab
