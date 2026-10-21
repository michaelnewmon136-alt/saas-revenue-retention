"""
Builds the MESSY invoices table from the clean synthetic truth.
All data is synthetic. One row = one payment attempt.
Annual accounts are invoiced once per 12 months for 12x the monthly MRR.
"""
import numpy as np
import pandas as pd

SEED = 42
rng = np.random.default_rng(SEED)

truth_accounts = pd.read_csv("data_generator/truth_accounts.csv")
truth_months = pd.read_csv("data_generator/truth_subscription_months.csv")

ANNUAL_SHARE = {"SMB": 0.10, "Mid-Market": 0.30, "Enterprise": 0.50}
FAIL_RATE = 0.06
RETRY_SUCCESS_RATE = 0.70

# 1. Decide which accounts pay annually
accounts = truth_accounts[["account_id", "segment"]].copy()
is_annual = rng.random(len(accounts)) < accounts["segment"].map(ANNUAL_SHARE)
accounts["billing_cycle"] = np.where(is_annual, "annual", "monthly")

# 2. Keep only months where the account really paid MRR
paying = truth_months[truth_months["mrr"] > 0].merge(accounts, on="account_id")
paying = paying.sort_values(["account_id", "month_idx"]).reset_index(drop=True)
paying["first_idx"] = paying.groupby("account_id")["month_idx"].transform("min")

# 3. Monthly accounts: invoice every paying month.
#    Annual accounts: invoice every 12th month after their first paying month.
due_annual = (paying["billing_cycle"] == "annual") & \
             ((paying["month_idx"] - paying["first_idx"]) % 12 == 0)
due_monthly = paying["billing_cycle"] == "monthly"
inv = paying[due_monthly | due_annual].copy().reset_index(drop=True)

inv["amount"] = np.where(inv["billing_cycle"] == "annual", inv["mrr"] * 12, inv["mrr"])
inv["invoice_date"] = pd.to_datetime(inv["month_start"])
inv["invoice_id"] = np.arange(1, len(inv) + 1)
inv["attempt"] = 1
inv["status"] = "paid"

# 4. Failed payments, and retries that sometimes succeed
fail = rng.random(len(inv)) < FAIL_RATE
retry_ok = fail & (rng.random(len(inv)) < RETRY_SUCCESS_RATE)
inv.loc[fail, "status"] = "failed"

retries = inv[retry_ok].copy()
retries["attempt"] = 2
retries["status"] = "paid"
retries["invoice_date"] = retries["invoice_date"] + pd.Timedelta(days=5)

cols = ["invoice_id", "account_id", "invoice_date", "amount",
        "billing_cycle", "attempt", "status"]
invoices = pd.concat([inv[cols], retries[cols]])
invoices = invoices.sort_values(["invoice_id", "attempt"]).reset_index(drop=True)
invoices["invoice_date"] = invoices["invoice_date"].dt.strftime("%Y-%m-%d")
invoices.to_csv("data_generator/raw_invoices.csv", index=False)

# 5. Add to the problem log (remove old invoice entries first, so reruns are safe)
n_annual = int((inv["billing_cycle"] == "annual").sum())
new_rows = pd.DataFrame([
    {"table": "invoices", "problem": "failed first payment attempt", "rows_affected": int(fail.sum())},
    {"table": "invoices", "problem": "failed then retried successfully", "rows_affected": int(retry_ok.sum())},
    {"table": "invoices", "problem": "failed and never recovered", "rows_affected": int(fail.sum() - retry_ok.sum())},
    {"table": "invoices", "problem": "annual invoices (cash is not MRR)", "rows_affected": n_annual},
])
log_path = "data_generator/problem_log.csv"
old = pd.read_csv(log_path)
old = old[old["table"] != "invoices"]
pd.concat([old, new_rows], ignore_index=True).to_csv(log_path, index=False)

# 6. Print a summary
paid = invoices[invoices["status"] == "paid"]
print("Rows in raw_invoices:", len(invoices))
print()
print(invoices.head(6).to_string(index=False))
print()
print("Status counts:")
print(invoices["status"].value_counts().to_string())
print()
print("Billing cycle of invoices:")
print(invoices.drop_duplicates("invoice_id")["billing_cycle"].value_counts().to_string())
print()
print("Total cash collected (paid rows): ", round(paid["amount"].sum()))
print("Total MRR summed over all months: ", int(truth_months["mrr"].sum()))
print()
print(new_rows.to_string(index=False))