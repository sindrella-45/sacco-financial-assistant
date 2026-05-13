import os
import pandas as pd
from app.config.settings import USERS_CSV_PATH, APP_CURRENCY

# --- CSV columns ---
COLUMNS = [
    "user_id", "name", "monthly_income",
    "loan_amount", "loan_term_months", "interest_rate",
    "savings_goal", "occupation"
]


def _load_csv() -> pd.DataFrame:
    """Load users CSV, creating it with headers if it doesn't exist."""
    if not os.path.exists(USERS_CSV_PATH):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(USERS_CSV_PATH, index=False)
        return df
    return pd.read_csv(USERS_CSV_PATH)


def _save_csv(df: pd.DataFrame):
    """Save dataframe back to CSV."""
    df.to_csv(USERS_CSV_PATH, index=False)


def load_user_profile(user_id: str) -> dict:
    """
    Load a user's financial profile from users.csv.
    Returns an empty dict if the user doesn't exist yet.
    """
    df = _load_csv()
    row = df[df["user_id"] == user_id]

    if row.empty:
        return {}

    return row.iloc[0].to_dict()


def save_user_profile(user_id: str, data: dict):
    """
    Save or update a user's financial profile in users.csv.
    Creates a new row if user doesn't exist, updates if they do.
    """
    df = _load_csv()
    data["user_id"] = user_id

    if user_id in df["user_id"].values:
        for key, value in data.items():
            if key in df.columns:
                df.loc[df["user_id"] == user_id, key] = value
    else:
        new_row = {col: data.get(col, None) for col in COLUMNS}
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    _save_csv(df)


def build_memory_context(profile: dict) -> str:
    """
    Convert a user profile dict into a plain sentence
    that gets injected into the AI system prompt.
    Returns a default message if no profile exists yet.
    """
    if not profile:
        return "No financial profile found for this user yet. Ask them for their details."

    parts = []

    if profile.get("name"):
        parts.append(f"The member's name is {profile['name']}.")

    if profile.get("occupation"):
        parts.append(f"They work as a {profile['occupation']}.")

    if profile.get("monthly_income"):
        parts.append(
            f"Their monthly income is {APP_CURRENCY} "
            f"{float(profile['monthly_income']):,.0f}."
        )

    if profile.get("loan_amount") and profile.get("loan_term_months") and profile.get("interest_rate"):
        parts.append(
            f"They have an outstanding loan of {APP_CURRENCY} "
            f"{float(profile['loan_amount']):,.0f} "
            f"at {profile['interest_rate']}% interest "
            f"over {profile['loan_term_months']} months."
        )

    if profile.get("savings_goal"):
        parts.append(
            f"Their monthly savings goal is {APP_CURRENCY} "
            f"{float(profile['savings_goal']):,.0f}."
        )

    return " ".join(parts) if parts else "Profile exists but no financial details recorded yet."
