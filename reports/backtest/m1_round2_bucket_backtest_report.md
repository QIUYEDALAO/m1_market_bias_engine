# M1 Round2 Bucket Backtest Report

- generated_at_utc: `2026-06-10T00:15:02+00:00`
- input_csv: `data/processed/market_features/m1_round2_market_features.csv`
- normalized_context_csv: `data/processed/normalized_matches/m1_round2_matches_normalized.csv`
- output_csv: `data/processed/backtest_ready/m1_round2_bucket_results.csv`
- checker: `PASS`
- backtest_scope: `COMPLETE_BACKTEST_ONLY`
- excluded_current_policy: `2025/26 CURRENT_NOT_FOR_BACKTEST excluded`
- recommendations_generated: `NO`
- round1_merged: `NO`
- official_written: `NO`
- pending_written: `NO`
- qq_written: `NO`
- old_system_touched: `NO`

## Summary

| metric | value |
| --- | --- |
| input_rows | 9063 |
| backtest_rows | 7606 |
| excluded_current_rows | 1457 |
| bucket_rows | 139 |
| positive_roi_bucket_count | 25 |

This is an offline Round2 bucket backtest over `COMPLETE_BACKTEST` rows only. It does not merge Round1 data, match current fixtures, generate recommendations, or write official/pending/QQ outputs.

AH closing line buckets and OU 2.5 closing probability buckets use `match_id`-joined closing line/odds context from the normalized table. The backtest row filter remains `season_role=COMPLETE_BACKTEST`.

## Reject Reason Counts

| reject_reason | bucket_count |
| --- | --- |
| CONCENTRATION_RISK | 16 |
| HIGH_DRAWDOWN_RISK | 9 |
| NONE | 53 |
| SMALL_SAMPLE | 86 |

## Backtest Distributions

League distribution:

| league | rows |
| --- | --- |
| B1 | 1542 |
| N1 | 1530 |
| P1 | 1530 |
| SC0 | 1140 |
| T1 | 1864 |

Season distribution:

| season | rows |
| --- | --- |
| 2020/21 | 1566 |
| 2021/22 | 1526 |
| 2022/23 | 1488 |
| 2023/24 | 1532 |
| 2024/25 | 1494 |

## Bucket Preview

| market | selection | bucket_type | bucket | sample_count | hit_rate | roi | reject_reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1X2 | home | closing_fair_probability | 0.0-0.1 | 206 | 0.07767 | -0.048544 | SMALL_SAMPLE |
| 1X2 | home | closing_fair_probability | 0.1-0.2 | 675 | 0.111111 | -0.321111 | NONE |
| 1X2 | home | closing_fair_probability | 0.2-0.3 | 882 | 0.241497 | -0.112154 | NONE |
| 1X2 | home | closing_fair_probability | 0.3-0.4 | 1605 | 0.344548 | -0.086081 | NONE |
| 1X2 | home | closing_fair_probability | 0.4-0.5 | 1688 | 0.449052 | -0.062778 | NONE |
| 1X2 | home | closing_fair_probability | 0.5-0.6 | 1071 | 0.571429 | -0.01887 | NONE |
| 1X2 | home | closing_fair_probability | 0.6-0.7 | 655 | 0.667176 | -0.031496 | NONE |
| 1X2 | home | closing_fair_probability | 0.7-0.8 | 506 | 0.810277 | 0.015692 | NONE |
| 1X2 | home | closing_fair_probability | 0.8-0.9 | 279 | 0.899642 | 0.012939 | SMALL_SAMPLE |
| 1X2 | home | closing_fair_probability | 0.9-1.0 | 9 | 0.888889 | -0.076667 | SMALL_SAMPLE|CONCENTRATION_RISK |
| 1X2 | home | closing_fair_probability | MISSING | 0 | 0 | 0 | SMALL_SAMPLE |
| 1X2 | draw | closing_fair_probability | 0.0-0.1 | 101 | 0.059406 | -0.247525 | SMALL_SAMPLE |
| 1X2 | draw | closing_fair_probability | 0.1-0.2 | 1365 | 0.141392 | -0.177289 | NONE |
| 1X2 | draw | closing_fair_probability | 0.2-0.3 | 5554 | 0.267015 | -0.043252 | NONE |
| 1X2 | draw | closing_fair_probability | 0.3-0.4 | 556 | 0.298561 | -0.095935 | NONE |
| 1X2 | draw | closing_fair_probability | MISSING | 1 | 1 | 2.75 | SMALL_SAMPLE|CONCENTRATION_RISK |
| 1X2 | away | closing_fair_probability | 0.0-0.1 | 639 | 0.034429 | -0.534429 | NONE |
| 1X2 | away | closing_fair_probability | 0.1-0.2 | 1297 | 0.145721 | -0.129915 | NONE |
| 1X2 | away | closing_fair_probability | 0.2-0.3 | 2009 | 0.22449 | -0.169597 | NONE |
| 1X2 | away | closing_fair_probability | 0.3-0.4 | 1617 | 0.337662 | -0.088262 | NONE |

## Self Check

| check | status |
| --- | --- |
| input_rows_9063 | PASS |
| backtest_rows_7606 | PASS |
| excluded_current_rows_1457 | PASS |
| no_2025_26_in_backtest | PASS |
| only_complete_backtest_rows_used | PASS |
| bucket_results_nonempty | PASS |
| sample_lt_500_marked_small_sample | PASS |
| positive_roi_high_drawdown_marked | PASS |
| recommendations_generated_no | PASS |
| old_system_touched_no | PASS |
