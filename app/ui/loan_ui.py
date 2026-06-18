import gradio as gr
from app.services.loan_service import (
    calculate_monthly_payment,
    calculate_total_interest,
    generate_repayment_schedule,
)
from app.services.ai_service import explain_loan


def build_loan_tab():
    with gr.Column():
        gr.Markdown("### Enter your loan details")

        with gr.Row():
            principal = gr.Number(label="Loan amount (UGX)", value=500000, minimum=0)
            rate = gr.Number(label="Annual interest rate (%)", value=18, minimum=0, maximum=100)

        with gr.Row():
            term = gr.Number(label="Loan term (months)", value=12, minimum=1)
            start = gr.Textbox(label="Start date (optional)", placeholder="e.g. Jan 2025")

        calc_btn = gr.Button("Calculate repayment plan", variant="primary")

        with gr.Row():
            monthly_box = gr.Textbox(label="Monthly payment", interactive=False)
            interest_box = gr.Textbox(label="Total interest", interactive=False)
            total_box = gr.Textbox(label="Total to repay", interactive=False)

        ai_explanation = gr.Textbox(
            label="AI explanation",
            interactive=False,
            lines=4,
            placeholder="Your personalised loan explanation will appear here..."
        )

        schedule_output = gr.Dataframe(
            headers=["Month", "Payment (UGX)", "Principal (UGX)", "Interest (UGX)", "Balance (UGX)"],
            label="Month-by-month repayment schedule",
            interactive=False,
            wrap=True,
        )

        def calculate(p, r, t):
            if not p or not r or not t:
                return "—", "—", "—", "Fill in all fields above.", []

            monthly = calculate_monthly_payment(p, r, int(t))
            interest = calculate_total_interest(p, r, int(t))
            total = p + interest

            try:
                explanation = explain_loan(p, r, int(t))
            except Exception as e:
                explanation = f"AI explanation unavailable: {str(e)}"

            schedule = generate_repayment_schedule(p, r, int(t))
            table = [
                [
                    row["month"],
                    f"{row['payment']:,.0f}",
                    f"{row['principal_paid']:,.0f}",
                    f"{row['interest_paid']:,.0f}",
                    f"{row['balance']:,.0f}",
                ]
                for row in schedule
            ]

            return (
                f"UGX {monthly:,.0f}",
                f"UGX {interest:,.0f}",
                f"UGX {total:,.0f}",
                explanation,
                table,
            )

        calc_btn.click(
            calculate,
            inputs=[principal, rate, term],
            outputs=[monthly_box, interest_box, total_box, ai_explanation, schedule_output],
        )
