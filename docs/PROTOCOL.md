# Harbor: frozen research protocol

Written 28 October 2026 before calculating this experiment's procurement results.

## Research question

How does constraining scenario-based tail cost change a flexible electricity schedule, and does the estimated protection hold when actual prices arrive? This extends familiar Nordcast data; it is not an untouched forecast validation or a live procurement service. No policy will be selected after inspecting realized savings.

## Data and chronology

Reuse the exact Nordcast predictions archive from commit a8244399f0886d07ddafbe1d71b757abcb97ae95, SHA256 11dc413033af9ddfda6e16b2b9d1a2a067ad6482e186453282d6c1f38625937c. Original June validation selected ridge for DK1 and boosted median for DK2. Retain those choices. Source: Energinet DayAheadPrices, EUR/MWh, CC BY 4.0. The archive can include price revisions and is not historical-vintage data.

Use July 2026 for initial residual history. Evaluate every day from 1 August through 30 September 2026: 61 days in each area. Decision is 10:00 Copenhagen time on D−1. A historical day's complete forecast errors become eligible only after its last delivery interval ends plus 24 hours. This matches the conservative research delay of the upstream model. Select the most recent 28 eligible complete days; stop if fewer are available. Record every scenario's source day and availability time.

Each scenario is the target day's frozen selected-model forecast plus one historical day's entire vector of actual minus forecast errors. Keep all 96 local quarter-hour residuals together; do not independently shuffle periods or inflate the scenario count by resampling. Assign equal weight 1/28. No residual centering, volatility scaling, weekday matching or learned weights. All replay days have 96 quarters. Reject incompatible day lengths rather than interpolating DST days.

Historical residuals may span monthly model updates. Later scenarios can use earlier evaluation observations only after the delay. This is prequential adaptation, not hindsight optimization. Target-day actual prices never enter scenario construction or optimization.

## Flexible load and risk constraint

A hypothetical fully interruptible load must consume exactly 4 MWh each day. Grid power can vary continuously between 0 and 1 MW every quarter hour, so each quantity is between 0 and 0.25 MWh. There is no continuity, ramp, minimum-run or switching constraint. Baseline is uniform demand, 4/96 MWh per quarter. A constant fee of EUR 0.50/MWh applies equally to all policies and cancels in cost differences.

For scenario s and schedule q, excess cost L_s = price_s dot (q − uniform). Positive means more expensive than uniform in that same scenario. Risk is empirical CVaR at alpha=0.90: the average of the worst 10% probability mass (2.8 out of 28 equally weighted scenarios, with fractional boundary weight).

Minimize scenario mean procurement cost subject to sum(q)=4, 0<=q<=0.25 and CVaR90(L)<=B. Use the exact linear epigraph: eta + sum(z)/(28*(1−alpha)) <= B, z_s >= L_s−eta, z_s >= 0. Eta is unrestricted. Fixed budgets B are EUR 0, EUR 25 and EUR 100 per day. Also report unconstrained mean-cost scheduling and uniform demand. Uniform is feasible for all nonnegative budgets. Solve with SciPy HiGHS linear programming, 20-second limit; accept status 0 only, and independently verify quantity and tail constraints.

All five policies are retained, with EUR 25 the neutral UI starting point, not a result-selected winner. Planned excess-cost CVaR is neither a maximum realized loss nor a guaranteed 90% coverage statement. Optimization and scenario risk assessment use the same small residual sample; overfitting and regime changes can invalidate the estimate.

## Realized evaluation and artifacts

Schedules commit early and settle unchanged at observed clearing prices, assuming full fills. A post-publication scheduler could use known day-ahead prices instead. No actual market bids, imbalance charges, taxes, grid tariffs or real customer constraints are included.

For each day and policy publish quantities, expected cost, scenario excess-cost distribution, its VaR90/CVaR90, observed cost, savings vs uniform, solver status and scenario lineage. Report aggregate cost, savings, worst realized excess cost, empirical CVaR90 of realized daily excess costs, count of days above the planning budget, and count above the estimated VaR90. A daily outcome above a CVaR budget is a diagnostic, not automatically a probability-model violation. Do not label the historical scenario constraint as a realized loss cap.

Provide full-precision interval and daily CSV exports and an interactive replay of forecast, load, scenarios and realized results. No investment returns, predictive guarantees or tuned profitability claims.
