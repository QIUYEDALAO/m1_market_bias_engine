# M1 Round2 Research Plan

Round2 is a research planning phase only. It does not implement a new backtest,
does not match current fixtures, does not create paper PLAY output, and does not
generate recommendations.

## Round1 Baseline

Round1 is frozen by `reports/backtest/M1_MARKET_BIAS_ROUND1_FREEZE_REPORT.md`.

| item | value |
| --- | --- |
| conclusion | NO_STABLE_EDGE_FOUND |
| backtest_rows | 8982 |
| bucket_rows | 139 |
| positive_roi_buckets | 25 |
| stable_count_before_stress | 1 |
| watch_count_before_stress | 1 |
| survived_after_stress | 0 |
| fragile_after_stress | 2 |

Round1 found positive ROI buckets before stress testing, but no candidate
survived the stability stress layer. The correct Round1 interpretation is:
`NO_STABLE_EDGE_FOUND`.

## Policy Lock

| policy | value |
| --- | --- |
| research_only | true |
| current_match_matching_allowed | false |
| paper_play_allowed | false |
| recommendations_generated | false |
| official_written | false |
| pending_written | false |
| qq_written | false |
| old_system_touched | NO |

Round2 must remain a research design round. It must not connect to V3/V4, current
match matching, paper PLAY, official records, pending records, QQ, cron, or any
old-system output.

## Round2 Research Directions

1. Expand league coverage to 9-12 leagues.

   Round1 used five leagues. Round2 should test whether the Market Bias signal is
   stable across a broader football universe. Expansion must remain historical
   and offline. New leagues require a field audit before entering any backtest.

2. Compare bookmakers: B365 vs Pinnacle/PS.

   Round1 primarily used B365-derived features. Round2 should compare B365 and
   Pinnacle/PS movement where Football-Data fields are available. The goal is to
   measure whether candidate behavior is bookmaker-specific or robust across
   sources.

3. Build finer market movement features.

   Round1 bucketed broad probability and odds movements. Round2 should add more
   granular movement descriptors, such as absolute movement, relative movement,
   direction changes, cross-market agreement, AH line plus price interaction, and
   OU movement symmetry.

4. Split favorite and underdog structures by home/away role.

   Round2 should separate home favorite, away favorite, home underdog, away
   underdog, draw-heavy, and near-pickem structures. This addresses whether the
   Round1 away bucket was a general signal or a role/price-structure artifact.

5. Split by season stage.

   Round2 should test early, middle, and late season stages. Phase 7B showed
   first-half versus second-half fragility, so season-stage stability must become
   first-class.

6. Exclude extreme odds.

   Round2 should test whether extreme favorites, extreme underdogs, sparse draw
   prices, and very high-variance buckets distort ROI. Exclusion rules must be
   explicit and fixed before backtesting.

7. Add walk-forward validation.

   Round2 should introduce walk-forward validation, such as train seasons then
   test on the next season. A bucket should not be promoted to stable research
   status unless it survives out-of-sample walk-forward checks.

## Round2 Acceptance Gate

Round2 research work may proceed only when the following are true:

- The expanded dataset has a fresh audit.
- The data contract states which seasons are complete backtest seasons.
- Current-season rows are excluded from complete backtests.
- Feature definitions are frozen before any backtest run.
- Walk-forward windows are defined before metrics are computed.
- Reports state research-only status and prohibit PLAY/recommendation output.

## Non-Goals

Round2 will not:

- Produce recommendations.
- Produce paper PLAY.
- Match current fixtures.
- Write official or pending records.
- Send QQ messages.
- Modify V3/V4.
- Reinterpret Round1 as a stable edge.
