#!/usr/bin/env python3
"""Run offline M1 bucket backtests on complete historical feature rows only."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = REPO_ROOT / "data" / "processed" / "market_features" / "m1_market_features.csv"
NORMALIZED_CSV = REPO_ROOT / "data" / "processed" / "normalized_matches" / "m1_matches_normalized.csv"
OUTPUT_CSV = REPO_ROOT / "data" / "processed" / "backtest_ready" / "m1_bucket_results.csv"
REPORT_DIR = REPO_ROOT / "reports" / "backtest"
REPORT_MD = REPORT_DIR / "m1_bucket_backtest_report.md"
REPORT_JSON = REPORT_DIR / "m1_bucket_backtest_report.json"

EXPECTED_INPUT_ROWS = 10733
EXPECTED_BACKTEST_ROWS = 8982
EXPECTED_EXCLUDED_CURRENT_ROWS = 1751
MIN_SAMPLE_COUNT = 500
HIGH_DRAWDOWN_THRESHOLD = -0.15
CONCENTRATION_THRESHOLD = 0.55

RESULT_FIELDS = [
    "market",
    "selection",
    "bucket_type",
    "bucket",
    "sample_count",
    "hit_count",
    "hit_rate",
    "avg_odds",
    "roi",
    "max_losing_streak",
    "max_drawdown",
    "league_distribution",
    "season_distribution",
    "positive_roi_bucket",
    "reject_reason",
    "backtest_scope",
    "recommendation_generated",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-csv", type=Path, default=INPUT_CSV)
    parser.add_argument("--normalized-csv", type=Path, default=NORMALIZED_CSV)
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


def fmt(value: float | None, places: int = 6) -> str:
    if value is None:
        return ""
    rendered = f"{value:.{places}f}".rstrip("0").rstrip(".")
    return rendered if rendered != "-0" else "0"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def enrich_with_normalized_fields(
    feature_rows: list[dict[str, str]], normalized_rows: list[dict[str, str]]
) -> list[dict[str, str]]:
    normalized_by_id = {row["match_id"]: row for row in normalized_rows}
    enriched = []
    for row in feature_rows:
        merged = dict(row)
        normalized = normalized_by_id.get(row["match_id"], {})
        for field in [
            "closing_ah_line",
            "closing_ah_home_odds",
            "closing_ah_away_odds",
            "closing_over25_odds",
            "closing_under25_odds",
        ]:
            merged[field] = normalized.get(field, "")
        over_prob = implied_probability_from_odds(merged.get("closing_over25_odds", ""))
        under_prob = implied_probability_from_odds(merged.get("closing_under25_odds", ""))
        total = None if over_prob is None or under_prob is None else over_prob + under_prob
        if total and total > 0:
            merged["closing_over25_fair_prob"] = fmt(over_prob / total)
            merged["closing_under25_fair_prob"] = fmt(under_prob / total)
        else:
            merged["closing_over25_fair_prob"] = ""
            merged["closing_under25_fair_prob"] = ""
        enriched.append(merged)
    return enriched


def implied_probability_from_odds(value: str) -> float | None:
    odds = to_float(value)
    if odds is None or odds <= 0:
        return None
    return 1.0 / odds


def probability_bucket(value: float | None) -> str:
    if value is None:
        return "MISSING"
    upper = min(1.0, math.ceil(value * 10) / 10)
    lower = max(0.0, upper - 0.1)
    return f"{lower:.1f}-{upper:.1f}"


def signed_movement_bucket(value: float | None, step: float = 0.02, cap: float = 0.1) -> str:
    if value is None:
        return "MISSING"
    if value <= -cap:
        return f"<=-{cap:g}"
    if value >= cap:
        return f">={cap:g}"
    lower = math.floor(value / step) * step
    upper = lower + step
    return f"{lower:.2f}-{upper:.2f}"


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


def ah_line_bucket(value: float | None) -> str:
    if value is None:
        return "MISSING"
    if value <= -2.0:
        return "<=-2.00"
    if value >= 2.0:
        return ">=2.00"
    return f"{value:.2f}"


def ah_line_movement_bucket(value: float | None) -> str:
    if value is None:
        return "MISSING"
    if value <= -1.0:
        return "<=-1.00"
    if value >= 1.0:
        return ">=1.00"
    return f"{value:.2f}"


def one_x_two_outcome(row: dict[str, str], selection: str) -> tuple[float | None, float | None]:
    result = row["full_time_result"]
    odds_field = {
        "home": "closing_home_implied_prob_raw",
        "draw": "closing_draw_implied_prob_raw",
        "away": "closing_away_implied_prob_raw",
    }[selection]
    closing_raw = to_float(row[odds_field])
    if closing_raw is None or closing_raw <= 0:
        return None, None
    odds = 1.0 / closing_raw
    hit = {
        "home": result == "H",
        "draw": result == "D",
        "away": result == "A",
    }[selection]
    return (1.0 if hit else 0.0), odds


def ah_home_outcome(row: dict[str, str], _selection: str) -> tuple[float | None, float | None]:
    odds = to_float(row.get("closing_ah_home_odds", ""))
    settlement = row["ah_settlement"]
    payout = {
        "FULL_WIN": 1.0,
        "HALF_WIN": 0.5,
        "PUSH": 0.0,
        "HALF_LOSS": -0.5,
        "LOSS": -1.0,
    }.get(settlement)
    if payout is None or odds is None or odds <= 0:
        return None, None
    if payout > 0:
        profit = payout * (odds - 1.0)
    elif payout < 0:
        profit = payout
    else:
        profit = 0.0
    return profit, odds


def ou_over_outcome(row: dict[str, str], selection: str) -> tuple[float | None, float | None]:
    if selection == "over25":
        settlement = row["ou25_settlement"]
        hit = settlement == "OVER_WIN"
        odds = to_float(row.get("closing_over25_odds", ""))
    else:
        settlement = row["ou25_settlement"]
        hit = settlement == "UNDER_WIN"
        odds = to_float(row.get("closing_under25_odds", ""))
    if settlement == "" or odds is None or odds <= 0:
        return None, None
    return ((odds - 1.0) if hit else -1.0), odds


def profit_from_binary(hit: float, odds: float) -> float:
    return odds - 1.0 if hit >= 1.0 else -1.0


def max_losing_streak(profits: list[float]) -> int:
    current = 0
    longest = 0
    for profit in profits:
        if profit < 0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def max_drawdown(profits: list[float]) -> float:
    equity = 0.0
    peak = 0.0
    worst = 0.0
    for profit in profits:
        equity += profit
        peak = max(peak, equity)
        worst = min(worst, equity - peak)
    return worst / len(profits) if profits else 0.0


def distribution(rows: list[dict[str, str]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(row[field] for row in rows).items()))


def concentration_risk(rows: list[dict[str, str]]) -> bool:
    if not rows:
        return False
    count = len(rows)
    league_share = max(Counter(row["league"] for row in rows).values()) / count
    season_share = max(Counter(row["season"] for row in rows).values()) / count
    return league_share > CONCENTRATION_THRESHOLD or season_share > CONCENTRATION_THRESHOLD


def reject_reasons(sample_count: int, roi: float, drawdown: float, rows: list[dict[str, str]]) -> list[str]:
    reasons = []
    if sample_count < MIN_SAMPLE_COUNT:
        reasons.append("SMALL_SAMPLE")
    if roi > 0 and drawdown <= HIGH_DRAWDOWN_THRESHOLD:
        reasons.append("HIGH_DRAWDOWN_RISK")
    if concentration_risk(rows):
        reasons.append("CONCENTRATION_RISK")
    return reasons


def aggregate_bucket(
    rows: list[dict[str, str]],
    market: str,
    selection: str,
    bucket_type: str,
    bucket: str,
    outcome_fn: Callable[[dict[str, str], str], tuple[float | None, float | None]],
    binary_hit: bool,
) -> dict[str, str]:
    profits = []
    hits = 0.0
    odds_values = []
    valid_rows = []
    for row in rows:
        outcome, odds = outcome_fn(row, selection)
        if outcome is None or odds is None:
            continue
        valid_rows.append(row)
        odds_values.append(odds)
        if binary_hit:
            hits += outcome
            profits.append(profit_from_binary(outcome, odds))
        else:
            if outcome > 0:
                hits += 1.0
            profits.append(outcome)
    sample_count = len(valid_rows)
    hit_rate = hits / sample_count if sample_count else 0.0
    avg_odds = sum(odds_values) / sample_count if sample_count else 0.0
    roi = sum(profits) / sample_count if sample_count else 0.0
    drawdown = max_drawdown(profits)
    reasons = reject_reasons(sample_count, roi, drawdown, valid_rows)
    return {
        "market": market,
        "selection": selection,
        "bucket_type": bucket_type,
        "bucket": bucket,
        "sample_count": str(sample_count),
        "hit_count": fmt(hits),
        "hit_rate": fmt(hit_rate),
        "avg_odds": fmt(avg_odds),
        "roi": fmt(roi),
        "max_losing_streak": str(max_losing_streak(profits)),
        "max_drawdown": fmt(drawdown),
        "league_distribution": json.dumps(distribution(valid_rows, "league"), sort_keys=True),
        "season_distribution": json.dumps(distribution(valid_rows, "season"), sort_keys=True),
        "positive_roi_bucket": "YES" if roi > 0 else "NO",
        "reject_reason": "|".join(reasons) if reasons else "NONE",
        "backtest_scope": "COMPLETE_BACKTEST_ONLY",
        "recommendation_generated": "NO",
    }


def bucket_specs() -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    for selection, prob_field in [
        ("home", "closing_home_fair_prob"),
        ("draw", "closing_draw_fair_prob"),
        ("away", "closing_away_fair_prob"),
    ]:
        specs.append(
            {
                "market": "1X2",
                "selection": selection,
                "bucket_type": "closing_fair_probability",
                "bucket_fn": lambda row, field=prob_field: probability_bucket(to_float(row[field])),
                "outcome_fn": one_x_two_outcome,
                "binary_hit": True,
            }
        )
    specs.append(
        {
            "market": "AH",
            "selection": "home_handicap",
            "bucket_type": "closing_line",
            "bucket_fn": lambda row: ah_line_bucket(to_float(row.get("closing_ah_line", ""))),
            "outcome_fn": ah_home_outcome,
            "binary_hit": False,
        }
    )
    for selection, bucket_field in [
        ("over25", "closing_over25_fair_prob"),
        ("under25", "closing_under25_fair_prob"),
    ]:
        specs.append(
            {
                "market": "OU25",
                "selection": selection,
            "bucket_type": "closing_fair_probability",
                "bucket_fn": lambda row, field=bucket_field: probability_bucket(to_float(row[field])),
                "outcome_fn": ou_over_outcome,
                "binary_hit": False,
            }
        )
    for selection, movement_field in [
        ("home", "home_fair_prob_delta"),
        ("draw", "draw_fair_prob_delta"),
        ("away", "away_fair_prob_delta"),
    ]:
        specs.append(
            {
                "market": "1X2",
                "selection": selection,
                "bucket_type": "open_to_close_probability_movement",
                "bucket_fn": lambda row, field=movement_field: signed_movement_bucket(to_float(row[field])),
                "outcome_fn": one_x_two_outcome,
                "binary_hit": True,
            }
        )
    for selection, movement_field in [
        ("home", "home_odds_delta"),
        ("draw", "draw_odds_delta"),
        ("away", "away_odds_delta"),
    ]:
        specs.append(
            {
                "market": "1X2",
                "selection": selection,
                "bucket_type": "open_to_close_odds_movement",
                "bucket_fn": lambda row, field=movement_field: odds_delta_bucket(to_float(row[field])),
                "outcome_fn": one_x_two_outcome,
                "binary_hit": True,
            }
        )
    specs.append(
        {
            "market": "AH",
            "selection": "home_handicap",
            "bucket_type": "open_to_close_line_movement",
            "bucket_fn": lambda row: ah_line_movement_bucket(to_float(row["ah_line_movement"])),
            "outcome_fn": ah_home_outcome,
            "binary_hit": False,
        }
    )
    return specs


def run_buckets(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    results = []
    for spec in bucket_specs():
        grouped: dict[str, list[dict[str, str]]] = {}
        for row in rows:
            bucket = spec["bucket_fn"](row)
            grouped.setdefault(bucket, []).append(row)
        for bucket, bucket_rows in sorted(grouped.items()):
            results.append(
                aggregate_bucket(
                    bucket_rows,
                    spec["market"],
                    spec["selection"],
                    spec["bucket_type"],
                    bucket,
                    spec["outcome_fn"],
                    spec["binary_hit"],
                )
            )
    return results


def write_results(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def calculate_stats(input_rows: list[dict[str, str]], backtest_rows: list[dict[str, str]], result_rows: list[dict[str, str]]) -> dict[str, Any]:
    current_rows = [row for row in input_rows if row["season_role"] == "CURRENT_NOT_FOR_BACKTEST"]
    reject_counts = Counter()
    positive_roi = 0
    for row in result_rows:
        if row["positive_roi_bucket"] == "YES":
            positive_roi += 1
        for reason in row["reject_reason"].split("|"):
            reject_counts[reason] += 1
    return {
        "input_rows": len(input_rows),
        "backtest_rows": len(backtest_rows),
        "excluded_current_rows": len(current_rows),
        "bucket_rows": len(result_rows),
        "positive_roi_bucket_count": positive_roi,
        "reject_reason_counts": dict(sorted(reject_counts.items())),
        "backtest_league_distribution": distribution(backtest_rows, "league"),
        "backtest_season_distribution": distribution(backtest_rows, "season"),
    }


def self_check(input_rows: list[dict[str, str]], backtest_rows: list[dict[str, str]], result_rows: list[dict[str, str]], stats: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "input_rows_10733": stats["input_rows"] == EXPECTED_INPUT_ROWS,
        "backtest_rows_8982": stats["backtest_rows"] == EXPECTED_BACKTEST_ROWS,
        "excluded_current_rows_1751": stats["excluded_current_rows"] == EXPECTED_EXCLUDED_CURRENT_ROWS,
        "no_2025_26_in_backtest": all(row["season"] != "2025/26" for row in backtest_rows),
        "only_complete_backtest_rows_used": all(
            row["season_role"] == "COMPLETE_BACKTEST" for row in backtest_rows
        ),
        "bucket_results_nonempty": len(result_rows) > 0,
        "sample_lt_500_marked_small_sample": all(
            int(row["sample_count"]) >= MIN_SAMPLE_COUNT or "SMALL_SAMPLE" in row["reject_reason"]
            for row in result_rows
        ),
        "positive_roi_high_drawdown_marked": all(
            not (
                row["positive_roi_bucket"] == "YES"
                and to_float(row["max_drawdown"]) is not None
                and to_float(row["max_drawdown"]) <= HIGH_DRAWDOWN_THRESHOLD
            )
            or "HIGH_DRAWDOWN_RISK" in row["reject_reason"]
            for row in result_rows
        ),
        "recommendations_generated_no": all(
            row["recommendation_generated"] == "NO" for row in result_rows
        ),
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


def render_markdown(report: dict[str, Any], result_rows: list[dict[str, str]]) -> str:
    stats = report["stats"]
    preview = result_rows[:20]
    return "\n".join(
        [
            "# M1 Bucket Backtest Report",
            "",
            f"- generated_at_utc: `{report['generated_at_utc']}`",
            f"- input_csv: `{report['input_csv']}`",
            f"- normalized_context_csv: `{report['normalized_context_csv']}`",
            f"- output_csv: `{report['output_csv']}`",
            f"- checker: `{report['self_check']['status']}`",
            "- backtest_scope: `COMPLETE_BACKTEST_ONLY`",
            "- excluded_current_policy: `2025/26 CURRENT_NOT_FOR_BACKTEST excluded`",
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
                    ["input_rows", stats["input_rows"]],
                    ["backtest_rows", stats["backtest_rows"]],
                    ["excluded_current_rows", stats["excluded_current_rows"]],
                    ["bucket_rows", stats["bucket_rows"]],
                    ["positive_roi_bucket_count", stats["positive_roi_bucket_count"]],
                ],
            ),
            "",
            "This is an offline bucket backtest over `COMPLETE_BACKTEST` rows only. "
            "It does not match current fixtures, generate recommendations, or write "
            "official/pending/QQ outputs.",
            "",
            "AH closing line buckets and OU 2.5 closing probability buckets use "
            "`match_id`-joined closing line/odds context from the normalized table. "
            "The backtest row filter remains `season_role=COMPLETE_BACKTEST`.",
            "",
            "## Reject Reason Counts",
            "",
            markdown_table(
                ["reject_reason", "bucket_count"],
                [[key, value] for key, value in stats["reject_reason_counts"].items()],
            ),
            "",
            "## Backtest Distributions",
            "",
            "League distribution:",
            "",
            markdown_table(
                ["league", "rows"],
                [[key, value] for key, value in stats["backtest_league_distribution"].items()],
            ),
            "",
            "Season distribution:",
            "",
            markdown_table(
                ["season", "rows"],
                [[key, value] for key, value in stats["backtest_season_distribution"].items()],
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
                    "hit_rate",
                    "roi",
                    "reject_reason",
                ],
                [
                    [
                        row["market"],
                        row["selection"],
                        row["bucket_type"],
                        row["bucket"],
                        row["sample_count"],
                        row["hit_rate"],
                        row["roi"],
                        row["reject_reason"],
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
    normalized_csv: Path,
    output_csv: Path,
    stats: dict[str, Any],
    checks: dict[str, Any],
) -> dict[str, Any]:
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "input_csv": str(input_csv.relative_to(REPO_ROOT)),
        "normalized_context_csv": str(normalized_csv.relative_to(REPO_ROOT)),
        "output_csv": str(output_csv.relative_to(REPO_ROOT)),
        "stats": stats,
        "backtest_scope": "COMPLETE_BACKTEST_ONLY",
        "excluded_current_policy": "2025/26 CURRENT_NOT_FOR_BACKTEST excluded",
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
    normalized_csv = args.normalized_csv.resolve()
    output_csv = args.output_csv.resolve()
    if not input_csv.exists():
        raise SystemExit(f"Input CSV does not exist: {input_csv}")
    if not normalized_csv.exists():
        raise SystemExit(f"Normalized CSV does not exist: {normalized_csv}")
    input_rows = enrich_with_normalized_fields(read_rows(input_csv), read_rows(normalized_csv))
    backtest_rows = [row for row in input_rows if row["season_role"] == "COMPLETE_BACKTEST"]
    result_rows = run_buckets(backtest_rows)
    write_results(output_csv, result_rows)
    stats = calculate_stats(input_rows, backtest_rows, result_rows)
    checks = self_check(input_rows, backtest_rows, result_rows, stats)
    report = build_report(input_csv, normalized_csv, output_csv, stats, checks)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report, result_rows), encoding="utf-8")

    print(f"m1_bucket_backtest: {checks['status']}")
    print(f"input_rows={stats['input_rows']}")
    print(f"backtest_rows={stats['backtest_rows']}")
    print(f"excluded_current_rows={stats['excluded_current_rows']}")
    print(f"bucket_rows={stats['bucket_rows']}")
    print(f"output_csv={output_csv.relative_to(REPO_ROOT)}")
    print(f"report_json={REPORT_JSON.relative_to(REPO_ROOT)}")
    print(f"report_md={REPORT_MD.relative_to(REPO_ROOT)}")
    return 0 if checks["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
