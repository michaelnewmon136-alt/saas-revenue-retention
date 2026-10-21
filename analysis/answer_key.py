"""
ANSWER KEY: computes the MRR bridge directly from the synthetic truth table.
Slow but obviously correct. Later we compare dbt's results against this.
"""
import pandas as pd

truth = pd.read_csv("data_generator/truth_subscription_months.csv")

# Table: one row per account, one column per month, values = MRR (0 if not paying)
t = (truth.pivot(index="account_id", columns="month_idx", values="mrr")
          .reindex(columns=range(36))
          .fillna(0))

rows = []
for m in range(1, 36):
    prev, cur = t[m - 1], t[m]
    had_before = t.loc[:, : m - 1].sum(axis=1) > 0   # paid at any earlier month

    new = cur[(prev == 0) & (cur > 0) & ~had_before].sum()
    react = cur[(prev == 0) & (cur > 0) & had_before].sum()
    churn = prev[(prev > 0) & (cur == 0)].sum()
    both = (prev > 0) & (cur > 0)
    expansion = (cur - prev)[both & (cur > prev)].sum()
    contraction = (prev - cur)[both & (cur < prev)].sum()

    opening, closing = prev.sum(), cur.sum()
    assert closing == opening + new + react + expansion - contraction - churn, \
        f"Bridge broke at month {m}"

    cohort = prev > 0
    rows.append({
        "month_idx": m,
        "opening": opening,
        "new": new,
        "expansion": expansion,
        "reactivation": react,
        "contraction": -contraction,
        "churn": -churn,
        "closing": closing,
        "grr": (opening - contraction - churn) / opening,
        "nrr": cur[cohort].sum() / opening,
    })

bridge = pd.DataFrame(rows)
bridge.to_csv("analysis/answer_key_bridge.csv", index=False)
print("Bridge reconciled for all 35 months.")
print()
print(bridge.round(3).tail(6).to_string(index=False))