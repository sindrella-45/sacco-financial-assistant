import gradio as gr
from app.services.loan_service import calculate_monthly_payment


def build_savings_tab(user_id_state):
    with gr.Column():
        gr.Markdown("### Plan your savings goal")

        with gr.Row():
            income = gr.Number(label="Monthly income (UGX)", value=800000, minimum=0)
            total_expenses = gr.Number(label="Total monthly expenses (UGX)", value=445840, minimum=0)

        gr.Markdown("**Your savings goal**")

        with gr.Row():
            goal_name = gr.Textbox(label="Goal name", value="Emergency fund", placeholder="e.g. Emergency fund, School fees...")
            goal_amount = gr.Number(label="Target amount (UGX)", value=1000000, minimum=0)

        with gr.Row():
            already_saved = gr.Number(label="Amount already saved (UGX)", value=620000, minimum=0)
            monthly_contribution = gr.Number(label="Planned monthly contribution (UGX)", value=80000, minimum=0)

        gr.Markdown("**Loan details** — to calculate when funds free up")

        with gr.Row():
            loan_amount = gr.Number(label="Loan amount (UGX)", value=500000, minimum=0)
            loan_rate = gr.Number(label="Interest rate (%)", value=18, minimum=0)
            loan_term = gr.Number(label="Term (months)", value=12, minimum=1)
            months_paid = gr.Number(label="Months already paid", value=4, minimum=0)

        calculate_btn = gr.Button("Calculate savings plan", variant="primary")

        with gr.Row():
            remaining_box = gr.Textbox(label="Remaining to save", interactive=False)
            months_box = gr.Textbox(label="Months to goal", interactive=False)
            available_box = gr.Textbox(label="Available to save monthly", interactive=False)
            rate_box = gr.Textbox(label="Current savings rate", interactive=False)

        progress_bar = gr.Textbox(
            label="Progress toward goal",
            interactive=False,
            lines=1,
        )

        ai_tips = gr.Textbox(
            label="AI savings advice & tips",
            interactive=False,
            lines=8,
            placeholder="Your personalised savings plan will appear here..."
        )

        def calculate_savings(inc, exp, g_name, g_amt, saved, contrib, l_amt, l_rate, l_term, m_paid):
            if not inc or not g_amt:
                return "—", "—", "—", "—", "Fill in income and goal amount.", ""

            remaining = max(g_amt - saved, 0)
            available = max(inc - exp, 0)

            months_left = remaining / contrib if contrib > 0 else float('inf')
            savings_rate = (contrib / inc * 100) if inc > 0 else 0

            # Progress bar as text
            progress_pct = min((saved / g_amt * 100), 100) if g_amt > 0 else 0
            filled = int(progress_pct / 5)
            bar = "█" * filled + "░" * (20 - filled)
            progress_text = f"{bar}  {progress_pct:.0f}% — UGX {saved:,.0f} of UGX {g_amt:,.0f} saved"

            # Loan freeing up calculation
            loan_monthly = calculate_monthly_payment(l_amt, l_rate, int(l_term)) if l_amt and l_rate and l_term else 0
            months_remaining_on_loan = max(int(l_term) - int(m_paid), 0)

            # Build AI prompt manually (no LLM call for savings — use rule-based tips)
            tips = []
            tips.append(f"📊 Savings goal: {g_name} — UGX {g_amt:,.0f}")
            tips.append(f"   Progress: {progress_pct:.0f}% complete ({progress_text.split('—')[1].strip()})\n")

            if months_left == float('inf'):
                tips.append("⚠️  You have not set a monthly contribution. Set one to start making progress.")
            elif months_left <= 6:
                tips.append(f"✅ Great progress! You will reach your goal in about {months_left:.0f} months at UGX {contrib:,.0f}/month.")
            else:
                tips.append(f"📅 At UGX {contrib:,.0f}/month, you will reach your goal in about {months_left:.0f} months.")

            if available > contrib:
                extra = available - contrib
                tips.append(f"\n💡 You have UGX {extra:,.0f} extra available each month beyond your contribution.")
                tips.append(f"   Consider increasing your savings to UGX {available * 0.5:,.0f}/month to reach your goal faster.")

            if months_remaining_on_loan > 0:
                tips.append(f"\n🔔 Your loan has {months_remaining_on_loan} months remaining (UGX {loan_monthly:,.0f}/month).")
                tips.append(f"   When it ends, redirect that UGX {loan_monthly:,.0f} into savings — your monthly contribution would jump to UGX {contrib + loan_monthly:,.0f}.")
                faster = remaining / (contrib + loan_monthly) if (contrib + loan_monthly) > 0 else months_left
                tips.append(f"   This could cut your remaining time to goal from {months_left:.0f} to {faster:.0f} months!")
            else:
                tips.append(f"\n✅ Your loan is paid off. Make sure that freed money is going into savings.")

            tips.append("\n📌 Practical tips:")
            tips.append("   • Save on income day — move your contribution immediately when you receive pay.")
            tips.append("   • Keep savings in your SACCO account where it earns interest.")
            tips.append(f"   • Once {g_name} is complete, start a new goal for business investment or school fees.")

            return (
                f"UGX {remaining:,.0f}",
                f"~{months_left:.0f} months" if months_left != float('inf') else "Set a contribution",
                f"UGX {available:,.0f}",
                f"{savings_rate:.0f}% of income",
                progress_text,
                "\n".join(tips),
            )

        calculate_btn.click(
            calculate_savings,
            inputs=[income, total_expenses, goal_name, goal_amount, already_saved,
                    monthly_contribution, loan_amount, loan_rate, loan_term, months_paid],
            outputs=[remaining_box, months_box, available_box, rate_box, progress_bar, ai_tips],
        )
