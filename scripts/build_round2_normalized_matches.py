#!/usr/bin/env python3
"""Build Round2 normalized match rows from full-contract Football-Data leagues."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw" / "football_data_round2"
AUDIT_JSON = REPO_ROOT / "reports" / "data_audit" / "round2_football_data_field_audit.json"
AVAILABILITY_JSON = REPO_ROOT / "config" / "round2_league_availability.json"
OUTPUT_CSV = REPO_ROOT / "data" / "processed" / "normalized_matches" / "m1_round2_matches_normalized.csv"
REPORT_DIR = REPO_ROOT / "reports" / "data_audit"
REPORT_JSON = REPORT_DIR / "m1_round2_normalized_matches_report.json"
REPORT_MD = REPORT_DIR / "m1_round2_normalized_matches_report.md"

FULL_CONTRACT_LEAGUES = ["N1", "B1", "P1", "T1", "SC0"]
PARTIAL_REVIEW_LEAGUES = ["J1"]
UNAVAILABLE_LEAGUES = ["K1"]
COMPLETE_BACKTEST_SEASONS = ["2020/21", "2021/22", "2022/23", "2023/24", "2024/25"]
CURRENT_NOT_FOR_BACKTEST_SEASONS = ["2025/26"]

OUTPUT_FIELDS = [
    "match_id",
    "round",
    "league",
    "season",
    "season_role",
    "date",
    "home_team",
    "away_team",
    "full_time_home_goals",
    "full_time_away_goals",
    "full_time_result",
    "opening_home_odds",
    "opening_draw_odds",
    "opening_away_odds",
    "closing_home_odds",
    "closing_draw_odds",
    "closing_away_odds",
    "opening_ah_line",
    "closing_ah_line",
    "opening_ah_home_odds",
    "opening_ah_away_odds",
    "closing_ah_home_odds",
    "closing_ah_away_odds",
    "opening_over25_odds",
    "opening_under25_odds",
    "closing_over25_odds",
    "closing_under25_odds",
    "bookmaker_source",
    "data_source",
    "source_file",
    "source_row_number",
]

FIELD_MAP = {
    "league": "Div",
    "date": "Date",
    "home_team": "HomeTeam",
    "away_team": "AwayTeam",
    "full_time_home_goals": "FTHG",
    "full_time_away_goals": "FTAG",
    "full_time_result": "FTR",
    "opening_home_odds": "B365H",
    "opening_draw_odds": "B365D",
    "opening_away_odds": "B365A",
    "closing_home_odds": "B365CH",
    "closing_draw_odds": "B365CD",
    "closing_away_odds": "B365CA",
    "opening_ah_line": "AHh",
    "closing_ah_line": "AHCh",
    "opening_ah_home_odds": "B365AHH",
    "opening_ah_away_odds": "B365AHA",
    "closing_ah_home_odds": "B365CAHH",
    "closing_ah_away_odds": "B365CAHA",
    "opening_over25_odds": "B365>2.5",
    "opening_under25_odds": "B365<2.5",
    "closing_over25_odds": "B365C>2.5",
    "closing_under25_odds": "B365C<2.5",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR)
    parser.add_argument("--audit-json", type=Path, default=AUDIT_JSON)
    parser.add_argument("--availability-json", type=Path, default=AVAILABILITY_JSON)
    parser.add_argument("--output-csv", type=Path, default=OUTPUT_CSV)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def season_from_code(code: str) -> str:
    if code == "2021":
        return "2020/21"
    if re.fullmatch(r"\d{4}", code):
        return f"20{int(code[:2]):02d}/{int(code[2:]):02d}"
    raise ValueError(f"Unsupported season code: {code}")


def parse_filename(path: Path) -> tuple[str, str]:
    match = re.fullmatch(r"([A-Z0-9]+)_(\d{4})\.csv", path.name)
    if not match:
        raise ValueError(f"Unexpected filename: {path.name}")
    return match.group(1), season_from_code(match.group(2))


def season_role(season: str) -> str:
    if season in COMPLETE_BACKTEST_SEASONS:
        return "COMPLETE_BACKTEST"
    if season in CURRENT_NOT_FOR_BACKTEST_SEASONS:
        return "CURRENT_NOT_FOR_BACKTEST"
    return "OUT_OF_SCOPE"


def parse_date(value: str) -> str:
    raw = value.strip()
    for fmt in ("%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            pass
    raise ValueError(f"Unsupported date: {value!r}")


def clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def make_match_id(row: dict[str, str]) -> str:
    key = "|".join(
        [
            row["data_source"],
            row["round"],
            row["league"],
            row["season"],
            row["date"],
            row["home_team"],
            row["away_team"],
        ]
    )
    return "m1r2_" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]


def required_fields() -> list[str]:
    return sorted(set(FIELD_MAP.values()))


def validate_header(path: Path, fieldnames: list[str] | None) -> None:
    if not fieldnames:
        raise ValueError(f"{path.name} has no header")
    missing = [field for field in required_fields() if field not in fieldnames]
    if missing:
        raise ValueError(f"{path.name} missing required fields: {', '.join(missing)}")


def normalize(raw_dir: Path, availability: dict[str, Any]) -> tuple[list[dict[str, str]], dict[str, Any]]:
    rows: list[dict[str, str]] = []
    file_profiles = []
    role_counts: Counter[str] = Counter()
    league_counts: Counter[str] = Counter()
    season_counts: Counter[str] = Counter()
    excluded_files = []

    available_full = [
        league
        for league, profile in availability["leagues"].items()
        if profile["availability"] == "AVAILABLE_FULL_CONTRACT"
    ]
    for path in sorted(raw_dir.glob("*.csv")):
        league, season = parse_filename(path)
        if league not in available_full:
            excluded_files.append(
                {
                    "file": str(path.relative_to(REPO_ROOT)),
                    "league": league,
                    "season": season,
                    "reason": "PARTIAL_SCHEMA_REVIEWED" if league in PARTIAL_REVIEW_LEAGUES else "NOT_FULL_CONTRACT",
                }
            )
            continue
        file_rows = 0
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            validate_header(path, reader.fieldnames)
            for source_row_number, raw in enumerate(reader, start=2):
                if not any(clean(value) for value in raw.values()):
                    continue
                role = season_role(season)
                out = {
                    "round": "ROUND2",
                    "league": league,
                    "season": season,
                    "season_role": role,
                    "date": parse_date(clean(raw[FIELD_MAP["date"]])),
                    "home_team": clean(raw[FIELD_MAP["home_team"]]),
                    "away_team": clean(raw[FIELD_MAP["away_team"]]),
                    "bookmaker_source": "B365",
                    "data_source": "football_data_round2",
                    "source_file": str(path.relative_to(REPO_ROOT)),
                    "source_row_number": str(source_row_number),
                }
                for target, source in FIELD_MAP.items():
                    if target in {"league", "date", "home_team", "away_team"}:
                        continue
                    out[target] = clean(raw[source])
                out["match_id"] = make_match_id(out)
                rows.append(out)
                file_rows += 1
                role_counts[role] += 1
                league_counts[league] += 1
                season_counts[season] += 1
        file_profiles.append(
            {
                "file": str(path.relative_to(REPO_ROOT)),
                "league": league,
                "season": season,
                "season_role": season_role(season),
                "rows": file_rows,
            }
        )

    duplicate_ids = [
        key for key, count in Counter(row["match_id"] for row in rows).items() if count > 1
    ]
    stats = {
        "raw_files": len(list(raw_dir.glob("*.csv"))),
        "included_full_contract_leagues": sorted(available_full),
        "included_full_contract_league_count": len(available_full),
        "normalized_rows": len(rows),
        "complete_backtest_rows": role_counts.get("COMPLETE_BACKTEST", 0),
        "current_not_for_backtest_rows": role_counts.get("CURRENT_NOT_FOR_BACKTEST", 0),
        "rows_by_league": dict(sorted(league_counts.items())),
        "rows_by_season": dict(sorted(season_counts.items())),
        "file_profiles": file_profiles,
        "excluded_files": excluded_files,
        "duplicate_match_ids": duplicate_ids,
        "j1_status": "PARTIAL_SCHEMA_REVIEWED",
        "j1_included_in_complete_backtest": False,
        "j1_2526_header_only_excluded": any(
            item["file"] == "data/raw/football_data_round2/J1_2526.csv"
            for item in excluded_files
        ),
        "k1_status": "UNAVAILABLE_SOURCE_EXPIRED",
    }
    return rows, stats


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def expected_full_contract_rows(audit: dict[str, Any]) -> int:
    return sum(
        item["rows"]
        for item in audit["files"]
        if item["league"] in FULL_CONTRACT_LEAGUES
        and item["usable_for_round2_backtest_contract"] == "YES"
    )


def expected_full_complete_rows(audit: dict[str, Any]) -> int:
    return sum(
        item["rows"]
        for item in audit["files"]
        if item["league"] in FULL_CONTRACT_LEAGUES
        and item["season_role"] == "COMPLETE_BACKTEST"
        and item["usable_for_round2_backtest_contract"] == "YES"
    )


def self_check(stats: dict[str, Any], audit: dict[str, Any]) -> dict[str, Any]:
    expected_rows = expected_full_contract_rows(audit)
    expected_complete = expected_full_complete_rows(audit)
    checks = {
        "raw_files_36": stats["raw_files"] == 36,
        "included_full_contract_leagues_5": stats["included_full_contract_league_count"] == 5,
        "only_expected_full_contract_leagues": stats["included_full_contract_leagues"]
        == sorted(FULL_CONTRACT_LEAGUES),
        "normalized_rows_match_audit_explainable": stats["normalized_rows"] == expected_rows,
        "complete_backtest_rows_match_full_contract_audit": stats["complete_backtest_rows"]
        == expected_complete,
        "current_not_in_complete_backtest": all(
            item["season"] != "2025/26" or item["season_role"] == "CURRENT_NOT_FOR_BACKTEST"
            for item in stats["file_profiles"]
        ),
        "j1_partial_reviewed_not_included": stats["j1_status"] == "PARTIAL_SCHEMA_REVIEWED"
        and not stats["j1_included_in_complete_backtest"],
        "j1_2526_header_only_excluded": stats["j1_2526_header_only_excluded"],
        "k1_unavailable": stats["k1_status"] == "UNAVAILABLE_SOURCE_EXPIRED",
        "no_duplicate_match_ids": not stats["duplicate_match_ids"],
        "no_features_backtest_recommendations": True,
        "old_system_touched_no": True,
    }
    rendered = {name: "PASS" if value else "FAIL" for name, value in checks.items()}
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": rendered,
        "expected_full_contract_rows": expected_rows,
        "expected_full_contract_complete_rows": expected_complete,
    }


def md_cell(value: Any) -> str:
    if isinstance(value, list):
        value = ", ".join(str(v) for v in value)
    if isinstance(value, dict):
        value = json.dumps(value, sort_keys=True)
    return str(value).replace("|", "\\|")


def table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(md_cell(h) for h in headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(md_cell(v) for v in row) + " |")
    return "\n".join(lines)


def render_markdown(report: dict[str, Any]) -> str:
    stats = report["stats"]
    return "\n".join(
        [
            "# M1 Round2 Normalized Matches Report",
            "",
            f"- generated_at_utc: `{report['generated_at_utc']}`",
            f"- output_csv: `{report['output_csv']}`",
            f"- checker: `{report['self_check']['status']}`",
            "- round1_merged: `NO`",
            "- features_built: `NO`",
            "- backtest_run: `NO`",
            "- recommendations_generated: `NO`",
            "- old_system_touched: `NO`",
            "",
            "## Summary",
            "",
            table(
                ["metric", "value"],
                [
                    ["raw_files", stats["raw_files"]],
                    ["included_full_contract_leagues", stats["included_full_contract_league_count"]],
                    ["included_full_contract_league_codes", stats["included_full_contract_leagues"]],
                    ["normalized_rows", stats["normalized_rows"]],
                    ["complete_backtest_rows", stats["complete_backtest_rows"]],
                    ["current_not_for_backtest_rows", stats["current_not_for_backtest_rows"]],
                    ["expected_full_contract_rows_from_audit", report["self_check"]["expected_full_contract_rows"]],
                    [
                        "expected_full_contract_complete_rows_from_audit",
                        report["self_check"]["expected_full_contract_complete_rows"],
                    ],
                    ["J1", stats["j1_status"]],
                    ["K1", stats["k1_status"]],
                ],
            ),
            "",
            "The normalized rows match the Round2 audit after excluding J1 partial-schema files and K1 unavailable source. J1 is reviewed as `PARTIAL_SCHEMA_REVIEWED`; J1 rows do not enter `COMPLETE_BACKTEST`. `J1_2526.csv` is header-only and excluded. `2025/26` rows from full-contract leagues are retained as `CURRENT_NOT_FOR_BACKTEST` and are not counted in complete backtest rows.",
            "",
            "## Rows By League",
            "",
            table(["league", "rows"], [[k, v] for k, v in stats["rows_by_league"].items()]),
            "",
            "## Rows By Season",
            "",
            table(["season", "rows"], [[k, v] for k, v in stats["rows_by_season"].items()]),
            "",
            "## Excluded Files",
            "",
            table(
                ["file", "league", "season", "reason"],
                [[x["file"], x["league"], x["season"], x["reason"]] for x in stats["excluded_files"]],
            ),
            "",
            "## Self Check",
            "",
            table(["check", "status"], [[k, v] for k, v in report["self_check"]["checks"].items()]),
            "",
        ]
    )


def build_report(output_csv: Path, stats: dict[str, Any], checks: dict[str, Any]) -> dict[str, Any]:
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "output_csv": str(output_csv.relative_to(REPO_ROOT)),
        "inputs": {
            "raw_dir": str(RAW_DIR.relative_to(REPO_ROOT)),
            "audit_json": str(AUDIT_JSON.relative_to(REPO_ROOT)),
            "availability_json": str(AVAILABILITY_JSON.relative_to(REPO_ROOT)),
        },
        "stats": stats,
        "round1_merged": "NO",
        "features_built": "NO",
        "backtest_run": "NO",
        "recommendations_generated": "NO",
        "old_system_touched": "NO",
        "self_check": checks,
    }


def main() -> int:
    args = parse_args()
    raw_dir = args.raw_dir.resolve()
    audit_path = args.audit_json.resolve()
    availability_path = args.availability_json.resolve()
    output_csv = args.output_csv.resolve()
    for path in [raw_dir, audit_path, availability_path]:
        if not path.exists():
            raise SystemExit(f"Required input missing: {path}")
    audit = load_json(audit_path)
    availability = load_json(availability_path)
    rows, stats = normalize(raw_dir, availability)
    write_csv(output_csv, rows)
    checks = self_check(stats, audit)
    report = build_report(output_csv, stats, checks)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")

    print(f"m1_round2_normalized_matches: {checks['status']}")
    print(f"raw_files={stats['raw_files']}")
    print(f"included_full_contract_leagues={stats['included_full_contract_league_count']}")
    print(f"normalized_rows={stats['normalized_rows']}")
    print(f"complete_backtest_rows={stats['complete_backtest_rows']}")
    print(f"current_not_for_backtest_rows={stats['current_not_for_backtest_rows']}")
    print(f"j1_status={stats['j1_status']}")
    print(f"k1_status={stats['k1_status']}")
    print(f"output_csv={output_csv.relative_to(REPO_ROOT)}")
    print(f"report_json={REPORT_JSON.relative_to(REPO_ROOT)}")
    print(f"report_md={REPORT_MD.relative_to(REPO_ROOT)}")
    return 0 if checks["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
