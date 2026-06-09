# M1 Data Contract

This document fixes the Phase 2 data contract for M1. It must stay aligned with:

- `reports/data_audit/football_data_field_audit.md`
- `reports/data_audit/football_data_field_audit.json`
- `config/m1_minimum_dataset_fields.json`
- `config/data_sources.json`
- `config/market_definitions.json`

## Contract Status

- `usable_for_m1=YES`
- `old_system_touched=NO`
- Phase 1 audit checker: `PASS`
- Audited CSV count: `30`
- Audited row count: `10733`
- Audited leagues: `D1`, `E0`, `F1`, `I1`, `SP1`

## Season Roles

Only complete seasons may enter complete historical backtests:

| season | role |
| --- | --- |
| 2020/21 | COMPLETE_BACKTEST |
| 2021/22 | COMPLETE_BACKTEST |
| 2022/23 | COMPLETE_BACKTEST |
| 2023/24 | COMPLETE_BACKTEST |
| 2024/25 | COMPLETE_BACKTEST |

Current-season data is not complete-season backtest data:

| season | role |
| --- | --- |
| 2025/26 | CURRENT_NOT_FOR_BACKTEST |

`CURRENT_NOT_FOR_BACKTEST` rows may be used for schema validation, forward
research preparation, and ingestion checks. They must not be included in
complete-season backtest metrics.

## Required Identity Fields

M1 requires these match identity fields:

- `Div`
- `Date`
- `HomeTeam`
- `AwayTeam`

`Time` may be present and useful, but the minimum contract does not require it
for Phase 2.

## Required Result Fields

Backtest target fields:

- `FTHG`
- `FTAG`
- `FTR`

Results are targets for offline evaluation only. They must not be interpreted as
live recommendations.

## Required Market Fields

1X2 opening:

- `B365H`
- `B365D`
- `B365A`

1X2 closing:

- `B365CH`
- `B365CD`
- `B365CA`

Asian Handicap opening:

- `AHh`
- `B365AHH`
- `B365AHA`

Asian Handicap closing:

- `AHCh`
- `B365CAHH`
- `B365CAHA`

Over/Under 2.5 opening:

- `B365>2.5`
- `B365<2.5`

Over/Under 2.5 closing:

- `B365C>2.5`
- `B365C<2.5`

Pinnacle/PS cross-check fields:

- `PSH`, `PSD`, `PSA`
- `PSCH`, `PSCD`, `PSCA`
- `P>2.5`, `P<2.5`
- `PC>2.5`, `PC<2.5`
- `PAHH`, `PAHA`
- `PCAHH`, `PCAHA`

## AH Line Naming

Football-Data files in this audited set expose `AHh` and `AHCh` as the Asian
Handicap opening and closing line fields. M1 treats `AHh/AHCh` as the minimum
line contract instead of legacy `BbAH/BbAHh` naming.

## Source Priority

P0: Football-Data.

Football-Data is the historical backtest source of truth for 1X2, AH, OU, and
match result fields.

P1: The Odds API.

The Odds API is an auxiliary source for 1X2 movement validation. It is not the
P0 AH/OU historical backtest source.

P2: api-football.

api-football is an auxiliary source for current-season polling experiments. It
is not a complete historical odds backtest source.

## Forbidden Coupling

This contract must not cause writes to V3/V4, official records, pending records,
QQ messaging, cron, cloud publishing, or old-system data.
