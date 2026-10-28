# Data provenance and reuse

Prices originate from Energinet's [DayAheadPrices dataset](https://www.energidataservice.dk/tso-electricity/DayAheadPrices), EUR/MWh for DK1/DK2. [Metadata](https://api.energidataservice.dk/meta/dataset/DayAheadPrices) and [source terms](https://www.energidataservice.dk/terms-and-conditions) document the dataset. Source-derived numerical artifacts retain Creative Commons Attribution 4.0 attribution to Energinet.

Harbor reuses the exact [Nordcast archive](https://github.com/Ehsan-Ch/danish-power-forecast-lab/blob/a8244399f0886d07ddafbe1d71b757abcb97ae95/reports/benchmark/predictions.csv.gz) at commit `a8244399f0886d07ddafbe1d71b757abcb97ae95`. Its SHA256 is `11dc413033af9ddfda6e16b2b9d1a2a067ad6482e186453282d6c1f38625937c`. Hash mismatch stops processing. The complete original compressed file is retained, including unused validation and other-model rows, to preserve this fingerprint.

Upstream raw price archive SHA256: `93ccd57867b2eae79705659e84a4aa8f1913b3a714204ccb859316a964ef7da2`; retrieved 24 October 2026 at 14:35:47 UTC. Its 70,080 native-quarter rows cover 1 October 2025 through 30 September 2026, local dates. Harbor does not redownload, revise or retrain this archive.

See [Nordcast's protocol](https://github.com/Ehsan-Ch/danish-power-forecast-lab/blob/a8244399f0886d07ddafbe1d71b757abcb97ae95/docs/PROTOCOL.md) for model training. Its original June validation choices remain ridge for DK1 and boosted median for DK2. Models refit monthly on eligible history. Features use lagged prices and calendars; no realized target-day weather or load. The source archive is retrospective and can contain revisions.

The imported test rows cover July–September. July provides initial residual history; Harbor evaluates August–September. A source day's errors become eligible after its final quarter ends plus 24 hours. On the 31 July decision for 1 August, the latest eligible residual day is 29 July. Later decisions may use earlier evaluation-day errors only after the same delay. Scenario lineage in results.json exposes all 28 source dates and availability times per decision.

The source loader was reused from Cellar under its MIT license, with its original forecast checks intact. New modules implement scenario construction and risk-constrained scheduling. Reports include full precision, source hash, protocol hash and package versions; compressed CSVs use a zero gzip timestamp. HTML and JavaScript use no remote libraries or fonts.

The LP uses [SciPy's documented linear-programming interface](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html), pinned to SciPy 1.15.3 with HiGHS. Third-party dependency licenses are separate from Harbor's code license.
