# M1 Stability Candidate Stress Test

- generated_at_utc: `2026-06-09T23:23:19+00:00`
- stability_csv: `data/processed/backtest_ready/m1_stability_filtered_buckets.csv`
- feature_csv: `data/processed/market_features/m1_market_features.csv`
- candidate_audit_json: `reports/backtest/m1_stability_candidate_audit.json`
- checker: `PASS`
- research_only: `YES`
- not_play: `YES`
- recommendations_generated: `NO`
- current_match_matching: `NO`
- official_written: `NO`
- pending_written: `NO`
- qq_written: `NO`
- old_system_touched: `NO`

This is a research-only stress test. SURVIVED does not mean PLAY; FRAGILE does not create a live action. No current fixtures are matched.

## Summary

| metric | value |
| --- | --- |
| stable_count | 1 |
| watch_count | 1 |
| candidate_count | 2 |
| stress_test_count | 32 |
| critical_stress_test_count | 30 |
| survived_count | 0 |
| fragile_count | 2 |
| current_2025_26_slice_rows | 0 |

## Candidate Stress Status

| status | market | selection | bucket_type | bucket | base_sample_count | stress_status | critical_failure_count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| STABLE_RESEARCH_CANDIDATE | 1X2 | away | closing_fair_probability | 0.4-0.5 | 1181 | FRAGILE | 3 |
| WATCHLIST_RESEARCH_ONLY | 1X2 | draw | open_to_close_odds_movement | 0.25-0.50 | 686 | FRAGILE | 1 |

## Stress Slices

### STABLE_RESEARCH_CANDIDATE 1X2 away closing_fair_probability 0.4-0.5

| slice_type | slice_name | critical | sample_count | hit_rate | roi | max_drawdown | slice_status | failure_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all_complete_backtest | all | True | 1181 | 0.480102 | 0.016943 | -0.037053 | PASS | NONE |
| leave_one_season_out | without_2020/21 | True | 940 | 0.481915 | 0.022649 | -0.038819 | PASS | NONE |
| leave_one_season_out | without_2021/22 | True | 926 | 0.480562 | 0.017203 | -0.036361 | PASS | NONE |
| leave_one_season_out | without_2022/23 | True | 951 | 0.491062 | 0.038675 | -0.030925 | PASS | NONE |
| leave_one_season_out | without_2023/24 | True | 955 | 0.478534 | 0.013759 | -0.039435 | PASS | NONE |
| leave_one_season_out | without_2024/25 | True | 952 | 0.468487 | -0.007458 | -0.05521 | FAIL | NON_POSITIVE_ROI |
| leave_one_league_out | without_D1 | True | 977 | 0.497441 | 0.053019 | -0.021279 | PASS | NONE |
| leave_one_league_out | without_E0 | True | 914 | 0.480306 | 0.018764 | -0.051007 | PASS | NONE |
| leave_one_league_out | without_F1 | True | 948 | 0.483122 | 0.02288 | -0.043365 | PASS | NONE |
| leave_one_league_out | without_I1 | True | 927 | 0.472492 | 0.002449 | -0.047206 | PASS | NONE |
| leave_one_league_out | without_SP1 | True | 958 | 0.466597 | -0.013434 | -0.045678 | FAIL | NON_POSITIVE_ROI |
| first_half_vs_second_half | first_half_2020_21_to_2022_23 | True | 726 | 0.46281 | -0.019242 | -0.065207 | FAIL | NON_POSITIVE_ROI |
| first_half_vs_second_half | second_half_2023_24_to_2024_25 | True | 455 | 0.507692 | 0.074681 | -0.034593 | PASS | NONE |
| league_group_split | group_a_e0_d1_sp1 | True | 694 | 0.474063 | 0.005692 | -0.059236 | PASS | NONE |
| league_group_split | group_b_i1_f1 | True | 487 | 0.488706 | 0.032977 | -0.038049 | PASS | NONE |
| odds_source_sanity_check | bookmaker_source_B365 | False | 1181 | 0.480102 | 0.016943 | -0.037053 | PASS | NONE |

### WATCHLIST_RESEARCH_ONLY 1X2 draw open_to_close_odds_movement 0.25-0.50

| slice_type | slice_name | critical | sample_count | hit_rate | roi | max_drawdown | slice_status | failure_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all_complete_backtest | all | True | 686 | 0.236152 | 0.041312 | -0.048353 | PASS | NONE |
| leave_one_season_out | without_2020/21 | True | 512 | 0.261719 | 0.168555 | -0.044766 | PASS | NONE |
| leave_one_season_out | without_2021/22 | True | 540 | 0.225926 | 0.005407 | -0.05713 | PASS | NONE |
| leave_one_season_out | without_2022/23 | True | 583 | 0.229846 | 0.016158 | -0.065403 | PASS | NONE |
| leave_one_season_out | without_2023/24 | True | 564 | 0.234043 | 0.01789 | -0.059486 | PASS | NONE |
| leave_one_season_out | without_2024/25 | True | 545 | 0.231193 | 0.008495 | -0.051229 | PASS | NONE |
| leave_one_league_out | without_D1 | True | 553 | 0.235081 | 0.031157 | -0.059982 | PASS | NONE |
| leave_one_league_out | without_E0 | True | 554 | 0.241877 | 0.054477 | -0.059874 | PASS | NONE |
| leave_one_league_out | without_F1 | True | 539 | 0.231911 | 0.02616 | -0.074991 | PASS | NONE |
| leave_one_league_out | without_I1 | True | 552 | 0.235507 | 0.03904 | -0.058062 | PASS | NONE |
| leave_one_league_out | without_SP1 | True | 546 | 0.236264 | 0.055495 | -0.060751 | PASS | NONE |
| first_half_vs_second_half | first_half_2020_21_to_2022_23 | True | 423 | 0.22695 | -0.032199 | -0.077045 | FAIL | NON_POSITIVE_ROI |
| first_half_vs_second_half | second_half_2023_24_to_2024_25 | True | 263 | 0.250951 | 0.159544 | -0.067681 | PASS | NONE |
| league_group_split | group_a_e0_d1_sp1 | True | 405 | 0.22963 | 0.018049 | -0.087185 | PASS | NONE |
| league_group_split | group_b_i1_f1 | True | 281 | 0.245552 | 0.07484 | -0.118043 | PASS | NONE |
| odds_source_sanity_check | bookmaker_source_B365 | False | 686 | 0.236152 | 0.041312 | -0.048353 | PASS | NONE |

## Self Check

| check | status |
| --- | --- |
| stable_count_1 | PASS |
| watch_count_1 | PASS |
| candidate_count_2 | PASS |
| stress_tests_generated | PASS |
| complete_backtest_only | PASS |
| feature_rows_10733 | PASS |
| complete_rows_8982 | PASS |
| current_rows_excluded_1751 | PASS |
| all_candidates_research_only_not_play | PASS |
| recommendations_generated_no | PASS |
| old_system_touched_no | PASS |
