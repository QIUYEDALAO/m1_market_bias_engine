# M1 Normalized Matches Report

- generated_at_utc: `2026-06-09T22:48:41+00:00`
- output_csv: `data/processed/normalized_matches/m1_matches_normalized.csv`
- checker: `PASS`
- old_system_touched: `NO`
- recommendations_generated: `NO`
- backtest_run: `NO`

## Summary

| metric | value |
| --- | --- |
| raw_csv_count | 30 |
| normalized_rows | 10733 |
| audit_rows | 10733 |
| row_delta_vs_audit | 0 |
| complete_backtest_rows | 8982 |
| current_not_for_backtest_rows | 1751 |

The normalized row count matches the Phase 1 Football-Data audit. `2025/26` rows are retained in the normalized table as `CURRENT_NOT_FOR_BACKTEST`, but they are not counted in `complete_backtest_rows`.

## Role Counts

| season_role | rows |
| --- | --- |
| COMPLETE_BACKTEST | 8982 |
| CURRENT_NOT_FOR_BACKTEST | 1751 |

## Season Counts

| season | season_role | rows |
| --- | --- | --- |
| 2020/21 | COMPLETE_BACKTEST | 1826 |
| 2021/22 | COMPLETE_BACKTEST | 1826 |
| 2022/23 | COMPLETE_BACKTEST | 1826 |
| 2023/24 | COMPLETE_BACKTEST | 1752 |
| 2024/25 | COMPLETE_BACKTEST | 1752 |
| 2025/26 | CURRENT_NOT_FOR_BACKTEST | 1751 |

## Normalized Fields

| field |
| --- |
| match_id |
| league |
| season |
| season_role |
| date |
| home_team |
| away_team |
| full_time_home_goals |
| full_time_away_goals |
| full_time_result |
| opening_home_odds |
| opening_draw_odds |
| opening_away_odds |
| closing_home_odds |
| closing_draw_odds |
| closing_away_odds |
| opening_ah_line |
| closing_ah_line |
| opening_ah_home_odds |
| opening_ah_away_odds |
| closing_ah_home_odds |
| closing_ah_away_odds |
| opening_over25_odds |
| opening_under25_odds |
| closing_over25_odds |
| closing_under25_odds |
| bookmaker_source |
| data_source |
| source_file |
| source_row_number |

## Empty Normalized Cell Counts

| field | empty_cells |
| --- | --- |
| closing_ah_away_odds | 2 |
| closing_ah_home_odds | 2 |
| closing_away_odds | 1 |
| closing_draw_odds | 1 |
| closing_home_odds | 1 |
| closing_over25_odds | 1 |
| closing_under25_odds | 1 |
| opening_ah_away_odds | 7 |
| opening_ah_home_odds | 7 |
| opening_ah_line | 7 |
| opening_away_odds | 5 |
| opening_draw_odds | 5 |
| opening_home_odds | 5 |
| opening_over25_odds | 9 |
| opening_under25_odds | 9 |

## Source File Counts

| file | league | season | season_role | rows |
| --- | --- | --- | --- | --- |
| data/raw/football_data/D1_2021.csv | D1 | 2020/21 | COMPLETE_BACKTEST | 306 |
| data/raw/football_data/D1_2122.csv | D1 | 2021/22 | COMPLETE_BACKTEST | 306 |
| data/raw/football_data/D1_2223.csv | D1 | 2022/23 | COMPLETE_BACKTEST | 306 |
| data/raw/football_data/D1_2324.csv | D1 | 2023/24 | COMPLETE_BACKTEST | 306 |
| data/raw/football_data/D1_2425.csv | D1 | 2024/25 | COMPLETE_BACKTEST | 306 |
| data/raw/football_data/D1_2526.csv | D1 | 2025/26 | CURRENT_NOT_FOR_BACKTEST | 306 |
| data/raw/football_data/E0_2021.csv | E0 | 2020/21 | COMPLETE_BACKTEST | 380 |
| data/raw/football_data/E0_2122.csv | E0 | 2021/22 | COMPLETE_BACKTEST | 380 |
| data/raw/football_data/E0_2223.csv | E0 | 2022/23 | COMPLETE_BACKTEST | 380 |
| data/raw/football_data/E0_2324.csv | E0 | 2023/24 | COMPLETE_BACKTEST | 380 |
| data/raw/football_data/E0_2425.csv | E0 | 2024/25 | COMPLETE_BACKTEST | 380 |
| data/raw/football_data/E0_2526.csv | E0 | 2025/26 | CURRENT_NOT_FOR_BACKTEST | 380 |
| data/raw/football_data/F1_2021.csv | F1 | 2020/21 | COMPLETE_BACKTEST | 380 |
| data/raw/football_data/F1_2122.csv | F1 | 2021/22 | COMPLETE_BACKTEST | 380 |
| data/raw/football_data/F1_2223.csv | F1 | 2022/23 | COMPLETE_BACKTEST | 380 |
| data/raw/football_data/F1_2324.csv | F1 | 2023/24 | COMPLETE_BACKTEST | 306 |
| data/raw/football_data/F1_2425.csv | F1 | 2024/25 | COMPLETE_BACKTEST | 306 |
| data/raw/football_data/F1_2526.csv | F1 | 2025/26 | CURRENT_NOT_FOR_BACKTEST | 305 |
| data/raw/football_data/I1_2021.csv | I1 | 2020/21 | COMPLETE_BACKTEST | 380 |
| data/raw/football_data/I1_2122.csv | I1 | 2021/22 | COMPLETE_BACKTEST | 380 |
| data/raw/football_data/I1_2223.csv | I1 | 2022/23 | COMPLETE_BACKTEST | 380 |
| data/raw/football_data/I1_2324.csv | I1 | 2023/24 | COMPLETE_BACKTEST | 380 |
| data/raw/football_data/I1_2425.csv | I1 | 2024/25 | COMPLETE_BACKTEST | 380 |
| data/raw/football_data/I1_2526.csv | I1 | 2025/26 | CURRENT_NOT_FOR_BACKTEST | 380 |
| data/raw/football_data/SP1_2021.csv | SP1 | 2020/21 | COMPLETE_BACKTEST | 380 |
| data/raw/football_data/SP1_2122.csv | SP1 | 2021/22 | COMPLETE_BACKTEST | 380 |
| data/raw/football_data/SP1_2223.csv | SP1 | 2022/23 | COMPLETE_BACKTEST | 380 |
| data/raw/football_data/SP1_2324.csv | SP1 | 2023/24 | COMPLETE_BACKTEST | 380 |
| data/raw/football_data/SP1_2425.csv | SP1 | 2024/25 | COMPLETE_BACKTEST | 380 |
| data/raw/football_data/SP1_2526.csv | SP1 | 2025/26 | CURRENT_NOT_FOR_BACKTEST | 380 |

## Self Check

| check | status |
| --- | --- |
| raw_csv_count_is_30 | PASS |
| normalized_rows_match_audit | PASS |
| complete_backtest_rows_match_audit | PASS |
| current_not_for_backtest_rows_match_audit | PASS |
| current_not_in_complete_backtest | PASS |
| no_duplicate_match_ids | PASS |
| recommendations_generated_no | PASS |
| backtest_run_no | PASS |
| old_system_touched_no | PASS |
