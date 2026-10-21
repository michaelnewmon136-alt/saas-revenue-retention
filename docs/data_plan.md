# Data Plan

All data is synthetic. Every table is derived from one hidden "truth"
table (what each account really paid each month), then deliberately
corrupted so the dbt models have something real to clean.

## Tables

| Table | One row represents | Derived from |
|---|---|---|
| accounts | one customer account | truth_accounts |
| subscriptions | one subscription period on one plan | truth plan changes |
| subscription_events | one neSw / upgrade / downgrade / cancel / reactivate event | truth month-to-month changes |
| subscription_months | one account-month as the billing system sees it | truth_subscription_months |
| invoices | one invoice (including failed payments) | truth MRR |
| product_usage | one account-month of usage | truth + planted usage decline before churn |
| support_tickets | one support ticket | truth + planted escalations before churn |

## Problems to plant (each one is counted, so we can test the cleaning)

- Duplicate rows in subscription_months
- Missing values (for example, missing churn dates and missing industry)
- Inconsistent status labels ("active", "Active", "ACTIVE", "live")
- Failed payments that are later retried
- Annual plans billed once a year (cash is not MRR)
- A subscription marked "active" while its MRR is 0

## Rule

Every planted problem is logged in a file, so we can prove later that the
dbt models found and fixed all of them.