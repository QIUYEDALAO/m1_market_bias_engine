# M1 Phase Plan

M1 advances through explicit research phases. Each phase must preserve the
old-system boundary and the no-recommendation rule.

## Phase 1: Field Audit

Status: complete.

Outputs:

- `scripts/audit_football_data_fields.py`
- `reports/data_audit/football_data_field_audit.md`
- `reports/data_audit/football_data_field_audit.json`
- `config/m1_minimum_dataset_fields.json`

Acceptance carried forward:

- `usable_for_m1=YES`
- `old_system_touched=NO`
- `checker=PASS`
- `2020/21`-`2024/25` = `COMPLETE_BACKTEST`
- `2025/26` = `CURRENT_NOT_FOR_BACKTEST`

## Phase 2: Blueprint And Contract Freeze

Status: this phase.

Outputs:

- `docs/M1_BLUEPRINT.md`
- `docs/M1_DATA_CONTRACT.md`
- `docs/M1_PHASE_PLAN.md`
- `docs/M1_RISK_POLICY.md`
- `docs/M1_DECISION_POLICY.md`
- `config/data_sources.json`
- `config/market_definitions.json`
- `config/decision_thresholds.json`

Purpose:

- Freeze M1 as a Market Bias research project.
- Freeze Football-Data as P0.
- Freeze The Odds API and api-football as auxiliary sources.
- Freeze the complete backtest season window.
- Freeze the current-season exclusion rule.
- Freeze V3 Lite as risk-filter only.
- Freeze V4 as out of scope.

## Phase 3: Feature Blueprint

Allowed work:

- Define offline Market Bias features.
- Define opening-to-closing movement formulas.
- Define AH line movement features using `AHh/AHCh`.
- Define OU 2.5 movement features.
- Define backtest labels that are not recommendations.

Forbidden work:

- No official records.
- No pending records.
- No QQ messages.
- No V3/V4 production writes.
- No live betting output.

## Phase 4: Offline Backtest Prototype

Allowed work:

- Read `COMPLETE_BACKTEST` seasons only.
- Produce offline aggregate metrics.
- Compare feature groups against result targets.
- Record uncertainty and sample-size limits.

Forbidden work:

- Do not include `CURRENT_NOT_FOR_BACKTEST` rows in complete backtests.
- Do not promote research metrics into recommendations.
- Do not write to old-system directories.

## Phase 5: Current-Season Observation Prototype

Allowed work:

- Validate current-season field shape.
- Test polling or snapshot mechanics.
- Label output as observation-only.

Forbidden work:

- Do not treat `2025/26` as complete backtest data.
- Do not emit operational picks.
- Do not connect to QQ, official, pending, or V4.
