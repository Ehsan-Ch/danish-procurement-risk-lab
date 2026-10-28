# Release verification

Verified on 28 October 2026.

## Published release

- Code/data commit: `ff9262200491b7703ae71d521fe9d3ebaa9f497d`.
- All 29 release files matched the local Git blob hashes.
- [Public preview](https://ehsan-ch.github.io/danish-procurement-risk-lab/).
- [Tests run 40770933251](https://github.com/Ehsan-Ch/danish-procurement-risk-lab/actions/runs/40770933251): successful Python 3.11, Python 3.12 and Node 22 jobs.
- [Pages run 40771319075](https://github.com/Ehsan-Ch/danish-procurement-risk-lab/actions/runs/40771319075): successful deployment.
- 20 Python tests and 6 JavaScript tests passed locally. GitHub repeated the Python suite on both supported versions.

## Browser verification

The public site loaded its complete report. Changing area to DK1, policy to uniform and date to 30 September updated the cost and comparisons. The constrained-day shortcut then selected DK2, 24 September, with the zero-euro scenario tail budget. The displayed planned CVaR rounded to EUR 0 and actual excess cost to EUR -140.

The public download produced 96 quarter-hour rows for that decision. Independent CSV reconciliation confirmed 4 MWh total and EUR 490.64692560650934 cost, matching the stored report within EUR 0.000001.

Local browser checks also covered the 390-by-844 mobile viewport, with no horizontal page overflow. This is a manual browser smoke check, not a claim of exhaustive browser compatibility.

## Scope

This record verifies publication, tested calculations and observed browser behavior. It does not establish that historical scenarios predict future risk or that the hypothetical procurement schedules can be executed in a real market.
