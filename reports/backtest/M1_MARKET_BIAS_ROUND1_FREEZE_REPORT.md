# M1 Market Bias Round 1 Freeze Report

- generated_at_utc: `2026-06-09T23:26:37+00:00`
- status: `FROZEN`
- conclusion: `NO_STABLE_EDGE_FOUND`
- current_match_matching_allowed: `false`
- paper_play_allowed: `false`
- recommendations_generated: `false`
- official_written: `false`
- pending_written: `false`
- qq_written: `false`
- old_system_touched: `NO`
- M1 remains research-only: `true`

This freeze report closes the first Market Bias research round. It is not a recommendation report, not a PLAY list, and not a current-match matching layer.

## Round Metrics

| metric | value |
| --- | --- |
| backtest_rows | 8982 |
| bucket_rows | 139 |
| positive_roi_buckets | 25 |
| stable_count_before_stress | 1 |
| watch_count_before_stress | 1 |
| survived_after_stress | 0 |
| fragile_after_stress | 2 |
| excluded_current_rows | 1751 |
| current_2025_26_slice_rows | 0 |

## Decision

`NO_STABLE_EDGE_FOUND`

Round 1 found 25 positive ROI buckets before stability filtering. Phase 6 left 1 stable and 1 watch bucket before stress. Phase 7B stress testing left 0 survived candidates and 2 fragile candidates. Therefore M1 Round 1 is frozen with no stable edge.

## Policy Lock

| policy | value |
| --- | --- |
| current_match_matching_allowed | false |
| paper_play_allowed | false |
| recommendations_generated | false |
| official_written | false |
| pending_written | false |
| qq_written | false |
| m1_research_only | true |
| old_system_touched | NO |

## Source Consistency

| source | self_test |
| --- | --- |
| phase5_self_test | PASS |
| phase6_self_test | PASS |
| phase7a_self_test | PASS |
| phase7b_self_test | PASS |

## Interpretation

- Round 1 found positive ROI buckets before stability filtering, but stress testing did not leave any survived candidate.
- The prior stable/watch buckets are frozen as fragile research observations, not playable edges.
- M1 remains research-only and must not match current fixtures or emit recommendations.

## Self Check

| check | status |
| --- | --- |
| backtest_rows_8982 | PASS |
| bucket_rows_139 | PASS |
| positive_roi_buckets_25 | PASS |
| stable_before_stress_1 | PASS |
| watch_before_stress_1 | PASS |
| survived_after_stress_0 | PASS |
| fragile_after_stress_2 | PASS |
| conclusion_no_stable_edge_found | PASS |
| current_match_matching_false | PASS |
| paper_play_false | PASS |
| recommendations_false | PASS |
| research_only_true | PASS |
| old_system_touched_no | PASS |
| all_source_self_tests_pass | PASS |
