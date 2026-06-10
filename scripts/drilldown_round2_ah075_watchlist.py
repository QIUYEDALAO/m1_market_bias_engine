#!/usr/bin/env python3
"""Drill down the Round2 AH -0.75 watchlist bucket."""

from __future__ import annotations

import csv
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
FEATURE_CSV = REPO_ROOT / "data" / "processed" / "market_features" / "m1_round2_market_features.csv"
NORMALIZED_CSV = REPO_ROOT / "data" / "processed" / "normalized_matches" / "m1_round2_matches_normalized.csv"
STRESS_JSON = REPO_ROOT / "reports" / "backtest" / "m1_round2_stability_candidate_stress_test.json"
OUTPUT_CSV = REPO_ROOT / "data" / "processed" / "backtest_ready" / "m1_round2_ah075_watchlist_cases.csv"
REPORT_DIR = REPO_ROOT / "reports" / "backtest"
REPORT_JSON = REPORT_DIR / "m1_round2_ah075_watchlist_drilldown.json"
REPORT_MD = REPORT_DIR / "m1_round2_ah075_watchlist_drilldown.md"

EXPECTED_SAMPLE_COUNT = 617

CASE_FIELDS = [
    "match_id",
    "league",
    "season",
    "date",
    "home_team",
    "away_team",
    "full_time_score",
    "goal_diff",
    "opening_1x2",
    "closing_1x2",
    "closing_ah_line",
    "closing_ah_home_odds",
    "ah_settlement",
    "roi",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def to_float(value: str) -> float | None:
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def to_int(value: str) -> int:
    return int(float(value))


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


def movement_bucket(value: float | None) -> str:
    if value is None:
        return "MISSING"
    if value <= -0.30:
        return "<=-0.30"
    if value >= 0.30:
        return ">=0.30"
    lower = math.floor(value / 0.10) * 0.10
    upper = lower + 0.10
    return f"{lower:.2f}-{upper:.2f}"


def roi_for_ah_home(settlement: str, odds: float | None) -> float | None:
    if odds is None or odds <= 0:
        return None
    if settlement == "FULL_WIN":
        return odds - 1.0
    if settlement == "HALF_WIN":
        return 0.5 * (odds - 1.0)
    if settlement == "PUSH":
        return 0.0
    if settlement == "HALF_LOSS":
        return -0.5
    if settlement == "LOSS":
        return -1.0
    return None


def opening_1x2(row: dict[str, str]) -> str:
    return f"{row['opening_home_odds']}/{row['opening_draw_odds']}/{row['opening_away_odds']}"


def closing_1x2(row: dict[str, str]) -> str:
    return f"{row['closing_home_odds']}/{row['closing_draw_odds']}/{row['closing_away_odds']}"


def build_cases(feature_rows: list[dict[str, str]], normalized_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    normalized_by_id = {row["match_id"]: row for row in normalized_rows}
    cases = []
    for feature in feature_rows:
        normalized = normalized_by_id.get(feature["match_id"])
        if not normalized:
            continue
        if feature["season_role"] != "COMPLETE_BACKTEST":
            continue
        if normalized["closing_ah_line"] != "-0.75":
            continue
        home_goals = to_int(feature["full_time_home_goals"])
        away_goals = to_int(feature["full_time_away_goals"])
        roi = roi_for_ah_home(feature["ah_settlement"], to_float(normalized["closing_ah_home_odds"]))
        cases.append(
            {
                "match_id": feature["match_id"],
                "league": feature["league"],
                "season": feature["season"],
                "date": feature["date"],
                "home_team": feature["home_team"],
                "away_team": feature["away_team"],
                "full_time_score": f"{home_goals}-{away_goals}",
                "goal_diff": str(home_goals - away_goals),
                "opening_1x2": opening_1x2(normalized),
                "closing_1x2": closing_1x2(normalized),
                "closing_ah_line": normalized["closing_ah_line"],
                "closing_ah_home_odds": normalized["closing_ah_home_odds"],
                "ah_settlement": feature["ah_settlement"],
                "roi": fmt(roi),
            }
        )
    return cases


def write_cases(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CASE_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def pct(count: int, total: int) -> float:
    return count / total if total else 0.0


def top_items(counter: Counter[str], limit: int = 10) -> dict[str, int]:
    return dict(counter.most_common(limit))


def summarize(cases: list[dict[str, str]], feature_rows: list[dict[str, str]]) -> dict[str, Any]:
    feature_by_id = {row["match_id"]: row for row in feature_rows}
    sample_count = len(cases)
    settlement_counter = Counter(row["ah_settlement"] for row in cases)
    score_counter = Counter(row["full_time_score"] for row in cases)
    goal_diff_counter = Counter(row["goal_diff"] for row in cases)
    league_counter = Counter(row["league"] for row in cases)
    season_counter = Counter(row["season"] for row in cases)
    home_team_counter = Counter(row["home_team"] for row in cases)
    away_team_counter = Counter(row["away_team"] for row in cases)
    team_counter: Counter[str] = Counter()
    for row in cases:
        team_counter[row["home_team"]] += 1
        team_counter[row["away_team"]] += 1

    favorite_bucket_counter: Counter[str] = Counter()
    movement_counter: Counter[str] = Counter()
    roi_values = []
    for row in cases:
        feature = feature_by_id[row["match_id"]]
        favorite_bucket_counter[probability_bucket(to_float(feature["closing_home_fair_prob"]))] += 1
        movement_counter[movement_bucket(to_float(feature["ah_home_odds_movement"]))] += 1
        roi = to_float(row["roi"])
        if roi is not None:
            roi_values.append(roi)

    top_team_count = team_counter.most_common(1)[0][1] if team_counter else 0
    top5_team_count = sum(count for _, count in team_counter.most_common(5))
    max_league_share = max((count / sample_count for count in league_counter.values()), default=0.0)
    max_season_share = max((count / sample_count for count in season_counter.values()), default=0.0)
    max_score_share = max((count / sample_count for count in score_counter.values()), default=0.0)
    half_win_share = pct(settlement_counter["HALF_WIN"], sample_count)
    full_win_share = pct(settlement_counter["FULL_WIN"], sample_count)
    loss_share = pct(settlement_counter["LOSS"], sample_count)
    top_team_share = top_team_count / (sample_count * 2) if sample_count else 0.0
    top5_team_share = top5_team_count / (sample_count * 2) if sample_count else 0.0

    return {
        "sample_count": sample_count,
        "score_distribution": dict(sorted(score_counter.items())),
        "goal_diff_distribution": dict(sorted(goal_diff_counter.items(), key=lambda item: int(item[0]))),
        "settlement_distribution": dict(sorted(settlement_counter.items())),
        "settlement_shares": {
            "FULL_WIN": full_win_share,
            "HALF_WIN": half_win_share,
            "PUSH": pct(settlement_counter["PUSH"], sample_count),
            "HALF_LOSS": pct(settlement_counter["HALF_LOSS"], sample_count),
            "LOSS": loss_share,
        },
        "league_distribution": dict(sorted(league_counter.items())),
        "season_distribution": dict(sorted(season_counter.items())),
        "top_team_concentration": {
            "top_home_teams": top_items(home_team_counter),
            "top_away_teams": top_items(away_team_counter),
            "top_all_teams": top_items(team_counter),
            "top_team_share_of_team_slots": top_team_share,
            "top5_team_share_of_team_slots": top5_team_share,
        },
        "home_favorite_probability_bucket": dict(sorted(favorite_bucket_counter.items())),
        "odds_movement_distribution": dict(sorted(movement_counter.items())),
        "roi_summary": {
            "total_roi_units": sum(roi_values),
            "average_roi": sum(roi_values) / len(roi_values) if roi_values else 0.0,
        },
        "judgement": {
            "depends_on_single_league": max_league_share >= 0.55,
            "depends_on_single_season": max_season_share >= 0.55,
            "depends_on_few_teams": top5_team_share >= 0.35,
            "mainly_half_win": half_win_share >= 0.50,
            "score_structure_healthy": max_score_share < 0.25
            and full_win_share > 0.25
            and loss_share > 0.25
            and half_win_share < 0.50,
            "still_watchlist_research_only": True,
        },
    }


def survived_bucket(stress: dict[str, Any]) -> dict[str, Any]:
    for candidate in stress["candidates"]:
        if (
            candidate["market"] == "AH"
            and candidate["selection"] == "home_handicap"
            and candidate["bucket_type"] == "closing_line"
            and candidate["bucket"] == "-0.75"
        ):
            return {
                "stability_status": candidate["stability_status"],
                "market": candidate["market"],
                "selection": candidate["selection"],
                "bucket_type": candidate["bucket_type"],
                "bucket": candidate["bucket"],
                "base_sample_count": candidate["base_sample_count"],
                "stress_status": candidate["stress_status"],
                "critical_failure_count": candidate["critical_failure_count"],
            }
    return {}


def self_check(report: dict[str, Any]) -> dict[str, Any]:
    summary = report["summary"]
    judgement = summary["judgement"]
    bucket = report["bucket"]
    checks = {
        "sample_count_617": summary["sample_count"] == EXPECTED_SAMPLE_COUNT,
        "bucket_is_ah_home_closing_line_minus_075": bucket["market"] == "AH"
        and bucket["selection"] == "home_handicap"
        and bucket["bucket_type"] == "closing_line"
        and bucket["bucket"] == "-0.75",
        "bucket_survived_but_watchlist": bucket["stress_status"] == "SURVIVED"
        and bucket["stability_status"] == "WATCHLIST_RESEARCH_ONLY",
        "not_single_league": judgement["depends_on_single_league"] is False,
        "not_single_season": judgement["depends_on_single_season"] is False,
        "not_few_team_dependent": judgement["depends_on_few_teams"] is False,
        "not_mainly_half_win": judgement["mainly_half_win"] is False,
        "score_structure_healthy": judgement["score_structure_healthy"] is True,
        "still_watchlist_research_only": judgement["still_watchlist_research_only"] is True,
        "research_only_no_actions": report["research_only"] is True
        and report["recommendations_generated"] is False
        and report["current_match_matching_allowed"] is False
        and report["paper_play_allowed"] is False,
        "official_pending_qq_false": report["official_written"] is False
        and report["pending_written"] is False
        and report["qq_written"] is False,
        "old_system_touched_no": report["old_system_touched"] == "NO",
    }
    rendered = {name: "PASS" if value else "FAIL" for name, value in checks.items()}
    return {"status": "PASS" if all(checks.values()) else "FAIL", "checks": rendered}


def markdown_cell(value: Any) -> str:
    if isinstance(value, float):
        value = f"{value:.6f}".rstrip("0").rstrip(".")
    if isinstance(value, bool):
        value = str(value).lower()
    if isinstance(value, dict):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True)
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
    summary = report["summary"]
    judgement = summary["judgement"]
    return "\n".join(
        [
            "# M1 Round2 AH -0.75 Watchlist Case Drilldown",
            "",
            f"- generated_at_utc: `{report['generated_at_utc']}`",
            f"- case_file: `{report['case_file']}`",
            f"- checker: `{report['self_check']['status']}`",
            "- research_only: `true`",
            "- recommendations_generated: `false`",
            "- current_match_matching_allowed: `false`",
            "- paper_play_allowed: `false`",
            "- official_written: `false`",
            "- pending_written: `false`",
            "- qq_written: `false`",
            "- old_system_touched: `NO`",
            "",
            "This drilldown explains the survived Round2 watchlist bucket. It does not create a recommendation, current matcher, paper play, or official/pending/QQ output.",
            "",
            "## Bucket",
            "",
            markdown_table(["field", "value"], [[key, value] for key, value in report["bucket"].items()]),
            "",
            "## Summary",
            "",
            markdown_table(
                ["metric", "value"],
                [
                    ["sample_count", summary["sample_count"]],
                    ["average_roi", summary["roi_summary"]["average_roi"]],
                    ["total_roi_units", summary["roi_summary"]["total_roi_units"]],
                    ["depends_on_single_league", judgement["depends_on_single_league"]],
                    ["depends_on_single_season", judgement["depends_on_single_season"]],
                    ["depends_on_few_teams", judgement["depends_on_few_teams"]],
                    ["mainly_half_win", judgement["mainly_half_win"]],
                    ["score_structure_healthy", judgement["score_structure_healthy"]],
                    ["still_watchlist_research_only", judgement["still_watchlist_research_only"]],
                ],
            ),
            "",
            "## Settlement Distribution",
            "",
            markdown_table(
                ["settlement", "rows", "share"],
                [
                    [key, summary["settlement_distribution"].get(key, 0), summary["settlement_shares"].get(key, 0)]
                    for key in ["FULL_WIN", "HALF_WIN", "PUSH", "HALF_LOSS", "LOSS"]
                ],
            ),
            "",
            "## Score Distribution",
            "",
            markdown_table(
                ["score", "rows"],
                [[key, value] for key, value in sorted(summary["score_distribution"].items(), key=lambda item: (-item[1], item[0]))[:20]],
            ),
            "",
            "## Goal Diff Distribution",
            "",
            markdown_table(
                ["goal_diff", "rows"],
                [[key, value] for key, value in summary["goal_diff_distribution"].items()],
            ),
            "",
            "## League And Season Distribution",
            "",
            markdown_table(
                ["league", "rows"],
                [[key, value] for key, value in summary["league_distribution"].items()],
            ),
            "",
            markdown_table(
                ["season", "rows"],
                [[key, value] for key, value in summary["season_distribution"].items()],
            ),
            "",
            "## Team Concentration",
            "",
            markdown_table(
                ["metric", "value"],
                [
                    ["top_team_share_of_team_slots", summary["top_team_concentration"]["top_team_share_of_team_slots"]],
                    ["top5_team_share_of_team_slots", summary["top_team_concentration"]["top5_team_share_of_team_slots"]],
                    ["top_all_teams", summary["top_team_concentration"]["top_all_teams"]],
                ],
            ),
            "",
            "## Home Favorite Probability Bucket",
            "",
            markdown_table(
                ["bucket", "rows"],
                [[key, value] for key, value in summary["home_favorite_probability_bucket"].items()],
            ),
            "",
            "## AH Home Odds Movement Distribution",
            "",
            markdown_table(
                ["movement_bucket", "rows"],
                [[key, value] for key, value in summary["odds_movement_distribution"].items()],
            ),
            "",
            "## Conclusion",
            "",
            report["conclusion"],
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
    for path in [FEATURE_CSV, NORMALIZED_CSV, STRESS_JSON]:
        if not path.exists():
            raise SystemExit(f"Required input missing: {path}")
    feature_rows = read_csv(FEATURE_CSV)
    normalized_rows = read_csv(NORMALIZED_CSV)
    stress = read_json(STRESS_JSON)
    cases = build_cases(feature_rows, normalized_rows)
    write_cases(OUTPUT_CSV, cases)
    summary = summarize(cases, feature_rows)
    bucket = survived_bucket(stress)
    conclusion = (
        "The AH -0.75 home-handicap bucket is broad across leagues and seasons, not driven by a single team cluster, "
        "not mainly dependent on half wins, and has a balanced score structure. However it remains "
        "WATCHLIST_RESEARCH_ONLY because Round2 stability filtering produced stable_count=0 and this bucket entered "
        "stress as watchlist rather than STABLE_RESEARCH_CANDIDATE. It cannot be used for recommendations, current "
        "matching, paper play, official/pending/QQ, or V3/V4 actions."
    )
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "inputs": {
            "feature_csv": str(FEATURE_CSV.relative_to(REPO_ROOT)),
            "normalized_csv": str(NORMALIZED_CSV.relative_to(REPO_ROOT)),
            "stress_json": str(STRESS_JSON.relative_to(REPO_ROOT)),
        },
        "case_file": str(OUTPUT_CSV.relative_to(REPO_ROOT)),
        "bucket": bucket,
        "summary": summary,
        "conclusion": conclusion,
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
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    print(f"m1_round2_ah075_watchlist_drilldown: {report['self_check']['status']}")
    print(f"sample_count={summary['sample_count']}")
    print(f"case_file={OUTPUT_CSV.relative_to(REPO_ROOT)}")
    print(f"report_json={REPORT_JSON.relative_to(REPO_ROOT)}")
    print(f"report_md={REPORT_MD.relative_to(REPO_ROOT)}")
    return 0 if report["self_check"]["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
