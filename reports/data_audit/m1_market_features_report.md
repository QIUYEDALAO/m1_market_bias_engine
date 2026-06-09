# M1 Market Features Report

- generated_at_utc: `2026-06-09T22:59:00+00:00`
- input_csv: `data/processed/normalized_matches/m1_matches_normalized.csv`
- output_csv: `data/processed/market_features/m1_market_features.csv`
- checker: `PASS`
- old_system_touched: `NO`
- recommendations_generated: `NO`
- backtest_run: `NO`

## Summary

| metric | value |
| --- | --- |
| input_rows | 10733 |
| output_rows | 10733 |
| complete_backtest_feature_rows | 8982 |
| current_not_for_backtest_feature_rows | 1751 |
| fair_opening_probability_rows | 10728 |
| fair_closing_probability_rows | 10732 |
| fair_probability_sum_failures | 0 |
| ah_settlement_coverage | 1.000000 |
| ou25_settlement_coverage | 1.000000 |

`2025/26` rows are preserved as `CURRENT_NOT_FOR_BACKTEST`; they are not included in `complete_backtest_feature_rows`. This phase computes features only. It does not run a backtest and does not generate recommendations.

## Feature Groups

| group | fields |
| --- | --- |
| 1X2 raw implied probability | opening_*_implied_prob_raw, closing_*_implied_prob_raw |
| 1X2 fair probability | opening_*_fair_prob, closing_*_fair_prob |
| probability delta | home_fair_prob_delta, draw_fair_prob_delta, away_fair_prob_delta |
| odds delta | home_odds_delta, draw_odds_delta, away_odds_delta |
| AH movement | ah_line_movement, ah_home_odds_movement, ah_away_odds_movement |
| settlement | ah_settlement, ou25_settlement |

## AH Settlement Counts

| settlement | rows |
| --- | --- |
| FULL_WIN | 4158 |
| HALF_LOSS | 822 |
| HALF_WIN | 731 |
| LOSS | 4308 |
| PUSH | 714 |

## OU 2.5 Settlement Counts

| settlement | rows |
| --- | --- |
| OVER_WIN | 5693 |
| UNDER_WIN | 5040 |

## Self Check

| check | status |
| --- | --- |
| input_rows_10733 | PASS |
| output_rows_10733 | PASS |
| complete_backtest_feature_rows_8982 | PASS |
| current_not_for_backtest_feature_rows_1751 | PASS |
| current_not_in_complete_backtest_features | PASS |
| fair_probabilities_sum_to_one | PASS |
| ah_settlement_coverage_reasonable | PASS |
| ou25_settlement_coverage_reasonable | PASS |
| backtest_run_no | PASS |
| recommendations_generated_no | PASS |
| old_system_touched_no | PASS |
