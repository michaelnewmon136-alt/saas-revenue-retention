"""
Builds the MESSY support_tickets table from the clean synthetic truth.
All data is synthetic. One row = one support ticket.
PLANTED PATTERN: about 40% of churn events get an extra escalated
ticket in the account's last paying month.
"""
import numpy as np
import pandas as pd

SEED = 42
rng = np.random.default_rng(SEED)

truth = pd.read_csv("data_generator/truth_subscription_months.csv")
truth = truth.sort_values(["account_id", "month_idx"]).reset_index(drop=True)

BASE_RATE = {0: 0.10, 1: 0.20, 2: 0.35, 3: 0.60}  # tickets per month, by plan
BASE_ESCALATION = 0.05
PRE_CHURN_SHARE = 0.40

# 1. Find the last paying month before each cancellation
truth["next_mrr"] = truth.groupby("account_id")["mrr"].shift(-1)
truth["churn_flag"] = (truth["mrr"] > 0) & (truth["next_mrr"] == 0)
truth["warn_event"] = truth["churn_flag"] & (rng.random(len(truth)) < PRE_CHURN_SHARE)

# 2. Ordinary tickets: a random number per paying month
paying = truth[truth["mrr"] > 0].copy()
rate = paying["plan_idx"].astype(int).map(BASE_RATE)
paying["n_tickets"] = rng.poisson(rate)
base = paying.loc[paying.index.repeat(paying["n_tickets"]),
                  ["account_id", "month_start"]].reset_index(drop=True)
base["escalated"] = rng.random(len(base)) < BASE_ESCALATION
base["planted"] = False

# 3. Planted tickets: one escalated ticket in the last paying month
warn = paying.loc[paying["warn_event"], ["account_id", "month_start"]].copy()
warn["escalated"] = True
warn["planted"] = True

tickets = pd.concat([base, warn], ignore_index=True)

# 4. Dates, ids, categories, priorities
days = rng.integers(0, 28, len(tickets))
tickets["created_date"] = pd.to_datetime(tickets["month_start"]) + pd.to_timedelta(days, unit="D")
tickets = tickets.sort_values(["created_date", "account_id"]).reset_index(drop=True)
tickets["ticket_id"] = np.arange(1, len(tickets) + 1)
tickets["category"] = rng.choice(["billing", "bug", "how-to", "feature request"], len(tickets))
normal = rng.choice(["low", "medium"], len(tickets), p=[0.6, 0.4])
tickets["priority"] = np.where(tickets["escalated"], "high", normal)
tickets["priority"] = tickets["priority"].astype(object)

# 5. Corrupt: inconsistent priority labels, then missing priority
variants = {"high": ["High", "HIGH"], "medium": ["Medium", "MED"], "low": ["Low", "LOW"]}
messy = rng.random(len(tickets)) < 0.10
for i in tickets.index[messy]:
    tickets.at[i, "priority"] = rng.choice(variants[tickets.at[i, "priority"]])

missing = (rng.random(len(tickets)) < 0.04) & ~messy
tickets.loc[missing, "priority"] = None

tickets["created_date"] = tickets["created_date"].dt.strftime("%Y-%m-%d")
out = tickets[["ticket_id", "account_id", "created_date", "category", "priority", "escalated"]]
out.to_csv("data_generator/raw_support_tickets.csv", index=False)

# 6. Add to the problem log (rerun-safe)
n_churns = int(truth["churn_flag"].sum())
n_planted = int(warn.shape[0])
new_rows = pd.DataFrame([
    {"table": "support_tickets", "problem": "inconsistent priority labels", "rows_affected": int(messy.sum())},
    {"table": "support_tickets", "problem": "missing priority", "rows_affected": int(missing.sum())},
    {"table": "support_tickets", "problem": "PLANTED: escalated ticket before churn", "rows_affected": n_planted},
])
log_path = "data_generator/problem_log.csv"
old = pd.read_csv(log_path)
old = old[old["table"] != "support_tickets"]
pd.concat([old, new_rows], ignore_index=True).to_csv(log_path, index=False)

# 7. Print
print("Rows in raw_support_tickets:", len(out))
print()
print(out.head(5).to_string(index=False))
print()
print("Priority labels found:")
print(out["priority"].value_counts(dropna=False).to_string())
print()
print("Escalated tickets:", int(out["escalated"].sum()))
print("Churn events:", n_churns, "| with planted escalation:", n_planted)
print()
print(new_rows.to_string(index=False))