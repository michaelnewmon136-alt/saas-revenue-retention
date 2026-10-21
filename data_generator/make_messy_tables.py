"""
Builds MESSY source tables from the clean synthetic truth.
All data is synthetic. Every planted problem is logged so we can
later prove the cleaning models found and fixed it.
"""
import numpy as np
import pandas as pd

SEED = 42
rng = np.random.default_rng(SEED)

truth_accounts = pd.read_csv("data_generator/truth_accounts.csv")
truth_months = pd.read_csv("data_generator/truth_subscription_months.csv")
problem_log = []  # one entry per planted problem type


def log(table, problem, count):
    problem_log.append({"table": table, "problem": problem, "rows_affected": count})


def make_accounts(clean: pd.DataFrame) -> pd.DataFrame:
    df = clean.copy()
    df["signup_date"] = df["signup_month_idx"].apply(
        lambda i: (pd.Timestamp("2023-01-01") + pd.DateOffset(months=int(i))).strftime("%Y-%m-%d")
    )
    df = df.drop(columns=["signup_month_idx"])

    # Problem 1: inconsistent segment labels
    variants = {
        "SMB": ["SMB", "smb", "Smb", "Small Business"],
        "Mid-Market": ["Mid-Market", "mid-market", "Mid Market"],
        "Enterprise": ["Enterprise", "enterprise", "ENTERPRISE"],
    }
    messy_idx = rng.random(len(df)) < 0.15
    df["segment"] = df["segment"].astype(object)
    changed = 0
    for i in df.index[messy_idx]:
        old = df.at[i, "segment"]
        new = rng.choice(variants[old])
        if new != old:
            changed += 1
        df.at[i, "segment"] = new
    log("accounts", "inconsistent segment labels", changed)

    # Problem 2: missing industry
    missing_idx = rng.random(len(df)) < 0.08
    df["industry"] = df["industry"].astype(object)
    df.loc[missing_idx, "industry"] = None
    log("accounts", "missing industry", int(missing_idx.sum()))

    # Problem 3: duplicate account rows
    dup = df.sample(n=20, random_state=SEED)
    df = pd.concat([df, dup], ignore_index=True)
    log("accounts", "duplicate account rows", 20)

    return df


def make_subscription_months(clean: pd.DataFrame) -> pd.DataFrame:
    df = clean[["account_id", "month_start", "plan_idx", "mrr"]].copy()
    plan_names = {0: "Starter", 1: "Growth", 2: "Scale", 3: "Enterprise"}
    df["plan"] = df["plan_idx"].map(plan_names)
    df = df.drop(columns=["plan_idx"])

    # Status labels: consistent at first, then corrupted below
    df["status"] = np.where(df["mrr"] > 0, "active", "cancelled")

    # Problem 4: inconsistent status labels (active rows only)
    active_idx = df.index[df["status"] == "active"]
    messy = active_idx[rng.random(len(active_idx)) < 0.10]
    df["status"] = df["status"].astype(object)
    changed = 0
    for i in messy:
        new = rng.choice(["Active", "ACTIVE", "live"])
        df.at[i, "status"] = new
        changed += 1
    log("subscription_months", "inconsistent status labels", changed)

    # Problem 5: status says active, but MRR is 0 (cancelled rows relabelled)
    cancelled_idx = df.index[df["status"] == "cancelled"]
    wrong = cancelled_idx[rng.random(len(cancelled_idx)) < 0.05]
    df.loc[wrong, "status"] = "active"
    log("subscription_months", "status active but MRR is 0", len(wrong))

    # Problem 6: missing MRR values (set to blank on active rows)
    still_active = df.index[df["mrr"] > 0]
    blank = still_active[rng.random(len(still_active)) < 0.01]
    df["mrr"] = df["mrr"].astype(float)
    df.loc[blank, "mrr"] = np.nan
    log("subscription_months", "missing MRR on a paying month", len(blank))

    # Problem 7: duplicate rows for the same account-month
    n_dup = 150
    dup = df.sample(n=n_dup, random_state=SEED)
    df = pd.concat([df, dup], ignore_index=True)
    log("subscription_months", "duplicate account-month rows", n_dup)

    return df


if __name__ == "__main__":
    accounts = make_accounts(truth_accounts)
    accounts.to_csv("data_generator/raw_accounts.csv", index=False)

    sub_months = make_subscription_months(truth_months)
    sub_months.to_csv("data_generator/raw_subscription_months.csv", index=False)

    log_df = pd.DataFrame(problem_log)
    log_df.to_csv("data_generator/problem_log.csv", index=False)

    print("Rows in raw_accounts:", len(accounts))
    print("Rows in raw_subscription_months:", len(sub_months))
    print()
    print(sub_months.head(6).to_string(index=False))
    print()
    print("Status labels found:")
    print(sub_months["status"].value_counts().to_string())
    print()
    print("Missing MRR values:", int(sub_months["mrr"].isna().sum()))
    print()
    print(log_df.to_string(index=False))