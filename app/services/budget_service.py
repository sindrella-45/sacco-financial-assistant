from app.config.settings import APP_CURRENCY


# Recommended budget proportions (can be adjusted)
BUDGET_GUIDELINES = {
    "needs": 0.50,      # rent, food, transport, utilities
    "loan_repayment": 0.20,
    "savings": 0.20,
    "wants": 0.10       # personal spending, leisure
}


def generate_budget(income: float, expenses: dict) -> dict:
    """
    Generate a structured budget given income and current expenses.

    Args:
        income: Monthly income in UGX
        expenses: Dict of expense categories and amounts
                  e.g. {"rent": 200000, "food": 150000, "transport": 50000}

    Returns:
        Dict with recommended allocations, actuals, and surplus/deficit
    """
    total_expenses = sum(expenses.values())
    surplus = income - total_expenses

    recommended = {
        category: round(income * proportion)
        for category, proportion in BUDGET_GUIDELINES.items()
    }

    return {
        "income": income,
        "expenses": expenses,
        "total_expenses": total_expenses,
        "surplus": surplus,
        "recommended_allocations": recommended,
        "status": "surplus" if surplus >= 0 else "deficit"
    }


def calculate_savings_potential(income: float, expenses: dict) -> float:
    """
    Calculate how much the user can realistically save per month.
    Returns 0 if expenses exceed income.
    """
    total_expenses = sum(expenses.values())
    potential = income - total_expenses
    return max(round(potential, 2), 0.0)


def categorize_expenses(expenses: dict) -> dict:
    """
    Group expenses into needs, wants, and loan repayment buckets.
    Uses simple keyword matching on expense names.
    """
    needs_keywords = ["rent", "food", "transport", "water", "electricity", "school", "medical", "utilities"]
    loan_keywords = ["loan", "repayment", "sacco", "debt"]

    categorized = {"needs": {}, "loan_repayment": {}, "wants": {}}

    for name, amount in expenses.items():
        key = name.lower()
        if any(word in key for word in loan_keywords):
            categorized["loan_repayment"][name] = amount
        elif any(word in key for word in needs_keywords):
            categorized["needs"][name] = amount
        else:
            categorized["wants"][name] = amount

    return categorized


def summarize_budget(income: float, expenses: dict) -> str:
    """
    Return a plain English budget summary.
    Used for injecting into AI responses or displaying directly.
    """
    budget = generate_budget(income, expenses)
    savings = calculate_savings_potential(income, expenses)
    status = budget["status"]

    lines = [
        f"Monthly income: {APP_CURRENCY} {income:,.0f}",
        f"Total expenses: {APP_CURRENCY} {budget['total_expenses']:,.0f}",
        f"{'Surplus' if status == 'surplus' else 'Deficit'}: "
        f"{APP_CURRENCY} {abs(budget['surplus']):,.0f}",
        f"Potential monthly savings: {APP_CURRENCY} {savings:,.0f}",
        "",
        "Recommended allocations:",
    ]

    for category, amount in budget["recommended_allocations"].items():
        lines.append(f"  - {category.replace('_', ' ').title()}: {APP_CURRENCY} {amount:,.0f}")

    return "\n".join(lines)
