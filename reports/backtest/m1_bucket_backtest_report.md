# M1 Bucket Backtest Report

- generated_at_utc: `2026-06-09T23:05:07+00:00`
- input_csv: `data/processed/market_features/m1_market_features.csv`
- normalized_context_csv: `data/processed/normalized_matches/m1_matches_normalized.csv`
- output_csv: `data/processed/backtest_ready/m1_bucket_results.csv`
- checker: `PASS`
- backtest_scope: `COMPLETE_BACKTEST_ONLY`
- excluded_current_policy: `2025/26 CURRENT_NOT_FOR_BACKTEST excluded`
- recommendations_generated: `NO`
- official_written: `NO`
- pending_written: `NO`
- qq_written: `NO`
- old_system_touched: `NO`

## Summary

| metric | value |
| --- | --- |
| input_rows | 10733 |
| backtest_rows | 8982 |
| excluded_current_rows | 1751 |
| bucket_rows | 139 |
| positive_roi_bucket_count | 25 |

This is an offline bucket backtest over `COMPLETE_BACKTEST` rows only. It does not match current fixtures, generate recommendations, or write official/pending/QQ outputs.

AH closing line buckets and OU 2.5 closing probability buckets use `match_id`-joined closing line/odds context from the normalized table. The backtest row filter remains `season_role=COMPLETE_BACKTEST`.

## Reject Reason Counts

| reject_reason | bucket_count |
| --- | --- |
| CONCENTRATION_RISK | 20 |
| HIGH_DRAWDOWN_RISK | 16 |
| NONE | 58 |
| SMALL_SAMPLE | 79 |

## Backtest Distributions

League distribution:

| league | rows |
| --- | --- |
| D1 | 1530 |
| E0 | 1900 |
| F1 | 1752 |
| I1 | 1900 |
| SP1 | 1900 |

Season distribution:

| season | rows |
| --- | --- |
| 2020/21 | 1826 |
| 2021/22 | 1826 |
| 2022/23 | 1826 |
| 2023/24 | 1752 |
| 2024/25 | 1752 |

## Bucket Preview

| market | selection | bucket_type | bucket | sample_count | hit_rate | roi | reject_reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1X2 | home | closing_fair_probability | 0.0-0.1 | 121 | 0.066116 | -0.173554 | SMALL_SAMPLE |
| 1X2 | home | closing_fair_probability | 0.1-0.2 | 824 | 0.128641 | -0.236044 | NONE |
| 1X2 | home | closing_fair_probability | 0.2-0.3 | 1392 | 0.220546 | -0.177162 | NONE |
| 1X2 | home | closing_fair_probability | 0.3-0.4 | 1706 | 0.333529 | -0.104109 | NONE |
| 1X2 | home | closing_fair_probability | 0.4-0.5 | 1767 | 0.434635 | -0.085688 | NONE |
| 1X2 | home | closing_fair_probability | 0.5-0.6 | 1322 | 0.562784 | -0.030106 | NONE |
| 1X2 | home | closing_fair_probability | 0.6-0.7 | 1032 | 0.682171 | -0.005107 | NONE |
| 1X2 | home | closing_fair_probability | 0.7-0.8 | 597 | 0.742044 | -0.05665 | NONE |
| 1X2 | home | closing_fair_probability | 0.8-0.9 | 218 | 0.844037 | -0.044312 | SMALL_SAMPLE |
| 1X2 | home | closing_fair_probability | 0.9-1.0 | 2 | 1 | 0.045 | SMALL_SAMPLE |
| 1X2 | home | closing_fair_probability | MISSING | 0 | 0 | 0 | SMALL_SAMPLE |
| 1X2 | draw | closing_fair_probability | 0.0-0.1 | 75 | 0.066667 | -0.28 | SMALL_SAMPLE |
| 1X2 | draw | closing_fair_probability | 0.1-0.2 | 1502 | 0.163782 | -0.065047 | NONE |
| 1X2 | draw | closing_fair_probability | 0.2-0.3 | 6567 | 0.268311 | -0.022749 | NONE |
| 1X2 | draw | closing_fair_probability | 0.3-0.4 | 836 | 0.316986 | -0.045742 | NONE |
| 1X2 | draw | closing_fair_probability | 0.4-0.5 | 1 | 1 | 1 | SMALL_SAMPLE|CONCENTRATION_RISK |
| 1X2 | draw | closing_fair_probability | MISSING | 0 | 0 | 0 | SMALL_SAMPLE |
| 1X2 | away | closing_fair_probability | 0.0-0.1 | 610 | 0.072131 | -0.081148 | NONE |
| 1X2 | away | closing_fair_probability | 0.1-0.2 | 1955 | 0.142711 | -0.140281 | NONE |
| 1X2 | away | closing_fair_probability | 0.2-0.3 | 2167 | 0.241347 | -0.094232 | NONE |

## Self Check

| check | status |
| --- | --- |
| input_rows_10733 | PASS |
| backtest_rows_8982 | PASS |
| excluded_current_rows_1751 | PASS |
| no_2025_26_in_backtest | PASS |
| only_complete_backtest_rows_used | PASS |
| bucket_results_nonempty | PASS |
| sample_lt_500_marked_small_sample | PASS |
| positive_roi_high_drawdown_marked | PASS |
| recommendations_generated_no | PASS |
| old_system_touched_no | PASS |
