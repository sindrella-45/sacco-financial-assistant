import gradio as gr
from app.ui.chatbot_ui import build_chat_tab
from app.ui.loan_ui import build_loan_tab
from app.ui.budget_ui import build_budget_tab
from app.ui.savings_ui import build_savings_tab
from app.ui.summary_ui import build_summary_tab
from app.services.memory_service import load_user_profile, save_user_profile

USER_ID = "member_001"

CSS = """
/* ── Force light mode regardless of browser/OS setting ── */
html, body {
    color-scheme: light only !important;
    background: #f4f4f0 !important;
    color: #1a1a18 !important;
}

/* ── Container ── */
.gradio-container {
    max-width: 800px !important;
    margin: 0 auto !important;
    background: #f4f4f0 !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

/* ── Kill dark mode on all elements ── */
*, *::before, *::after {
    color-scheme: light !important;
}

/* ── Header ── */
.sacco-header {
    background: #0F6E56 !important;
    color: white !important;
    padding: 18px 24px !important;
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    border-radius: 10px !important;
    margin-bottom: 12px !important;
}
.sacco-header h1 { font-size: 20px !important; font-weight: 700 !important; margin: 0 !important; color: white !important; }
.sacco-header p  { font-size: 12px !important; margin: 2px 0 0 !important; color: rgba(255,255,255,0.85) !important; }
.sacco-badge {
    margin-left: auto !important;
    background: rgba(255,255,255,0.25) !important;
    padding: 5px 14px !important;
    border-radius: 20px !important;
    font-size: 12px !important;
    color: white !important;
}

/* ── Override ALL Gradio theme colors to green ── */
:root {
    --color-accent:              #0F6E56 !important;
    --color-accent-soft:         #E1F5EE !important;
    --primary-50:                #f0faf6 !important;
    --primary-100:               #E1F5EE !important;
    --primary-200:               #b2dece !important;
    --primary-300:               #80c4ae !important;
    --primary-400:               #1D9E75 !important;
    --primary-500:               #0F6E56 !important;
    --primary-600:               #085041 !important;
    --primary-700:               #064033 !important;
    --color-blue-50:             #f0faf6 !important;
    --color-blue-100:            #E1F5EE !important;
    --color-blue-200:            #b2dece !important;
    --color-blue-300:            #80c4ae !important;
    --color-blue-400:            #1D9E75 !important;
    --color-blue-500:            #0F6E56 !important;
    --color-blue-600:            #085041 !important;
    --button-primary-background-fill:       #0F6E56 !important;
    --button-primary-background-fill-hover: #085041 !important;
    --button-primary-text-color:            white   !important;
    --block-label-border-color:  #0F6E56 !important;
    --border-color-accent:       #0F6E56 !important;
    --background-fill-primary:   #ffffff !important;
    --background-fill-secondary: #f4f4f0 !important;
    --color-grey-100:            #f4f4f0 !important;
    --body-background-fill:      #f4f4f0 !important;
    --body-text-color:           #1a1a18 !important;
    --body-text-color-subdued:   #5f5e5a !important;
    --border-color-primary:      #d3d1c7 !important;
    --input-background-fill:     #ffffff !important;
    --block-background-fill:     #ffffff !important;
    --panel-background-fill:     #f4f4f0 !important;
    --chatbot-code-background-color: #f4f4f0 !important;
}

/* ── Tabs ── */
.tab-nav { border-bottom: 1px solid #d3d1c7 !important; background: white !important; }
.tab-nav button {
    font-size: 13px !important;
    padding: 10px 16px !important;
    border-bottom: 2px solid transparent !important;
    color: #888780 !important;
    background: transparent !important;
    border-radius: 0 !important;
}
.tab-nav button.selected {
    color: #0F6E56 !important;
    border-bottom: 2px solid #0F6E56 !important;
    font-weight: 600 !important;
}
.tab-nav button:hover { color: #0F6E56 !important; }

/* ── Inputs ── */
input, textarea, select {
    background: #ffffff !important;
    color: #1a1a18 !important;
    border-color: #d3d1c7 !important;
}
input:focus, textarea:focus {
    border-color: #0F6E56 !important;
    box-shadow: 0 0 0 2px rgba(15,110,86,0.15) !important;
    outline: none !important;
}

/* ── Buttons ── */
button.primary, .gr-button-primary {
    background: #0F6E56 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
}
button.primary:hover { background: #085041 !important; }
button.secondary {
    border: 1px solid #0F6E56 !important;
    color: #0F6E56 !important;
    background: white !important;
}

/* ── Chatbot ── */
.chatbot { background: white !important; border: 1px solid #d3d1c7 !important; border-radius: 10px !important; }

/* ── Labels and text ── */
label span, .gr-form label { color: #5f5e5a !important; font-size: 13px !important; }
.gr-markdown h3 { color: #0F6E56 !important; font-size: 14px !important; font-weight: 600 !important; }

/* ── Accordion ── */
.gr-accordion { background: white !important; border: 1px solid #d3d1c7 !important; border-radius: 8px !important; }

/* ── Selection ── */
::selection { background: #b2dece !important; }
a { color: #0F6E56 !important; }

/* ── Footer ── */
.sacco-footer {
    text-align: center !important;
    padding: 12px !important;
    font-size: 11px !important;
    color: #888780 !important;
    margin-top: 8px !important;
}
"""


def build_profile_block(user_id_state):
    profile = load_user_profile(USER_ID)

    with gr.Accordion("👤 Member profile", open=not bool(profile.get("name"))) as profile_acc:
        if profile.get("name"):
            gr.Markdown(f"*Logged in as **{profile['name']}**. Update your details below if anything has changed.*")
        else:
            gr.Markdown("*Fill in your details so the assistant can personalise its advice.*")

        with gr.Row():
            name_in       = gr.Textbox(label="Your name",  placeholder="e.g. Aisha Nakato",
                                       value=profile.get("name", ""))
            occupation_in = gr.Textbox(label="Occupation", placeholder="e.g. Market vendor",
                                       value=profile.get("occupation", ""))
        with gr.Row():
            income_in       = gr.Number(label="Monthly income (UGX)",       minimum=0,
                                        value=float(profile.get("monthly_income", 0) or 0))
            savings_goal_in = gr.Number(label="Monthly savings goal (UGX)", minimum=0,
                                        value=float(profile.get("savings_goal", 0) or 0))
        with gr.Row():
            loan_amt_in  = gr.Number(label="Loan amount (UGX)",  minimum=0,
                                     value=float(profile.get("loan_amount", 0) or 0))
            loan_rate_in = gr.Number(label="Interest rate (%)",  minimum=0,
                                     value=float(profile.get("interest_rate", 18) or 18))
            loan_term_in = gr.Number(label="Loan term (months)", minimum=1,
                                     value=float(profile.get("loan_term_months", 12) or 12))

        save_btn       = gr.Button("Save profile", variant="primary")
        profile_status = gr.Textbox(label="", interactive=False, show_label=False)

        def save_profile(user_id, name, occ, inc, sg, la, lr, lt):
            save_user_profile(user_id, {
                "name": name, "occupation": occ,
                "monthly_income": inc, "savings_goal": sg,
                "loan_amount": la, "interest_rate": lr, "loan_term_months": lt,
            })
            return f"✅ Profile saved for {name}. Your details will be remembered next time."

        save_btn.click(
            save_profile,
            inputs=[user_id_state, name_in, occupation_in, income_in,
                    savings_goal_in, loan_amt_in, loan_rate_in, loan_term_in],
            outputs=[profile_status]
        )
    return profile_acc


def create_app():
    with gr.Blocks(title="SACCO Financial Assistant") as demo:

        user_id_state = gr.State(USER_ID)

        gr.HTML("""
        <div class="sacco-header">
            <div style="width:40px;height:40px;background:rgba(255,255,255,0.2);
                        border-radius:10px;display:flex;align-items:center;
                        justify-content:center;font-size:22px;">🏦</div>
            <div>
                <h1>SACCO Financial Assistant</h1>
                <p>Powered by AI &middot; Member portal</p>
            </div>
            <div class="sacco-badge">Powered by Groq</div>
        </div>
        """)

        build_profile_block(user_id_state)

        with gr.Tabs():
            with gr.Tab("💬 Chat"):
                build_chat_tab(user_id_state)
            with gr.Tab("🧾 Loan Calculator"):
                build_loan_tab()
            with gr.Tab("📊 Budget Planner"):
                build_budget_tab()
            with gr.Tab("🐷 Savings Planner"):
                build_savings_tab(user_id_state)
            with gr.Tab("📋 Summary"):
                build_summary_tab(user_id_state)

        gr.HTML('<div class="sacco-footer">SACCO Financial Assistant &middot; Built for SACCO members in Uganda &middot; Advice is for guidance only</div>')

    return demo


if __name__ == "__main__":
    app = create_app()
    app.launch(
        inbrowser=True,
        server_name="localhost",
        server_port=7860,
        css=CSS,
        theme=gr.themes.Default()
    )