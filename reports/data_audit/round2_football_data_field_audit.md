# Round2 Football-Data Field Audit

- generated_at_utc: `2026-06-09T23:41:27+00:00`
- data_dir: `data/raw/football_data_round2`
- checker: `PASS`
- files_checked: `36`
- usable_for_round2: `NO`
- old_system_touched: `NO`
- normalized_built: `NO`
- features_built: `NO`
- backtest_run: `NO`
- recommendations_generated: `NO`

## Summary

| metric | value |
| --- | --- |
| files_checked | 36 |
| complete_backtest_rows | 9362 |
| current_not_for_backtest_rows | 1457 |
| empty_files | data/raw/football_data_round2/J1_2526.csv |
| failed_files | 6 |
| K1 | UNAVAILABLE_SOURCE_EXPIRED |

## League Availability

| league | name | availability | files | rows | seasons | failed_files | empty_files |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B1 | Belgium Jupiler League | AVAILABLE_FULL_CONTRACT | 6 | 1853 | 2020/21, 2021/22, 2022/23, 2023/24, 2024/25, 2025/26 | 0 |  |
| J1 | Japan J1 League | AVAILABLE_PARTIAL_SCHEMA | 6 | 1756 | 2020/21, 2021/22, 2022/23, 2023/24, 2024/25, 2025/26 | 6 | data/raw/football_data_round2/J1_2526.csv |
| K1 | South Korea K League 1 | UNAVAILABLE_SOURCE_EXPIRED | 0 | 0 |  | 0 |  |
| N1 | Netherlands Eredivisie | AVAILABLE_FULL_CONTRACT | 6 | 1836 | 2020/21, 2021/22, 2022/23, 2023/24, 2024/25, 2025/26 | 0 |  |
| P1 | Portugal Primeira Liga | AVAILABLE_FULL_CONTRACT | 6 | 1836 | 2020/21, 2021/22, 2022/23, 2023/24, 2024/25, 2025/26 | 0 |  |
| SC0 | Scotland Premiership | AVAILABLE_FULL_CONTRACT | 6 | 1368 | 2020/21, 2021/22, 2022/23, 2023/24, 2024/25, 2025/26 | 0 |  |
| T1 | Turkey Super Lig | AVAILABLE_FULL_CONTRACT | 6 | 2170 | 2020/21, 2021/22, 2022/23, 2023/24, 2024/25, 2025/26 | 0 |  |

## Special Rules

- `J1_2526.csv` is header-only and labeled `CURRENT_EMPTY`; it is not counted in current rows.
- `K1` is labeled `UNAVAILABLE_SOURCE_EXPIRED`; it is not counted as a failed CSV.
- This phase does not merge normalized rows, build features, run backtests, or generate recommendations.

## File Coverage

| file | league | season | season_role | rows | header_only | usable | identity_result | 1x2_open | 1x2_close | ah_open | ah_close | ou25_open | ou25_close | b365 | pinnacle_ps | AHh_AHCh |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| data/raw/football_data_round2/B1_2021.csv | B1 | 2020/21 | COMPLETE_BACKTEST | 306 | False | YES | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| data/raw/football_data_round2/B1_2122.csv | B1 | 2021/22 | COMPLETE_BACKTEST | 306 | False | YES | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| data/raw/football_data_round2/B1_2223.csv | B1 | 2022/23 | COMPLETE_BACKTEST | 306 | False | YES | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| data/raw/football_data_round2/B1_2324.csv | B1 | 2023/24 | COMPLETE_BACKTEST | 312 | False | YES | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| data/raw/football_data_round2/B1_2425.csv | B1 | 2024/25 | COMPLETE_BACKTEST | 312 | False | YES | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| data/raw/football_data_round2/B1_2526.csv | B1 | 2025/26 | CURRENT_NOT_FOR_BACKTEST | 311 | False | YES | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| data/raw/football_data_round2/J1_2021.csv | J1 | 2020/21 | COMPLETE_BACKTEST | 380 | False | NO | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| data/raw/football_data_round2/J1_2122.csv | J1 | 2021/22 | COMPLETE_BACKTEST | 310 | False | NO | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| data/raw/football_data_round2/J1_2223.csv | J1 | 2022/23 | COMPLETE_BACKTEST | 306 | False | NO | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| data/raw/football_data_round2/J1_2324.csv | J1 | 2023/24 | COMPLETE_BACKTEST | 380 | False | NO | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| data/raw/football_data_round2/J1_2425.csv | J1 | 2024/25 | COMPLETE_BACKTEST | 380 | False | NO | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| data/raw/football_data_round2/J1_2526.csv | J1 | 2025/26 | CURRENT_EMPTY | 0 | True | NO | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| data/raw/football_data_round2/N1_2021.csv | N1 | 2020/21 | COMPLETE_BACKTEST | 306 | False | YES | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| data/raw/football_data_round2/N1_2122.csv | N1 | 2021/22 | COMPLETE_BACKTEST | 306 | False | YES | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| data/raw/football_data_round2/N1_2223.csv | N1 | 2022/23 | COMPLETE_BACKTEST | 306 | False | YES | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| data/raw/football_data_round2/N1_2324.csv | N1 | 2023/24 | COMPLETE_BACKTEST | 306 | False | YES | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| data/raw/football_data_round2/N1_2425.csv | N1 | 2024/25 | COMPLETE_BACKTEST | 306 | False | YES | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| data/raw/football_data_round2/N1_2526.csv | N1 | 2025/26 | CURRENT_NOT_FOR_BACKTEST | 306 | False | YES | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| data/raw/football_data_round2/P1_2021.csv | P1 | 2020/21 | COMPLETE_BACKTEST | 306 | False | YES | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| data/raw/football_data_round2/P1_2122.csv | P1 | 2021/22 | COMPLETE_BACKTEST | 306 | False | YES | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| data/raw/football_data_round2/P1_2223.csv | P1 | 2022/23 | COMPLETE_BACKTEST | 306 | False | YES | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| data/raw/football_data_round2/P1_2324.csv | P1 | 2023/24 | COMPLETE_BACKTEST | 306 | False | YES | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| data/raw/football_data_round2/P1_2425.csv | P1 | 2024/25 | COMPLETE_BACKTEST | 306 | False | YES | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| data/raw/football_data_round2/P1_2526.csv | P1 | 2025/26 | CURRENT_NOT_FOR_BACKTEST | 306 | False | YES | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| data/raw/football_data_round2/SC0_2021.csv | SC0 | 2020/21 | COMPLETE_BACKTEST | 228 | False | YES | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| data/raw/football_data_round2/SC0_2122.csv | SC0 | 2021/22 | COMPLETE_BACKTEST | 228 | False | YES | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| data/raw/football_data_round2/SC0_2223.csv | SC0 | 2022/23 | COMPLETE_BACKTEST | 228 | False | YES | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| data/raw/football_data_round2/SC0_2324.csv | SC0 | 2023/24 | COMPLETE_BACKTEST | 228 | False | YES | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| data/raw/football_data_round2/SC0_2425.csv | SC0 | 2024/25 | COMPLETE_BACKTEST | 228 | False | YES | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| data/raw/football_data_round2/SC0_2526.csv | SC0 | 2025/26 | CURRENT_NOT_FOR_BACKTEST | 228 | False | YES | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| data/raw/football_data_round2/T1_2021.csv | T1 | 2020/21 | COMPLETE_BACKTEST | 420 | False | YES | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| data/raw/football_data_round2/T1_2122.csv | T1 | 2021/22 | COMPLETE_BACKTEST | 380 | False | YES | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| data/raw/football_data_round2/T1_2223.csv | T1 | 2022/23 | COMPLETE_BACKTEST | 342 | False | YES | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| data/raw/football_data_round2/T1_2324.csv | T1 | 2023/24 | COMPLETE_BACKTEST | 380 | False | YES | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| data/raw/football_data_round2/T1_2425.csv | T1 | 2024/25 | COMPLETE_BACKTEST | 342 | False | YES | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| data/raw/football_data_round2/T1_2526.csv | T1 | 2025/26 | CURRENT_NOT_FOR_BACKTEST | 306 | False | YES | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |

## Self Check

| check | status |
| --- | --- |
| files_checked_36 | PASS |
| empty_files_listed | PASS |
| j1_2526_current_empty | PASS |
| k1_unavailable_listed | PASS |
| usable_for_round2_explicit | PASS |
| season_roles_valid | PASS |
| current_empty_not_in_current_rows | PASS |
| old_system_touched_no | PASS |
| no_normalized_features_backtest | PASS |
| recommendations_generated_no | PASS |
