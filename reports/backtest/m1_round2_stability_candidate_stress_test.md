# M1 Round2 Stability Candidate Stress Test

- generated_at_utc: `2026-06-10T00:32:40+00:00`
- stability_csv: `data/processed/backtest_ready/m1_round2_stability_filtered_buckets.csv`
- feature_csv: `data/processed/market_features/m1_round2_market_features.csv`
- normalized_csv: `data/processed/normalized_matches/m1_round2_matches_normalized.csv`
- candidate_audit_json: `reports/backtest/m1_round2_stability_candidate_audit.json`
- checker: `PASS`
- research_only: `YES`
- not_play: `YES`
- recommendations_generated: `NO`
- round1_merged: `NO`
- five_dimension_can_create_candidate: `false`
- current_match_matching: `NO`
- official_written: `NO`
- pending_written: `NO`
- qq_written: `NO`
- old_system_touched: `NO`

This is a Round2 research-only stress test. SURVIVED does not mean PLAY; FRAGILE does not create a live action. No current fixtures are matched, and five-dimension evaluation cannot create candidates.

## Summary

| metric | value |
| --- | --- |
| stable_count | 0 |
| watch_count | 3 |
| candidate_count | 3 |
| stress_test_count | 48 |
| critical_stress_test_count | 45 |
| survived_count | 1 |
| fragile_count | 2 |
| current_2025_26_slice_rows | 0 |

## Candidate Stress Status

| status | market | selection | bucket_type | bucket | base_sample_count | stress_status | critical_failure_count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| WATCHLIST_RESEARCH_ONLY | 1X2 | home | closing_fair_probability | 0.7-0.8 | 506 | FRAGILE | 1 |
| WATCHLIST_RESEARCH_ONLY | AH | home_handicap | closing_line | -0.75 | 617 | SURVIVED | 0 |
| WATCHLIST_RESEARCH_ONLY | 1X2 | draw | open_to_close_odds_movement | 0.25-0.50 | 603 | FRAGILE | 5 |

## Stress Slices

### WATCHLIST_RESEARCH_ONLY 1X2 home closing_fair_probability 0.7-0.8

| slice_type | slice_name | critical | sample_count | hit_rate | roi | max_drawdown | slice_status | failure_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all_complete_backtest | all | True | 506 | 0.810277 | 0.015692 | -0.022115 | PASS | NONE |
| leave_one_season_out | without_2020/21 | True | 408 | 0.823529 | 0.030711 | -0.011005 | PASS | NONE |
| leave_one_season_out | without_2021/22 | True | 416 | 0.814904 | 0.022115 | -0.019567 | PASS | NONE |
| leave_one_season_out | without_2022/23 | True | 412 | 0.798544 | 0.001408 | -0.037888 | PASS | NONE |
| leave_one_season_out | without_2023/24 | True | 379 | 0.804749 | 0.010264 | -0.031214 | PASS | NONE |
| leave_one_season_out | without_2024/25 | True | 409 | 0.809291 | 0.013594 | -0.028704 | PASS | NONE |
| leave_one_league_out | without_B1 | True | 421 | 0.817102 | 0.022779 | -0.02266 | PASS | NONE |
| leave_one_league_out | without_N1 | True | 377 | 0.830239 | 0.039629 | -0.014005 | PASS | NONE |
| leave_one_league_out | without_P1 | True | 370 | 0.791892 | -0.005027 | -0.030243 | FAIL | NON_POSITIVE_ROI |
| leave_one_league_out | without_SC0 | True | 435 | 0.806897 | 0.013287 | -0.025724 | PASS | NONE |
| leave_one_league_out | without_T1 | True | 421 | 0.805226 | 0.007862 | -0.02658 | PASS | NONE |
| first_half_vs_second_half | first_half_2020_21_to_2022_23 | True | 282 | 0.801418 | 0.005355 | -0.043901 | PASS | NONE |
| first_half_vs_second_half | second_half_2023_24_to_2024_25 | True | 224 | 0.821429 | 0.028705 | -0.020446 | PASS | NONE |
| league_group_split | group_a_n1_b1_p1 | True | 350 | 0.8 | 0.003286 | -0.031971 | PASS | NONE |
| league_group_split | group_b_t1_sc0 | True | 156 | 0.833333 | 0.043526 | -0.024423 | PASS | NONE |
| odds_source_sanity_check | bookmaker_source_B365 | False | 506 | 0.810277 | 0.015692 | -0.022115 | PASS | NONE |

### WATCHLIST_RESEARCH_ONLY AH home_handicap closing_line -0.75

| slice_type | slice_name | critical | sample_count | hit_rate | roi | max_drawdown | slice_status | failure_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all_complete_backtest | all | True | 617 | 0.614263 | 0.060024 | -0.021386 | PASS | NONE |
| leave_one_season_out | without_2020/21 | True | 500 | 0.622 | 0.07068 | -0.01799 | PASS | NONE |
| leave_one_season_out | without_2021/22 | True | 498 | 0.626506 | 0.074197 | -0.016556 | PASS | NONE |
| leave_one_season_out | without_2022/23 | True | 508 | 0.606299 | 0.050797 | -0.025974 | PASS | NONE |
| leave_one_season_out | without_2023/24 | True | 495 | 0.610101 | 0.053071 | -0.026657 | PASS | NONE |
| leave_one_season_out | without_2024/25 | True | 467 | 0.605996 | 0.05091 | -0.028255 | PASS | NONE |
| leave_one_league_out | without_B1 | True | 456 | 0.60307 | 0.036787 | -0.028936 | PASS | NONE |
| leave_one_league_out | without_N1 | True | 498 | 0.626506 | 0.07996 | -0.017861 | PASS | NONE |
| leave_one_league_out | without_P1 | True | 539 | 0.617811 | 0.067931 | -0.024481 | PASS | NONE |
| leave_one_league_out | without_SC0 | True | 522 | 0.605364 | 0.042423 | -0.025278 | PASS | NONE |
| leave_one_league_out | without_T1 | True | 453 | 0.618102 | 0.072373 | -0.029128 | PASS | NONE |
| first_half_vs_second_half | first_half_2020_21_to_2022_23 | True | 345 | 0.597101 | 0.03771 | -0.038246 | PASS | NONE |
| first_half_vs_second_half | second_half_2023_24_to_2024_25 | True | 272 | 0.636029 | 0.088327 | -0.032849 | PASS | NONE |
| league_group_split | group_a_n1_b1_p1 | True | 358 | 0.606145 | 0.049986 | -0.036858 | PASS | NONE |
| league_group_split | group_b_t1_sc0 | True | 259 | 0.625483 | 0.0739 | -0.034344 | PASS | NONE |
| odds_source_sanity_check | bookmaker_source_B365 | False | 617 | 0.614263 | 0.060024 | -0.021386 | PASS | NONE |

### WATCHLIST_RESEARCH_ONLY 1X2 draw open_to_close_odds_movement 0.25-0.50

| slice_type | slice_name | critical | sample_count | hit_rate | roi | max_drawdown | slice_status | failure_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all_complete_backtest | all | True | 603 | 0.232172 | 0.005257 | -0.069635 | PASS | NONE |
| leave_one_season_out | without_2020/21 | True | 467 | 0.222698 | -0.041306 | -0.107752 | FAIL | NON_POSITIVE_ROI |
| leave_one_season_out | without_2021/22 | True | 474 | 0.225738 | -0.01384 | -0.093017 | FAIL | NON_POSITIVE_ROI |
| leave_one_season_out | without_2022/23 | True | 497 | 0.243461 | 0.053742 | -0.068249 | PASS | NONE |
| leave_one_season_out | without_2023/24 | True | 484 | 0.235537 | 0.014669 | -0.063926 | PASS | NONE |
| leave_one_season_out | without_2024/25 | True | 490 | 0.232653 | 0.009633 | -0.071612 | PASS | NONE |
| leave_one_league_out | without_B1 | True | 454 | 0.231278 | 0.007996 | -0.078172 | PASS | NONE |
| leave_one_league_out | without_N1 | True | 468 | 0.237179 | 0.014081 | -0.082415 | PASS | NONE |
| leave_one_league_out | without_P1 | True | 504 | 0.234127 | 0.019524 | -0.070377 | PASS | NONE |
| leave_one_league_out | without_SC0 | True | 527 | 0.222011 | -0.047647 | -0.086907 | FAIL | NON_POSITIVE_ROI |
| leave_one_league_out | without_T1 | True | 459 | 0.237473 | 0.038627 | -0.091481 | PASS | NONE |
| first_half_vs_second_half | first_half_2020_21_to_2022_23 | True | 371 | 0.237197 | 0.023315 | -0.077493 | PASS | NONE |
| first_half_vs_second_half | second_half_2023_24_to_2024_25 | True | 232 | 0.224138 | -0.023621 | -0.171638 | FAIL | NON_POSITIVE_ROI |
| league_group_split | group_a_n1_b1_p1 | True | 383 | 0.224543 | -0.027546 | -0.109634 | FAIL | NON_POSITIVE_ROI |
| league_group_split | group_b_t1_sc0 | True | 220 | 0.245455 | 0.062364 | -0.161227 | PASS | NONE |
| odds_source_sanity_check | bookmaker_source_B365 | False | 603 | 0.232172 | 0.005257 | -0.069635 | PASS | NONE |

## Self Check

| check | status |
| --- | --- |
| stable_count_0 | PASS |
| watch_count_3 | PASS |
| candidate_count_3 | PASS |
| stress_tests_generated | PASS |
| complete_backtest_only | PASS |
| feature_rows_9063 | PASS |
| complete_rows_7606 | PASS |
| current_rows_excluded_1457 | PASS |
| all_candidates_research_only_not_play | PASS |
| recommendations_generated_no | PASS |
| old_system_touched_no | PASS |
