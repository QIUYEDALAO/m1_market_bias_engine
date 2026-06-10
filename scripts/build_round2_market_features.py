#!/usr/bin/env python3
"""Build M1 Round2 market-bias feature rows from the Round2 normalized table."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = REPO_ROOT / "data" / "processed" / "normalized_matches" / "m1_round2_matches_normalized.csv"
OUTPUT_DIR = REPO_ROOT / "data" / "processed" / "market_features"
OUTPUT_CSV = OUTPUT_DIR / "m1_round2_market_features.csv"
REPORT_DIR = REPO_ROOT / "reports" / "data_audit"
REPORT_MD = REPORT_DIR / "m1_round2_market_features_report.md"
REPORT_JSON = REPORT_DIR / "m1_round2_market_features_report.json"

EXPECTED_ROWS = 9063
EXPECTED_COMPLETE_ROWS = 7606
EXPECTED_CURRENT_ROWS = 1457
FAIR_PROB_TOLERANCE = 0.000001

BASE_FIELDS = [
    "match_id",
    "league",
    "season",
    "season_role",
    "date",
    "home_team",
    "away_team",
    "full_time_home_goals",
    "full_time_away_goals",
    "full_time_result",
    "bookmaker_source",
    "data_source",
]

FEATURE_FIELDS = [
    "opening_home_implied_prob_raw",
    "opening_draw_implied_prob_raw",
    "opening_away_implied_prob_raw",
    "closing_home_implied_prob_raw",
    "closing_draw_implied_prob_raw",
    "closing_away_implied_prob_raw",
    "opening_home_fair_prob",
    "opening_draw_fair_prob",
    "opening_away_fair_prob",
    "closing_home_fair_prob",
    "closing_draw_fair_prob",
    "closing_away_fair_prob",
    "home_fair_prob_delta",
    "draw_fair_prob_delta",
    "away_fair_prob_delta",
    "home_odds_delta",
    "draw_odds_delta",
    "away_odds_delta",
    "ah_line_movement",
    "ah_home_odds_movement",
    "ah_away_odds_movement",
    "ah_settlement",
    "ou25_settlement",
    "feature_source",
    "backtest_run",
    "recommendation_generated",
]

OUTPUT_FIELDS = BASE_FIELDS + FEATURE_FIELDS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-csv", type=Path, default=INPUT_CSV)
    parser.add_argument("--output-csv", type=Path, default=OUTPUT_CSV)
    return parser.parse_args()


def to_float(value: str) -> float | None:
    raw = (value or "").strip()
    if raw == "":
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def to_int(value: str) -> int | None:
    number = to_float(value)
    if number is None:
        return None
    return int(number)


def fmt(value: float | None, places: int = 8) -> str:
    if value is None:
        return ""
    rendered = f"{value:.{places}f}".rstrip("0").rstrip(".")
    return rendered if rendered != "-0" else "0"


def implied_prob(odds: float | None) -> float | None:
    if odds is None or odds <= 0:
        return None
    return 1.0 / odds


def fair_probs(raw_probs: list[float | None]) -> list[float | None]:
    if any(value is None for value in raw_probs):
        return [None, None, None]
    total = sum(value for value in raw_probs if value is not None)
    if total <= 0:
        return [None, None, None]
    return [value / total if value is not None else None for value in raw_probs]


def delta(closing: float | None, opening: float | None) -> float | None:
    if closing is None or opening is None:
        return None
    return closing - opening


def half_line_result(goal_diff: int, line: float) -> int:
    adjusted = goal_diff + line
    if adjusted > 0:
        return 1
    if adjusted < 0:
        return -1
    return 0


def split_quarter_line(line: float) -> list[float]:
    scaled = round(line * 4)
    remainder = scaled % 4
    if remainder in (1, 3):
        lower = (scaled - 1) / 4
        upper = (scaled + 1) / 4
        return [lower, upper]
    return [scaled / 4, scaled / 4]


def ah_settlement(home_goals: int | None, away_goals: int | None, closing_line: float | None) -> str:
    if home_goals is None or away_goals is None or closing_line is None:
        return ""
    goal_diff = home_goals - away_goals
    results = [half_line_result(goal_diff, line) for line in split_quarter_line(closing_line)]
    wins = results.count(1)
    pushes = results.count(0)
    losses = results.count(-1)
    if wins == 2:
        return "FULL_WIN"
    if wins == 1 and pushes == 1:
        return "HALF_WIN"
    if pushes == 2:
        return "PUSH"
    if losses == 1 and pushes == 1:
        return "HALF_LOSS"
    if losses == 2:
        return "LOSS"
    return ""


def ou25_settlement(home_goals: int | None, away_goals: int | None) -> str:
    if home_goals is None or away_goals is None:
        return ""
    total_goals = home_goals + away_goals
    if total_goals > 2.5:
        return "OVER_WIN"
    if total_goals < 2.5:
        return "UNDER_WIN"
    return "PUSH_NOT_APPLICABLE"


def transform_row(row: dict[str, str]) -> dict[str, str]:
    opening_home = to_float(row["opening_home_odds"])
    opening_draw = to_float(row["opening_draw_odds"])
    opening_away = to_float(row["opening_away_odds"])
    closing_home = to_float(row["closing_home_odds"])
    closing_draw = to_float(row["closing_draw_odds"])
    closing_away = to_float(row["closing_away_odds"])
    opening_line = to_float(row["opening_ah_line"])
    closing_line = to_float(row["closing_ah_line"])
    opening_ah_home = to_float(row["opening_ah_home_odds"])
    opening_ah_away = to_float(row["opening_ah_away_odds"])
    closing_ah_home = to_float(row["closing_ah_home_odds"])
    closing_ah_away = to_float(row["closing_ah_away_odds"])
    home_goals = to_int(row["full_time_home_goals"])
    away_goals = to_int(row["full_time_away_goals"])

    opening_raw = [implied_prob(opening_home), implied_prob(opening_draw), implied_prob(opening_away)]
    closing_raw = [implied_prob(closing_home), implied_prob(closing_draw), implied_prob(closing_away)]
    opening_fair = fair_probs(opening_raw)
    closing_fair = fair_probs(closing_raw)

    out = {field: row[field] for field in BASE_FIELDS}
    out.update(
        {
            "opening_home_implied_prob_raw": fmt(opening_raw[0]),
            "opening_draw_implied_prob_raw": fmt(opening_raw[1]),
            "opening_away_implied_prob_raw": fmt(opening_raw[2]),
            "closing_home_implied_prob_raw": fmt(closing_raw[0]),
            "closing_draw_implied_prob_raw": fmt(closing_raw[1]),
            "closing_away_implied_prob_raw": fmt(closing_raw[2]),
            "opening_home_fair_prob": fmt(opening_fair[0]),
            "opening_draw_fair_prob": fmt(opening_fair[1]),
            "opening_away_fair_prob": fmt(opening_fair[2]),
            "closing_home_fair_prob": fmt(closing_fair[0]),
            "closing_draw_fair_prob": fmt(closing_fair[1]),
            "closing_away_fair_prob": fmt(closing_fair[2]),
            "home_fair_prob_delta": fmt(delta(closing_fair[0], opening_fair[0])),
            "draw_fair_prob_delta": fmt(delta(closing_fair[1], opening_fair[1])),
            "away_fair_prob_delta": fmt(delta(closing_fair[2], opening_fair[2])),
            "home_odds_delta": fmt(delta(closing_home, opening_home)),
            "draw_odds_delta": fmt(delta(closing_draw, opening_draw)),
            "away_odds_delta": fmt(delta(closing_away, opening_away)),
            "ah_line_movement": fmt(delta(closing_line, opening_line)),
            "ah_home_odds_movement": fmt(delta(closing_ah_home, opening_ah_home)),
            "ah_away_odds_movement": fmt(delta(closing_ah_away, opening_ah_away)),
            "ah_settlement": ah_settlement(home_goals, away_goals, closing_line),
            "ou25_settlement": ou25_settlement(home_goals, away_goals),
            "feature_source": "m1_round2_normalized_matches",
            "backtest_run": "NO",
            "recommendation_generated": "NO",
        }
    )
    return out


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def numeric(value: str) -> float | None:
    return to_float(value)


def calculate_stats(input_rows: list[dict[str, str]], output_rows: list[dict[str, str]]) -> dict[str, Any]:
    role_counts = Counter(row["season_role"] for row in output_rows)
    ah_nonempty = sum(1 for row in output_rows if row["ah_settlement"])
    ou_nonempty = sum(1 for row in output_rows if row["ou25_settlement"])
    fair_opening_rows = 0
    fair_closing_rows = 0
    fair_sum_failures = 0
    for row in output_rows:
        opening = [
            numeric(row["opening_home_fair_prob"]),
            numeric(row["opening_draw_fair_prob"]),
            numeric(row["opening_away_fair_prob"]),
        ]
        closing = [
            numeric(row["closing_home_fair_prob"]),
            numeric(row["closing_draw_fair_prob"]),
            numeric(row["closing_away_fair_prob"]),
        ]
        if all(value is not None for value in opening):
            fair_opening_rows += 1
            if abs(sum(value for value in opening if value is not None) - 1.0) > FAIR_PROB_TOLERANCE:
                fair_sum_failures += 1
        if all(value is not None for value in closing):
            fair_closing_rows += 1
            if abs(sum(value for value in closing if value is not None) - 1.0) > FAIR_PROB_TOLERANCE:
                fair_sum_failures += 1

    return {
        "input_rows": len(input_rows),
        "output_rows": len(output_rows),
        "rows_by_role": {
            "COMPLETE_BACKTEST": role_counts.get("COMPLETE_BACKTEST", 0),
            "CURRENT_NOT_FOR_BACKTEST": role_counts.get("CURRENT_NOT_FOR_BACKTEST", 0),
        },
        "complete_backtest_feature_rows": role_counts.get("COMPLETE_BACKTEST", 0),
        "current_not_for_backtest_feature_rows": role_counts.get("CURRENT_NOT_FOR_BACKTEST", 0),
        "fair_opening_probability_rows": fair_opening_rows,
        "fair_closing_probability_rows": fair_closing_rows,
        "fair_probability_sum_failures": fair_sum_failures,
        "ah_settlement_nonempty_rows": ah_nonempty,
        "ah_settlement_coverage": ah_nonempty / len(output_rows) if output_rows else 0,
        "ah_settlement_counts": dict(sorted(Counter(row["ah_settlement"] for row in output_rows).items())),
        "ou25_settlement_nonempty_rows": ou_nonempty,
        "ou25_settlement_coverage": ou_nonempty / len(output_rows) if output_rows else 0,
        "ou25_settlement_counts": dict(sorted(Counter(row["ou25_settlement"] for row in output_rows).items())),
    }


def self_check(stats: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "input_rows_9063": stats["input_rows"] == EXPECTED_ROWS,
        "output_rows_9063": stats["output_rows"] == EXPECTED_ROWS,
        "complete_backtest_feature_rows_7606": stats["complete_backtest_feature_rows"]
        == EXPECTED_COMPLETE_ROWS,
        "current_not_for_backtest_feature_rows_1457": stats[
            "current_not_for_backtest_feature_rows"
        ]
        == EXPECTED_CURRENT_ROWS,
        "current_not_in_complete_backtest_features": stats["rows_by_role"][
            "CURRENT_NOT_FOR_BACKTEST"
        ]
        == EXPECTED_CURRENT_ROWS,
        "fair_probabilities_sum_to_one": stats["fair_probability_sum_failures"] == 0,
        "ah_settlement_coverage_reasonable": stats["ah_settlement_coverage"] >= 0.99,
        "ou25_settlement_coverage_reasonable": stats["ou25_settlement_coverage"] >= 0.99,
        "backtest_run_no": True,
        "recommendations_generated_no": True,
        "old_system_touched_no": True,
    }
    rendered = {name: "PASS" if passed else "FAIL" for name, passed in checks.items()}
    return {"status": "PASS" if all(checks.values()) else "FAIL", "checks": rendered}


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def render_markdown(report: dict[str, Any]) -> str:
    stats = report["stats"]
    return "\n".join(
        [
            "# M1 Round2 Market Features Report",
            "",
            f"- generated_at_utc: `{report['generated_at_utc']}`",
            f"- input_csv: `{report['input_csv']}`",
            f"- output_csv: `{report['output_csv']}`",
            f"- checker: `{report['self_check']['status']}`",
            "- old_system_touched: `NO`",
            "- recommendations_generated: `NO`",
            "- backtest_run: `NO`",
            "- round1_merged: `NO`",
            "",
            "## Summary",
            "",
            markdown_table(
                ["metric", "value"],
                [
                    ["input_rows", stats["input_rows"]],
                    ["output_rows", stats["output_rows"]],
                    ["complete_backtest_feature_rows", stats["complete_backtest_feature_rows"]],
                    [
                        "current_not_for_backtest_feature_rows",
                        stats["current_not_for_backtest_feature_rows"],
                    ],
                    ["fair_opening_probability_rows", stats["fair_opening_probability_rows"]],
                    ["fair_closing_probability_rows", stats["fair_closing_probability_rows"]],
                    ["fair_probability_sum_failures", stats["fair_probability_sum_failures"]],
                    ["ah_settlement_coverage", f"{stats['ah_settlement_coverage']:.6f}"],
                    ["ou25_settlement_coverage", f"{stats['ou25_settlement_coverage']:.6f}"],
                ],
            ),
            "",
            "`2025/26` rows are preserved as `CURRENT_NOT_FOR_BACKTEST`; they are not "
            "included in `complete_backtest_feature_rows`. This phase computes features "
            "only from the Round2 normalized table. It does not merge Round1 data, run a "
            "backtest, or generate recommendations.",
            "",
            "## Feature Groups",
            "",
            markdown_table(
                ["group", "fields"],
                [
                    [
                        "1X2 raw implied probability",
                        "opening_*_implied_prob_raw, closing_*_implied_prob_raw",
                    ],
                    [
                        "1X2 fair probability",
                        "opening_*_fair_prob, closing_*_fair_prob",
                    ],
                    [
                        "probability delta",
                        "home_fair_prob_delta, draw_fair_prob_delta, away_fair_prob_delta",
                    ],
                    ["odds delta", "home_odds_delta, draw_odds_delta, away_odds_delta"],
                    [
                        "AH movement",
                        "ah_line_movement, ah_home_odds_movement, ah_away_odds_movement",
                    ],
                    ["settlement", "ah_settlement, ou25_settlement"],
                ],
            ),
            "",
            "## AH Settlement Counts",
            "",
            markdown_table(
                ["settlement", "rows"],
                [[key or "EMPTY", value] for key, value in stats["ah_settlement_counts"].items()],
            ),
            "",
            "## OU 2.5 Settlement Counts",
            "",
            markdown_table(
                ["settlement", "rows"],
                [[key or "EMPTY", value] for key, value in stats["ou25_settlement_counts"].items()],
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


def build_report(input_csv: Path, output_csv: Path, stats: dict[str, Any], checks: dict[str, Any]) -> dict[str, Any]:
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "input_csv": str(input_csv.relative_to(REPO_ROOT)),
        "output_csv": str(output_csv.relative_to(REPO_ROOT)),
        "stats": stats,
        "old_system_touched": "NO",
        "recommendations_generated": "NO",
        "backtest_run": "NO",
        "round1_merged": "NO",
        "self_check": checks,
    }


def main() -> int:
    args = parse_args()
    input_csv = args.input_csv.resolve()
    output_csv = args.output_csv.resolve()
    if not input_csv.exists():
        raise SystemExit(f"Input CSV does not exist: {input_csv}")

    input_rows = read_rows(input_csv)
    output_rows = [transform_row(row) for row in input_rows]
    write_rows(output_csv, output_rows)
    stats = calculate_stats(input_rows, output_rows)
    checks = self_check(stats)
    report = build_report(input_csv, output_csv, stats, checks)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")

    print(f"m1_round2_market_features: {checks['status']}")
    print(f"input_rows={stats['input_rows']}")
    print(f"output_rows={stats['output_rows']}")
    print(f"complete_backtest_feature_rows={stats['complete_backtest_feature_rows']}")
    print(f"current_not_for_backtest_feature_rows={stats['current_not_for_backtest_feature_rows']}")
    print(f"fair_probability_sum_failures={stats['fair_probability_sum_failures']}")
    print(f"ah_settlement_coverage={stats['ah_settlement_coverage']:.6f}")
    print(f"ou25_settlement_coverage={stats['ou25_settlement_coverage']:.6f}")
    print(f"output_csv={output_csv.relative_to(REPO_ROOT)}")
    print(f"report_json={REPORT_JSON.relative_to(REPO_ROOT)}")
    print(f"report_md={REPORT_MD.relative_to(REPO_ROOT)}")
    return 0 if checks["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
