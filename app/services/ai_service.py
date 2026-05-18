import google.generativeai as genai
from jinja2 import Environment, FileSystemLoader

from app.config.settings import API_KEY, MODEL_NAME, PROMPTS_DIR
from app.services.memory_service import load_user_profile, build_memory_context
from app.services.rag_service import query as rag_query

# Jinja2 environment for loading prompt templates
env = Environment(loader=FileSystemLoader(PROMPTS_DIR))

# Add a number formatting filter to Jinja2
env.filters["format_number"] = lambda value: f"{value:,.0f}"

# Configure Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(MODEL_NAME)


def _build_history(history: list) -> list:
    """
    Convert history from {"role": "user/assistant", "content": "..."}
    to Gemini's format {"role": "user/model", "parts": ["..."]}
    """
    gemini_history = []
    for msg in history:
        role = "model" if msg["role"] == "assistant" else "user"
        gemini_history.append({
            "role": role,
            "parts": [msg["content"]]
        })
    return gemini_history


def chat(message: str, user_id: str, history: list) -> str:
    """
    Main chat function — called by the Gradio UI on every user message.

    Args:
        message:  The user's current message
        user_id:  Identifier for the current user (used to load their profile)
        history:  List of prior messages in the format:
                  [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]

    Returns:
        The assistant's reply as a plain string.
    """
    # 1. Load what we know about the user
    profile = load_user_profile(user_id)
    memory_context = build_memory_context(profile)

    # 2. Search documents for relevant context
    rag_context = rag_query(message)

    # 3. Build the system prompt from template
    template = env.get_template("system_prompt.j2")
    system_prompt = template.render(
        memory_context=memory_context,
        rag_context=rag_context
    )

    # 4. Start a chat session with history and system prompt injected
    chat_session = model.start_chat(history=_build_history(history))

    # Prepend system prompt to the user message on first turn
    full_message = f"{system_prompt}\n\nMember: {message}" if not history else message

    response = chat_session.send_message(full_message)
    return response.text


def explain_loan(principal: float, interest_rate: float, term_months: int) -> str:
    """
    Generate a plain English explanation of a loan using the loan prompt template.
    Called by the loan UI tab.
    """
    from app.services.loan_service import calculate_monthly_payment, calculate_total_interest

    monthly_payment = calculate_monthly_payment(principal, interest_rate, term_months)
    total_interest = calculate_total_interest(principal, interest_rate, term_months)

    template = env.get_template("loan_prompt.j2")
    prompt = template.render(
        principal=principal,
        interest_rate=interest_rate,
        term_months=term_months,
        monthly_payment=monthly_payment,
        total_interest=total_interest
    )

    response = model.generate_content(prompt)
    return response.text


def explain_budget(income: float, expenses: dict) -> str:
    """
    Generate personalised budget advice using the budget prompt template.
    Called by the budget UI tab.
    """
    from app.services.budget_service import generate_budget

    budget = generate_budget(income, expenses)

    template = env.get_template("budget_prompt.j2")
    prompt = template.render(
        income=income,
        expenses=expenses,
        total_expenses=budget["total_expenses"],
        surplus=budget["surplus"],
        status=budget["status"]
    )

    response = model.generate_content(prompt)
    return response.text
