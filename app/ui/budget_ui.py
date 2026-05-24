import gradio as gr
from app.services.budget_service import generate_budget, calculate_savings_potential
from app.services.ai_service import explain_budget


def build_budget_tab():
    with gr.Column():
        gr.Markdown("### Enter your monthly income and expenses")

        income = gr.Number(label="Monthly income (UGX)", value=800000, minimum=0)

        gr.Markdown("**Monthly expenses** — fill in what applies to you")

        with gr.Row():
            rent = gr.Number(label="Rent (UGX)", value=200000, minimum=0)
            food = gr.Number(label="Food (UGX)", value=150000, minimum=0)

        with gr.Row():
            transport = gr.Number(label="Transport (UGX)", value=50000, minimum=0)
            loan_repay = gr.Number(label="Loan repayment (UGX)", value=45840, minimum=0)

        with gr.Row():
            school = gr.Number(label="School fees (UGX)", value=0, minimum=0)
            medical = gr.Number(label="Medical (UGX)", value=0, minimum=0)

        with gr.Row():
            utilities = gr.Number(label="Utilities / Airtime (UGX)", value=0, minimum=0)
            other = gr.Number(label="Other expenses (UGX)", value=0, minimum=0)

        analyse_btn = gr.Button("Analyse my budget", variant="primary")

        with gr.Row():
            total_exp_box = gr.Textbox(label="Total expenses", interactive=False)
            surplus_box = gr.Textbox(label="Surplus / Deficit", interactive=False)
            savings_box = gr.Textbox(label="Potential monthly savings", interactive=False)

        budget_status = gr.Textbox(
            label="Budget status",
            interactive=False,
            lines=1,
            placeholder="Status will appear here..."
        )

        ai_advice = gr.Textbox(
            label="AI budget advice",
            interactive=False,
            lines=5,
            placeholder="Personalised budget advice will appear here..."
        )

        breakdown = gr.Dataframe(
            headers=["Category", "Recommended (UGX)", "% of Income"],
            label="Recommended budget breakdown",
            interactive=False,
        )

        def analyse(inc, r, f, tr, lr, sc, med, ut, oth):
            expenses = {}
            if r: expenses["Rent"] = r
            if f: expenses["Food"] = f
            if tr: expenses["Transport"] = tr
            if lr: expenses["Loan repayment"] = lr
            if sc: expenses["School fees"] = sc
            if med: expenses["Medical"] = med
            if ut: expenses["Utilities"] = ut
            if oth: expenses["Other"] = oth

            if not inc:
                return "—", "—", "—", "Please enter your income.", "", []

            budget = generate_budget(inc, expenses)
            savings = calculate_savings_potential(inc, expenses)
            surplus = budget["surplus"]
            status = "✅ You are in surplus — good position!" if surplus >= 0 else "⚠️ You are in deficit — expenses exceed income."

            try:
                advice = explain_budget(inc, expenses)
            except Exception as e:
                advice = f"AI advice unavailable: {str(e)}"

            table = [
                [cat.replace("_", " ").title(), f"{amt:,.0f}", f"{(amt/inc*100):.0f}%"]
                for cat, amt in budget["recommended_allocations"].items()
            ]

            return (
                f"UGX {budget['total_expenses']:,.0f}",
                f"UGX {abs(surplus):,.0f} {'surplus' if surplus >= 0 else 'deficit'}",
                f"UGX {savings:,.0f}",
                status,
                advice,
                table,
            )

        analyse_btn.click(
            analyse,
            inputs=[income, rent, food, transport, loan_repay, school, medical, utilities, other],
            outputs=[total_exp_box, surplus_box, savings_box, budget_status, ai_advice, breakdown],
        )
