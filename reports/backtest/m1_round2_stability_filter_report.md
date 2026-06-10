# M1 Round2 Stability Filter Report

- generated_at_utc: `2026-06-10T00:30:13+00:00`
- input_csv: `data/processed/backtest_ready/m1_round2_bucket_results.csv`
- input_report: `reports/backtest/m1_round2_bucket_backtest_report.json`
- thresholds: `config/round2_stability_thresholds.json`
- output_csv: `data/processed/backtest_ready/m1_round2_stability_filtered_buckets.csv`
- checker: `PASS`
- research_only: `YES`
- recommendations_generated: `NO`
- round1_merged: `NO`
- five_dimension_can_create_candidate: `false`
- official_written: `NO`
- pending_written: `NO`
- qq_written: `NO`
- old_system_touched: `NO`

## Summary

| metric | value |
| --- | --- |
| input_bucket_rows | 139 |
| output_bucket_rows | 139 |
| stable_count | 0 |
| watch_count | 3 |
| rejected_count | 136 |
| positive_roi_bucket_count | 25 |
| current_2025_26_bucket_rows | 0 |

This phase filters Round2 offline bucket results only. It does not merge Round1, match current fixtures, generate recommendations, write official/pending/QQ outputs, or allow five-dimension evaluation to create candidates.

## Status Counts

| status | bucket_count |
| --- | --- |
| REJECT_CONCENTRATION\|REJECT_HIGH_DRAWDOWN\|REJECT_SMALL_SAMPLE | 6 |
| REJECT_CONCENTRATION\|REJECT_NON_POSITIVE_ROI\|REJECT_SMALL_SAMPLE | 8 |
| REJECT_CONCENTRATION\|REJECT_SMALL_SAMPLE | 2 |
| REJECT_HIGH_DRAWDOWN\|REJECT_SMALL_SAMPLE | 3 |
| REJECT_NON_POSITIVE_ROI | 50 |
| REJECT_NON_POSITIVE_ROI\|REJECT_SMALL_SAMPLE | 56 |
| REJECT_SMALL_SAMPLE | 11 |
| WATCHLIST_RESEARCH_ONLY | 3 |

## Hard Reject Reason Counts

| reason | bucket_count |
| --- | --- |
| REJECT_CONCENTRATION | 16 |
| REJECT_HIGH_DRAWDOWN | 9 |
| REJECT_NON_POSITIVE_ROI | 114 |
| REJECT_SMALL_SAMPLE | 86 |

## Watchlist Reason Counts

| reason | bucket_count |
| --- | --- |
| WATCH_LOW_SAMPLE_MARGIN | 3 |

## Bucket Preview

| market | selection | bucket_type | bucket | sample_count | roi | stability_status | stability_reject_reasons | watchlist_reasons |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1X2 | home | closing_fair_probability | 0.0-0.1 | 206 | -0.048544 | REJECT_NON_POSITIVE_ROI\|REJECT_SMALL_SAMPLE | REJECT_NON_POSITIVE_ROI\|REJECT_SMALL_SAMPLE | NONE |
| 1X2 | home | closing_fair_probability | 0.1-0.2 | 675 | -0.321111 | REJECT_NON_POSITIVE_ROI | REJECT_NON_POSITIVE_ROI | NONE |
| 1X2 | home | closing_fair_probability | 0.2-0.3 | 882 | -0.112154 | REJECT_NON_POSITIVE_ROI | REJECT_NON_POSITIVE_ROI | NONE |
| 1X2 | home | closing_fair_probability | 0.3-0.4 | 1605 | -0.086081 | REJECT_NON_POSITIVE_ROI | REJECT_NON_POSITIVE_ROI | NONE |
| 1X2 | home | closing_fair_probability | 0.4-0.5 | 1688 | -0.062778 | REJECT_NON_POSITIVE_ROI | REJECT_NON_POSITIVE_ROI | NONE |
| 1X2 | home | closing_fair_probability | 0.5-0.6 | 1071 | -0.01887 | REJECT_NON_POSITIVE_ROI | REJECT_NON_POSITIVE_ROI | NONE |
| 1X2 | home | closing_fair_probability | 0.6-0.7 | 655 | -0.031496 | REJECT_NON_POSITIVE_ROI | REJECT_NON_POSITIVE_ROI | NONE |
| 1X2 | home | closing_fair_probability | 0.7-0.8 | 506 | 0.015692 | WATCHLIST_RESEARCH_ONLY | NONE | WATCH_LOW_SAMPLE_MARGIN |
| 1X2 | home | closing_fair_probability | 0.8-0.9 | 279 | 0.012939 | REJECT_SMALL_SAMPLE | REJECT_SMALL_SAMPLE | NONE |
| 1X2 | home | closing_fair_probability | 0.9-1.0 | 9 | -0.076667 | REJECT_CONCENTRATION\|REJECT_NON_POSITIVE_ROI\|REJECT_SMALL_SAMPLE | REJECT_CONCENTRATION\|REJECT_NON_POSITIVE_ROI\|REJECT_SMALL_SAMPLE | NONE |
| 1X2 | home | closing_fair_probability | MISSING | 0 | 0 | REJECT_NON_POSITIVE_ROI\|REJECT_SMALL_SAMPLE | REJECT_NON_POSITIVE_ROI\|REJECT_SMALL_SAMPLE | NONE |
| 1X2 | draw | closing_fair_probability | 0.0-0.1 | 101 | -0.247525 | REJECT_NON_POSITIVE_ROI\|REJECT_SMALL_SAMPLE | REJECT_NON_POSITIVE_ROI\|REJECT_SMALL_SAMPLE | NONE |
| 1X2 | draw | closing_fair_probability | 0.1-0.2 | 1365 | -0.177289 | REJECT_NON_POSITIVE_ROI | REJECT_NON_POSITIVE_ROI | NONE |
| 1X2 | draw | closing_fair_probability | 0.2-0.3 | 5554 | -0.043252 | REJECT_NON_POSITIVE_ROI | REJECT_NON_POSITIVE_ROI | NONE |
| 1X2 | draw | closing_fair_probability | 0.3-0.4 | 556 | -0.095935 | REJECT_NON_POSITIVE_ROI | REJECT_NON_POSITIVE_ROI | NONE |
| 1X2 | draw | closing_fair_probability | MISSING | 1 | 2.75 | REJECT_CONCENTRATION\|REJECT_SMALL_SAMPLE | REJECT_CONCENTRATION\|REJECT_SMALL_SAMPLE | NONE |
| 1X2 | away | closing_fair_probability | 0.0-0.1 | 639 | -0.534429 | REJECT_NON_POSITIVE_ROI | REJECT_NON_POSITIVE_ROI | NONE |
| 1X2 | away | closing_fair_probability | 0.1-0.2 | 1297 | -0.129915 | REJECT_NON_POSITIVE_ROI | REJECT_NON_POSITIVE_ROI | NONE |
| 1X2 | away | closing_fair_probability | 0.2-0.3 | 2009 | -0.169597 | REJECT_NON_POSITIVE_ROI | REJECT_NON_POSITIVE_ROI | NONE |
| 1X2 | away | closing_fair_probability | 0.3-0.4 | 1617 | -0.088262 | REJECT_NON_POSITIVE_ROI | REJECT_NON_POSITIVE_ROI | NONE |

## Self Check

| check | status |
| --- | --- |
| input_bucket_rows_139 | PASS |
| output_bucket_rows_match_input | PASS |
| stable_watch_rejected_counted | PASS |
| positive_roi_buckets_have_stability_status | PASS |
| no_current_2025_26 | PASS |
| phase4_backtest_rows_7606 | PASS |
| phase4_excluded_current_rows_1457 | PASS |
| research_only_no_recommendations | PASS |
| no_official_pending_qq | PASS |
| old_system_touched_no | PASS |
