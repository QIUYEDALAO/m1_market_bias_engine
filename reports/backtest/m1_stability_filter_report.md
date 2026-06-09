# M1 Stability Filter Report

- generated_at_utc: `2026-06-09T23:09:23+00:00`
- input_csv: `data/processed/backtest_ready/m1_bucket_results.csv`
- input_report: `reports/backtest/m1_bucket_backtest_report.json`
- thresholds: `config/stability_thresholds.json`
- output_csv: `data/processed/backtest_ready/m1_stability_filtered_buckets.csv`
- checker: `PASS`
- research_only: `YES`
- recommendations_generated: `NO`
- official_written: `NO`
- pending_written: `NO`
- qq_written: `NO`
- old_system_touched: `NO`

## Summary

| metric | value |
| --- | --- |
| input_bucket_rows | 139 |
| output_bucket_rows | 139 |
| stable_count | 1 |
| watch_count | 1 |
| rejected_count | 137 |
| positive_roi_bucket_count | 25 |
| current_2025_26_bucket_rows | 0 |

This phase filters offline bucket results only. It does not match current fixtures, generate recommendations, or write official/pending/QQ outputs.

## Status Counts

| status | bucket_count |
| --- | --- |
| REJECT_CONCENTRATION\|REJECT_HIGH_DRAWDOWN\|REJECT_SMALL_SAMPLE | 7 |
| REJECT_CONCENTRATION\|REJECT_NON_POSITIVE_ROI | 2 |
| REJECT_CONCENTRATION\|REJECT_NON_POSITIVE_ROI\|REJECT_SMALL_SAMPLE | 10 |
| REJECT_CONCENTRATION\|REJECT_SMALL_SAMPLE | 1 |
| REJECT_HIGH_DRAWDOWN\|REJECT_SMALL_SAMPLE | 9 |
| REJECT_NON_POSITIVE_ROI | 56 |
| REJECT_NON_POSITIVE_ROI\|REJECT_SMALL_SAMPLE | 46 |
| REJECT_SMALL_SAMPLE | 6 |
| STABLE_RESEARCH_CANDIDATE | 1 |
| WATCHLIST_RESEARCH_ONLY | 1 |

## Hard Reject Reason Counts

| reason | bucket_count |
| --- | --- |
| REJECT_CONCENTRATION | 20 |
| REJECT_HIGH_DRAWDOWN | 16 |
| REJECT_NON_POSITIVE_ROI | 114 |
| REJECT_SMALL_SAMPLE | 79 |

## Watchlist Reason Counts

| reason | bucket_count |
| --- | --- |
| WATCH_LOW_SAMPLE_MARGIN | 1 |

## Bucket Preview

| market | selection | bucket_type | bucket | sample_count | roi | stability_status | stability_reject_reasons | watchlist_reasons |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1X2 | home | closing_fair_probability | 0.0-0.1 | 121 | -0.173554 | REJECT_NON_POSITIVE_ROI\|REJECT_SMALL_SAMPLE | REJECT_NON_POSITIVE_ROI\|REJECT_SMALL_SAMPLE | NONE |
| 1X2 | home | closing_fair_probability | 0.1-0.2 | 824 | -0.236044 | REJECT_NON_POSITIVE_ROI | REJECT_NON_POSITIVE_ROI | NONE |
| 1X2 | home | closing_fair_probability | 0.2-0.3 | 1392 | -0.177162 | REJECT_NON_POSITIVE_ROI | REJECT_NON_POSITIVE_ROI | NONE |
| 1X2 | home | closing_fair_probability | 0.3-0.4 | 1706 | -0.104109 | REJECT_NON_POSITIVE_ROI | REJECT_NON_POSITIVE_ROI | NONE |
| 1X2 | home | closing_fair_probability | 0.4-0.5 | 1767 | -0.085688 | REJECT_NON_POSITIVE_ROI | REJECT_NON_POSITIVE_ROI | NONE |
| 1X2 | home | closing_fair_probability | 0.5-0.6 | 1322 | -0.030106 | REJECT_NON_POSITIVE_ROI | REJECT_NON_POSITIVE_ROI | NONE |
| 1X2 | home | closing_fair_probability | 0.6-0.7 | 1032 | -0.005107 | REJECT_NON_POSITIVE_ROI | REJECT_NON_POSITIVE_ROI | NONE |
| 1X2 | home | closing_fair_probability | 0.7-0.8 | 597 | -0.05665 | REJECT_NON_POSITIVE_ROI | REJECT_NON_POSITIVE_ROI | NONE |
| 1X2 | home | closing_fair_probability | 0.8-0.9 | 218 | -0.044312 | REJECT_NON_POSITIVE_ROI\|REJECT_SMALL_SAMPLE | REJECT_NON_POSITIVE_ROI\|REJECT_SMALL_SAMPLE | NONE |
| 1X2 | home | closing_fair_probability | 0.9-1.0 | 2 | 0.045 | REJECT_SMALL_SAMPLE | REJECT_SMALL_SAMPLE | NONE |
| 1X2 | home | closing_fair_probability | MISSING | 0 | 0 | REJECT_NON_POSITIVE_ROI\|REJECT_SMALL_SAMPLE | REJECT_NON_POSITIVE_ROI\|REJECT_SMALL_SAMPLE | NONE |
| 1X2 | draw | closing_fair_probability | 0.0-0.1 | 75 | -0.28 | REJECT_NON_POSITIVE_ROI\|REJECT_SMALL_SAMPLE | REJECT_NON_POSITIVE_ROI\|REJECT_SMALL_SAMPLE | NONE |
| 1X2 | draw | closing_fair_probability | 0.1-0.2 | 1502 | -0.065047 | REJECT_NON_POSITIVE_ROI | REJECT_NON_POSITIVE_ROI | NONE |
| 1X2 | draw | closing_fair_probability | 0.2-0.3 | 6567 | -0.022749 | REJECT_NON_POSITIVE_ROI | REJECT_NON_POSITIVE_ROI | NONE |
| 1X2 | draw | closing_fair_probability | 0.3-0.4 | 836 | -0.045742 | REJECT_NON_POSITIVE_ROI | REJECT_NON_POSITIVE_ROI | NONE |
| 1X2 | draw | closing_fair_probability | 0.4-0.5 | 1 | 1 | REJECT_CONCENTRATION\|REJECT_SMALL_SAMPLE | REJECT_CONCENTRATION\|REJECT_SMALL_SAMPLE | NONE |
| 1X2 | draw | closing_fair_probability | MISSING | 0 | 0 | REJECT_NON_POSITIVE_ROI\|REJECT_SMALL_SAMPLE | REJECT_NON_POSITIVE_ROI\|REJECT_SMALL_SAMPLE | NONE |
| 1X2 | away | closing_fair_probability | 0.0-0.1 | 610 | -0.081148 | REJECT_NON_POSITIVE_ROI | REJECT_NON_POSITIVE_ROI | NONE |
| 1X2 | away | closing_fair_probability | 0.1-0.2 | 1955 | -0.140281 | REJECT_NON_POSITIVE_ROI | REJECT_NON_POSITIVE_ROI | NONE |
| 1X2 | away | closing_fair_probability | 0.2-0.3 | 2167 | -0.094232 | REJECT_NON_POSITIVE_ROI | REJECT_NON_POSITIVE_ROI | NONE |

## Self Check

| check | status |
| --- | --- |
| input_bucket_rows_139 | PASS |
| output_bucket_rows_match_input | PASS |
| stable_watch_rejected_counted | PASS |
| positive_roi_buckets_have_stability_status | PASS |
| no_current_2025_26 | PASS |
| phase5_backtest_rows_8982 | PASS |
| phase5_excluded_current_rows_1751 | PASS |
| research_only_no_recommendations | PASS |
| no_official_pending_qq | PASS |
| old_system_touched_no | PASS |
