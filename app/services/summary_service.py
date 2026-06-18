from app.services.memory_service import load_user_profile, build_memory_context
from app.services.loan_service import calculate_monthly_payment, calculate_total_interest
from app.config.settings import APP_CURRENCY


def generate_text_summary(user_id: str) -> str:
    """
    Generate a plain text financial summary for a user.
    Does not call the LLM — just formats stored data.
    Used as a fallback or for quick display without AI narration.
    """
    profile = load_user_profile(user_id)

    if not profile:
        return "No profile found. Please enter your financial details first."

    lines = ["=== Your Financial Summary ===", ""]

    if profile.get("name"):
        lines.append(f"Member: {profile['name']}")

    if profile.get("monthly_income"):
        income = float(profile["monthly_income"])
        lines.append(f"Monthly income: {APP_CURRENCY} {income:,.0f}")

    if profile.get("loan_amount") and profile.get("interest_rate") and profile.get("loan_term_months"):
        principal = float(profile["loan_amount"])
        rate = float(profile["interest_rate"])
        term = int(profile["loan_term_months"])

        monthly = calculate_monthly_payment(principal, rate, term)
        total_interest = calculate_total_interest(principal, rate, term)

        lines.append("")
        lines.append("--- Loan ---")
        lines.append(f"Loan amount: {APP_CURRENCY} {principal:,.0f}")
        lines.append(f"Interest rate: {rate}% per year")
        lines.append(f"Term: {term} months")
        lines.append(f"Monthly payment: {APP_CURRENCY} {monthly:,.0f}")
        lines.append(f"Total interest: {APP_CURRENCY} {total_interest:,.0f}")

    if profile.get("savings_goal"):
        goal = float(profile["savings_goal"])
        lines.append("")
        lines.append("--- Savings ---")
        lines.append(f"Monthly savings goal: {APP_CURRENCY} {goal:,.0f}")

        if profile.get("monthly_income") and profile.get("loan_amount"):
            income = float(profile["monthly_income"])
            loan_payment = calculate_monthly_payment(
                float(profile["loan_amount"]),
                float(profile["interest_rate"]),
                int(profile["loan_term_months"])
            )
            remaining = income - loan_payment
            lines.append(f"Income after loan repayment: {APP_CURRENCY} {remaining:,.0f}")

            if remaining >= goal:
                lines.append("✓ Your savings goal is achievable with your current income.")
            else:
                lines.append("⚠ Your savings goal may be difficult given your loan repayment.")

    return "\n".join(lines)
