# M1 Decision Policy

M1 decisions are research decisions. They are not betting decisions.

## Decision Types

Allowed decision labels:

- `RESEARCH_INCLUDE`
- `RESEARCH_EXCLUDE`
- `RISK_FILTERED`
- `SCHEMA_PASS`
- `SCHEMA_FAIL`
- `BACKTEST_ELIGIBLE`
- `CURRENT_NOT_FOR_BACKTEST`

Forbidden decision outputs:

- `official`
- `pending`
- QQ send payloads
- betting picks
- stake sizing
- live-bet instructions
- V3/V4 production updates

## Research Inclusion

A match row may be included in complete backtest research only when all of these
conditions hold:

- The season is `COMPLETE_BACKTEST`.
- Required identity fields are present.
- Required result fields are present.
- Required 1X2 opening and closing fields are present.
- Required AH opening and closing fields are present.
- Required OU opening and closing fields are present.
- Source provenance is Football-Data P0.

## Research Exclusion

A match row must be excluded from complete backtest research when any of these
conditions hold:

- The season is `CURRENT_NOT_FOR_BACKTEST`.
- Required fields are missing.
- Source provenance is not allowed by the current contract.
- The row is being evaluated for live action.
- The output path would touch old-system records.

## Threshold Policy

Thresholds in `config/decision_thresholds.json` are research gates only. They
may define minimum sample size, missing-field tolerance, and risk-filter
behavior. They must not define betting action thresholds.

Any future threshold that implies a recommendation must be rejected unless the
project charter is explicitly changed in a separate approved phase.

## Output Policy

M1 can output:

- Audit status.
- Contract status.
- Feature values.
- Backtest metrics.
- Research include/exclude labels.
- Risk-filter labels.

M1 cannot output:

- Official selections.
- Pending selections.
- QQ messages.
- Production bet instructions.
- V3/V4 scoring changes.

`old_system_touched=NO` remains mandatory.
