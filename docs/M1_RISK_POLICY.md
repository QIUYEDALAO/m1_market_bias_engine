# M1 Risk Policy

M1 risk policy exists to constrain research interpretation. It does not produce
betting recommendations.

## Core Rule

Risk labels may filter, block, or downgrade research candidates inside offline
analysis. They must not create action instructions.

Allowed words include:

- `ALLOW_RESEARCH`
- `FILTERED_RISK`
- `INSUFFICIENT_SAMPLE`
- `CURRENT_NOT_FOR_BACKTEST`
- `SCHEMA_ONLY`

Forbidden meanings include:

- bet now
- official
- pending
- send QQ
- production pick
- live-bet instruction

## V3 Lite Boundary

V3 Lite may be referenced only as a risk-filter layer. It is not the M1 main
model, and it must not convert Market Bias research labels into recommendations.

If V3 Lite risk information is unavailable, M1 may still run offline research
with an explicit missing-risk note. Missing V3 Lite data must not trigger V3/V4
mutation.

## V4 Boundary

V4 is frozen for M1. M1 must not change V4 scoring, thresholds, dashboards,
validation records, official outputs, pending outputs, QQ behavior, cron, or
cloud publishing.

## Data Risk Rules

Complete historical backtest risk:

- Use only `COMPLETE_BACKTEST` seasons.
- Exclude `CURRENT_NOT_FOR_BACKTEST`.
- Preserve source provenance.
- Preserve field coverage evidence from the Phase 1 audit.

Current-season risk:

- `2025/26` is `CURRENT_NOT_FOR_BACKTEST`.
- Current-season data can validate fields and pipeline shape.
- Current-season data cannot enter complete-season backtest metrics.

Source risk:

- Football-Data is P0 for historical backtests.
- The Odds API is auxiliary for 1X2 validation.
- api-football is auxiliary for current-season polling.
- Auxiliary sources cannot override the P0 Football-Data backtest contract
  without a new audit.

## Old-System Safety

`old_system_touched=NO`.

Risk policy work must not write to V3/V4, official records, pending records, QQ
files, old-system data, cron jobs, or cloud publishing setup.
