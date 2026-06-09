#!/usr/bin/env python3
"""Stress test Phase 7A stability candidates across seasons and leagues."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
STABILITY_CSV = REPO_ROOT / "data" / "processed" / "backtest_ready" / "m1_stability_filtered_buckets.csv"
FEATURE_CSV = REPO_ROOT / "data" / "processed" / "market_features" / "m1_market_features.csv"
CANDIDATE_AUDIT_JSON = REPO_ROOT / "reports" / "backtest" / "m1_stability_candidate_audit.json"
REPORT_DIR = REPO_ROOT / "reports" / "backtest"
REPORT_MD = REPORT_DIR / "m1_stability_candidate_stress_test.md"
REPORT_JSON = REPORT_DIR / "m1_stability_candidate_stress_test.json"

MIN_SLICE_SAMPLE = 100
EXPECTED_STABLE_COUNT = 1
EXPECTED_WATCH_COUNT = 1
COMPLETE_BACKTEST_SEASONS = ["2020/21", "2021/22", "2022/23", "2023/24", "2024/25"]
LEAGUE_GROUPS = {
    "group_a_e0_d1_sp1": {"E0", "D1", "SP1"},
    "group_b_i1_f1": {"I1", "F1"},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stability-csv", type=Path, default=STABILITY_CSV)
    parser.add_argument("--feature-csv", type=Path, default=FEATURE_CSV)
    parser.add_argument("--candidate-audit-json", type=Path, default=CANDIDATE_AUDIT_JSON)
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def to_float(value: str) -> float | None:
    raw = (value or "").strip()
    if raw == "":
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def fmt(value: float | None, places: int = 6) -> str:
    if value is None:
        return ""
    rendered = f"{value:.{places}f}".rstrip("0").rstrip(".")
    return rendered if rendered != "-0" else "0"


def probability_bucket(value: float | None) -> str:
    if value is None:
        return "MISSING"
    upper = min(1.0, math.ceil(value * 10) / 10)
    lower = max(0.0, upper - 0.1)
    return f"{lower:.1f}-{upper:.1f}"


def odds_delta_bucket(value: float | None) -> str:
    if value is None:
        return "MISSING"
    if value <= -1.0:
        return "<=-1.00"
    if value >= 1.0:
        return ">=1.00"
    lower = math.floor(value / 0.25) * 0.25
    upper = lower + 0.25
    return f"{lower:.2f}-{upper:.2f}"


def candidate_rows(stability_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        row
        for row in stability_rows
        if row["stability_status"] in {"STABLE_RESEARCH_CANDIDATE", "WATCHLIST_RESEARCH_ONLY"}
    ]


def row_matches_candidate(row: dict[str, str], candidate: dict[str, str]) -> bool:
    if row["season_role"] != "COMPLETE_BACKTEST":
        return False
    if candidate["market"] != "1X2":
        return False
    selection = candidate["selection"]
    bucket_type = candidate["bucket_type"]
    bucket = candidate["bucket"]
    if bucket_type == "closing_fair_probability":
        field = {
            "home": "closing_home_fair_prob",
            "draw": "closing_draw_fair_prob",
            "away": "closing_away_fair_prob",
        }[selection]
        return probability_bucket(to_float(row.get(field, ""))) == bucket
    if bucket_type == "open_to_close_odds_movement":
        field = {
            "home": "home_odds_delta",
            "draw": "draw_odds_delta",
            "away": "away_odds_delta",
        }[selection]
        return odds_delta_bucket(to_float(row.get(field, ""))) == bucket
    return False


def closing_odds(row: dict[str, str], selection: str) -> float | None:
    raw_field = {
        "home": "closing_home_implied_prob_raw",
        "draw": "closing_draw_implied_prob_raw",
        "away": "closing_away_implied_prob_raw",
    }[selection]
    raw_prob = to_float(row.get(raw_field, ""))
    if raw_prob is None or raw_prob <= 0:
        return None
    return 1.0 / raw_prob


def is_hit(row: dict[str, str], selection: str) -> bool:
    return {
        "home": row["full_time_result"] == "H",
        "draw": row["full_time_result"] == "D",
        "away": row["full_time_result"] == "A",
    }[selection]


def max_drawdown(profits: list[float]) -> float:
    equity = 0.0
    peak = 0.0
    worst = 0.0
    for profit in profits:
        equity += profit
        peak = max(peak, equity)
        worst = min(worst, equity - peak)
    return worst / len(profits) if profits else 0.0


def slice_metrics(rows: list[dict[str, str]], selection: str) -> dict[str, Any]:
    profits = []
    hit_count = 0
    odds_values = []
    for row in rows:
        odds = closing_odds(row, selection)
        if odds is None:
            continue
        odds_values.append(odds)
        if is_hit(row, selection):
            hit_count += 1
            profits.append(odds - 1.0)
        else:
            profits.append(-1.0)
    sample_count = len(profits)
    roi = sum(profits) / sample_count if sample_count else 0.0
    return {
        "sample_count": sample_count,
        "hit_count": hit_count,
        "hit_rate": hit_count / sample_count if sample_count else 0.0,
        "avg_odds": sum(odds_values) / sample_count if sample_count else 0.0,
        "roi": roi,
        "max_drawdown": max_drawdown(profits),
        "league_distribution": dict(sorted(Counter(row["league"] for row in rows).items())),
        "season_distribution": dict(sorted(Counter(row["season"] for row in rows).items())),
    }


def build_slices(candidate: dict[str, str], rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    selection = candidate["selection"]
    specs: list[tuple[str, str, list[dict[str, str]], bool]] = []
    specs.append(("all_complete_backtest", "all", rows, True))
    for season in COMPLETE_BACKTEST_SEASONS:
        specs.append(
            (
                "leave_one_season_out",
                f"without_{season}",
                [row for row in rows if row["season"] != season],
                True,
            )
        )
    for league in sorted({row["league"] for row in rows}):
        specs.append(
            (
                "leave_one_league_out",
                f"without_{league}",
                [row for row in rows if row["league"] != league],
                True,
            )
        )
    first_half = {"2020/21", "2021/22", "2022/23"}
    second_half = {"2023/24", "2024/25"}
    specs.extend(
        [
            (
                "first_half_vs_second_half",
                "first_half_2020_21_to_2022_23",
                [row for row in rows if row["season"] in first_half],
                True,
            ),
            (
                "first_half_vs_second_half",
                "second_half_2023_24_to_2024_25",
                [row for row in rows if row["season"] in second_half],
                True,
            ),
        ]
    )
    for group_name, leagues in LEAGUE_GROUPS.items():
        specs.append(
            (
                "league_group_split",
                group_name,
                [row for row in rows if row["league"] in leagues],
                True,
            )
        )
    bookmaker_sources = sorted({row.get("bookmaker_source", "") for row in rows})
    for source in bookmaker_sources:
        specs.append(
            (
                "odds_source_sanity_check",
                f"bookmaker_source_{source or 'UNKNOWN'}",
                [row for row in rows if row.get("bookmaker_source", "") == source],
                False,
            )
        )
    output = []
    for slice_type, slice_name, slice_rows, critical in specs:
        metrics = slice_metrics(slice_rows, selection)
        failed = metrics["sample_count"] < MIN_SLICE_SAMPLE or metrics["roi"] <= 0
        output.append(
            {
                "slice_type": slice_type,
                "slice_name": slice_name,
                "critical": critical,
                "sample_count": metrics["sample_count"],
                "hit_count": metrics["hit_count"],
                "hit_rate": metrics["hit_rate"],
                "avg_odds": metrics["avg_odds"],
                "roi": metrics["roi"],
                "max_drawdown": metrics["max_drawdown"],
                "league_distribution": metrics["league_distribution"],
                "season_distribution": metrics["season_distribution"],
                "slice_status": "FAIL" if critical and failed else "PASS",
                "failure_reason": (
                    "SAMPLE_TOO_SMALL"
                    if critical and metrics["sample_count"] < MIN_SLICE_SAMPLE
                    else "NON_POSITIVE_ROI"
                    if critical and metrics["roi"] <= 0
                    else "NONE"
                ),
            }
        )
    return output


def stress_candidate(candidate: dict[str, str], feature_rows: list[dict[str, str]]) -> dict[str, Any]:
    rows = [row for row in feature_rows if row_matches_candidate(row, candidate)]
    slices = build_slices(candidate, rows)
    critical_failures = [
        row for row in slices if row["critical"] and row["slice_status"] == "FAIL"
    ]
    return {
        "stability_status": candidate["stability_status"],
        "market": candidate["market"],
        "selection": candidate["selection"],
        "bucket_type": candidate["bucket_type"],
        "bucket": candidate["bucket"],
        "base_sample_count": len(rows),
        "stress_status": "FRAGILE" if critical_failures else "SURVIVED",
        "critical_failure_count": len(critical_failures),
        "critical_failures": critical_failures,
        "slices": slices,
        "research_only": "YES",
        "not_play": "YES",
    }


def calculate_stats(stability_rows: list[dict[str, str]], feature_rows: list[dict[str, str]], stress: list[dict[str, Any]]) -> dict[str, Any]:
    stable_count = sum(1 for row in stability_rows if row["stability_status"] == "STABLE_RESEARCH_CANDIDATE")
    watch_count = sum(1 for row in stability_rows if row["stability_status"] == "WATCHLIST_RESEARCH_ONLY")
    complete_rows = sum(1 for row in feature_rows if row["season_role"] == "COMPLETE_BACKTEST")
    current_rows = sum(1 for row in feature_rows if row["season_role"] == "CURRENT_NOT_FOR_BACKTEST")
    slice_count = sum(len(item["slices"]) for item in stress)
    critical_slice_count = sum(1 for item in stress for row in item["slices"] if row["critical"])
    return {
        "stable_count": stable_count,
        "watch_count": watch_count,
        "candidate_count": len(stress),
        "feature_rows": len(feature_rows),
        "complete_backtest_feature_rows": complete_rows,
        "current_not_for_backtest_feature_rows": current_rows,
        "stress_test_count": slice_count,
        "critical_stress_test_count": critical_slice_count,
        "survived_count": sum(1 for item in stress if item["stress_status"] == "SURVIVED"),
        "fragile_count": sum(1 for item in stress if item["stress_status"] == "FRAGILE"),
        "current_2025_26_slice_rows": sum(
            1
            for item in stress
            for row in item["slices"]
            if "2025/26" in row["season_distribution"]
        ),
    }


def self_check(report: dict[str, Any]) -> dict[str, Any]:
    stats = report["stats"]
    checks = {
        "stable_count_1": stats["stable_count"] == 1,
        "watch_count_1": stats["watch_count"] == 1,
        "candidate_count_2": stats["candidate_count"] == 2,
        "stress_tests_generated": stats["stress_test_count"] > 0
        and all(item["slices"] for item in report["candidates"]),
        "complete_backtest_only": stats["current_2025_26_slice_rows"] == 0,
        "feature_rows_10733": stats["feature_rows"] == 10733,
        "complete_rows_8982": stats["complete_backtest_feature_rows"] == 8982,
        "current_rows_excluded_1751": stats["current_not_for_backtest_feature_rows"] == 1751,
        "all_candidates_research_only_not_play": all(
            item["research_only"] == "YES" and item["not_play"] == "YES"
            for item in report["candidates"]
        ),
        "recommendations_generated_no": report["recommendations_generated"] == "NO",
        "old_system_touched_no": report["old_system_touched"] == "NO",
    }
    rendered = {name: "PASS" if passed else "FAIL" for name, passed in checks.items()}
    return {"status": "PASS" if all(checks.values()) else "FAIL", "checks": rendered}


def markdown_cell(value: Any) -> str:
    if isinstance(value, float):
        value = f"{value:.6f}".rstrip("0").rstrip(".")
    if isinstance(value, dict):
        value = json.dumps(value, sort_keys=True)
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
    summary_rows = [
        [
            item["stability_status"],
            item["market"],
            item["selection"],
            item["bucket_type"],
            item["bucket"],
            item["base_sample_count"],
            item["stress_status"],
            item["critical_failure_count"],
        ]
        for item in report["candidates"]
    ]
    sections = []
    for item in report["candidates"]:
        rows = [
            [
                row["slice_type"],
                row["slice_name"],
                row["critical"],
                row["sample_count"],
                row["hit_rate"],
                row["roi"],
                row["max_drawdown"],
                row["slice_status"],
                row["failure_reason"],
            ]
            for row in item["slices"]
        ]
        sections.append(
            "\n".join(
                [
                    f"### {item['stability_status']} {item['market']} {item['selection']} {item['bucket_type']} {item['bucket']}",
                    "",
                    markdown_table(
                        [
                            "slice_type",
                            "slice_name",
                            "critical",
                            "sample_count",
                            "hit_rate",
                            "roi",
                            "max_drawdown",
                            "slice_status",
                            "failure_reason",
                        ],
                        rows,
                    ),
                ]
            )
        )
    return "\n".join(
        [
            "# M1 Stability Candidate Stress Test",
            "",
            f"- generated_at_utc: `{report['generated_at_utc']}`",
            f"- stability_csv: `{report['inputs']['stability_csv']}`",
            f"- feature_csv: `{report['inputs']['feature_csv']}`",
            f"- candidate_audit_json: `{report['inputs']['candidate_audit_json']}`",
            f"- checker: `{report['self_check']['status']}`",
            "- research_only: `YES`",
            "- not_play: `YES`",
            "- recommendations_generated: `NO`",
            "- current_match_matching: `NO`",
            "- official_written: `NO`",
            "- pending_written: `NO`",
            "- qq_written: `NO`",
            "- old_system_touched: `NO`",
            "",
            "This is a research-only stress test. SURVIVED does not mean PLAY; "
            "FRAGILE does not create a live action. No current fixtures are matched.",
            "",
            "## Summary",
            "",
            markdown_table(
                ["metric", "value"],
                [
                    ["stable_count", stats["stable_count"]],
                    ["watch_count", stats["watch_count"]],
                    ["candidate_count", stats["candidate_count"]],
                    ["stress_test_count", stats["stress_test_count"]],
                    ["critical_stress_test_count", stats["critical_stress_test_count"]],
                    ["survived_count", stats["survived_count"]],
                    ["fragile_count", stats["fragile_count"]],
                    ["current_2025_26_slice_rows", stats["current_2025_26_slice_rows"]],
                ],
            ),
            "",
            "## Candidate Stress Status",
            "",
            markdown_table(
                [
                    "status",
                    "market",
                    "selection",
                    "bucket_type",
                    "bucket",
                    "base_sample_count",
                    "stress_status",
                    "critical_failure_count",
                ],
                summary_rows,
            ),
            "",
            "## Stress Slices",
            "",
            "\n\n".join(sections),
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
    feature_csv: Path,
    candidate_audit_json: Path,
    stability_rows: list[dict[str, str]],
    feature_rows: list[dict[str, str]],
) -> dict[str, Any]:
    candidates = [stress_candidate(row, feature_rows) for row in candidate_rows(stability_rows)]
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "inputs": {
            "stability_csv": str(stability_csv.relative_to(REPO_ROOT)),
            "feature_csv": str(feature_csv.relative_to(REPO_ROOT)),
            "candidate_audit_json": str(candidate_audit_json.relative_to(REPO_ROOT)),
        },
        "candidates": candidates,
        "stats": calculate_stats(stability_rows, feature_rows, candidates),
        "research_only": "YES",
        "not_play": "YES",
        "recommendations_generated": "NO",
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
    feature_csv = args.feature_csv.resolve()
    candidate_audit_json = args.candidate_audit_json.resolve()
    for path in [stability_csv, feature_csv, candidate_audit_json]:
        if not path.exists():
            raise SystemExit(f"Required input does not exist: {path}")

    stability_rows = read_csv(stability_csv)
    feature_rows = read_csv(feature_csv)
    _candidate_audit = read_json(candidate_audit_json)
    report = build_report(stability_csv, feature_csv, candidate_audit_json, stability_rows, feature_rows)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")

    stats = report["stats"]
    print(f"m1_stability_candidate_stress_test: {report['self_check']['status']}")
    print(f"stable_count={stats['stable_count']}")
    print(f"watch_count={stats['watch_count']}")
    print(f"stress_test_count={stats['stress_test_count']}")
    print(f"survived_count={stats['survived_count']}")
    print(f"fragile_count={stats['fragile_count']}")
    print(f"current_2025_26_slice_rows={stats['current_2025_26_slice_rows']}")
    print(f"report_json={REPORT_JSON.relative_to(REPO_ROOT)}")
    print(f"report_md={REPORT_MD.relative_to(REPO_ROOT)}")
    return 0 if report["self_check"]["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
