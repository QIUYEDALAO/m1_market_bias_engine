#!/usr/bin/env python3
"""Build the M1 Round2 Market Bias freeze report."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
ROUND1_FREEZE_JSON = REPO_ROOT / "reports" / "backtest" / "M1_MARKET_BIAS_ROUND1_FREEZE_REPORT.json"
BUCKET_JSON = REPO_ROOT / "reports" / "backtest" / "m1_round2_bucket_backtest_report.json"
STABILITY_JSON = REPO_ROOT / "reports" / "backtest" / "m1_round2_stability_filter_report.json"
AUDIT_JSON = REPO_ROOT / "reports" / "backtest" / "m1_round2_stability_candidate_audit.json"
STRESS_JSON = REPO_ROOT / "reports" / "backtest" / "m1_round2_stability_candidate_stress_test.json"
HYBRID_POLICY_JSON = REPO_ROOT / "config" / "hybrid_decision_policy.json"
REPORT_DIR = REPO_ROOT / "reports" / "backtest"
REPORT_JSON = REPORT_DIR / "M1_ROUND2_MARKET_BIAS_FREEZE_REPORT.json"
REPORT_MD = REPORT_DIR / "M1_ROUND2_MARKET_BIAS_FREEZE_REPORT.md"


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


def build_report() -> dict[str, Any]:
    round1 = read_json(ROUND1_FREEZE_JSON)
    bucket = read_json(BUCKET_JSON)
    stability = read_json(STABILITY_JSON)
    audit = read_json(AUDIT_JSON)
    stress = read_json(STRESS_JSON)
    hybrid = read_json(HYBRID_POLICY_JSON)

    bucket_stats = bucket["stats"]
    stability_stats = stability["stats"]
    audit_stats = audit["stats"]
    stress_stats = stress["stats"]
    hybrid_rules = hybrid["hard_rules"]

    conclusion = "NO_STABLE_EDGE_FOUND"
    interpretation = [
        "Round2 expanded the league universe and found positive ROI buckets before stability filtering.",
        "Round2 Phase 5 produced no STABLE_RESEARCH_CANDIDATE buckets; it produced watchlist-only research candidates.",
        "Round2 stress testing left one WATCHLIST_RESEARCH_ONLY bucket as SURVIVED, but watchlist survival is not a stable edge.",
        "Five-dimension evaluation is locked as a risk filter and downgrade layer only; it cannot create candidates.",
        "M1 remains research-only and must not match current fixtures or emit recommendations.",
    ]

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "FROZEN",
        "conclusion": conclusion,
        "inputs": {
            "round1_freeze": str(ROUND1_FREEZE_JSON.relative_to(REPO_ROOT)),
            "round2_bucket": str(BUCKET_JSON.relative_to(REPO_ROOT)),
            "round2_stability": str(STABILITY_JSON.relative_to(REPO_ROOT)),
            "round2_candidate_audit": str(AUDIT_JSON.relative_to(REPO_ROOT)),
            "round2_stress": str(STRESS_JSON.relative_to(REPO_ROOT)),
            "hybrid_policy": str(HYBRID_POLICY_JSON.relative_to(REPO_ROOT)),
        },
        "metrics": {
            "round1_conclusion": round1["conclusion"],
            "input_rows": bucket_stats["input_rows"],
            "backtest_rows": bucket_stats["backtest_rows"],
            "excluded_current_rows": bucket_stats["excluded_current_rows"],
            "bucket_rows": bucket_stats["bucket_rows"],
            "positive_roi_buckets": bucket_stats["positive_roi_bucket_count"],
            "stable_count_before_stress": stability_stats["stable_count"],
            "watch_count_before_stress": stability_stats["watch_count"],
            "rejected_count": stability_stats["rejected_count"],
            "candidate_audit_count": audit_stats["candidate_audit_count"],
            "survived_after_stress": stress_stats["survived_count"],
            "fragile_after_stress": stress_stats["fragile_count"],
            "current_2025_26_slice_rows": stress_stats["current_2025_26_slice_rows"],
        },
        "hybrid_policy_lock": {
            "M1_can_create_candidate": hybrid_rules["M1_can_create_candidate"],
            "FiveDimension_can_create_candidate": hybrid_rules["FiveDimension_can_create_candidate"],
            "No_market_edge_no_candidate": hybrid_rules["No_market_edge_no_candidate"],
            "current_match_matching_allowed": hybrid_rules["current_match_matching_allowed"],
            "paper_play_allowed": hybrid_rules["paper_play_allowed"],
        },
        "research_only": True,
        "current_match_matching_allowed": False,
        "paper_play_allowed": False,
        "recommendations_generated": False,
        "official_written": False,
        "pending_written": False,
        "qq_written": False,
        "old_system_touched": "NO",
        "five_dimension_can_create_candidate": False,
        "round1_merged": "NO",
        "interpretation": interpretation,
        "consistency": {
            "round2_bucket_self_test": bucket["self_check"]["status"],
            "round2_stability_self_test": stability["self_check"]["status"],
            "round2_candidate_audit_self_test": audit["self_check"]["status"],
            "round2_stress_self_test": stress["self_check"]["status"],
        },
    }
    report["self_check"] = self_check(report)
    return report


def self_check(report: dict[str, Any]) -> dict[str, Any]:
    metrics = report["metrics"]
    policy = report["hybrid_policy_lock"]
    checks = {
        "round1_no_stable_edge": metrics["round1_conclusion"] == "NO_STABLE_EDGE_FOUND",
        "input_rows_9063": metrics["input_rows"] == 9063,
        "backtest_rows_7606": metrics["backtest_rows"] == 7606,
        "excluded_current_rows_1457": metrics["excluded_current_rows"] == 1457,
        "bucket_rows_139": metrics["bucket_rows"] == 139,
        "positive_roi_buckets_25": metrics["positive_roi_buckets"] == 25,
        "stable_before_stress_0": metrics["stable_count_before_stress"] == 0,
        "watch_before_stress_3": metrics["watch_count_before_stress"] == 3,
        "survived_after_stress_1": metrics["survived_after_stress"] == 1,
        "fragile_after_stress_2": metrics["fragile_after_stress"] == 2,
        "conclusion_no_stable_edge_found": report["conclusion"] == "NO_STABLE_EDGE_FOUND",
        "current_match_matching_false": report["current_match_matching_allowed"] is False,
        "paper_play_false": report["paper_play_allowed"] is False,
        "recommendations_false": report["recommendations_generated"] is False,
        "official_pending_qq_false": not report["official_written"]
        and not report["pending_written"]
        and not report["qq_written"],
        "five_dimension_cannot_create_candidate": policy["FiveDimension_can_create_candidate"] is False
        and report["five_dimension_can_create_candidate"] is False,
        "m1_can_create_candidate": policy["M1_can_create_candidate"] is True,
        "no_market_edge_no_candidate": policy["No_market_edge_no_candidate"] is True,
        "current_2025_26_not_in_stress": metrics["current_2025_26_slice_rows"] == 0,
        "old_system_touched_no": report["old_system_touched"] == "NO",
        "all_source_self_tests_pass": all(value == "PASS" for value in report["consistency"].values()),
    }
    rendered = {name: "PASS" if value else "FAIL" for name, value in checks.items()}
    return {"status": "PASS" if all(checks.values()) else "FAIL", "checks": rendered}


def render_markdown(report: dict[str, Any]) -> str:
    metrics = report["metrics"]
    policy = report["hybrid_policy_lock"]
    return "\n".join(
        [
            "# M1 Round2 Market Bias Freeze Report",
            "",
            f"- generated_at_utc: `{report['generated_at_utc']}`",
            f"- status: `{report['status']}`",
            f"- conclusion: `{report['conclusion']}`",
            f"- current_match_matching_allowed: `{str(report['current_match_matching_allowed']).lower()}`",
            f"- paper_play_allowed: `{str(report['paper_play_allowed']).lower()}`",
            f"- recommendations_generated: `{str(report['recommendations_generated']).lower()}`",
            f"- official_written: `{str(report['official_written']).lower()}`",
            f"- pending_written: `{str(report['pending_written']).lower()}`",
            f"- qq_written: `{str(report['qq_written']).lower()}`",
            f"- five_dimension_can_create_candidate: `{str(report['five_dimension_can_create_candidate']).lower()}`",
            f"- old_system_touched: `{report['old_system_touched']}`",
            f"- checker: `{report['self_check']['status']}`",
            "",
            "This freeze report closes the Round2 Market Bias research pipeline. It is not a recommendation report, not a PLAY list, and not a current-match matching layer.",
            "",
            "## Round Metrics",
            "",
            markdown_table(
                ["metric", "value"],
                [
                    ["round1_conclusion", metrics["round1_conclusion"]],
                    ["input_rows", metrics["input_rows"]],
                    ["backtest_rows", metrics["backtest_rows"]],
                    ["excluded_current_rows", metrics["excluded_current_rows"]],
                    ["bucket_rows", metrics["bucket_rows"]],
                    ["positive_roi_buckets", metrics["positive_roi_buckets"]],
                    ["stable_count_before_stress", metrics["stable_count_before_stress"]],
                    ["watch_count_before_stress", metrics["watch_count_before_stress"]],
                    ["rejected_count", metrics["rejected_count"]],
                    ["candidate_audit_count", metrics["candidate_audit_count"]],
                    ["survived_after_stress", metrics["survived_after_stress"]],
                    ["fragile_after_stress", metrics["fragile_after_stress"]],
                    ["current_2025_26_slice_rows", metrics["current_2025_26_slice_rows"]],
                ],
            ),
            "",
            "## Decision",
            "",
            "`NO_STABLE_EDGE_FOUND`",
            "",
            "Round2 found 25 positive ROI buckets before stability filtering. The stability filter left 0 stable buckets and 3 watchlist-only buckets. Stress testing left 1 survived watchlist observation and 2 fragile observations. Because no bucket reached `STABLE_RESEARCH_CANDIDATE` before stress, the survived watchlist observation is not a stable edge and cannot become PLAY.",
            "",
            "## Hybrid Policy Lock",
            "",
            markdown_table(
                ["policy", "value"],
                [
                    ["M1_can_create_candidate", policy["M1_can_create_candidate"]],
                    ["FiveDimension_can_create_candidate", policy["FiveDimension_can_create_candidate"]],
                    ["No_market_edge_no_candidate", policy["No_market_edge_no_candidate"]],
                    ["current_match_matching_allowed", policy["current_match_matching_allowed"]],
                    ["paper_play_allowed", policy["paper_play_allowed"]],
                    ["recommendations_generated", report["recommendations_generated"]],
                    ["official_written", report["official_written"]],
                    ["pending_written", report["pending_written"]],
                    ["qq_written", report["qq_written"]],
                    ["old_system_touched", report["old_system_touched"]],
                ],
            ),
            "",
            "## Interpretation",
            "",
            "\n".join(f"- {item}" for item in report["interpretation"]),
            "",
            "## Source Consistency",
            "",
            markdown_table(
                ["source", "self_test"],
                [[key, value] for key, value in report["consistency"].items()],
            ),
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
    for path in [ROUND1_FREEZE_JSON, BUCKET_JSON, STABILITY_JSON, AUDIT_JSON, STRESS_JSON, HYBRID_POLICY_JSON]:
        if not path.exists():
            raise SystemExit(f"Required input missing: {path}")
    report = build_report()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    metrics = report["metrics"]
    print(f"m1_round2_freeze_report: {report['self_check']['status']}")
    print(f"conclusion={report['conclusion']}")
    print(f"stable_count_before_stress={metrics['stable_count_before_stress']}")
    print(f"watch_count_before_stress={metrics['watch_count_before_stress']}")
    print(f"survived_after_stress={metrics['survived_after_stress']}")
    print(f"fragile_after_stress={metrics['fragile_after_stress']}")
    print(f"report_json={REPORT_JSON.relative_to(REPO_ROOT)}")
    print(f"report_md={REPORT_MD.relative_to(REPO_ROOT)}")
    return 0 if report["self_check"]["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
