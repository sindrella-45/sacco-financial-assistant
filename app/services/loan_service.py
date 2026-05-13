from app.config.settings import APP_CURRENCY


def calculate_monthly_payment(principal: float, annual_rate: float, term_months: int) -> float:
    """
    Calculate the fixed monthly payment using the reducing balance method.

    Args:
        principal: Loan amount in UGX
        annual_rate: Annual interest rate as a percentage (e.g. 18 for 18%)
        term_months: Loan duration in months

    Returns:
        Monthly payment amount in UGX
    """
    if annual_rate == 0:
        return principal / term_months

    monthly_rate = annual_rate / 100 / 12
    payment = principal * (monthly_rate * (1 + monthly_rate) ** term_months) / \
              ((1 + monthly_rate) ** term_months - 1)
    return round(payment, 2)


def calculate_total_interest(principal: float, annual_rate: float, term_months: int) -> float:
    """
    Calculate the total interest paid over the life of the loan.
    """
    monthly_payment = calculate_monthly_payment(principal, annual_rate, term_months)
    total_paid = monthly_payment * term_months
    return round(total_paid - principal, 2)


def generate_repayment_schedule(principal: float, annual_rate: float, term_months: int) -> list:
    """
    Generate a month-by-month repayment schedule.

    Returns a list of dicts, one per month:
    [
        {
            "month": 1,
            "payment": 95000.0,
            "principal_paid": 80000.0,
            "interest_paid": 15000.0,
            "balance": 420000.0
        },
        ...
    ]
    """
    monthly_rate = annual_rate / 100 / 12
    monthly_payment = calculate_monthly_payment(principal, annual_rate, term_months)
    balance = principal
    schedule = []

    for month in range(1, term_months + 1):
        interest_paid = round(balance * monthly_rate, 2)
        principal_paid = round(monthly_payment - interest_paid, 2)
        balance = round(balance - principal_paid, 2)

        # Handle floating point on last month
        if month == term_months:
            balance = 0.0

        schedule.append({
            "month": month,
            "payment": round(monthly_payment, 2),
            "principal_paid": principal_paid,
            "interest_paid": interest_paid,
            "balance": max(balance, 0.0)
        })

    return schedule


def summarize_loan(principal: float, annual_rate: float, term_months: int) -> str:
    """
    Return a plain English summary of the loan terms.
    Used for injecting into AI responses or displaying directly.
    """
    monthly_payment = calculate_monthly_payment(principal, annual_rate, term_months)
    total_interest = calculate_total_interest(principal, annual_rate, term_months)
    total_paid = principal + total_interest

    return (
        f"Loan amount: {APP_CURRENCY} {principal:,.0f}\n"
        f"Interest rate: {annual_rate}% per year\n"
        f"Loan term: {term_months} months\n"
        f"Monthly payment: {APP_CURRENCY} {monthly_payment:,.0f}\n"
        f"Total interest: {APP_CURRENCY} {total_interest:,.0f}\n"
        f"Total amount to repay: {APP_CURRENCY} {total_paid:,.0f}"
    )
