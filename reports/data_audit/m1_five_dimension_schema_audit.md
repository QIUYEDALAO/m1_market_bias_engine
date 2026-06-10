# M1 Five-Dimension Schema Audit

- generated_at_utc: `2026-06-10T04:59:30+00:00`
- checker: `PASS`
- research_only: `true`
- five_dimension_can_create_candidate: `false`
- current_match_matching_allowed: `false`
- paper_play_allowed: `false`
- recommendations_generated: `false`
- old_system_touched: `NO`

This audit converts the five-dimension match evaluation method into an M1 risk-filter field contract. It does not simulate matches, generate candidates, produce recommendations, or touch V3/V4.

## Schema Counts

| category | count |
| --- | --- |
| required_filter_fields | 13 |
| optional_context_fields | 43 |
| unavailable_or_external_fields | 15 |
| forbidden_candidate_fields | 10 |
| schema_fields_total | 81 |

## Required Filter Fields

| field | type | allowed_use |
| --- | --- | --- |
| five_dimension_schema_version | string | schema_traceability |
| m1_market_edge_required | boolean | assert M1 gate must exist before five-dimension filtering |
| five_dimension_can_create_candidate | boolean | hard boundary |
| overall_five_dimension_risk_level | enum | downgrade_or_block_m1_supported_research_candidate |
| dimension_strength_risk_level | enum | strength_core |
| dimension_tactical_risk_level | enum | advanced_tactical_metrics |
| dimension_chemistry_risk_level | enum | squad_chemistry |
| dimension_market_heat_risk_level | enum | market_popularity_wisdom |
| dimension_environment_risk_level | enum | environment_externalities |
| five_dimension_downgrade_label | enum | filter_or_downgrade_only |
| five_dimension_evidence_confidence | enum | block_or_downgrade_when evidence is missing |
| five_dimension_explanation_notes | array[string] | human-readable risk explanation |
| five_dimension_source_provenance | object | document external source availability and timestamp |

## Optional Context Fields

| field | allowed_use |
| --- | --- |
| elo_delta | risk_explanation_only |
| elo_expected_win_rate | risk_explanation_only |
| fifa_ranking_delta | risk_explanation_only |
| league_points_gap | risk_explanation_only |
| home_away_points_split | risk_explanation_only |
| squad_value_ratio | risk_explanation_only |
| wage_dispersion_risk | risk_explanation_only |
| top_star_recent_rating_weighted | risk_explanation_only |
| star_rating_trend | risk_explanation_only |
| breakout_player_index | risk_explanation_only |
| breakout_player_matchup_note | risk_explanation_only |
| squad_depth_gap | risk_explanation_only |
| npxg_delta_last10 | risk_explanation_only |
| npxg_per_shot_profile | risk_explanation_only |
| shot_conversion_temperature | risk_explanation_only |
| xA_creator_profile | risk_explanation_only |
| ppda_profile | risk_explanation_only |
| pressure_quality_index | risk_explanation_only |
| psxg_ga_per90 | risk_explanation_only |
| goalkeeper_distribution_index | risk_explanation_only |
| club_link_grade | risk_explanation_only |
| same_league_rhythm_index | risk_explanation_only |
| passing_network_link_note | risk_explanation_only |
| centre_back_partnership_starts | risk_explanation_only |
| defensive_coordination_index | risk_explanation_only |
| coach_tenure_months | risk_explanation_only |
| media_attention_ratio | risk_explanation_only |
| fan_sentiment_index | risk_explanation_only |
| fund_flow_concentration | risk_explanation_only |
| odds_movement_speed_note | risk_explanation_only |
| head_to_head_weighted_signal | risk_explanation_only |
| similar_style_mapping_signal | risk_explanation_only |
| major_stage_resilience_index | risk_explanation_only |
| style_clash_note | risk_explanation_only |
| rest_days_delta | risk_explanation_only |
| travel_fatigue_index | risk_explanation_only |
| rotation_depth_note | risk_explanation_only |
| referee_strictness_index | risk_explanation_only |
| team_foul_vs_referee_style_note | risk_explanation_only |
| injury_impact_index | risk_explanation_only |
| yellow_card_crisis_note | risk_explanation_only |
| locker_room_health_index | risk_explanation_only |
| penalty_shootout_readiness_note | risk_explanation_only |

## Unavailable Or External Fields

| field | source | reason |
| --- | --- | --- |
| raw_world_football_elo | eloratings.net | external live source |
| raw_club_elo | clubelo.com | external live source |
| raw_fifa_ranking | fifa.com | external ranking source |
| raw_transfermarkt_squad_value | Transfermarkt | external commercial/reference source |
| raw_capology_wage_data | Capology | external wage source |
| raw_player_ratings | WhoScored/SofaScore/FotMob | external match-rating source |
| raw_opta_wyscout_statsbomb_metrics | Opta/Wyscout/StatsBomb | licensed event data |
| raw_fbref_understat_xg | FBref/Understat | external xG source |
| raw_google_trends | Google Trends | external popularity source |
| raw_social_sentiment | Twitter/Reddit/forums | external sentiment source |
| raw_bookmaker_fund_flow | bookmaker platform data | not in Football-Data P0 contract |
| raw_referee_profile | WorldReferee/Transfermarkt/WhoScored | external referee source |
| raw_injury_feed | Premier Injuries/Transfermarkt | external injury source |
| raw_weather_or_travel_feed | weather/travel APIs | external physical environment source |
| raw_locker_room_signals | public news/social media | manual or NLP extraction required |

## Forbidden Candidate Fields

| field | reason |
| --- | --- |
| five_dimension_candidate | five-dimension layer cannot create candidates |
| five_dimension_play_label | paper play and recommendation output are disabled |
| five_dimension_betting_pick | betting recommendation is forbidden |
| five_dimension_predicted_winner | M1 is market-bias research, not team prediction |
| five_dimension_stake_size | stake sizing implies betting advice |
| five_dimension_official_record | official output is forbidden |
| five_dimension_pending_record | pending output is forbidden |
| five_dimension_qq_message | QQ output is forbidden |
| five_dimension_current_match_candidate | current matching is disabled |
| five_dimension_total_score_candidate_gate | total score may explain risk but must not independently create a candidate |

## Allowed Use

- `risk_filter`
- `downgrade`
- `explanation`
- `missing_evidence_block`
- `research_only_review`

## Blocked Use

- `candidate_generation`
- `current_match_matching`
- `paper_play`
- `recommendation`
- `official_record`
- `pending_record`
- `qq_message`
- `v3_v4_mutation`

## Self Check

| check | status |
| --- | --- |
| json_schema_has_required_categories | PASS |
| five_dimensions_present_in_source | PASS |
| required_filter_fields_nonempty | PASS |
| optional_context_fields_nonempty | PASS |
| external_fields_nonempty | PASS |
| forbidden_candidate_fields_nonempty | PASS |
| five_dimension_cannot_create_candidate | PASS |
| m1_can_create_candidate | PASS |
| no_market_edge_no_candidate | PASS |
| current_matching_disabled | PASS |
| paper_play_disabled | PASS |
| recommendations_disabled | PASS |
| official_pending_qq_disabled | PASS |
| forbidden_candidate_generation_fields_present | PASS |
| source_disclaimer_no_betting | PASS |
| old_system_touched_no | PASS |
