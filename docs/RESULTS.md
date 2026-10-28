# Results: estimated protection and observed cost

The daily load consumes 4 MWh (244 MWh per area over 61 days), with maximum 1 MW in each quarter. All costs below include the common €0.50/MWh fee. They exclude real tariffs, taxes, imbalance and execution costs.

| Area / policy | Total observed cost | Savings vs uniform | Worst excess cost | Realized CVaR90 |
|---|---:|---:|---:|---:|
| DK1 €0 / €25 / €100 / mean-only | €12,499.79 | €20,062.64 | −€45.22 | −€97.37 |
| DK1 uniform | €32,562.43 | €0 | €0 | €0 |
| DK2 €0 budget | €13,899.35 | €19,158.25 | −€50.27 | −€99.30 |
| DK2 €25 budget | €13,777.20 | €19,280.41 | −€50.27 | −€99.22 |
| DK2 €100 / mean-only | €13,667.39 | €19,390.22 | −€50.27 | −€97.88 |
| DK2 uniform | €33,057.61 | €0 | €0 | €0 |

Excess cost means cost above the uniform schedule, not absolute cost. A negative worst excess cost means even the least favorable observed day saved money. Realized CVaR90 averages the worst 10% probability mass across the 61 daily excess costs (6.1 observations), distinct from the daily planning estimate over 28 historical paths (2.8 observations).

## When the risk control matters

In DK1, mean-only estimated CVaR is already below zero on all 61 days. All three budgets leave the schedule and cost unchanged. In DK2, mean-only CVaR exceeds €25 on five days: 24, 25, 28, 29 and 30 September. Its maximum is approximately €69.02. Therefore €100 never binds, while €0 and €25 change decisions on those five days.

Over the full DK2 period the €0 policy costs €231.96 more than mean-only; the €25 policy costs €109.81 more. Tighter budgets improve the empirical realized tail metric slightly, but do not change the worst day in this short sample. No policy is chosen as a universally optimal trade-off. The UI starts at €25 by predeclared convention, and the constrained-day shortcut uses planned risk, not observed outcomes.

## Risk estimates are not guarantees

Observed excess cost exceeds estimated VaR90 on 7 of 61 days in DK1 and 8 of 61 in DK2 for every optimized policy. These correspond to empirical threshold coverage of 88.5% and 86.9%. The small dependent sample, scenario reuse for optimization and changing forecast regimes prevent a formal coverage guarantee or strong statistical inference.

No realized outcome exceeds its nonnegative planning budget in this sample. That does not make CVaR a maximum-loss limit: it is an estimated average tail cost, and individual future outcomes can exceed it. Nor does the absence of observed loss imply a risk-free load-shifting opportunity. This flexible synthetic load has substantially more freedom than many real processes.

## Verification and scope

All 488 optimization runs returned status 0; the 122 uniform-policy records are direct baselines. Every schedule meets 4 MWh/day and 1 MW limits, and independent fractional-tail calculations verify every stated risk budget. Reports contain 610 policy-day records and 58,560 quarter-hour records, with every source residual timestamp retained.

This experiment extends familiar July–September Nordcast data; it is not new prospective forecast validation. The July warm-up is followed by chronological adaptation using eligible earlier outcomes. Entire historical error vectors preserve within-day dependence but not next-day regimes, seasonal matching or a calibrated probability distribution. Twenty-eight scenarios remain only 28 scenarios.

Next research steps would be untouched seasons, authentic publication-time archives, realistic process constraints and tariff schedules, and separate scenario-model calibration. Those extensions are not represented as completed here.
