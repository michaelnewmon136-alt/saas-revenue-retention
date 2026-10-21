"""
Builds the MESSY subscriptions and subscription_events tables.
All data is synthetic. Both are derived from the clean truth table.
"""
import numpy as np
import pandas as pd

SEED = 42
rng = np.random.default_rng(SEED)
LAST_MONTH_IDX = 35

truth = pd.read_csv("data_generator/truth_subscription_months.csv")
truth = truth.sort_values(["account_id", "month_idx"]).reset_index(drop=True)
truth["prev_mrr"] = truth.groupby("account_id")["mrr"].shift(1)
plan_names = {0: "Starter", 1: "Growth", 2: "Scale", 3: "Enterprise"}

# ---------------------------------------------------------------
# TABLE 1: subscription_events
# ---------------------------------------------------------------
prev = truth["prev_mrr"]
cur = truth["mrr"]
truth["event_type"] = np.select(
    [prev.isna(),
     (prev > 0) & (cur > prev),
     (prev > 0) & (cur > 0) & (cur < prev),
     (prev > 0) & (cur == 0),
     (prev == 0) & (cur > 0)],
    ["new", "upgrade", "downgrade", "cancel", "reactivate"],
    default="none",
)
ev = truth[truth["event_type"] != "none"].copy()
ev["old_mrr"] = ev["prev_mrr"].fillna(0)
ev["new_mrr"] = ev["mrr"]

# Reconciliation BEFORE corrupting anything
net_change = float((ev["new_mrr"] - ev["old_mrr"]).sum())
final_mrr = float(truth.loc[truth["month_idx"] == LAST_MONTH_IDX, "mrr"].sum())

ev["event_date"] = ev["month_start"]
ev = ev.sort_values(["event_date", "account_id"]).reset_index(drop=True)
ev["event_id"] = np.arange(1, len(ev) + 1)
ev = ev[["event_id", "account_id", "event_date", "event_type", "old_mrr", "new_mrr"]]
clean_event_counts = ev["event_type"].value_counts()

# Corruption 1: inconsistent event type labels
variants = {
    "new": ["New", "NEW"],
    "upgrade": ["Upgrade", "UPGRADE"],
    "downgrade": ["Downgrade", "DOWNGRADE"],
    "cancel": ["Cancelled", "canceled", "churned"],
    "reactivate": ["Reactivated", "reactivation"],
}
messy = rng.random(len(ev)) < 0.08
ev["event_type"] = ev["event_type"].astype(object)
for i in ev.index[messy]:
    ev.at[i, "event_type"] = rng.choice(variants[ev.at[i, "event_type"]])

# Corruption 2: missing new_mrr
miss = rng.random(len(ev)) < 0.02
ev["new_mrr"] = ev["new_mrr"].astype(float)
ev.loc[miss, "new_mrr"] = np.nan

# Corruption 3: duplicate events
n_dup_ev = 60
ev = pd.concat([ev, ev.sample(n=n_dup_ev, random_state=SEED)], ignore_index=True)
ev.to_csv("data_generator/raw_subscription_events.csv", index=False)

# ---------------------------------------------------------------
# TABLE 2: subscriptions (one row per continuous period on one plan)
# ---------------------------------------------------------------
paying = truth[truth["mrr"] > 0].copy()
g = paying.groupby("account_id")
prev_plan = g["plan_idx"].shift(1)
prev_idx = g["month_idx"].shift(1)
new_period = ((prev_plan != paying["plan_idx"]) |
              (paying["month_idx"] != prev_idx + 1)).astype(int)
paying["period_no"] = new_period.groupby(paying["account_id"]).cumsum()

subs = (paying.groupby(["account_id", "period_no"])
        .agg(plan_idx=("plan_idx", "first"), mrr=("mrr", "first"),
             start_date=("month_start", "min"), end_date=("month_start", "max"),
             last_idx=("month_idx", "max"))
        .reset_index())
subs["plan"] = subs["plan_idx"].astype(int).map(plan_names)
subs["status"] = np.where(subs["last_idx"] == LAST_MONTH_IDX, "active", "ended")
subs["subscription_id"] = np.arange(1, len(subs) + 1)
n_active_clean = int((subs["status"] == "active").sum())
n_ended_clean = int((subs["status"] == "ended").sum())

ended = subs.index[subs["status"] == "ended"]

# Corruption 4: ended subscriptions with a missing end date
no_end = ended[rng.random(len(ended)) < 0.08]
subs.loc[no_end, "end_date"] = None

# Corruption 5: ended subscriptions whose status still says active
stale = ended[rng.random(len(ended)) < 0.05]
subs["status"] = subs["status"].astype(object)
subs.loc[stale, "status"] = "active"

# Corruption 6: inconsistent status labels
status_variants = {"active": ["Active", "ACTIVE", "live"],
                   "ended": ["Ended", "ENDED", "cancelled"]}
messy_s = rng.random(len(subs)) < 0.08
for i in subs.index[messy_s]:
    subs.at[i, "status"] = rng.choice(status_variants[subs.at[i, "status"]])

out = subs[["subscription_id", "account_id", "plan", "mrr",
            "start_date", "end_date", "status"]]
out.to_csv("data_generator/raw_subscriptions.csv", index=False)

# ---------------------------------------------------------------
# Problem log (rerun-safe)
# ---------------------------------------------------------------
new_rows = pd.DataFrame([
    {"table": "subscription_events", "problem": "inconsistent event type labels", "rows_affected": int(messy.sum())},
    {"table": "subscription_events", "problem": "missing new_mrr", "rows_affected": int(miss.sum())},
    {"table": "subscription_events", "problem": "duplicate event rows", "rows_affected": n_dup_ev},
    {"table": "subscriptions", "problem": "ended but end_date missing", "rows_affected": int(len(no_end))},
    {"table": "subscriptions", "problem": "ended but status says active", "rows_affected": int(len(stale))},
    {"table": "subscriptions", "problem": "inconsistent status labels", "rows_affected": int(messy_s.sum())},
])
log_path = "data_generator/problem_log.csv"
old = pd.read_csv(log_path)
old = old[~old["table"].isin(["subscription_events", "subscriptions"])]
pd.concat([old, new_rows], ignore_index=True).to_csv(log_path, index=False)

# ---------------------------------------------------------------
# Print
# ---------------------------------------------------------------
print("Rows in raw_subscription_events:", len(ev))
print("Rows in raw_subscriptions:", len(out))
print()
print("Clean event counts (before corruption):")
print(clean_event_counts.to_string())
print()
print("RECONCILIATION: sum of all event MRR changes =", int(net_change))
print("RECONCILIATION: total MRR in final month     =", int(final_mrr))
print("Match:", net_change == final_mrr)
print()
print("Subscriptions before corruption: active =", n_active_clean,
      "| ended =", n_ended_clean)
print()
print(out.head(5).to_string(index=False))
print()
print(new_rows.to_string(index=False))