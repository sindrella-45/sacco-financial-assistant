"""
app/ui/chatbot_ui.py — Chatbot tab (Person 3)
==============================================
Gradio interface for the AI chat assistant.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 HANDSHAKE 2  —  Person 2 → Person 3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 This file imports:
     from app.services.ai_service import chat

 Expected signature:
     chat(message: str, user_id: str, history: list) -> str

 history format (list of dicts):
     [{"role": "user",      "content": "Hello"},
      {"role": "assistant", "content": "Hi! How can I help?"}]

 Until Person 2 delivers ai_service, _mock_chat() is used as a
 transparent fallback — no code changes required after merging.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import gradio as gr

from app.utils.constants import DEMO_USER_IDS, APP_TITLE

# ── Handshake 2: try real service, fall back to mock ──────────────────────────
try:
    from app.services.ai_service import chat as _ai_chat
    _CHAT_READY = True
except ImportError:
    _CHAT_READY = False


def _mock_chat(message: str, user_id: str, history: list) -> str:
    """Temporary mock — replaced automatically once ai_service is merged."""
    question_lower = message.lower()

    if any(w in question_lower for w in ["loan", "balance", "repayment", "interest"]):
        return (
            "**[Mock response]** SACCO loans typically carry interest rates of "
            "15–24 % per annum on a reducing balance. Your exact balance and "
            "monthly repayment will appear here once the AI service is connected."
        )
    if any(w in question_lower for w in ["budget", "spend", "expense"]):
        return (
            "**[Mock response]** A healthy budget follows the **50/20/20/10** rule: "
            "50 % on needs, 20 % on loan repayment, 20 % on savings, 10 % on personal items. "
            "Try the **Budget Planner** tab for a detailed analysis."
        )
    if any(w in question_lower for w in ["save", "savings", "goal"]):
        return (
            "**[Mock response]** Aim to save at least 20 % of your monthly income. "
            "Even small consistent deposits add up over time. "
            "The **Financial Summary** tab can show your current savings target."
        )
    return (
        f"**[Mock — ai_service not yet connected]**\n\n"
        f"You asked: *{message}*\n\n"
        "Once Person 2's `ai_service` is merged into this branch, you will receive "
        "real AI-powered answers about your SACCO loans, budget, and financial literacy."
    )


def _dispatch_chat(message: str, user_id: str, history: list) -> str:
    """Route to the real service or the mock depending on availability."""
    if _CHAT_READY:
        return _ai_chat(message=message, user_id=user_id, history=history)
    return _mock_chat(message=message, user_id=user_id, history=history)


def build_chatbot_ui() -> gr.Blocks:
    """Return a gr.Blocks component for the Chatbot tab."""

    with gr.Blocks() as chat_tab:
        gr.Markdown(f"## {APP_TITLE} — Chat")
        gr.Markdown(
            "Ask about your **loan balance**, **repayment schedule**, "
            "**budgeting tips**, or anything about your SACCO finances."
        )

        with gr.Row():
            user_id_input = gr.Dropdown(
                choices=DEMO_USER_IDS,
                value=DEMO_USER_IDS[0],
                label="Member ID",
                scale=1,
            )
            status_badge = gr.Markdown(
                "🟢 AI ready" if _CHAT_READY else "🟡 Running in demo mode (mock responses)",
                scale=3,
            )

        chatbot = gr.Chatbot(
            label="SACCO Assistant",
            type="messages",
            height=440,
            show_copy_button=True,
        )

        with gr.Row():
            msg_input = gr.Textbox(
                placeholder="Type your question here and press Enter…",
                label="Your message",
                scale=5,
                autofocus=True,
            )
            send_btn = gr.Button("Send", variant="primary", scale=1)

        clear_btn = gr.Button("Clear Chat", variant="secondary")

        def _respond(message: str, user_id: str, history: list):
            if not message or not message.strip():
                return history, ""

            history = history or []
            history.append({"role": "user", "content": message})
            reply = _dispatch_chat(message=message, user_id=user_id, history=history)
            history.append({"role": "assistant", "content": reply})
            return history, ""

        send_btn.click(
            fn=_respond,
            inputs=[msg_input, user_id_input, chatbot],
            outputs=[chatbot, msg_input],
        )
        msg_input.submit(
            fn=_respond,
            inputs=[msg_input, user_id_input, chatbot],
            outputs=[chatbot, msg_input],
        )
        clear_btn.click(fn=lambda: ([], ""), outputs=[chatbot, msg_input])

    return chat_tab
