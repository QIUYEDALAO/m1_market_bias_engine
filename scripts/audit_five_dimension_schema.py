#!/usr/bin/env python3
"""Create the M1 five-dimension risk-filter schema audit."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
HYBRID_DESIGN = REPO_ROOT / "docs" / "M1_FIVE_DIMENSION_HYBRID_DESIGN.md"
HYBRID_POLICY = REPO_ROOT / "config" / "hybrid_decision_policy.json"
SOURCE_DOC = Path("/Users/liudehua/Desktop/五维赛事评估系统-完整版.md")
CONFIG_JSON = REPO_ROOT / "config" / "five_dimension_schema_contract.json"
REPORT_DIR = REPO_ROOT / "reports" / "data_audit"
REPORT_JSON = REPORT_DIR / "m1_five_dimension_schema_audit.json"
REPORT_MD = REPORT_DIR / "m1_five_dimension_schema_audit.md"

REQUIRED_FILTER_FIELDS = [
    {
        "field": "five_dimension_schema_version",
        "type": "string",
        "required": True,
        "allowed_use": "schema_traceability",
    },
    {
        "field": "m1_market_edge_required",
        "type": "boolean",
        "required": True,
        "fixed_value": True,
        "allowed_use": "assert M1 gate must exist before five-dimension filtering",
    },
    {
        "field": "five_dimension_can_create_candidate",
        "type": "boolean",
        "required": True,
        "fixed_value": False,
        "allowed_use": "hard boundary",
    },
    {
        "field": "overall_five_dimension_risk_level",
        "type": "enum",
        "required": True,
        "allowed_values": ["LOW", "MEDIUM", "HIGH", "MISSING_REQUIRED_EVIDENCE"],
        "allowed_use": "downgrade_or_block_m1_supported_research_candidate",
    },
    {
        "field": "dimension_strength_risk_level",
        "dimension": "strength_core",
        "type": "enum",
        "required": True,
        "allowed_values": ["LOW", "MEDIUM", "HIGH", "MISSING"],
        "source_sections": ["ELO", "ranking_or_points_gap", "squad_value", "star_form", "breakout_players"],
    },
    {
        "field": "dimension_tactical_risk_level",
        "dimension": "advanced_tactical_metrics",
        "type": "enum",
        "required": True,
        "allowed_values": ["LOW", "MEDIUM", "HIGH", "MISSING"],
        "source_sections": ["npxG", "conversion_rate", "PPDA", "press_success", "PSxG_GA"],
    },
    {
        "field": "dimension_chemistry_risk_level",
        "dimension": "squad_chemistry",
        "type": "enum",
        "required": True,
        "allowed_values": ["LOW", "MEDIUM", "HIGH", "MISSING"],
        "source_sections": ["club_links", "same_league_rhythm", "cb_partnership", "defensive_coordination"],
    },
    {
        "field": "dimension_market_heat_risk_level",
        "dimension": "market_popularity_wisdom",
        "type": "enum",
        "required": True,
        "allowed_values": ["LOW", "MEDIUM", "HIGH", "MISSING"],
        "source_sections": ["media_attention", "fan_sentiment", "fund_flow", "historical_mapping"],
    },
    {
        "field": "dimension_environment_risk_level",
        "dimension": "environment_externalities",
        "type": "enum",
        "required": True,
        "allowed_values": ["LOW", "MEDIUM", "HIGH", "MISSING"],
        "source_sections": ["rest_days", "travel_fatigue", "referee_profile", "injury_suspension", "locker_room"],
    },
    {
        "field": "five_dimension_downgrade_label",
        "type": "enum",
        "required": True,
        "allowed_values": ["NO_DOWNGRADE", "WATCH_RESEARCH_ONLY", "DOWNGRADED_BY_FIVE_DIMENSION_RISK", "PASS"],
        "allowed_use": "filter_or_downgrade_only",
    },
    {
        "field": "five_dimension_evidence_confidence",
        "type": "enum",
        "required": True,
        "allowed_values": ["HIGH", "MEDIUM", "LOW", "MISSING"],
        "allowed_use": "block_or_downgrade_when evidence is missing",
    },
    {
        "field": "five_dimension_explanation_notes",
        "type": "array[string]",
        "required": True,
        "allowed_use": "human-readable risk explanation",
    },
    {
        "field": "five_dimension_source_provenance",
        "type": "object",
        "required": True,
        "allowed_use": "document external source availability and timestamp",
    },
]

OPTIONAL_CONTEXT_FIELDS = [
    "elo_delta",
    "elo_expected_win_rate",
    "fifa_ranking_delta",
    "league_points_gap",
    "home_away_points_split",
    "squad_value_ratio",
    "wage_dispersion_risk",
    "top_star_recent_rating_weighted",
    "star_rating_trend",
    "breakout_player_index",
    "breakout_player_matchup_note",
    "squad_depth_gap",
    "npxg_delta_last10",
    "npxg_per_shot_profile",
    "shot_conversion_temperature",
    "xA_creator_profile",
    "ppda_profile",
    "pressure_quality_index",
    "psxg_ga_per90",
    "goalkeeper_distribution_index",
    "club_link_grade",
    "same_league_rhythm_index",
    "passing_network_link_note",
    "centre_back_partnership_starts",
    "defensive_coordination_index",
    "coach_tenure_months",
    "media_attention_ratio",
    "fan_sentiment_index",
    "fund_flow_concentration",
    "odds_movement_speed_note",
    "head_to_head_weighted_signal",
    "similar_style_mapping_signal",
    "major_stage_resilience_index",
    "style_clash_note",
    "rest_days_delta",
    "travel_fatigue_index",
    "rotation_depth_note",
    "referee_strictness_index",
    "team_foul_vs_referee_style_note",
    "injury_impact_index",
    "yellow_card_crisis_note",
    "locker_room_health_index",
    "penalty_shootout_readiness_note",
]

UNAVAILABLE_OR_EXTERNAL_FIELDS = [
    {"field": "raw_world_football_elo", "source": "eloratings.net", "reason": "external live source"},
    {"field": "raw_club_elo", "source": "clubelo.com", "reason": "external live source"},
    {"field": "raw_fifa_ranking", "source": "fifa.com", "reason": "external ranking source"},
    {"field": "raw_transfermarkt_squad_value", "source": "Transfermarkt", "reason": "external commercial/reference source"},
    {"field": "raw_capology_wage_data", "source": "Capology", "reason": "external wage source"},
    {"field": "raw_player_ratings", "source": "WhoScored/SofaScore/FotMob", "reason": "external match-rating source"},
    {"field": "raw_opta_wyscout_statsbomb_metrics", "source": "Opta/Wyscout/StatsBomb", "reason": "licensed event data"},
    {"field": "raw_fbref_understat_xg", "source": "FBref/Understat", "reason": "external xG source"},
    {"field": "raw_google_trends", "source": "Google Trends", "reason": "external popularity source"},
    {"field": "raw_social_sentiment", "source": "Twitter/Reddit/forums", "reason": "external sentiment source"},
    {"field": "raw_bookmaker_fund_flow", "source": "bookmaker platform data", "reason": "not in Football-Data P0 contract"},
    {"field": "raw_referee_profile", "source": "WorldReferee/Transfermarkt/WhoScored", "reason": "external referee source"},
    {"field": "raw_injury_feed", "source": "Premier Injuries/Transfermarkt", "reason": "external injury source"},
    {"field": "raw_weather_or_travel_feed", "source": "weather/travel APIs", "reason": "external physical environment source"},
    {"field": "raw_locker_room_signals", "source": "public news/social media", "reason": "manual or NLP extraction required"},
]

FORBIDDEN_CANDIDATE_FIELDS = [
    {
        "field": "five_dimension_candidate",
        "reason": "five-dimension layer cannot create candidates",
    },
    {
        "field": "five_dimension_play_label",
        "reason": "paper play and recommendation output are disabled",
    },
    {
        "field": "five_dimension_betting_pick",
        "reason": "betting recommendation is forbidden",
    },
    {
        "field": "five_dimension_predicted_winner",
        "reason": "M1 is market-bias research, not team prediction",
    },
    {
        "field": "five_dimension_stake_size",
        "reason": "stake sizing implies betting advice",
    },
    {
        "field": "five_dimension_official_record",
        "reason": "official output is forbidden",
    },
    {
        "field": "five_dimension_pending_record",
        "reason": "pending output is forbidden",
    },
    {
        "field": "five_dimension_qq_message",
        "reason": "QQ output is forbidden",
    },
    {
        "field": "five_dimension_current_match_candidate",
        "reason": "current matching is disabled",
    },
    {
        "field": "five_dimension_total_score_candidate_gate",
        "reason": "total score may explain risk but must not independently create a candidate",
    },
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_schema() -> dict[str, Any]:
    policy = read_json(HYBRID_POLICY)
    rules = policy["hard_rules"]
    return {
        "name": "m1_five_dimension_schema_contract",
        "version": "0.1.0",
        "mode": "research_only_risk_filter_schema",
        "source_documents": {
            "hybrid_design": str(HYBRID_DESIGN.relative_to(REPO_ROOT)),
            "five_dimension_reference": str(SOURCE_DOC),
        },
        "policy_locks": {
            "M1_can_create_candidate": rules["M1_can_create_candidate"],
            "FiveDimension_can_create_candidate": rules["FiveDimension_can_create_candidate"],
            "No_market_edge_no_candidate": rules["No_market_edge_no_candidate"],
            "current_match_matching_allowed": rules["current_match_matching_allowed"],
            "paper_play_allowed": rules["paper_play_allowed"],
            "recommendations_generated": rules["recommendations_generated"],
            "official_written": rules["official_written"],
            "pending_written": rules["pending_written"],
            "qq_written": rules["qq_written"],
            "old_system_touched": rules["old_system_touched"],
        },
        "allowed_use": [
            "risk_filter",
            "downgrade",
            "explanation",
            "missing_evidence_block",
            "research_only_review",
        ],
        "blocked_use": [
            "candidate_generation",
            "current_match_matching",
            "paper_play",
            "recommendation",
            "official_record",
            "pending_record",
            "qq_message",
            "v3_v4_mutation",
        ],
        "required_filter_fields": REQUIRED_FILTER_FIELDS,
        "optional_context_fields": [{"field": field, "required": False, "allowed_use": "risk_explanation_only"} for field in OPTIONAL_CONTEXT_FIELDS],
        "unavailable_or_external_fields": UNAVAILABLE_OR_EXTERNAL_FIELDS,
        "forbidden_candidate_fields": FORBIDDEN_CANDIDATE_FIELDS,
    }


def audit_source_presence(source_text: str) -> dict[str, bool]:
    terms = {
        "strength_core": "绝对实力面" in source_text and "ELO" in source_text,
        "advanced_tactical_metrics": "战术高阶指标" in source_text and "npxG" in source_text and "PPDA" in source_text,
        "squad_chemistry": "阵型化学反应" in source_text and "俱乐部羁绊" in source_text,
        "market_popularity_wisdom": "市场与热度智慧" in source_text and "大众热度" in source_text,
        "environment_externalities": "外部物理与环境" in source_text and "裁判" in source_text and "伤停" in source_text,
        "disclaimer_no_betting": "投注建议" in source_text and "禁止" in source_text,
    }
    return terms


def self_check(schema: dict[str, Any], source_presence: dict[str, bool]) -> dict[str, Any]:
    locks = schema["policy_locks"]
    required_fields = {item["field"] for item in schema["required_filter_fields"]}
    forbidden_fields = {item["field"] for item in schema["forbidden_candidate_fields"]}
    checks = {
        "json_schema_has_required_categories": all(
            key in schema
            for key in [
                "required_filter_fields",
                "optional_context_fields",
                "unavailable_or_external_fields",
                "forbidden_candidate_fields",
            ]
        ),
        "five_dimensions_present_in_source": all(
            source_presence[key]
            for key in [
                "strength_core",
                "advanced_tactical_metrics",
                "squad_chemistry",
                "market_popularity_wisdom",
                "environment_externalities",
            ]
        ),
        "required_filter_fields_nonempty": len(schema["required_filter_fields"]) >= 10,
        "optional_context_fields_nonempty": len(schema["optional_context_fields"]) >= 20,
        "external_fields_nonempty": len(schema["unavailable_or_external_fields"]) >= 10,
        "forbidden_candidate_fields_nonempty": len(schema["forbidden_candidate_fields"]) >= 8,
        "five_dimension_cannot_create_candidate": locks["FiveDimension_can_create_candidate"] is False
        and "five_dimension_can_create_candidate" in required_fields,
        "m1_can_create_candidate": locks["M1_can_create_candidate"] is True,
        "no_market_edge_no_candidate": locks["No_market_edge_no_candidate"] is True,
        "current_matching_disabled": locks["current_match_matching_allowed"] is False,
        "paper_play_disabled": locks["paper_play_allowed"] is False,
        "recommendations_disabled": locks["recommendations_generated"] is False,
        "official_pending_qq_disabled": locks["official_written"] is False
        and locks["pending_written"] is False
        and locks["qq_written"] is False,
        "forbidden_candidate_generation_fields_present": "five_dimension_candidate" in forbidden_fields
        and "five_dimension_total_score_candidate_gate" in forbidden_fields,
        "source_disclaimer_no_betting": source_presence["disclaimer_no_betting"],
        "old_system_touched_no": locks["old_system_touched"] == "NO",
    }
    rendered = {name: "PASS" if value else "FAIL" for name, value in checks.items()}
    return {"status": "PASS" if all(checks.values()) else "FAIL", "checks": rendered}


def markdown_cell(value: Any) -> str:
    if isinstance(value, bool):
        value = str(value).lower()
    return str(value).replace("|", "\\|")


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(markdown_cell(header) for header in headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(markdown_cell(value) for value in row) + " |")
    return "\n".join(lines)


def render_report(report: dict[str, Any]) -> str:
    schema = report["schema"]
    return "\n".join(
        [
            "# M1 Five-Dimension Schema Audit",
            "",
            f"- generated_at_utc: `{report['generated_at_utc']}`",
            f"- checker: `{report['self_check']['status']}`",
            "- research_only: `true`",
            "- five_dimension_can_create_candidate: `false`",
            "- current_match_matching_allowed: `false`",
            "- paper_play_allowed: `false`",
            "- recommendations_generated: `false`",
            "- old_system_touched: `NO`",
            "",
            "This audit converts the five-dimension match evaluation method into an M1 risk-filter field contract. It does not simulate matches, generate candidates, produce recommendations, or touch V3/V4.",
            "",
            "## Schema Counts",
            "",
            markdown_table(
                ["category", "count"],
                [
                    ["required_filter_fields", len(schema["required_filter_fields"])],
                    ["optional_context_fields", len(schema["optional_context_fields"])],
                    ["unavailable_or_external_fields", len(schema["unavailable_or_external_fields"])],
                    ["forbidden_candidate_fields", len(schema["forbidden_candidate_fields"])],
                    ["schema_fields_total", report["schema_fields_total"]],
                ],
            ),
            "",
            "## Required Filter Fields",
            "",
            markdown_table(
                ["field", "type", "allowed_use"],
                [[item["field"], item["type"], item.get("allowed_use", item.get("dimension", ""))] for item in schema["required_filter_fields"]],
            ),
            "",
            "## Optional Context Fields",
            "",
            markdown_table(
                ["field", "allowed_use"],
                [[item["field"], item["allowed_use"]] for item in schema["optional_context_fields"]],
            ),
            "",
            "## Unavailable Or External Fields",
            "",
            markdown_table(
                ["field", "source", "reason"],
                [[item["field"], item["source"], item["reason"]] for item in schema["unavailable_or_external_fields"]],
            ),
            "",
            "## Forbidden Candidate Fields",
            "",
            markdown_table(
                ["field", "reason"],
                [[item["field"], item["reason"]] for item in schema["forbidden_candidate_fields"]],
            ),
            "",
            "## Allowed Use",
            "",
            "\n".join(f"- `{item}`" for item in schema["allowed_use"]),
            "",
            "## Blocked Use",
            "",
            "\n".join(f"- `{item}`" for item in schema["blocked_use"]),
            "",
            "## Self Check",
            "",
            markdown_table(
                ["check", "status"],
                [[key, value] for key, value in report["self_check"]["checks"].items()],
            ),
            "",
        ]
    )


def main() -> int:
    for path in [HYBRID_DESIGN, HYBRID_POLICY, SOURCE_DOC]:
        if not path.exists():
            raise SystemExit(f"Required input missing: {path}")
    source_text = read_text(SOURCE_DOC)
    schema = build_schema()
    source_presence = audit_source_presence(source_text)
    checks = self_check(schema, source_presence)
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "schema": schema,
        "schema_fields_total": len(schema["required_filter_fields"])
        + len(schema["optional_context_fields"])
        + len(schema["unavailable_or_external_fields"])
        + len(schema["forbidden_candidate_fields"]),
        "source_presence": source_presence,
        "self_check": checks,
        "research_only": True,
        "recommendations_generated": False,
        "current_match_matching_allowed": False,
        "paper_play_allowed": False,
        "official_written": False,
        "pending_written": False,
        "qq_written": False,
        "old_system_touched": "NO",
    }
    CONFIG_JSON.write_text(json.dumps(schema, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_report(report), encoding="utf-8")
    print(f"m1_five_dimension_schema_audit: {checks['status']}")
    print(f"schema_fields_total={report['schema_fields_total']}")
    print(f"required_filter_fields={len(schema['required_filter_fields'])}")
    print(f"optional_context_fields={len(schema['optional_context_fields'])}")
    print(f"unavailable_or_external_fields={len(schema['unavailable_or_external_fields'])}")
    print(f"forbidden_candidate_fields={len(schema['forbidden_candidate_fields'])}")
    print(f"config_json={CONFIG_JSON.relative_to(REPO_ROOT)}")
    print(f"report_json={REPORT_JSON.relative_to(REPO_ROOT)}")
    print(f"report_md={REPORT_MD.relative_to(REPO_ROOT)}")
    return 0 if checks["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
