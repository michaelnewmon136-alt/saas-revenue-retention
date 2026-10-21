# Metric Contract

This document defines how every metric in this project is calculated.
All data is synthetic.

## 1. Grain
One row represents one account in one calendar month, starting from the month the account signed up. It records the plan the account was on and its MRR that month. There is at most one row per account per month.
## 2. Active customer
An account is active in a month when its MRR in that month is greater than 0. An account with MRR of 0 has churned, or has not yet reactivated.
## 3. Annual plans
An annual plan is converted to MRR by dividing the annual price by 12. The cash received from an annual prepayment is not MRR. It is tracked separately as invoiced cash, so cash and recurring revenue are never mixed in one number.
## 4. Reactivation
A reactivation is an account that had MRR greater than 0 in an earlier month, had MRR of 0 in the previous month, and has MRR greater than 0 again in the current month. A first-ever paying month is New, not Reactivation.
## 5. Duplicates and conflicting statuses
When two records describe the same subscription and month, we keep the most recently updated record and discard the others. When a status field contradicts the billing data (for example, a status of "active" with no paid invoice and no MRR), the billing data wins. Every discarded or overridden record is counted and reported, never silently dropped.
## 6. Missing churn dates
A missing churn date is not treated as proof that the account is still active. We use the monthly MRR to decide: an account is active while it has MRR greater than 0 in the latest observed month. If an account has MRR of 0 and no churn date, we infer the churn month from the first month its MRR drops to 0, and flag the date as inferred. An account with no churn date that is still paying at the end of the data is treated as active, not as an account that will never churn.
## 7. NRR and GRR
NRR is calculated as: (TO FILL)
The denominator is: (TO FILL)
Reactivations are treated as: (TO FILL)

## 8. Reporting window
We report NRR over: (TO FILL)