import gradio as gr
from app.services.ai_service import chat


def build_chat_tab(user_id_state):
    with gr.Column():
        chatbot = gr.Chatbot(
            label="",
            height=360,
            avatar_images=("👤", "🏦"),
            layout="bubble",
            value=[
                {"role": "assistant", "content": "Hello! I am your SACCO financial assistant. I can help you understand your loan, plan your budget, and build savings. What would you like help with today?"}
            ]
        )
        with gr.Row():
            msg_input = gr.Textbox(
                placeholder="Ask about your loan, budget, or savings...",
                show_label=False,
                scale=5,
                container=False,
            )
            send_btn = gr.Button("Send →", variant="primary", scale=1)

        with gr.Row():
            q1 = gr.Button("💬 Explain my loan",   size="sm")
            q2 = gr.Button("💡 Savings tips",       size="sm")
            q3 = gr.Button("❓ Missed payment?",    size="sm")
            q4 = gr.Button("📊 Budget advice",      size="sm")

    def respond(message, history, user_id):
        if not message.strip():
            return history, ""
        api_history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in (history or [])
            if isinstance(msg, dict) and msg.get("role") in ("user", "assistant")
        ]
        reply = chat(message, user_id, api_history)
        history = (history or []) + [
            {"role": "user",      "content": message},
            {"role": "assistant", "content": reply},
        ]
        return history, ""

    def quick(q, history, user_id):
        updated, _ = respond(q, history, user_id)
        return updated

    send_btn.click(respond, [msg_input, chatbot, user_id_state], [chatbot, msg_input])
    msg_input.submit(respond, [msg_input, chatbot, user_id_state], [chatbot, msg_input])
    q1.click(lambda h, u: quick("Explain my loan in simple terms",        h, u), [chatbot, user_id_state], [chatbot])
    q2.click(lambda h, u: quick("How can I save more money this month?",   h, u), [chatbot, user_id_state], [chatbot])
    q3.click(lambda h, u: quick("What happens if I miss a loan payment?",  h, u), [chatbot, user_id_state], [chatbot])
    q4.click(lambda h, u: quick("Give me practical budget advice",         h, u), [chatbot, user_id_state], [chatbot])

    return chatbot