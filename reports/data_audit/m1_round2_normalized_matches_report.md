# M1 Round2 Normalized Matches Report

- generated_at_utc: `2026-06-09T23:48:19+00:00`
- output_csv: `data/processed/normalized_matches/m1_round2_matches_normalized.csv`
- checker: `PASS`
- round1_merged: `NO`
- features_built: `NO`
- backtest_run: `NO`
- recommendations_generated: `NO`
- old_system_touched: `NO`

## Summary

| metric | value |
| --- | --- |
| raw_files | 36 |
| included_full_contract_leagues | 5 |
| included_full_contract_league_codes | B1, N1, P1, SC0, T1 |
| normalized_rows | 9063 |
| complete_backtest_rows | 7606 |
| current_not_for_backtest_rows | 1457 |
| expected_full_contract_rows_from_audit | 9063 |
| expected_full_contract_complete_rows_from_audit | 7606 |
| J1 | PARTIAL_SCHEMA_REVIEWED |
| K1 | UNAVAILABLE_SOURCE_EXPIRED |

The normalized rows match the Round2 audit after excluding J1 partial-schema files and K1 unavailable source. J1 is reviewed as `PARTIAL_SCHEMA_REVIEWED`; J1 rows do not enter `COMPLETE_BACKTEST`. `J1_2526.csv` is header-only and excluded. `2025/26` rows from full-contract leagues are retained as `CURRENT_NOT_FOR_BACKTEST` and are not counted in complete backtest rows.

## Rows By League

| league | rows |
| --- | --- |
| B1 | 1853 |
| N1 | 1836 |
| P1 | 1836 |
| SC0 | 1368 |
| T1 | 2170 |

## Rows By Season

| season | rows |
| --- | --- |
| 2020/21 | 1566 |
| 2021/22 | 1526 |
| 2022/23 | 1488 |
| 2023/24 | 1532 |
| 2024/25 | 1494 |
| 2025/26 | 1457 |

## Excluded Files

| file | league | season | reason |
| --- | --- | --- | --- |
| data/raw/football_data_round2/J1_2021.csv | J1 | 2020/21 | PARTIAL_SCHEMA_REVIEWED |
| data/raw/football_data_round2/J1_2122.csv | J1 | 2021/22 | PARTIAL_SCHEMA_REVIEWED |
| data/raw/football_data_round2/J1_2223.csv | J1 | 2022/23 | PARTIAL_SCHEMA_REVIEWED |
| data/raw/football_data_round2/J1_2324.csv | J1 | 2023/24 | PARTIAL_SCHEMA_REVIEWED |
| data/raw/football_data_round2/J1_2425.csv | J1 | 2024/25 | PARTIAL_SCHEMA_REVIEWED |
| data/raw/football_data_round2/J1_2526.csv | J1 | 2025/26 | PARTIAL_SCHEMA_REVIEWED |

## Self Check

| check | status |
| --- | --- |
| raw_files_36 | PASS |
| included_full_contract_leagues_5 | PASS |
| only_expected_full_contract_leagues | PASS |
| normalized_rows_match_audit_explainable | PASS |
| complete_backtest_rows_match_full_contract_audit | PASS |
| current_not_in_complete_backtest | PASS |
| j1_partial_reviewed_not_included | PASS |
| j1_2526_header_only_excluded | PASS |
| k1_unavailable | PASS |
| no_duplicate_match_ids | PASS |
| no_features_backtest_recommendations | PASS |
| old_system_touched_no | PASS |
