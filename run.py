"""
run.py — Application entry point (Person 3)
============================================
Assembles the four Gradio tabs into a single TabbedInterface and launches
the app on the configured port.

Usage:
    python run.py
    # Then open http://localhost:7860
"""

import gradio as gr

from app.ui.chatbot_ui  import build_chatbot_ui
from app.ui.budget_ui   import build_budget_ui
from app.ui.loan_ui     import build_loan_ui
from app.ui.summary_ui  import build_summary_ui
from app.config.settings import APP_TITLE, APP_PORT


def main() -> None:
    chat_tab    = build_chatbot_ui()
    budget_tab  = build_budget_ui()
    loan_tab    = build_loan_ui()
    summary_tab = build_summary_ui()

    app = gr.TabbedInterface(
        interface_list=[chat_tab, budget_tab, loan_tab, summary_tab],
        tab_names=["Chat", "Budget Planner", "Loan Calculator", "Financial Summary"],
        title=APP_TITLE,
    )

    app.launch(server_port=APP_PORT, share=False)


if __name__ == "__main__":
    main()
