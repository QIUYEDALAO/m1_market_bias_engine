# M1 Blueprint

M1 is a Market Bias research engine. It studies how opening odds, closing odds,
Asian Handicap lines, and Over/Under prices move before a match, then evaluates
whether those market movements have statistical research value.

M1 is not an AI team prediction system. It must not rank teams by subjective
strength, produce betting picks, write official records, create pending records,
send QQ messages, or feed V3/V4 production workflows.

## Scope

M1 owns only offline research artifacts:

- Football-Data field audits and dataset contracts.
- Market definition contracts for 1X2, AH, and OU.
- Market Bias feature blueprints.
- Backtest-only research reports for complete historical seasons.
- Current-season data validation that is explicitly excluded from complete
  backtests.

M1 does not own production recommendations, live-bet records, V3/V4 scoring, QQ
delivery, or any old-system mutation.

## Model Principle

The main model is Market Bias:

- Compare opening and closing 1X2 odds.
- Compare opening and closing AH prices and line movement.
- Compare opening and closing OU 2.5 prices.
- Treat bookmaker movement as the observed signal.
- Treat match result only as backtest target data.

The model question is not "which team is better". The model question is whether
market movement carries repeatable research signal under a fixed data contract.

## Data Source Roles

Football-Data is P0 and is the historical backtest source of truth. The Phase 1
audit report is the source for the current P0 field contract:
`reports/data_audit/football_data_field_audit.md`.

The Odds API is P1. It can support cross-checks for 1X2 movement, especially
where historical snapshot granularity is useful. It is not the AH/OU backtest
source.

api-football is P2. It can support current-season polling experiments and field
shape checks. It is not a historical odds backtest source.

## Season Policy

The complete backtest window is fixed:

- `2020/21` = `COMPLETE_BACKTEST`
- `2021/22` = `COMPLETE_BACKTEST`
- `2022/23` = `COMPLETE_BACKTEST`
- `2023/24` = `COMPLETE_BACKTEST`
- `2024/25` = `COMPLETE_BACKTEST`

The current season is fixed:

- `2025/26` = `CURRENT_NOT_FOR_BACKTEST`

Current-season rows may validate field coverage and future pipeline shape. They
must not be mixed into complete-season historical backtests.

## Old-System Boundary

`old_system_touched=NO`.

M1 must not edit V3/V4 code, V3/V4 data, live-bet records, official records,
pending records, QQ delivery files, cron jobs, or cloud publishing setup.

V3 Lite, if referenced later, is only a risk-filter input. It does not become
the M1 main model and must not turn M1 research labels into betting output.

V4 is frozen for M1 work. M1 must not change V4 thresholds, scoring, dashboards,
validation records, official output, or QQ behavior.

## Output Policy

Allowed outputs:

- Dataset audits.
- Dataset contracts.
- Market definitions.
- Offline feature descriptions.
- Offline backtest research metrics.
- Risk-filter labels that do not instruct action.

Forbidden outputs:

- Betting recommendations.
- Official selections.
- Pending selections.
- QQ messages.
- V3/V4 production mutations.
- Any file or field that implies live operational advice.
