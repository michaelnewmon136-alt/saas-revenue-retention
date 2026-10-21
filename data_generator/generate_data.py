"""
SYNTHETIC DATA GENERATOR for the saas-revenue-retention project.
All data is fictional and randomly generated.
Nothing here represents a real company.
"""
import numpy as np
import pandas as pd

SEED = 42
rng = np.random.default_rng(SEED)

N_ACCOUNTS = 1500
N_MONTHS = 36
START = pd.Timestamp("2023-01-01")

SEGMENTS = ["SMB", "Mid-Market", "Enterprise"]
SEG_WEIGHTS = [0.65, 0.28, 0.07]

PRICE = {0: 49, 1: 199, 2: 599, 3: 1999}  # monthly price by plan number
START_PLAN_PROBS = {
    "SMB": [0.70, 0.25, 0.05, 0.00],
    "Mid-Market": [0.10, 0.50, 0.35, 0.05],
    "Enterprise": [0.00, 0.10, 0.50, 0.40],
}
BASE_CHURN = {"SMB": 0.030, "Mid-Market": 0.015, "Enterprise": 0.007}
P_UPGRADE, P_DOWNGRADE, P_REACTIVATE = 0.020, 0.015, 0.010


def build_accounts() -> pd.DataFrame:
    # Later months get more signups, so acquisition grows over time
    month_weights = np.linspace(1.0, 2.0, N_MONTHS)
    month_weights = month_weights / month_weights.sum()

    signup_idx = rng.choice(N_MONTHS, size=N_ACCOUNTS, p=month_weights)
    segment = rng.choice(SEGMENTS, size=N_ACCOUNTS, p=SEG_WEIGHTS)

    return pd.DataFrame({
        "account_id": np.arange(1, N_ACCOUNTS + 1),
        "signup_month_idx": signup_idx,
        "segment": segment,
        "industry": rng.choice(["Tech", "Retail", "Health", "Finance", "Education"], N_ACCOUNTS),
        "channel": rng.choice(["Organic", "Paid", "Partner", "Outbound"], N_ACCOUNTS),
    })


def simulate_truth(accounts: pd.DataFrame) -> pd.DataFrame:
    """One row per account per month since signup: the 'real' plan and MRR."""
    rows = []
    for a in accounts.itertuples():
        plan = rng.choice(4, p=START_PLAN_PROBS[a.segment])
        active = True
        for m in range(a.signup_month_idx, N_MONTHS):
            if m > a.signup_month_idx:
                tenure = m - a.signup_month_idx
                if active:
                    p_churn = BASE_CHURN[a.segment] * (2.0 if tenure < 6 else 1.0)
                    r = rng.random()
                    if r < p_churn:
                        active = False
                    elif r < p_churn + P_UPGRADE and plan < 3:
                        plan += 1
                    elif r < p_churn + P_UPGRADE + P_DOWNGRADE and plan > 0:
                        plan -= 1
                else:
                    if rng.random() < P_REACTIVATE:
                        active = True
            rows.append((a.account_id, m, int(plan) if active else None,
                         PRICE[int(plan)] if active else 0))
    truth = pd.DataFrame(rows, columns=["account_id", "month_idx", "plan_idx", "mrr"])
    truth["month_start"] = truth["month_idx"].apply(
        lambda i: START + pd.DateOffset(months=int(i))
    )
    return truth


if __name__ == "__main__":
    accounts = build_accounts()
    truth = simulate_truth(accounts)
    print("Rows in truth table:", len(truth))
    print()
    print(truth.head())
    print()
    monthly = truth.groupby("month_idx")["mrr"].sum()
    print("Total MRR, first 3 months:")
    print(monthly.head(3))
    print("Total MRR, last 3 months:")
    print(monthly.tail(3))
    print()
    accounts.to_csv("data_generator/truth_accounts.csv", index=False)
    truth.to_csv("data_generator/truth_subscription_months.csv", index=False)
    print("Saved: truth_accounts.csv and truth_subscription_months.csv")