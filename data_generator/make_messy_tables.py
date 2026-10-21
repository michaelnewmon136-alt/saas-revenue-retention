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


if __name__ == "__main__":
    accounts = make_accounts(truth_accounts)
    accounts.to_csv("data_generator/raw_accounts.csv", index=False)

    log_df = pd.DataFrame(problem_log)
    log_df.to_csv("data_generator/problem_log.csv", index=False)

    print("Rows in raw_accounts:", len(accounts))
    print()
    print(accounts.head(8).to_string(index=False))
    print()
    print("Segment labels found:")
    print(accounts["segment"].value_counts().to_string())
    print()
    print("Missing industry values:", int(accounts["industry"].isna().sum()))
    print()
    print(log_df.to_string(index=False))