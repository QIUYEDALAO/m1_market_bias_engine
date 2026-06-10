# M1 Round2 Market Bias Freeze Report

- generated_at_utc: `2026-06-10T00:34:30+00:00`
- status: `FROZEN`
- conclusion: `NO_STABLE_EDGE_FOUND`
- current_match_matching_allowed: `false`
- paper_play_allowed: `false`
- recommendations_generated: `false`
- official_written: `false`
- pending_written: `false`
- qq_written: `false`
- five_dimension_can_create_candidate: `false`
- old_system_touched: `NO`
- checker: `PASS`

This freeze report closes the Round2 Market Bias research pipeline. It is not a recommendation report, not a PLAY list, and not a current-match matching layer.

## Round Metrics

| metric | value |
| --- | --- |
| round1_conclusion | NO_STABLE_EDGE_FOUND |
| input_rows | 9063 |
| backtest_rows | 7606 |
| excluded_current_rows | 1457 |
| bucket_rows | 139 |
| positive_roi_buckets | 25 |
| stable_count_before_stress | 0 |
| watch_count_before_stress | 3 |
| rejected_count | 136 |
| candidate_audit_count | 3 |
| survived_after_stress | 1 |
| fragile_after_stress | 2 |
| current_2025_26_slice_rows | 0 |

## Decision

`NO_STABLE_EDGE_FOUND`

Round2 found 25 positive ROI buckets before stability filtering. The stability filter left 0 stable buckets and 3 watchlist-only buckets. Stress testing left 1 survived watchlist observation and 2 fragile observations. Because no bucket reached `STABLE_RESEARCH_CANDIDATE` before stress, the survived watchlist observation is not a stable edge and cannot become PLAY.

## Hybrid Policy Lock

| policy | value |
| --- | --- |
| M1_can_create_candidate | true |
| FiveDimension_can_create_candidate | false |
| No_market_edge_no_candidate | true |
| current_match_matching_allowed | false |
| paper_play_allowed | false |
| recommendations_generated | false |
| official_written | false |
| pending_written | false |
| qq_written | false |
| old_system_touched | NO |

## Interpretation

- Round2 expanded the league universe and found positive ROI buckets before stability filtering.
- Round2 Phase 5 produced no STABLE_RESEARCH_CANDIDATE buckets; it produced watchlist-only research candidates.
- Round2 stress testing left one WATCHLIST_RESEARCH_ONLY bucket as SURVIVED, but watchlist survival is not a stable edge.
- Five-dimension evaluation is locked as a risk filter and downgrade layer only; it cannot create candidates.
- M1 remains research-only and must not match current fixtures or emit recommendations.

## Source Consistency

| source | self_test |
| --- | --- |
| round2_bucket_self_test | PASS |
| round2_stability_self_test | PASS |
| round2_candidate_audit_self_test | PASS |
| round2_stress_self_test | PASS |

## Self Check

| check | status |
| --- | --- |
| round1_no_stable_edge | PASS |
| input_rows_9063 | PASS |
| backtest_rows_7606 | PASS |
| excluded_current_rows_1457 | PASS |
| bucket_rows_139 | PASS |
| positive_roi_buckets_25 | PASS |
| stable_before_stress_0 | PASS |
| watch_before_stress_3 | PASS |
| survived_after_stress_1 | PASS |
| fragile_after_stress_2 | PASS |
| conclusion_no_stable_edge_found | PASS |
| current_match_matching_false | PASS |
| paper_play_false | PASS |
| recommendations_false | PASS |
| official_pending_qq_false | PASS |
| five_dimension_cannot_create_candidate | PASS |
| m1_can_create_candidate | PASS |
| no_market_edge_no_candidate | PASS |
| current_2025_26_not_in_stress | PASS |
| old_system_touched_no | PASS |
| all_source_self_tests_pass | PASS |
