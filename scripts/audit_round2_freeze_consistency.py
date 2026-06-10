#!/usr/bin/env python3
"""Audit consistency between Round2 survived stress buckets and freeze conclusion."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
STABILITY_JSON = REPO_ROOT / "reports" / "backtest" / "m1_round2_stability_filter_report.json"
STRESS_JSON = REPO_ROOT / "reports" / "backtest" / "m1_round2_stability_candidate_stress_test.json"
FREEZE_JSON = REPO_ROOT / "reports" / "backtest" / "M1_ROUND2_MARKET_BIAS_FREEZE_REPORT.json"
HYBRID_POLICY_JSON = REPO_ROOT / "config" / "hybrid_decision_policy.json"
REPORT_DIR = REPO_ROOT / "reports" / "backtest"
REPORT_JSON = REPORT_DIR / "M1_ROUND2_FREEZE_CONSISTENCY_AUDIT.json"
REPORT_MD = REPORT_DIR / "M1_ROUND2_FREEZE_CONSISTENCY_AUDIT.md"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def survived_candidates(stress: dict[str, Any]) -> list[dict[str, Any]]:
    return [candidate for candidate in stress["candidates"] if candidate["stress_status"] == "SURVIVED"]


def play_gate_audit(candidate: dict[str, Any], stability: dict[str, Any], freeze: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    rules = policy["hard_rules"]
    gates = {
        "stable_research_candidate_before_stress": candidate["stability_status"] == "STABLE_RESEARCH_CANDIDATE",
        "not_watchlist_only": candidate["stability_status"] != "WATCHLIST_RESEARCH_ONLY",
        "round2_stable_count_positive": stability["stats"]["stable_count"] > 0,
        "freeze_conclusion_allows_edge": freeze["conclusion"] != "NO_STABLE_EDGE_FOUND",
        "current_match_matching_allowed": rules["current_match_matching_allowed"],
        "paper_play_allowed": rules["paper_play_allowed"],
        "recommendations_generated_allowed": rules["recommendations_generated"],
        "five_dimension_can_create_candidate": rules["FiveDimension_can_create_candidate"],
        "no_market_edge_rule_satisfied": not rules["No_market_edge_no_candidate"] or freeze["conclusion"] != "NO_STABLE_EDGE_FOUND",
    }
    failed = [name for name, passed in gates.items() if not passed]
    return {
        "gates": gates,
        "failed_gates": failed,
        "all_play_prerequisites_met": not failed,
    }


def build_report() -> dict[str, Any]:
    stability = read_json(STABILITY_JSON)
    stress = read_json(STRESS_JSON)
    freeze = read_json(FREEZE_JSON)
    policy = read_json(HYBRID_POLICY_JSON)
    survived = survived_candidates(stress)
    survived_bucket = survived[0] if survived else {}
    gate_audit = play_gate_audit(survived_bucket, stability, freeze, policy) if survived else {
        "gates": {},
        "failed_gates": ["NO_SURVIVED_BUCKET"],
        "all_play_prerequisites_met": False,
    }
    consistency_result = (
        "CONSISTENT_NO_STABLE_EDGE"
        if freeze["conclusion"] == "NO_STABLE_EDGE_FOUND"
        and stress["stats"]["survived_count"] == 1
        and stability["stats"]["stable_count"] == 0
        and survived_bucket.get("stability_status") == "WATCHLIST_RESEARCH_ONLY"
        and not gate_audit["all_play_prerequisites_met"]
        else "INCONSISTENT_REVIEW_REQUIRED"
    )
    why_not_edge = [
        "The survived bucket survived stress only after entering stress as WATCHLIST_RESEARCH_ONLY, not as STABLE_RESEARCH_CANDIDATE.",
        "Round2 Phase 5 stability filtering produced stable_count=0, so no bucket crossed the stable-edge gate before stress.",
        "The freeze report conclusion is NO_STABLE_EDGE_FOUND, and the hybrid policy has No_market_edge_no_candidate=true.",
        "current_match_matching_allowed=false, paper_play_allowed=false, and recommendations_generated=false.",
        "Five-dimension evaluation is locked as risk filter/downgrade only and cannot create or upgrade a candidate.",
    ]
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "inputs": {
            "stability_report": str(STABILITY_JSON.relative_to(REPO_ROOT)),
            "stress_report": str(STRESS_JSON.relative_to(REPO_ROOT)),
            "freeze_report": str(FREEZE_JSON.relative_to(REPO_ROOT)),
            "hybrid_policy": str(HYBRID_POLICY_JSON.relative_to(REPO_ROOT)),
        },
        "consistency_result": consistency_result,
        "survived_count": stress["stats"]["survived_count"],
        "fragile_count": stress["stats"]["fragile_count"],
        "stable_count_before_stress": stability["stats"]["stable_count"],
        "watch_count_before_stress": stability["stats"]["watch_count"],
        "freeze_conclusion": freeze["conclusion"],
        "survived_bucket": {
            "stability_status": survived_bucket.get("stability_status", ""),
            "market": survived_bucket.get("market", ""),
            "selection": survived_bucket.get("selection", ""),
            "bucket_type": survived_bucket.get("bucket_type", ""),
            "bucket": survived_bucket.get("bucket", ""),
            "base_sample_count": survived_bucket.get("base_sample_count", 0),
            "stress_status": survived_bucket.get("stress_status", ""),
            "critical_failure_count": survived_bucket.get("critical_failure_count", 0),
        },
        "play_prerequisite_audit": gate_audit,
        "why_not_edge": why_not_edge,
        "allowed_next": [
            "research_only_review",
            "five_dimension_schema_audit",
            "hybrid_offline_simulation_after_explicit_approval",
            "additional_round3_research_design",
        ],
        "blocked_actions": [
            "current_match_matching",
            "paper_play",
            "recommendation_generation",
            "official_record",
            "pending_record",
            "qq_message",
            "v3_v4_mutation",
            "five_dimension_candidate_creation",
        ],
        "research_only": True,
        "recommendations_generated": False,
        "current_match_matching_allowed": False,
        "paper_play_allowed": False,
        "official_written": False,
        "pending_written": False,
        "qq_written": False,
        "old_system_touched": "NO",
    }
    report["self_check"] = self_check(report)
    return report


def self_check(report: dict[str, Any]) -> dict[str, Any]:
    gates = report["play_prerequisite_audit"]["gates"]
    checks = {
        "consistency_result_pass": report["consistency_result"] == "CONSISTENT_NO_STABLE_EDGE",
        "freeze_conclusion_no_stable_edge": report["freeze_conclusion"] == "NO_STABLE_EDGE_FOUND",
        "survived_count_1": report["survived_count"] == 1,
        "stable_count_before_stress_0": report["stable_count_before_stress"] == 0,
        "survived_bucket_is_watchlist": report["survived_bucket"]["stability_status"] == "WATCHLIST_RESEARCH_ONLY",
        "play_prerequisites_not_met": report["play_prerequisite_audit"]["all_play_prerequisites_met"] is False,
        "stable_gate_failed": gates.get("stable_research_candidate_before_stress") is False,
        "current_matching_blocked": report["current_match_matching_allowed"] is False,
        "paper_play_blocked": report["paper_play_allowed"] is False,
        "recommendations_blocked": report["recommendations_generated"] is False,
        "official_pending_qq_blocked": not report["official_written"] and not report["pending_written"] and not report["qq_written"],
        "old_system_touched_no": report["old_system_touched"] == "NO",
    }
    rendered = {name: "PASS" if value else "FAIL" for name, value in checks.items()}
    return {"status": "PASS" if all(checks.values()) else "FAIL", "checks": rendered}


def render_markdown(report: dict[str, Any]) -> str:
    bucket = report["survived_bucket"]
    gate_rows = [
        [name, passed, "PASS" if passed else "FAIL"]
        for name, passed in report["play_prerequisite_audit"]["gates"].items()
    ]
    return "\n".join(
        [
            "# M1 Round2 Freeze Consistency Audit",
            "",
            f"- generated_at_utc: `{report['generated_at_utc']}`",
            f"- consistency_result: `{report['consistency_result']}`",
            f"- freeze_conclusion: `{report['freeze_conclusion']}`",
            f"- self_check: `{report['self_check']['status']}`",
            "- research_only: `true`",
            "- recommendations_generated: `false`",
            "- current_match_matching_allowed: `false`",
            "- paper_play_allowed: `false`",
            "- old_system_touched: `NO`",
            "",
            "## Survived Bucket",
            "",
            markdown_table(
                ["field", "value"],
                [[key, value] for key, value in bucket.items()],
            ),
            "",
            "## Why This Is Not An Edge",
            "",
            "\n".join(f"- {item}" for item in report["why_not_edge"]),
            "",
            "## PLAY Prerequisite Audit",
            "",
            markdown_table(["gate", "value", "status"], gate_rows),
            "",
            "The survived bucket fails the PLAY/current-matching prerequisites. The most important failed gate is that it entered stress as `WATCHLIST_RESEARCH_ONLY`, while Round2 stability filtering produced `stable_count=0`. Stress survival of a watchlist observation does not override the frozen `NO_STABLE_EDGE_FOUND` conclusion.",
            "",
            "## Allowed Next",
            "",
            "\n".join(f"- `{item}`" for item in report["allowed_next"]),
            "",
            "## Blocked Actions",
            "",
            "\n".join(f"- `{item}`" for item in report["blocked_actions"]),
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
    for path in [STABILITY_JSON, STRESS_JSON, FREEZE_JSON, HYBRID_POLICY_JSON]:
        if not path.exists():
            raise SystemExit(f"Required input missing: {path}")
    report = build_report()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    print(f"m1_round2_freeze_consistency_audit: {report['self_check']['status']}")
    print(f"consistency_result={report['consistency_result']}")
    print(f"survived_bucket={report['survived_bucket']['market']} {report['survived_bucket']['selection']} {report['survived_bucket']['bucket_type']} {report['survived_bucket']['bucket']}")
    print(f"freeze_conclusion={report['freeze_conclusion']}")
    print(f"report_json={REPORT_JSON.relative_to(REPO_ROOT)}")
    print(f"report_md={REPORT_MD.relative_to(REPO_ROOT)}")
    return 0 if report["self_check"]["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
