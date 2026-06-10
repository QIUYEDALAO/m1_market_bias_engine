# M1 Round2 Stability Candidate Audit

- generated_at_utc: `2026-06-10T00:31:10+00:00`
- stability_csv: `data/processed/backtest_ready/m1_round2_stability_filtered_buckets.csv`
- bucket_csv: `data/processed/backtest_ready/m1_round2_bucket_results.csv`
- feature_csv: `data/processed/market_features/m1_round2_market_features.csv`
- checker: `PASS`
- research_only: `YES`
- not_play: `YES`
- recommendations_generated: `NO`
- round1_merged: `NO`
- five_dimension_can_create_candidate: `false`
- official_written: `NO`
- pending_written: `NO`
- qq_written: `NO`
- old_system_touched: `NO`

This audit explains Round2 stable/watch buckets for research review only. It is not PLAY, not a recommendation, not a current-match matching layer, and five-dimension evaluation cannot create candidates.

## Summary

| metric | value |
| --- | --- |
| stable_count | 0 |
| watch_count | 3 |
| positive_roi_bucket_count | 25 |
| candidate_audit_count | 3 |
| current_2025_26_candidate_rows | 0 |

## Candidate Audit

| status | market | selection | bucket_type | bucket | sample_count | hit_rate | roi | avg_odds | max_losing_streak | max_drawdown | cross_league | cross_season | single_league_dependent | single_season_dependent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WATCHLIST_RESEARCH_ONLY | 1X2 | home | closing_fair_probability | 0.7-0.8 | 506 | 0.810277 | 0.015692 | 1.254625 | 3 | -0.022115 | True | True | False | False |
| WATCHLIST_RESEARCH_ONLY | AH | home_handicap | closing_line | -0.75 | 617 | 0.614263 | 0.060024 | 1.927812 | 7 | -0.021386 | True | True | False | False |
| WATCHLIST_RESEARCH_ONLY | 1X2 | draw | open_to_close_odds_movement | 0.25-0.50 | 603 | 0.232172 | 0.005257 | 4.393433 | 32 | -0.069635 | True | True | False | False |

## Field And Settlement Bias Review

| status | risk_flags | notes |
| --- | --- | --- |
| WATCHLIST_RESEARCH_ONLY | NO_MAJOR_FIELD_OR_SETTLEMENT_BIAS_DETECTED | Uses full_time_result and B365 1X2 closing odds/fair probability features. |
| WATCHLIST_RESEARCH_ONLY | SETTLEMENT_FORMULA_SENSITIVITY | Uses AH settlement and AH closing line context; quarter-line settlement can create half outcomes. |
| WATCHLIST_RESEARCH_ONLY | DRAW_OUTCOME_VOLATILITY, FIELD_MOVEMENT_SENSITIVITY | Uses full_time_result and B365 1X2 closing odds/fair probability features. Depends on opening-to-closing B365 odds delta; sensitive to stale or sparse opening quotes. Draw buckets can be more volatile because draw hit rate is structurally lower. |

## Candidate Distributions

### WATCHLIST_RESEARCH_ONLY 1X2 home closing_fair_probability 0.7-0.8

League distribution:

| league | rows |
| --- | --- |
| B1 | 85 |
| N1 | 129 |
| P1 | 136 |
| SC0 | 71 |
| T1 | 85 |

Season distribution:

| season | rows |
| --- | --- |
| 2020/21 | 98 |
| 2021/22 | 90 |
| 2022/23 | 94 |
| 2023/24 | 127 |
| 2024/25 | 97 |

### WATCHLIST_RESEARCH_ONLY AH home_handicap closing_line -0.75

League distribution:

| league | rows |
| --- | --- |
| B1 | 161 |
| N1 | 119 |
| P1 | 78 |
| SC0 | 95 |
| T1 | 164 |

Season distribution:

| season | rows |
| --- | --- |
| 2020/21 | 117 |
| 2021/22 | 119 |
| 2022/23 | 109 |
| 2023/24 | 122 |
| 2024/25 | 150 |

### WATCHLIST_RESEARCH_ONLY 1X2 draw open_to_close_odds_movement 0.25-0.50

League distribution:

| league | rows |
| --- | --- |
| B1 | 149 |
| N1 | 135 |
| P1 | 99 |
| SC0 | 76 |
| T1 | 144 |

Season distribution:

| season | rows |
| --- | --- |
| 2020/21 | 136 |
| 2021/22 | 129 |
| 2022/23 | 106 |
| 2023/24 | 119 |
| 2024/25 | 113 |

## Positive ROI Bucket Reject Summary

| metric | value |
| --- | --- |
| positive_roi_bucket_count | 25 |

Status counts:

| status | count |
| --- | --- |
| REJECT_CONCENTRATION\|REJECT_HIGH_DRAWDOWN\|REJECT_SMALL_SAMPLE | 6 |
| REJECT_CONCENTRATION\|REJECT_SMALL_SAMPLE | 2 |
| REJECT_HIGH_DRAWDOWN\|REJECT_SMALL_SAMPLE | 3 |
| REJECT_SMALL_SAMPLE | 11 |
| WATCHLIST_RESEARCH_ONLY | 3 |

Hard reject reason counts:

| reason | count |
| --- | --- |
| REJECT_CONCENTRATION | 8 |
| REJECT_HIGH_DRAWDOWN | 9 |
| REJECT_SMALL_SAMPLE | 22 |

Watchlist reason counts:

| reason | count |
| --- | --- |
| WATCH_LOW_SAMPLE_MARGIN | 3 |

## Self Check

| check | status |
| --- | --- |
| stable_count_0 | PASS |
| watch_count_3 | PASS |
| positive_roi_bucket_count_25 | PASS |
| candidate_audit_count_3 | PASS |
| input_feature_rows_9063 | PASS |
| no_current_2025_26_candidates | PASS |
| all_candidates_research_only_not_play | PASS |
| all_candidates_have_distribution_review | PASS |
| recommendations_generated_no | PASS |
| old_system_touched_no | PASS |
