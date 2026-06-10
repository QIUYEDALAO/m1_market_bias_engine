# M1 Five-Dimension Hybrid Design

This document freezes the design boundary for combining M1 Market Bias research
with a Lite risk filter derived from the external five-dimension match
evaluation framework. It is a blueprint only. It does not run a backtest, match
current fixtures, or generate recommendations.

## Baseline

| item | value |
| --- | --- |
| Round1 freeze conclusion | `NO_STABLE_EDGE_FOUND` |
| Round2 status | Phase 4 bucket backtest complete; stability filtering not complete |
| current_match_matching_allowed | `false` |
| paper_play_allowed | `false` |
| recommendations_generated | `false` |
| Full Five-Dimension Scoring | `PAUSED` |
| Lite Risk Filter | `ACTIVE_FOR_SCHEMA_ONLY` |
| old_system_touched | `NO` |

Round1 found positive ROI buckets before stability stress, but no stable edge
survived. Round2 expanded the offline bucket backtest but has not passed a
stability filter. Therefore the hybrid design remains research-only.

## Role Boundary

M1 Market Bias is the primary screening layer. It owns market-edge evidence:
opening-to-closing movement, closing fair probability buckets, AH line movement,
OU 2.5 probability buckets, sample size, ROI, drawdown, concentration, and
stability status.

Full five-dimension scoring is paused. M1 may keep only a Lite risk filter as a
secondary risk and explanation layer. The Lite filter may classify contextual
risk, explain why a market bucket looks dangerous, or downgrade a research
candidate. It must not create a candidate by itself.

| layer | role | can create candidate |
| --- | --- | --- |
| M1 Market Bias | primary market-edge screening | `true` |
| Five-Dimension Lite Risk Filter | risk filter, explanation, downgrade | `false` |

## Five-Dimension Mode

Full five-dimension scoring is `PAUSED`.

Allowed Lite risk-filter fields:

- `lineup_status`
- `major_absence`
- `rotation_risk`
- `match_type`
- `market_conflict`
- `weather_extreme`
- `motivation_unclear`

No other five-dimension fields are active in the M1 hybrid layer. Lite fields
can only filter, explain, or downgrade an M1-supported research candidate.

## Decision Order

1. Validate data contract and phase scope.
2. Require M1 market-edge support from a completed offline research gate.
3. Reject immediately when M1 has no market edge.
4. Apply Lite risk review only after M1 support exists.
5. Downgrade M1-supported items when Lite risk is high.
6. Keep all current-stage outputs as research labels only.

The key rule is fixed: no market edge means no candidate. If M1 does not support
a candidate but the Lite risk filter is positive, the output remains `PASS`.

## Input Data Requirements

M1 inputs:

- Normalized match identity and result fields.
- 1X2 opening and closing odds.
- AH opening and closing line and odds.
- OU 2.5 opening and closing odds.
- Season role, with `2020/21` through `2024/25` as `COMPLETE_BACKTEST` and
  `2025/26` as `CURRENT_NOT_FOR_BACKTEST`.
- Bucket backtest and stability evidence before any future promotion beyond
  research review.

Lite risk-filter inputs:

- `lineup_status`
- `major_absence`
- `rotation_risk`
- `match_type`
- `market_conflict`
- `weather_extreme`
- `motivation_unclear`

The Lite input must be treated as a risk review object, not as a source of
market edge. Missing Lite data may block or downgrade a research candidate, but
it must not promote a non-M1 item.

## Output Labels

Allowed hybrid labels:

- `PASS`
- `WATCH_RESEARCH_ONLY`
- `M1_RESEARCH_CANDIDATE`
- `DOWNGRADED_BY_FIVE_DIMENSION_RISK`
- `BLOCKED_NO_MARKET_EDGE`
- `BLOCKED_CURRENT_MATCH_MATCHING_DISABLED`
- `BLOCKED_PAPER_PLAY_DISABLED`

Forbidden outputs:

- betting recommendation
- official record
- pending record
- QQ message
- live-bet instruction
- V3/V4 mutation

## Downgrade Rules

| M1 market edge | five-dimension risk | hybrid label |
| --- | --- | --- |
| no | any positive or negative score | `PASS` |
| yes | low Lite risk | `M1_RESEARCH_CANDIDATE` |
| yes | medium risk | `WATCH_RESEARCH_ONLY` |
| yes | high risk | `DOWNGRADED_BY_FIVE_DIMENSION_RISK` or `PASS` |
| yes | missing required risk evidence | `WATCH_RESEARCH_ONLY` |

Lite support cannot upgrade `PASS` to candidate. Lite risk can only keep,
explain, downgrade, or block an M1-supported research candidate.

## Prohibited Rules

- No current match matching in this stage.
- No paper PLAY output.
- No recommendation generation.
- No official records.
- No pending records.
- No QQ output.
- No V3/V4 edits.
- No Round1 reinterpretation as a stable edge.
- No Round2 bucket promotion before stability filtering.
- No candidate when M1 market edge is absent.
- No candidate created by five-dimension evaluation alone.
- No full five-dimension scoring while status is `PAUSED`.
- No five-dimension fields outside the Lite allowlist.

## Policy Mapping

This document is paired with `config/hybrid_decision_policy.json`.

Required policy values:

- `FiveDimension_can_create_candidate=false`
- `M1_can_create_candidate=true`
- `No_market_edge_no_candidate=true`
- `current_match_matching_allowed=false`
- `paper_play_allowed=false`
- `recommendations_generated=false`
- `official_written=false`
- `pending_written=false`
- `qq_written=false`
- `old_system_touched=NO`
- `full_five_dimension_scoring=PAUSED`
- `lite_risk_filter_enabled=true`
- `lite_allowed_fields=[lineup_status, major_absence, rotation_risk, match_type, market_conflict, weather_extreme, motivation_unclear]`

## Follow-Up Phase Route

1. Round2 stability filter over expanded buckets.
2. Round2 candidate audit and stress test, if any stable research candidate
   exists.
3. Lite risk-filter schema audit using the seven-field allowlist only.
4. Hybrid offline simulation that applies Lite downgrade rules after
   M1 gates.
5. Hybrid freeze report that states whether any research-only candidate survived.
6. Separate approval gate before any current matching or paper-play discussion.

Until that route is complete and separately approved, M1 plus Lite risk-filter
hybrid output remains research-only and cannot produce recommendations.
