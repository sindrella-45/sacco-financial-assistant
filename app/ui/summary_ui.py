import gradio as gr
from app.services.summary_service import generate_text_summary
from app.services.ai_service import generate_summary


def build_summary_tab(user_id_state):
    with gr.Column():
        gr.Markdown("### Your financial summary")
        gr.Markdown("*A complete overview of your current financial position.*")

        with gr.Row():
            refresh_btn = gr.Button("Generate my summary", variant="primary", scale=2)
            ai_btn      = gr.Button("Get AI narration", scale=1)

        text_summary = gr.Textbox(
            label="Financial summary",
            interactive=False,
            lines=14,
            placeholder="Click 'Generate my summary' to see your full financial overview..."
        )

        ai_narration = gr.Textbox(
            label="AI narration",
            interactive=False,
            lines=6,
            placeholder="Click 'Get AI narration' for a personalised assessment from the assistant..."
        )

        def get_text_summary(user_id):
            return generate_text_summary(user_id)

        def get_ai_summary(user_id):
            try:
                return generate_summary(user_id)
            except Exception as e:
                return f"AI narration unavailable: {str(e)}"

        refresh_btn.click(get_text_summary, inputs=[user_id_state], outputs=[text_summary])
        ai_btn.click(get_ai_summary,        inputs=[user_id_state], outputs=[ai_narration])
