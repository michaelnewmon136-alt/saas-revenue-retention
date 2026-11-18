# Recommendation Memo: Retention Priority

> **All data in this project is synthetic.** The findings below describe a simulated company. They show that the analysis pipeline works. They are not findings about a real business, and no real savings are claimed.

## The question

If the company could fund only one retention intervention, which customer segment should be investigated first, why, and how would we know it worked?

## Recommendation

**Investigate the SMB segment first.**

## Why (what the simulated data shows)

1. **Growth is slowing because leakage grew faster than additions.** Gross added MRR rose each year (128K, 186K, 243K), but lost MRR rose faster (29K, 61K, 133K). In 2025, about $55 was lost for every $100 added, and net growth fell from 125K in 2024 to 110K in 2025.
2. **Existing revenue is shrinking before expansion.** Trailing 12-month NRR is 87.6% and GRR is 65.4%. Expansion hides a large leak.
3. **SMB has the weakest retention.** Twelve-month logo retention was 71.0% (2023 cohort) and 63.7% (2024 cohort) for SMB, versus 77% and 75% for Mid-Market and 85% and 88% for Enterprise.
4. **SMB is the largest group.** It holds about 983 of 1,500 accounts, so a gain here affects the most customers.
5. **Revenue is not concentrated.** The largest account is under 1% of MRR, so the problem is broad, not a few large accounts.

## What this does not show

- SMB churn and early-tenure churn were **planted** in the generator, so finding them tests the pipeline. It is not a discovery.
- Logo retention counts accounts, not dollars. An SMB account is worth much less than an Enterprise one, so **revenue** impact must be checked before committing budget.
- The Enterprise tier contributes the most **contraction** dollars (about 60% of the total). A second investigation there is worth considering.
- Low usage and escalations coincide with churn here, but that is correlation. It does not show that raising usage or resolving tickets would prevent churn.
- Small groups (for example about 40 Enterprise accounts a year) swing by chance. The 2023 to 2024 SMB drop has not been tested against random variation.

## Proposed validation plan (not a claim of results)

1. **Define the intervention first.** For example, proactive outreach to SMB accounts whose usage falls below 70% of plan norm for a month, or who raise an escalated ticket.
2. **Run a randomized test.** Among eligible SMB accounts, randomly assign half to receive the intervention and half to continue as usual. Random assignment is what separates cause from correlation.
3. **Pre-register the success metric.** Twelve-month SMB logo retention and trailing 12-month GRR for the group, measured per account from the date of assignment.
4. **Set the sample size before starting.** Use a power calculation, so the test is large enough to detect the smallest improvement worth paying for.
5. **Check guardrails.** Support cost per account, contraction (a retained account that downgrades is a weak win), and customer satisfaction.
6. **Decide in advance.** Scale the intervention only if the treated group beats the control group by the agreed margin, with the result unlikely to be chance. Otherwise stop.

## Evidence that would change this recommendation

- If revenue retention (not logo retention) is fine for SMB but poor for Enterprise contraction, prioritize Enterprise instead.
- If the 2023 to 2024 SMB drop is within random variation, prioritize by cost to fix rather than by the gap.