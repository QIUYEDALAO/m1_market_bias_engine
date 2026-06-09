# M1 Stability Candidate Audit

- generated_at_utc: `2026-06-09T23:13:36+00:00`
- stability_csv: `data/processed/backtest_ready/m1_stability_filtered_buckets.csv`
- bucket_csv: `data/processed/backtest_ready/m1_bucket_results.csv`
- feature_csv: `data/processed/market_features/m1_market_features.csv`
- checker: `PASS`
- research_only: `YES`
- not_play: `YES`
- recommendations_generated: `NO`
- official_written: `NO`
- pending_written: `NO`
- qq_written: `NO`
- old_system_touched: `NO`

This audit explains stable/watch buckets for research review only. It is not PLAY, not a recommendation, and not a current-match matching layer.

## Summary

| metric | value |
| --- | --- |
| stable_count | 1 |
| watch_count | 1 |
| positive_roi_bucket_count | 25 |
| candidate_audit_count | 2 |
| current_2025_26_candidate_rows | 0 |

## Candidate Audit

| status | market | selection | bucket_type | bucket | sample_count | hit_rate | roi | avg_odds | max_losing_streak | max_drawdown | cross_league | cross_season | single_league_dependent | single_season_dependent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| STABLE_RESEARCH_CANDIDATE | 1X2 | away | closing_fair_probability | 0.4-0.5 | 1181 | 0.480102 | 0.016943 | 2.124793 | 10 | -0.037053 | True | True | False | False |
| WATCHLIST_RESEARCH_ONLY | 1X2 | draw | open_to_close_odds_movement | 0.25-0.50 | 686 | 0.236152 | 0.041312 | 4.524082 | 16 | -0.048353 | True | True | False | False |

## Field And Settlement Bias Review

| status | risk_flags | notes |
| --- | --- | --- |
| STABLE_RESEARCH_CANDIDATE | NO_MAJOR_FIELD_OR_SETTLEMENT_BIAS_DETECTED | Uses full_time_result and B365 1X2 closing odds/fair probability features. |
| WATCHLIST_RESEARCH_ONLY | DRAW_OUTCOME_VOLATILITY, FIELD_MOVEMENT_SENSITIVITY | Uses full_time_result and B365 1X2 closing odds/fair probability features. Depends on opening-to-closing B365 odds delta; sensitive to stale or sparse opening quotes. Draw buckets can be more volatile because draw hit rate is structurally lower. |

## Candidate Distributions

### STABLE_RESEARCH_CANDIDATE 1X2 away closing_fair_probability 0.4-0.5

League distribution:

| league | rows |
| --- | --- |
| D1 | 204 |
| E0 | 267 |
| F1 | 233 |
| I1 | 254 |
| SP1 | 223 |

Season distribution:

| season | rows |
| --- | --- |
| 2020/21 | 241 |
| 2021/22 | 255 |
| 2022/23 | 230 |
| 2023/24 | 226 |
| 2024/25 | 229 |

### WATCHLIST_RESEARCH_ONLY 1X2 draw open_to_close_odds_movement 0.25-0.50

League distribution:

| league | rows |
| --- | --- |
| D1 | 133 |
| E0 | 132 |
| F1 | 147 |
| I1 | 134 |
| SP1 | 140 |

Season distribution:

| season | rows |
| --- | --- |
| 2020/21 | 174 |
| 2021/22 | 146 |
| 2022/23 | 103 |
| 2023/24 | 122 |
| 2024/25 | 141 |

## Positive ROI Bucket Reject Summary

| metric | value |
| --- | --- |
| positive_roi_bucket_count | 25 |

Status counts:

| status | count |
| --- | --- |
| REJECT_CONCENTRATION\|REJECT_HIGH_DRAWDOWN\|REJECT_SMALL_SAMPLE | 7 |
| REJECT_CONCENTRATION\|REJECT_SMALL_SAMPLE | 1 |
| REJECT_HIGH_DRAWDOWN\|REJECT_SMALL_SAMPLE | 9 |
| REJECT_SMALL_SAMPLE | 6 |
| STABLE_RESEARCH_CANDIDATE | 1 |
| WATCHLIST_RESEARCH_ONLY | 1 |

Hard reject reason counts:

| reason | count |
| --- | --- |
| REJECT_CONCENTRATION | 8 |
| REJECT_HIGH_DRAWDOWN | 16 |
| REJECT_SMALL_SAMPLE | 23 |

Watchlist reason counts:

| reason | count |
| --- | --- |
| WATCH_LOW_SAMPLE_MARGIN | 1 |

## Self Check

| check | status |
| --- | --- |
| stable_count_1 | PASS |
| watch_count_1 | PASS |
| positive_roi_bucket_count_25 | PASS |
| candidate_audit_count_2 | PASS |
| input_feature_rows_10733 | PASS |
| no_current_2025_26_candidates | PASS |
| all_candidates_research_only_not_play | PASS |
| all_candidates_have_distribution_review | PASS |
| recommendations_generated_no | PASS |
| old_system_touched_no | PASS |
