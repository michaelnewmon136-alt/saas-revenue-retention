"""
Builds the MESSY product_usage table from the clean synthetic truth.
All data is synthetic. One row = one account in one paying month.
PLANTED PATTERN: about 70% of churning accounts show falling usage
in their last 3 paying months. The rest churn with no warning.
"""
import numpy as np
import pandas as pd

SEED = 42
rng = np.random.default_rng(SEED)

truth = pd.read_csv("data_generator/truth_subscription_months.csv")
truth = truth.sort_values(["account_id", "month_idx"]).reset_index(drop=True)

BASE_LOGINS = {0: 20, 1: 60, 2: 150, 3: 400}   # per month, by plan
BASE_USERS = {0: 3, 1: 10, 2: 30, 3: 100}
DECLINE_SHARE = 0.70

# 1. Find the last paying month before each cancellation
truth["next_mrr"] = truth.groupby("account_id")["mrr"].shift(-1)
truth["churn_flag"] = (truth["mrr"] > 0) & (truth["next_mrr"] == 0)
truth["decline_event"] = truth["churn_flag"] & (rng.random(len(truth)) < DECLINE_SHARE)

# 2. Usage multiplier: 1.0 normally, lower in the 3 months before churn
truth["factor"] = 1.0
for k, f in [(2, 0.75), (1, 0.55), (0, 0.35)]:
    hit = truth.groupby("account_id")["decline_event"].shift(-k).eq(True)
    truth.loc[hit, "factor"] = f

# 3. Usage only exists for paying months
use = truth[truth["mrr"] > 0].copy()
plan = use["plan_idx"].astype(int)
use["base"] = plan.map(BASE_LOGINS)
noise = rng.lognormal(0, 0.15, len(use))
use["logins"] = rng.poisson(use["base"] * use["factor"] * noise)
use["active_users"] = rng.poisson(plan.map(BASE_USERS) * use["factor"] * noise)

# 4. Summary BEFORE we corrupt anything: usage relative to the plan's normal
use["ratio"] = use["logins"] / use["base"]
ratio_by_factor = use.groupby("factor")["ratio"].mean().round(2)

# 5. Corrupt: some logins values are missing
missing = rng.random(len(use)) < 0.03
use["logins"] = use["logins"].astype(float)
use.loc[missing, "logins"] = np.nan

out = use[["account_id", "month_start", "logins", "active_users"]]
out.to_csv("data_generator/raw_product_usage.csv", index=False)

# 6. Add to the problem log (rerun-safe)
n_events = int(truth["decline_event"].sum())
n_churns = int(truth["churn_flag"].sum())
new_rows = pd.DataFrame([
    {"table": "product_usage", "problem": "missing logins value", "rows_affected": int(missing.sum())},
    {"table": "product_usage", "problem": "PLANTED: churn events with usage decline", "rows_affected": n_events},
])
log_path = "data_generator/problem_log.csv"
old = pd.read_csv(log_path)
old = old[old["table"] != "product_usage"]
pd.concat([old, new_rows], ignore_index=True).to_csv(log_path, index=False)

# 7. Print
print("Rows in raw_product_usage:", len(out))
print()
print(out.head(5).to_string(index=False))
print()
print("Churn events:", n_churns, "| with planted decline:", n_events)
print()
print("Average logins as a fraction of the plan's normal level:")
print("(1.0 = normal; factor 0.75 / 0.55 / 0.35 = 3 / 2 / 1 months before churn)")
print(ratio_by_factor.to_string())
print()
print("Missing logins:", int(out["logins"].isna().sum()))
print()
print(new_rows.to_string(index=False))