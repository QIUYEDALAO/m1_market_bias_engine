# Football-Data Field Audit

- generated_at_utc: `2026-06-09T22:25:24+00:00`
- data_dir: `data/raw/football_data`
- usable_for_m1: `YES`
- old_system_touched: `NO`
- checker: `PASS`

## Summary

| metric | value |
| --- | --- |
| file_count | 30 |
| league_count | 5 |
| season_count | 6 |
| row_count | 10733 |
| complete_backtest_rows | 8982 |
| current_not_for_backtest_rows | 1751 |

## Season Classification

| season | label | files | rows | leagues |
| --- | --- | --- | --- | --- |
| 2020/21 | COMPLETE_BACKTEST | 5 | 1826 | D1, E0, F1, I1, SP1 |
| 2021/22 | COMPLETE_BACKTEST | 5 | 1826 | D1, E0, F1, I1, SP1 |
| 2022/23 | COMPLETE_BACKTEST | 5 | 1826 | D1, E0, F1, I1, SP1 |
| 2023/24 | COMPLETE_BACKTEST | 5 | 1752 | D1, E0, F1, I1, SP1 |
| 2024/25 | COMPLETE_BACKTEST | 5 | 1752 | D1, E0, F1, I1, SP1 |
| 2025/26 | CURRENT_NOT_FOR_BACKTEST | 5 | 1751 | D1, E0, F1, I1, SP1 |

Policy: `2020/21`-`2024/25` are `COMPLETE_BACKTEST`; `2025/26` is `CURRENT_NOT_FOR_BACKTEST` and must not be mixed into complete-season backtests.

## League Coverage

| code | league | files | rows | seasons |
| --- | --- | --- | --- | --- |
| D1 | Germany Bundesliga | 6 | 1836 | 2020/21, 2021/22, 2022/23, 2023/24, 2024/25, 2025/26 |
| E0 | England Premier League | 6 | 2280 | 2020/21, 2021/22, 2022/23, 2023/24, 2024/25, 2025/26 |
| F1 | France Ligue 1 | 6 | 2057 | 2020/21, 2021/22, 2022/23, 2023/24, 2024/25, 2025/26 |
| I1 | Italy Serie A | 6 | 2280 | 2020/21, 2021/22, 2022/23, 2023/24, 2024/25, 2025/26 |
| SP1 | Spain La Liga | 6 | 2280 | 2020/21, 2021/22, 2022/23, 2023/24, 2024/25, 2025/26 |

## Field Coverage

| group | status | files_passed | required_fields |
| --- | --- | --- | --- |
| result | PASS | 30/30 | FTHG, FTAG, FTR |
| one_x_two_opening | PASS | 30/30 | B365H, B365D, B365A |
| one_x_two_closing | PASS | 30/30 | B365CH, B365CD, B365CA |
| ah_opening | PASS | 30/30 | AHh, B365AHH, B365AHA |
| ah_closing | PASS | 30/30 | AHCh, B365CAHH, B365CAHA |
| ou_opening | PASS | 30/30 | B365>2.5, B365<2.5 |
| ou_closing | PASS | 30/30 | B365C>2.5, B365C<2.5 |
| b365 | PASS | 30/30 | B365H, B365D, B365A, B365CH, B365CD, B365CA, B365>2.5, B365<2.5, B365C>2.5, B365C<2.5, B365AHH, B365AHA, B365CAHH, B365CAHA |
| pinnacle_ps | PASS | 30/30 | PSH, PSD, PSA, PSCH, PSCD, PSCA, P>2.5, P<2.5, PC>2.5, PC<2.5, PAHH, PAHA, PCAHH, PCAHA |
| ah_line_replacement | PASS | 30/30 | AHh, AHCh |

## AH Line Field Note

Football-Data files in this sample expose AHh and AHCh as the Asian Handicap opening and closing line fields. M1 treats AHh/AHCh as the minimum line contract instead of legacy BbAH/BbAHh naming.

## File Inventory

| file | league | season | label | rows | fields |
| --- | --- | --- | --- | --- | --- |
| data/raw/football_data/D1_2021.csv | D1 | 2020/21 | COMPLETE_BACKTEST | 306 | 105 |
| data/raw/football_data/D1_2122.csv | D1 | 2021/22 | COMPLETE_BACKTEST | 306 | 105 |
| data/raw/football_data/D1_2223.csv | D1 | 2022/23 | COMPLETE_BACKTEST | 306 | 105 |
| data/raw/football_data/D1_2324.csv | D1 | 2023/24 | COMPLETE_BACKTEST | 306 | 105 |
| data/raw/football_data/D1_2425.csv | D1 | 2024/25 | COMPLETE_BACKTEST | 306 | 119 |
| data/raw/football_data/D1_2526.csv | D1 | 2025/26 | CURRENT_NOT_FOR_BACKTEST | 306 | 131 |
| data/raw/football_data/E0_2021.csv | E0 | 2020/21 | COMPLETE_BACKTEST | 380 | 106 |
| data/raw/football_data/E0_2122.csv | E0 | 2021/22 | COMPLETE_BACKTEST | 380 | 106 |
| data/raw/football_data/E0_2223.csv | E0 | 2022/23 | COMPLETE_BACKTEST | 380 | 106 |
| data/raw/football_data/E0_2324.csv | E0 | 2023/24 | COMPLETE_BACKTEST | 380 | 106 |
| data/raw/football_data/E0_2425.csv | E0 | 2024/25 | COMPLETE_BACKTEST | 380 | 120 |
| data/raw/football_data/E0_2526.csv | E0 | 2025/26 | CURRENT_NOT_FOR_BACKTEST | 380 | 132 |
| data/raw/football_data/F1_2021.csv | F1 | 2020/21 | COMPLETE_BACKTEST | 380 | 105 |
| data/raw/football_data/F1_2122.csv | F1 | 2021/22 | COMPLETE_BACKTEST | 380 | 105 |
| data/raw/football_data/F1_2223.csv | F1 | 2022/23 | COMPLETE_BACKTEST | 380 | 105 |
| data/raw/football_data/F1_2324.csv | F1 | 2023/24 | COMPLETE_BACKTEST | 306 | 105 |
| data/raw/football_data/F1_2425.csv | F1 | 2024/25 | COMPLETE_BACKTEST | 306 | 119 |
| data/raw/football_data/F1_2526.csv | F1 | 2025/26 | CURRENT_NOT_FOR_BACKTEST | 305 | 131 |
| data/raw/football_data/I1_2021.csv | I1 | 2020/21 | COMPLETE_BACKTEST | 380 | 105 |
| data/raw/football_data/I1_2122.csv | I1 | 2021/22 | COMPLETE_BACKTEST | 380 | 105 |
| data/raw/football_data/I1_2223.csv | I1 | 2022/23 | COMPLETE_BACKTEST | 380 | 105 |
| data/raw/football_data/I1_2324.csv | I1 | 2023/24 | COMPLETE_BACKTEST | 380 | 105 |
| data/raw/football_data/I1_2425.csv | I1 | 2024/25 | COMPLETE_BACKTEST | 380 | 119 |
| data/raw/football_data/I1_2526.csv | I1 | 2025/26 | CURRENT_NOT_FOR_BACKTEST | 380 | 131 |
| data/raw/football_data/SP1_2021.csv | SP1 | 2020/21 | COMPLETE_BACKTEST | 380 | 105 |
| data/raw/football_data/SP1_2122.csv | SP1 | 2021/22 | COMPLETE_BACKTEST | 380 | 105 |
| data/raw/football_data/SP1_2223.csv | SP1 | 2022/23 | COMPLETE_BACKTEST | 380 | 105 |
| data/raw/football_data/SP1_2324.csv | SP1 | 2023/24 | COMPLETE_BACKTEST | 380 | 105 |
| data/raw/football_data/SP1_2425.csv | SP1 | 2024/25 | COMPLETE_BACKTEST | 380 | 119 |
| data/raw/football_data/SP1_2526.csv | SP1 | 2025/26 | CURRENT_NOT_FOR_BACKTEST | 380 | 131 |

## Self Check

| check | status |
| --- | --- |
| file_count_is_30 | PASS |
| usable_for_m1_yes | PASS |
| old_system_touched_no | PASS |
| all_coverage_pass | PASS |
| complete_backtest_2020_21_to_2024_25 | PASS |
| current_2025_26_not_for_backtest | PASS |
| current_not_mixed_into_complete_backtest | PASS |
