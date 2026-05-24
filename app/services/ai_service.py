from groq import Groq
from jinja2 import Environment, FileSystemLoader

from app.config.settings import API_KEY, MODEL_NAME, MAX_TOKENS, PROMPTS_DIR
from app.services.memory_service import load_user_profile, build_memory_context
from app.services.rag_service import query as rag_query

# Jinja2 environment for loading prompt templates
env = Environment(loader=FileSystemLoader(PROMPTS_DIR))
env.filters["format_number"] = lambda value: f"{value:,.0f}"

# Lazy client — initialised on first use so missing key doesn't crash on import
_client = None

def _get_client():
    global _client
    if _client is None:
        if not API_KEY:
            raise ValueError("GROQ_API_KEY not set. Add it to your .env file.")
        _client = Groq(api_key=API_KEY)
    return _client


def _call(messages: list) -> str:
    """Single helper that calls Groq and returns the text response."""
    response = _get_client().chat.completions.create(
        model=MODEL_NAME,
        max_tokens=MAX_TOKENS,
        messages=messages
    )
    return response.choices[0].message.content


def chat(message: str, user_id: str, history: list) -> str:
    """
    Main chat function — called by the Gradio UI on every user message.

    Args:
        message:  The user's current message
        user_id:  Identifier for the current user
        history:  List of prior messages:
                  [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]

    Returns:
        The assistant's reply as a plain string.
    """
    profile = load_user_profile(user_id)
    memory_context = build_memory_context(profile)
    rag_context = rag_query(message)

    template = env.get_template("system_prompt.j2")
    system_prompt = template.render(
        memory_context=memory_context,
        rag_context=rag_context
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages += history
    messages.append({"role": "user", "content": message})

    return _call(messages)


def explain_loan(principal: float, interest_rate: float, term_months: int) -> str:
    """Generate a plain English loan explanation."""
    from app.services.loan_service import calculate_monthly_payment, calculate_total_interest

    monthly_payment = calculate_monthly_payment(principal, interest_rate, term_months)
    total_interest  = calculate_total_interest(principal, interest_rate, term_months)

    template = env.get_template("loan_prompt.j2")
    prompt = template.render(
        principal=principal,
        interest_rate=interest_rate,
        term_months=term_months,
        monthly_payment=monthly_payment,
        total_interest=total_interest
    )

    return _call([{"role": "user", "content": prompt}])


def explain_budget(income: float, expenses: dict) -> str:
    """Generate personalised budget advice."""
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

    return _call([{"role": "user", "content": prompt}])


def generate_summary(user_id: str) -> str:
    """Generate a personalised financial summary."""
    profile = load_user_profile(user_id)
    memory_context = build_memory_context(profile)

    template = env.get_template("summary_prompt.j2")
    prompt = template.render(memory_context=memory_context)

    return _call([{"role": "user", "content": prompt}])