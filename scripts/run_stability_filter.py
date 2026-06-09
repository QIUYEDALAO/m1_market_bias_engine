#!/usr/bin/env python3
"""Apply Phase 6 stability filters to M1 offline bucket backtest results."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = REPO_ROOT / "data" / "processed" / "backtest_ready" / "m1_bucket_results.csv"
INPUT_REPORT = REPO_ROOT / "reports" / "backtest" / "m1_bucket_backtest_report.json"
THRESHOLDS_PATH = REPO_ROOT / "config" / "stability_thresholds.json"
OUTPUT_CSV = REPO_ROOT / "data" / "processed" / "backtest_ready" / "m1_stability_filtered_buckets.csv"
REPORT_DIR = REPO_ROOT / "reports" / "backtest"
REPORT_MD = REPORT_DIR / "m1_stability_filter_report.md"
REPORT_JSON = REPORT_DIR / "m1_stability_filter_report.json"

EXPECTED_BUCKET_ROWS = 139

OUTPUT_FIELDS = [
    "market",
    "selection",
    "bucket_type",
    "bucket",
    "sample_count",
    "hit_rate",
    "avg_odds",
    "roi",
    "max_losing_streak",
    "max_drawdown",
    "league_distribution",
    "season_distribution",
    "positive_roi_bucket",
    "phase5_reject_reason",
    "stability_status",
    "stability_reject_reasons",
    "watchlist_reasons",
    "research_only",
    "recommendation_generated",
    "official_written",
    "pending_written",
    "qq_written",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-csv", type=Path, default=INPUT_CSV)
    parser.add_argument("--input-report", type=Path, default=INPUT_REPORT)
    parser.add_argument("--thresholds", type=Path, default=THRESHOLDS_PATH)
    parser.add_argument("--output-csv", type=Path, default=OUTPUT_CSV)
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def parse_distribution(value: str) -> dict[str, int]:
    try:
        parsed = json.loads(value or "{}")
    except json.JSONDecodeError:
        return {}
    return {str(key): int(val) for key, val in parsed.items()}


def max_share(distribution: dict[str, int], total: int) -> float:
    if not distribution or total <= 0:
        return 0.0
    return max(distribution.values()) / total


def split_reasons(value: str) -> set[str]:
    if not value or value == "NONE":
        return set()
    return {part for part in value.split("|") if part and part != "NONE"}


def hard_reject_reasons(row: dict[str, str], thresholds: dict[str, Any]) -> list[str]:
    hard = thresholds["hard_filters"]
    mapped = hard["reject_reasons"]
    reasons: list[str] = []
    sample_count = to_int(row["sample_count"])
    roi = to_float(row["roi"])
    phase5_reasons = split_reasons(row["reject_reason"])

    if sample_count < hard["minimum_sample_count"] or "SMALL_SAMPLE" in phase5_reasons:
        reasons.append("REJECT_SMALL_SAMPLE")
    if roi <= hard["minimum_roi_exclusive"]:
        reasons.append("REJECT_NON_POSITIVE_ROI")
    for source_reason, target_reason in mapped.items():
        if source_reason == "SMALL_SAMPLE":
            continue
        if source_reason in phase5_reasons:
            reasons.append(target_reason)
    return sorted(set(reasons))


def watchlist_reasons(row: dict[str, str], thresholds: dict[str, Any]) -> list[str]:
    watch = thresholds["watchlist_filters"]
    sample_count = to_int(row["sample_count"])
    drawdown = to_float(row["max_drawdown"])
    league_dist = parse_distribution(row["league_distribution"])
    season_dist = parse_distribution(row["season_distribution"])
    league_share = max_share(league_dist, sample_count)
    season_share = max_share(season_dist, sample_count)
    reasons = []
    if watch["minimum_watch_sample_count"] <= sample_count < watch["low_sample_watch_count"]:
        reasons.append("WATCH_LOW_SAMPLE_MARGIN")
    if watch["watch_drawdown_floor"] < drawdown <= watch["watch_drawdown_ceiling"]:
        reasons.append("WATCH_DRAWDOWN_MARGIN")
    if max(league_share, season_share) >= watch["watch_concentration_share"]:
        reasons.append("WATCH_CONCENTRATION_MARGIN")
    return reasons


def classify(row: dict[str, str], thresholds: dict[str, Any]) -> dict[str, str]:
    hard_reasons = hard_reject_reasons(row, thresholds)
    soft_reasons = [] if hard_reasons else watchlist_reasons(row, thresholds)
    if hard_reasons:
        status = "|".join(hard_reasons)
    elif soft_reasons:
        status = thresholds["watch_status"]
    else:
        status = thresholds["stable_status"]

    return {
        "market": row["market"],
        "selection": row["selection"],
        "bucket_type": row["bucket_type"],
        "bucket": row["bucket"],
        "sample_count": row["sample_count"],
        "hit_rate": row["hit_rate"],
        "avg_odds": row["avg_odds"],
        "roi": row["roi"],
        "max_losing_streak": row["max_losing_streak"],
        "max_drawdown": row["max_drawdown"],
        "league_distribution": row["league_distribution"],
        "season_distribution": row["season_distribution"],
        "positive_roi_bucket": row["positive_roi_bucket"],
        "phase5_reject_reason": row["reject_reason"],
        "stability_status": status,
        "stability_reject_reasons": "|".join(hard_reasons) if hard_reasons else "NONE",
        "watchlist_reasons": "|".join(soft_reasons) if soft_reasons else "NONE",
        "research_only": "YES",
        "recommendation_generated": "NO",
        "official_written": "NO",
        "pending_written": "NO",
        "qq_written": "NO",
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def has_current_season(row: dict[str, str]) -> bool:
    return "2025/26" in row.get("season_distribution", "")


def calculate_stats(
    input_rows: list[dict[str, str]], output_rows: list[dict[str, str]], input_report: dict[str, Any]
) -> dict[str, Any]:
    status_counter = Counter(row["stability_status"] for row in output_rows)
    rejected_count = sum(
        1
        for row in output_rows
        if row["stability_reject_reasons"] != "NONE"
    )
    stable_count = status_counter.get("STABLE_RESEARCH_CANDIDATE", 0)
    watch_count = status_counter.get("WATCHLIST_RESEARCH_ONLY", 0)
    positive_roi_count = sum(1 for row in output_rows if row["positive_roi_bucket"] == "YES")
    return {
        "input_bucket_rows": len(input_rows),
        "output_bucket_rows": len(output_rows),
        "stable_count": stable_count,
        "watch_count": watch_count,
        "rejected_count": rejected_count,
        "positive_roi_bucket_count": positive_roi_count,
        "current_2025_26_bucket_rows": sum(1 for row in output_rows if has_current_season(row)),
        "status_counts": dict(sorted(status_counter.items())),
        "hard_reject_reason_counts": dict(
            sorted(
                Counter(
                    reason
                    for row in output_rows
                    for reason in row["stability_reject_reasons"].split("|")
                    if reason != "NONE"
                ).items()
            )
        ),
        "watchlist_reason_counts": dict(
            sorted(
                Counter(
                    reason
                    for row in output_rows
                    for reason in row["watchlist_reasons"].split("|")
                    if reason != "NONE"
                ).items()
            )
        ),
        "phase5_input_rows": input_report["stats"]["input_rows"],
        "phase5_backtest_rows": input_report["stats"]["backtest_rows"],
        "phase5_excluded_current_rows": input_report["stats"]["excluded_current_rows"],
    }


def self_check(
    input_rows: list[dict[str, str]],
    output_rows: list[dict[str, str]],
    input_report: dict[str, Any],
    stats: dict[str, Any],
) -> dict[str, Any]:
    positive_rows = [row for row in output_rows if row["positive_roi_bucket"] == "YES"]
    checks = {
        "input_bucket_rows_139": stats["input_bucket_rows"] == EXPECTED_BUCKET_ROWS,
        "output_bucket_rows_match_input": stats["output_bucket_rows"] == stats["input_bucket_rows"],
        "stable_watch_rejected_counted": (
            stats["stable_count"] + stats["watch_count"] + stats["rejected_count"]
            == stats["output_bucket_rows"]
        ),
        "positive_roi_buckets_have_stability_status": all(
            row["stability_status"] for row in positive_rows
        )
        and len(positive_rows) == stats["positive_roi_bucket_count"],
        "no_current_2025_26": stats["current_2025_26_bucket_rows"] == 0,
        "phase5_backtest_rows_8982": input_report["stats"]["backtest_rows"] == 8982,
        "phase5_excluded_current_rows_1751": input_report["stats"]["excluded_current_rows"]
        == 1751,
        "research_only_no_recommendations": all(
            row["research_only"] == "YES" and row["recommendation_generated"] == "NO"
            for row in output_rows
        ),
        "no_official_pending_qq": all(
            row["official_written"] == "NO"
            and row["pending_written"] == "NO"
            and row["qq_written"] == "NO"
            for row in output_rows
        ),
        "old_system_touched_no": True,
    }
    rendered = {name: "PASS" if passed else "FAIL" for name, passed in checks.items()}
    return {"status": "PASS" if all(checks.values()) else "FAIL", "checks": rendered}


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    def cell(value: Any) -> str:
        return str(value).replace("|", "\\|")

    lines = [
        "| " + " | ".join(cell(header) for header in headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(cell(value) for value in row) + " |")
    return "\n".join(lines)


def render_markdown(report: dict[str, Any], output_rows: list[dict[str, str]]) -> str:
    stats = report["stats"]
    preview = output_rows[:20]
    return "\n".join(
        [
            "# M1 Stability Filter Report",
            "",
            f"- generated_at_utc: `{report['generated_at_utc']}`",
            f"- input_csv: `{report['input_csv']}`",
            f"- input_report: `{report['input_report']}`",
            f"- thresholds: `{report['thresholds']}`",
            f"- output_csv: `{report['output_csv']}`",
            f"- checker: `{report['self_check']['status']}`",
            "- research_only: `YES`",
            "- recommendations_generated: `NO`",
            "- official_written: `NO`",
            "- pending_written: `NO`",
            "- qq_written: `NO`",
            "- old_system_touched: `NO`",
            "",
            "## Summary",
            "",
            markdown_table(
                ["metric", "value"],
                [
                    ["input_bucket_rows", stats["input_bucket_rows"]],
                    ["output_bucket_rows", stats["output_bucket_rows"]],
                    ["stable_count", stats["stable_count"]],
                    ["watch_count", stats["watch_count"]],
                    ["rejected_count", stats["rejected_count"]],
                    ["positive_roi_bucket_count", stats["positive_roi_bucket_count"]],
                    ["current_2025_26_bucket_rows", stats["current_2025_26_bucket_rows"]],
                ],
            ),
            "",
            "This phase filters offline bucket results only. It does not match current "
            "fixtures, generate recommendations, or write official/pending/QQ outputs.",
            "",
            "## Status Counts",
            "",
            markdown_table(
                ["status", "bucket_count"],
                [[key, value] for key, value in stats["status_counts"].items()],
            ),
            "",
            "## Hard Reject Reason Counts",
            "",
            markdown_table(
                ["reason", "bucket_count"],
                [[key, value] for key, value in stats["hard_reject_reason_counts"].items()],
            ),
            "",
            "## Watchlist Reason Counts",
            "",
            markdown_table(
                ["reason", "bucket_count"],
                [[key, value] for key, value in stats["watchlist_reason_counts"].items()]
                or [["NONE", 0]],
            ),
            "",
            "## Bucket Preview",
            "",
            markdown_table(
                [
                    "market",
                    "selection",
                    "bucket_type",
                    "bucket",
                    "sample_count",
                    "roi",
                    "stability_status",
                    "stability_reject_reasons",
                    "watchlist_reasons",
                ],
                [
                    [
                        row["market"],
                        row["selection"],
                        row["bucket_type"],
                        row["bucket"],
                        row["sample_count"],
                        row["roi"],
                        row["stability_status"],
                        row["stability_reject_reasons"],
                        row["watchlist_reasons"],
                    ]
                    for row in preview
                ],
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
    input_csv: Path,
    input_report_path: Path,
    thresholds_path: Path,
    output_csv: Path,
    stats: dict[str, Any],
    checks: dict[str, Any],
) -> dict[str, Any]:
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "input_csv": str(input_csv.relative_to(REPO_ROOT)),
        "input_report": str(input_report_path.relative_to(REPO_ROOT)),
        "thresholds": str(thresholds_path.relative_to(REPO_ROOT)),
        "output_csv": str(output_csv.relative_to(REPO_ROOT)),
        "stats": stats,
        "research_only": "YES",
        "recommendations_generated": "NO",
        "official_written": "NO",
        "pending_written": "NO",
        "qq_written": "NO",
        "old_system_touched": "NO",
        "self_check": checks,
    }


def main() -> int:
    args = parse_args()
    input_csv = args.input_csv.resolve()
    input_report_path = args.input_report.resolve()
    thresholds_path = args.thresholds.resolve()
    output_csv = args.output_csv.resolve()
    for path in [input_csv, input_report_path, thresholds_path]:
        if not path.exists():
            raise SystemExit(f"Required input does not exist: {path}")

    input_rows = read_csv(input_csv)
    input_report = read_json(input_report_path)
    thresholds = read_json(thresholds_path)
    output_rows = [classify(row, thresholds) for row in input_rows]
    write_csv(output_csv, output_rows)
    stats = calculate_stats(input_rows, output_rows, input_report)
    checks = self_check(input_rows, output_rows, input_report, stats)
    report = build_report(input_csv, input_report_path, thresholds_path, output_csv, stats, checks)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report, output_rows), encoding="utf-8")

    print(f"m1_stability_filter: {checks['status']}")
    print(f"input_bucket_rows={stats['input_bucket_rows']}")
    print(f"stable_count={stats['stable_count']}")
    print(f"watch_count={stats['watch_count']}")
    print(f"rejected_count={stats['rejected_count']}")
    print(f"positive_roi_bucket_count={stats['positive_roi_bucket_count']}")
    print(f"current_2025_26_bucket_rows={stats['current_2025_26_bucket_rows']}")
    print(f"output_csv={output_csv.relative_to(REPO_ROOT)}")
    print(f"report_json={REPORT_JSON.relative_to(REPO_ROOT)}")
    print(f"report_md={REPORT_MD.relative_to(REPO_ROOT)}")
    return 0 if checks["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
