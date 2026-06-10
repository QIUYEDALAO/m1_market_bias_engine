#!/usr/bin/env python3
"""Audit Round2 stable/watch stability candidates for research-only review."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
STABILITY_CSV = REPO_ROOT / "data" / "processed" / "backtest_ready" / "m1_round2_stability_filtered_buckets.csv"
BUCKET_CSV = REPO_ROOT / "data" / "processed" / "backtest_ready" / "m1_round2_bucket_results.csv"
FEATURE_CSV = REPO_ROOT / "data" / "processed" / "market_features" / "m1_round2_market_features.csv"
REPORT_DIR = REPO_ROOT / "reports" / "backtest"
REPORT_MD = REPORT_DIR / "m1_round2_stability_candidate_audit.md"
REPORT_JSON = REPORT_DIR / "m1_round2_stability_candidate_audit.json"

EXPECTED_STABLE_COUNT = 0
EXPECTED_WATCH_COUNT = 3
EXPECTED_POSITIVE_ROI_BUCKET_COUNT = 25
EXPECTED_FEATURE_ROWS = 9063


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stability-csv", type=Path, default=STABILITY_CSV)
    parser.add_argument("--bucket-csv", type=Path, default=BUCKET_CSV)
    parser.add_argument("--feature-csv", type=Path, default=FEATURE_CSV)
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_json_map(value: str) -> dict[str, int]:
    try:
        parsed = json.loads(value or "{}")
    except json.JSONDecodeError:
        return {}
    return {str(key): int(val) for key, val in parsed.items()}


def to_float(value: str) -> float:
    try:
        return float((value or "").strip())
    except ValueError:
        return 0.0


def to_int(value: str) -> int:
    try:
        return int(float((value or "").strip()))
    except ValueError:
        return 0


def share_summary(distribution: dict[str, int], sample_count: int) -> dict[str, Any]:
    if not distribution or sample_count <= 0:
        return {
            "count": 0,
            "max_key": "",
            "max_rows": 0,
            "max_share": 0.0,
            "is_single_source": False,
        }
    max_key, max_rows = max(distribution.items(), key=lambda item: item[1])
    return {
        "count": len(distribution),
        "max_key": max_key,
        "max_rows": max_rows,
        "max_share": max_rows / sample_count,
        "is_single_source": len(distribution) == 1,
    }


def split_reasons(value: str) -> list[str]:
    if not value or value == "NONE":
        return []
    return [part for part in value.split("|") if part and part != "NONE"]


def candidate_rows(stability_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        row
        for row in stability_rows
        if row["stability_status"] in {"STABLE_RESEARCH_CANDIDATE", "WATCHLIST_RESEARCH_ONLY"}
    ]


def find_matching_feature_rows(candidate: dict[str, str], feature_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    market = candidate["market"]
    selection = candidate["selection"]
    bucket_type = candidate["bucket_type"]
    bucket = candidate["bucket"]
    rows = [row for row in feature_rows if row["season_role"] == "COMPLETE_BACKTEST"]

    def probability_bucket(value: float) -> str:
        import math

        upper = min(1.0, math.ceil(value * 10) / 10)
        lower = max(0.0, upper - 0.1)
        return f"{lower:.1f}-{upper:.1f}"

    def odds_delta_bucket(value: float) -> str:
        import math

        if value <= -1.0:
            return "<=-1.00"
        if value >= 1.0:
            return ">=1.00"
        lower = math.floor(value / 0.25) * 0.25
        upper = lower + 0.25
        return f"{lower:.2f}-{upper:.2f}"

    if market == "1X2" and bucket_type == "closing_fair_probability":
        field = {
            "home": "closing_home_fair_prob",
            "draw": "closing_draw_fair_prob",
            "away": "closing_away_fair_prob",
        }[selection]
        return [
            row
            for row in rows
            if row.get(field)
            and probability_bucket(to_float(row[field])) == bucket
        ]
    if market == "1X2" and bucket_type == "open_to_close_odds_movement":
        field = {
            "home": "home_odds_delta",
            "draw": "draw_odds_delta",
            "away": "away_odds_delta",
        }[selection]
        return [
            row
            for row in rows
            if row.get(field)
            and odds_delta_bucket(to_float(row[field])) == bucket
        ]
    return []


def settlement_or_field_risk(candidate: dict[str, str], matching_rows: list[dict[str, str]]) -> dict[str, Any]:
    market = candidate["market"]
    bucket_type = candidate["bucket_type"]
    selection = candidate["selection"]
    notes = []
    risk_flags = []

    if market == "1X2":
        notes.append("Uses full_time_result and B365 1X2 closing odds/fair probability features.")
        if bucket_type == "open_to_close_odds_movement":
            notes.append("Depends on opening-to-closing B365 odds delta; sensitive to stale or sparse opening quotes.")
            risk_flags.append("FIELD_MOVEMENT_SENSITIVITY")
        if selection == "draw":
            notes.append("Draw buckets can be more volatile because draw hit rate is structurally lower.")
            risk_flags.append("DRAW_OUTCOME_VOLATILITY")
    elif market == "AH":
        notes.append("Uses AH settlement and AH closing line context; quarter-line settlement can create half outcomes.")
        risk_flags.append("SETTLEMENT_FORMULA_SENSITIVITY")
    elif market == "OU25":
        notes.append("Uses OU 2.5 settlement; 2.5 line has no push state.")

    empty_feature_cells = 0
    for row in matching_rows:
        if bucket_type == "closing_fair_probability":
            field = f"closing_{selection}_fair_prob"
            if field in row and not row[field]:
                empty_feature_cells += 1
        elif bucket_type == "open_to_close_odds_movement":
            field = f"{selection}_odds_delta"
            if field in row and not row[field]:
                empty_feature_cells += 1
    if empty_feature_cells:
        risk_flags.append("EMPTY_FEATURE_CELLS_PRESENT")
        notes.append(f"Matched rows include {empty_feature_cells} empty relevant feature cells.")

    return {
        "risk_flags": sorted(set(risk_flags)) or ["NO_MAJOR_FIELD_OR_SETTLEMENT_BIAS_DETECTED"],
        "notes": notes,
        "matched_feature_rows": len(matching_rows),
    }


def audit_candidate(candidate: dict[str, str], feature_rows: list[dict[str, str]]) -> dict[str, Any]:
    sample_count = to_int(candidate["sample_count"])
    league_dist = parse_json_map(candidate["league_distribution"])
    season_dist = parse_json_map(candidate["season_distribution"])
    league_share = share_summary(league_dist, sample_count)
    season_share = share_summary(season_dist, sample_count)
    matching_rows = find_matching_feature_rows(candidate, feature_rows)
    field_risk = settlement_or_field_risk(candidate, matching_rows)
    return {
        "market": candidate["market"],
        "selection": candidate["selection"],
        "bucket_type": candidate["bucket_type"],
        "bucket": candidate["bucket"],
        "stability_status": candidate["stability_status"],
        "sample_count": sample_count,
        "hit_rate": to_float(candidate["hit_rate"]),
        "roi": to_float(candidate["roi"]),
        "avg_odds": to_float(candidate["avg_odds"]),
        "max_losing_streak": to_int(candidate["max_losing_streak"]),
        "max_drawdown": to_float(candidate["max_drawdown"]),
        "league_distribution": league_dist,
        "season_distribution": season_dist,
        "league_coverage_count": league_share["count"],
        "season_coverage_count": season_share["count"],
        "cross_league": league_share["count"] > 1,
        "cross_season": season_share["count"] > 1,
        "single_league_dependent": league_share["is_single_source"] or league_share["max_share"] >= 0.55,
        "single_season_dependent": season_share["is_single_source"] or season_share["max_share"] >= 0.55,
        "max_league_share": league_share["max_share"],
        "max_season_share": season_share["max_share"],
        "field_or_settlement_bias": field_risk,
        "research_only": "YES",
        "not_play": "YES",
    }


def positive_roi_reject_summary(stability_rows: list[dict[str, str]]) -> dict[str, Any]:
    positive_rows = [row for row in stability_rows if row["positive_roi_bucket"] == "YES"]
    status_counts = Counter(row["stability_status"] for row in positive_rows)
    hard_counts = Counter()
    watch_counts = Counter()
    phase5_counts = Counter()
    for row in positive_rows:
        for reason in split_reasons(row["stability_reject_reasons"]):
            hard_counts[reason] += 1
        for reason in split_reasons(row["watchlist_reasons"]):
            watch_counts[reason] += 1
        for reason in split_reasons(row["phase5_reject_reason"]):
            phase5_counts[reason] += 1
    return {
        "positive_roi_bucket_count": len(positive_rows),
        "status_counts": dict(sorted(status_counts.items())),
        "hard_reject_reason_counts": dict(sorted(hard_counts.items())),
        "watchlist_reason_counts": dict(sorted(watch_counts.items())),
        "phase5_reject_reason_counts": dict(sorted(phase5_counts.items())),
    }


def calculate_stats(stability_rows: list[dict[str, str]], feature_rows: list[dict[str, str]], candidates: list[dict[str, Any]]) -> dict[str, Any]:
    stable_count = sum(1 for row in stability_rows if row["stability_status"] == "STABLE_RESEARCH_CANDIDATE")
    watch_count = sum(1 for row in stability_rows if row["stability_status"] == "WATCHLIST_RESEARCH_ONLY")
    positive_count = sum(1 for row in stability_rows if row["positive_roi_bucket"] == "YES")
    return {
        "input_stability_rows": len(stability_rows),
        "input_feature_rows": len(feature_rows),
        "stable_count": stable_count,
        "watch_count": watch_count,
        "candidate_audit_count": len(candidates),
        "positive_roi_bucket_count": positive_count,
        "current_2025_26_candidate_rows": sum(
            1
            for candidate in candidates
            if "2025/26" in candidate["season_distribution"]
        ),
    }


def self_check(report: dict[str, Any]) -> dict[str, Any]:
    stats = report["stats"]
    candidates = report["candidates"]
    checks = {
        "stable_count_0": stats["stable_count"] == EXPECTED_STABLE_COUNT,
        "watch_count_3": stats["watch_count"] == EXPECTED_WATCH_COUNT,
        "positive_roi_bucket_count_25": stats["positive_roi_bucket_count"]
        == EXPECTED_POSITIVE_ROI_BUCKET_COUNT,
        "candidate_audit_count_3": stats["candidate_audit_count"] == 3,
        "input_feature_rows_9063": stats["input_feature_rows"] == EXPECTED_FEATURE_ROWS,
        "no_current_2025_26_candidates": stats["current_2025_26_candidate_rows"] == 0,
        "all_candidates_research_only_not_play": all(
            candidate["research_only"] == "YES" and candidate["not_play"] == "YES"
            for candidate in candidates
        ),
        "all_candidates_have_distribution_review": all(
            "cross_league" in candidate
            and "cross_season" in candidate
            and "single_league_dependent" in candidate
            and "single_season_dependent" in candidate
            for candidate in candidates
        ),
        "recommendations_generated_no": report["recommendations_generated"] == "NO",
        "old_system_touched_no": report["old_system_touched"] == "NO",
    }
    rendered = {name: "PASS" if passed else "FAIL" for name, passed in checks.items()}
    return {"status": "PASS" if all(checks.values()) else "FAIL", "checks": rendered}


def markdown_cell(value: Any) -> str:
    if isinstance(value, float):
        value = f"{value:.6f}".rstrip("0").rstrip(".")
    return str(value).replace("|", "\\|")


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(markdown_cell(header) for header in headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(markdown_cell(value) for value in row) + " |")
    return "\n".join(lines)


def render_markdown(report: dict[str, Any]) -> str:
    stats = report["stats"]
    candidates = report["candidates"]
    positive = report["positive_roi_reject_summary"]
    candidate_rows = [
        [
            c["stability_status"],
            c["market"],
            c["selection"],
            c["bucket_type"],
            c["bucket"],
            c["sample_count"],
            c["hit_rate"],
            c["roi"],
            c["avg_odds"],
            c["max_losing_streak"],
            c["max_drawdown"],
            c["cross_league"],
            c["cross_season"],
            c["single_league_dependent"],
            c["single_season_dependent"],
        ]
        for c in candidates
    ]
    bias_rows = [
        [
            c["stability_status"],
            ", ".join(c["field_or_settlement_bias"]["risk_flags"]),
            " ".join(c["field_or_settlement_bias"]["notes"]),
        ]
        for c in candidates
    ]
    return "\n".join(
        [
            "# M1 Round2 Stability Candidate Audit",
            "",
            f"- generated_at_utc: `{report['generated_at_utc']}`",
            f"- stability_csv: `{report['inputs']['stability_csv']}`",
            f"- bucket_csv: `{report['inputs']['bucket_csv']}`",
            f"- feature_csv: `{report['inputs']['feature_csv']}`",
            f"- checker: `{report['self_check']['status']}`",
            "- research_only: `YES`",
            "- not_play: `YES`",
            "- recommendations_generated: `NO`",
            "- round1_merged: `NO`",
            "- five_dimension_can_create_candidate: `false`",
            "- official_written: `NO`",
            "- pending_written: `NO`",
            "- qq_written: `NO`",
            "- old_system_touched: `NO`",
            "",
            "This audit explains Round2 stable/watch buckets for research review only. "
            "It is not PLAY, not a recommendation, not a current-match matching layer, "
            "and five-dimension evaluation cannot create candidates.",
            "",
            "## Summary",
            "",
            markdown_table(
                ["metric", "value"],
                [
                    ["stable_count", stats["stable_count"]],
                    ["watch_count", stats["watch_count"]],
                    ["positive_roi_bucket_count", stats["positive_roi_bucket_count"]],
                    ["candidate_audit_count", stats["candidate_audit_count"]],
                    ["current_2025_26_candidate_rows", stats["current_2025_26_candidate_rows"]],
                ],
            ),
            "",
            "## Candidate Audit",
            "",
            markdown_table(
                [
                    "status",
                    "market",
                    "selection",
                    "bucket_type",
                    "bucket",
                    "sample_count",
                    "hit_rate",
                    "roi",
                    "avg_odds",
                    "max_losing_streak",
                    "max_drawdown",
                    "cross_league",
                    "cross_season",
                    "single_league_dependent",
                    "single_season_dependent",
                ],
                candidate_rows,
            ),
            "",
            "## Field And Settlement Bias Review",
            "",
            markdown_table(["status", "risk_flags", "notes"], bias_rows),
            "",
            "## Candidate Distributions",
            "",
            "\n\n".join(
                [
                    "\n".join(
                        [
                            f"### {c['stability_status']} {c['market']} {c['selection']} {c['bucket_type']} {c['bucket']}",
                            "",
                            "League distribution:",
                            "",
                            markdown_table(
                                ["league", "rows"],
                                [[k, v] for k, v in c["league_distribution"].items()],
                            ),
                            "",
                            "Season distribution:",
                            "",
                            markdown_table(
                                ["season", "rows"],
                                [[k, v] for k, v in c["season_distribution"].items()],
                            ),
                        ]
                    )
                    for c in candidates
                ]
            ),
            "",
            "## Positive ROI Bucket Reject Summary",
            "",
            markdown_table(
                ["metric", "value"],
                [["positive_roi_bucket_count", positive["positive_roi_bucket_count"]]],
            ),
            "",
            "Status counts:",
            "",
            markdown_table(
                ["status", "count"],
                [[k, v] for k, v in positive["status_counts"].items()],
            ),
            "",
            "Hard reject reason counts:",
            "",
            markdown_table(
                ["reason", "count"],
                [[k, v] for k, v in positive["hard_reject_reason_counts"].items()]
                or [["NONE", 0]],
            ),
            "",
            "Watchlist reason counts:",
            "",
            markdown_table(
                ["reason", "count"],
                [[k, v] for k, v in positive["watchlist_reason_counts"].items()]
                or [["NONE", 0]],
            ),
            "",
            "## Self Check",
            "",
            markdown_table(
                ["check", "status"],
                [[name, status] for name, status in report["self_check"]["checks"].items()],
            ),
            "",
        ]
    )


def build_report(
    stability_csv: Path,
    bucket_csv: Path,
    feature_csv: Path,
    stability_rows: list[dict[str, str]],
    feature_rows: list[dict[str, str]],
) -> dict[str, Any]:
    candidates = [audit_candidate(row, feature_rows) for row in candidate_rows(stability_rows)]
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "inputs": {
            "stability_csv": str(stability_csv.relative_to(REPO_ROOT)),
            "bucket_csv": str(bucket_csv.relative_to(REPO_ROOT)),
            "feature_csv": str(feature_csv.relative_to(REPO_ROOT)),
        },
        "stats": calculate_stats(stability_rows, feature_rows, candidates),
        "candidates": candidates,
        "positive_roi_reject_summary": positive_roi_reject_summary(stability_rows),
        "research_only": "YES",
        "not_play": "YES",
        "recommendations_generated": "NO",
        "round1_merged": "NO",
        "five_dimension_can_create_candidate": False,
        "current_match_matching": "NO",
        "official_written": "NO",
        "pending_written": "NO",
        "qq_written": "NO",
        "old_system_touched": "NO",
    }
    report["self_check"] = self_check(report)
    return report


def main() -> int:
    args = parse_args()
    stability_csv = args.stability_csv.resolve()
    bucket_csv = args.bucket_csv.resolve()
    feature_csv = args.feature_csv.resolve()
    for path in [stability_csv, bucket_csv, feature_csv]:
        if not path.exists():
            raise SystemExit(f"Required input does not exist: {path}")

    stability_rows = read_csv(stability_csv)
    _bucket_rows = read_csv(bucket_csv)
    feature_rows = read_csv(feature_csv)
    report = build_report(stability_csv, bucket_csv, feature_csv, stability_rows, feature_rows)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")

    stats = report["stats"]
    print(f"m1_round2_stability_candidate_audit: {report['self_check']['status']}")
    print(f"stable_count={stats['stable_count']}")
    print(f"watch_count={stats['watch_count']}")
    print(f"positive_roi_bucket_count={stats['positive_roi_bucket_count']}")
    print(f"candidate_audit_count={stats['candidate_audit_count']}")
    print(f"current_2025_26_candidate_rows={stats['current_2025_26_candidate_rows']}")
    print(f"report_json={REPORT_JSON.relative_to(REPO_ROOT)}")
    print(f"report_md={REPORT_MD.relative_to(REPO_ROOT)}")
    return 0 if report["self_check"]["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
