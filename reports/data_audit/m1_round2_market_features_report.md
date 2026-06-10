# M1 Round2 Market Features Report

- generated_at_utc: `2026-06-10T00:12:36+00:00`
- input_csv: `data/processed/normalized_matches/m1_round2_matches_normalized.csv`
- output_csv: `data/processed/market_features/m1_round2_market_features.csv`
- checker: `PASS`
- old_system_touched: `NO`
- recommendations_generated: `NO`
- backtest_run: `NO`
- round1_merged: `NO`

## Summary

| metric | value |
| --- | --- |
| input_rows | 9063 |
| output_rows | 9063 |
| complete_backtest_feature_rows | 7606 |
| current_not_for_backtest_feature_rows | 1457 |
| fair_opening_probability_rows | 9013 |
| fair_closing_probability_rows | 9033 |
| fair_probability_sum_failures | 0 |
| ah_settlement_coverage | 0.996690 |
| ou25_settlement_coverage | 1.000000 |

`2025/26` rows are preserved as `CURRENT_NOT_FOR_BACKTEST`; they are not included in `complete_backtest_feature_rows`. This phase computes features only from the Round2 normalized table. It does not merge Round1 data, run a backtest, or generate recommendations.

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
| EMPTY | 30 |
| FULL_WIN | 3559 |
| HALF_LOSS | 748 |
| HALF_WIN | 568 |
| LOSS | 3530 |
| PUSH | 628 |

## OU 2.5 Settlement Counts

| settlement | rows |
| --- | --- |
| OVER_WIN | 4892 |
| UNDER_WIN | 4171 |

## Self Check

| check | status |
| --- | --- |
| input_rows_9063 | PASS |
| output_rows_9063 | PASS |
| complete_backtest_feature_rows_7606 | PASS |
| current_not_for_backtest_feature_rows_1457 | PASS |
| current_not_in_complete_backtest_features | PASS |
| fair_probabilities_sum_to_one | PASS |
| ah_settlement_coverage_reasonable | PASS |
| ou25_settlement_coverage_reasonable | PASS |
| backtest_run_no | PASS |
| recommendations_generated_no | PASS |
| old_system_touched_no | PASS |
