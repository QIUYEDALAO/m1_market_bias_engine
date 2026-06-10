# M1 Round2 AH -0.75 Watchlist Case Drilldown

- generated_at_utc: `2026-06-10T05:06:44+00:00`
- case_file: `data/processed/backtest_ready/m1_round2_ah075_watchlist_cases.csv`
- checker: `PASS`
- research_only: `true`
- recommendations_generated: `false`
- current_match_matching_allowed: `false`
- paper_play_allowed: `false`
- official_written: `false`
- pending_written: `false`
- qq_written: `false`
- old_system_touched: `NO`

This drilldown explains the survived Round2 watchlist bucket. It does not create a recommendation, current matcher, paper play, or official/pending/QQ output.

## Bucket

| field | value |
| --- | --- |
| stability_status | WATCHLIST_RESEARCH_ONLY |
| market | AH |
| selection | home_handicap |
| bucket_type | closing_line |
| bucket | -0.75 |
| base_sample_count | 617 |
| stress_status | SURVIVED |
| critical_failure_count | 0 |

## Summary

| metric | value |
| --- | --- |
| sample_count | 617 |
| average_roi | 0.060024 |
| total_roi_units | 37.035 |
| depends_on_single_league | false |
| depends_on_single_season | false |
| depends_on_few_teams | false |
| mainly_half_win | false |
| score_structure_healthy | true |
| still_watchlist_research_only | true |

## Settlement Distribution

| settlement | rows | share |
| --- | --- | --- |
| FULL_WIN | 217 | 0.351702 |
| HALF_WIN | 162 | 0.262561 |
| PUSH | 0 | 0 |
| HALF_LOSS | 0 | 0 |
| LOSS | 238 | 0.385737 |

## Score Distribution

| score | rows |
| --- | --- |
| 1-1 | 79 |
| 1-0 | 72 |
| 2-0 | 67 |
| 2-1 | 64 |
| 3-0 | 45 |
| 0-0 | 38 |
| 3-1 | 35 |
| 2-2 | 30 |
| 1-2 | 26 |
| 4-0 | 25 |
| 3-2 | 23 |
| 0-1 | 22 |
| 4-1 | 22 |
| 0-2 | 12 |
| 2-3 | 12 |
| 0-3 | 9 |
| 4-2 | 7 |
| 5-2 | 6 |
| 1-3 | 5 |
| 5-0 | 4 |

## Goal Diff Distribution

| goal_diff | rows |
| --- | --- |
| -4 | 2 |
| -3 | 10 |
| -2 | 18 |
| -1 | 60 |
| 0 | 148 |
| 1 | 162 |
| 2 | 109 |
| 3 | 74 |
| 4 | 29 |
| 5 | 5 |

## League And Season Distribution

| league | rows |
| --- | --- |
| B1 | 161 |
| N1 | 119 |
| P1 | 78 |
| SC0 | 95 |
| T1 | 164 |

| season | rows |
| --- | --- |
| 2020/21 | 117 |
| 2021/22 | 119 |
| 2022/23 | 109 |
| 2023/24 | 122 |
| 2024/25 | 150 |

## Team Concentration

| metric | value |
| --- | --- |
| top_team_share_of_team_slots | 0.02107 |
| top5_team_share_of_team_slots | 0.097245 |
| top_all_teams | {"Cercle Brugge": 24, "Charleroi": 22, "Gent": 20, "Hearts": 23, "Hibernian": 23, "Kortrijk": 23, "Mechelen": 24, "Sparta Rotterdam": 20, "St Truiden": 21, "Trabzonspor": 26} |

## Home Favorite Probability Bucket

| bucket | rows |
| --- | --- |
| 0.5-0.6 | 609 |
| 0.6-0.7 | 8 |

## AH Home Odds Movement Distribution

| movement_bucket | rows |
| --- | --- |
| -0.10-0.00 | 185 |
| -0.20--0.10 | 87 |
| -0.30--0.20 | 25 |
| 0.00-0.10 | 182 |
| 0.10-0.20 | 104 |
| 0.20-0.30 | 23 |
| <=-0.30 | 5 |
| >=0.30 | 4 |
| MISSING | 2 |

## Conclusion

The AH -0.75 home-handicap bucket is broad across leagues and seasons, not driven by a single team cluster, not mainly dependent on half wins, and has a balanced score structure. However it remains WATCHLIST_RESEARCH_ONLY because Round2 stability filtering produced stable_count=0 and this bucket entered stress as watchlist rather than STABLE_RESEARCH_CANDIDATE. It cannot be used for recommendations, current matching, paper play, official/pending/QQ, or V3/V4 actions.

## Self Check

| check | status |
| --- | --- |
| sample_count_617 | PASS |
| bucket_is_ah_home_closing_line_minus_075 | PASS |
| bucket_survived_but_watchlist | PASS |
| not_single_league | PASS |
| not_single_season | PASS |
| not_few_team_dependent | PASS |
| not_mainly_half_win | PASS |
| score_structure_healthy | PASS |
| still_watchlist_research_only | PASS |
| research_only_no_actions | PASS |
| official_pending_qq_false | PASS |
| old_system_touched_no | PASS |
