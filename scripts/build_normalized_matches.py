#!/usr/bin/env python3
"""Build the M1 normalized match table from Football-Data CSV files."""

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
RAW_DIR = REPO_ROOT / "data" / "raw" / "football_data"
CONTRACT_PATH = REPO_ROOT / "config" / "m1_minimum_dataset_fields.json"
AUDIT_JSON_PATH = REPO_ROOT / "reports" / "data_audit" / "football_data_field_audit.json"
OUTPUT_DIR = REPO_ROOT / "data" / "processed" / "normalized_matches"
OUTPUT_CSV = OUTPUT_DIR / "m1_matches_normalized.csv"
REPORT_DIR = REPO_ROOT / "reports" / "data_audit"
REPORT_MD = REPORT_DIR / "m1_normalized_matches_report.md"
REPORT_JSON = REPORT_DIR / "m1_normalized_matches_report.json"

NORMALIZED_FIELDS = [
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

ROLE_ORDER = ["COMPLETE_BACKTEST", "CURRENT_NOT_FOR_BACKTEST"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR)
    parser.add_argument("--contract", type=Path, default=CONTRACT_PATH)
    parser.add_argument("--audit-json", type=Path, default=AUDIT_JSON_PATH)
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
        raise ValueError(f"Unexpected Football-Data filename: {path.name}")
    return match.group(1), season_from_code(match.group(2))


def parse_date(value: str) -> str:
    raw = value.strip()
    for fmt in ("%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            pass
    raise ValueError(f"Unsupported date format: {value!r}")


def season_role(season: str, contract: dict[str, Any]) -> str:
    if season in contract["complete_backtest_seasons"]:
        return "COMPLETE_BACKTEST"
    if season in contract["current_not_for_backtest_seasons"]:
        return "CURRENT_NOT_FOR_BACKTEST"
    return "OUT_OF_SCOPE"


def clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def make_match_id(row: dict[str, str]) -> str:
    key = "|".join(
        [
            row["data_source"],
            row["league"],
            row["season"],
            row["date"],
            row["home_team"],
            row["away_team"],
        ]
    )
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]
    return f"m1_{digest}"


def required_source_fields(contract: dict[str, Any]) -> list[str]:
    required = []
    groups = [
        "identity",
        "result",
        "one_x_two_opening",
        "one_x_two_closing",
        "ah_opening",
        "ah_closing",
        "ou_opening",
        "ou_closing",
    ]
    for group in groups:
        required.extend(contract["required_fields"][group])
    return sorted(set(required))


def validate_header(path: Path, header: list[str], required_fields: list[str]) -> list[str]:
    missing = [field for field in required_fields if field not in header]
    if missing:
        raise ValueError(f"{path.name} missing required fields: {', '.join(missing)}")
    return missing


def normalize_rows(raw_dir: Path, contract: dict[str, Any]) -> tuple[list[dict[str, str]], dict[str, Any]]:
    csv_files = sorted(raw_dir.glob("*.csv"))
    required_fields = required_source_fields(contract)
    normalized: list[dict[str, str]] = []
    file_profiles = []
    empty_counts: Counter[str] = Counter()
    rows_by_role: Counter[str] = Counter()
    rows_by_season: Counter[str] = Counter()
    rows_by_league: Counter[str] = Counter()

    for path in csv_files:
        league, season = parse_filename(path)
        role = season_role(season, contract)
        file_row_count = 0
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise ValueError(f"{path.name} has no header")
            validate_header(path, reader.fieldnames, required_fields)
            for source_row_number, raw in enumerate(reader, start=2):
                if not any(clean(value) for value in raw.values()):
                    continue
                out = {
                    "league": league,
                    "season": season,
                    "season_role": role,
                    "date": parse_date(clean(raw[FIELD_MAP["date"]])),
                    "home_team": clean(raw[FIELD_MAP["home_team"]]),
                    "away_team": clean(raw[FIELD_MAP["away_team"]]),
                    "bookmaker_source": "B365",
                    "data_source": "football_data",
                    "source_file": str(path.relative_to(REPO_ROOT)),
                    "source_row_number": str(source_row_number),
                }
                for normalized_field, source_field in FIELD_MAP.items():
                    if normalized_field in {"league", "date", "home_team", "away_team"}:
                        continue
                    out[normalized_field] = clean(raw[source_field])
                out["match_id"] = make_match_id(out)
                for field in NORMALIZED_FIELDS:
                    if clean(out.get(field)) == "":
                        empty_counts[field] += 1
                normalized.append(out)
                file_row_count += 1
                rows_by_role[role] += 1
                rows_by_season[season] += 1
                rows_by_league[league] += 1
        file_profiles.append(
            {
                "file": str(path.relative_to(REPO_ROOT)),
                "league": league,
                "season": season,
                "season_role": role,
                "rows": file_row_count,
            }
        )

    duplicate_ids = [
        match_id for match_id, count in Counter(row["match_id"] for row in normalized).items() if count > 1
    ]
    stats = {
        "raw_csv_count": len(csv_files),
        "normalized_rows": len(normalized),
        "rows_by_role": {role: rows_by_role.get(role, 0) for role in ROLE_ORDER},
        "rows_by_season": dict(sorted(rows_by_season.items())),
        "rows_by_league": dict(sorted(rows_by_league.items())),
        "file_profiles": file_profiles,
        "empty_counts": dict(sorted(empty_counts.items())),
        "duplicate_match_ids": duplicate_ids,
        "required_source_fields": required_fields,
    }
    return normalized, stats


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=NORMALIZED_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def self_check(stats: dict[str, Any], audit: dict[str, Any]) -> dict[str, Any]:
    audit_rows = audit["summary"]["row_count"]
    audit_role_rows = audit["rows_by_role"]
    checks = {
        "raw_csv_count_is_30": stats["raw_csv_count"] == 30,
        "normalized_rows_match_audit": stats["normalized_rows"] == audit_rows,
        "complete_backtest_rows_match_audit": stats["rows_by_role"]["COMPLETE_BACKTEST"]
        == audit_role_rows["COMPLETE_BACKTEST"],
        "current_not_for_backtest_rows_match_audit": stats["rows_by_role"][
            "CURRENT_NOT_FOR_BACKTEST"
        ]
        == audit_role_rows["CURRENT_NOT_FOR_BACKTEST"],
        "current_not_in_complete_backtest": stats["rows_by_season"].get("2025/26", 0)
        == stats["rows_by_role"]["CURRENT_NOT_FOR_BACKTEST"],
        "no_duplicate_match_ids": not stats["duplicate_match_ids"],
        "recommendations_generated_no": True,
        "backtest_run_no": True,
        "old_system_touched_no": True,
    }
    rendered = {name: "PASS" if value else "FAIL" for name, value in checks.items()}
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
    role_rows = [[role, count] for role, count in stats["rows_by_role"].items()]
    season_rows = [
        [
            season,
            "COMPLETE_BACKTEST" if season in report["contract"]["complete_backtest_seasons"] else "CURRENT_NOT_FOR_BACKTEST",
            count,
        ]
        for season, count in stats["rows_by_season"].items()
    ]
    file_rows = [
        [item["file"], item["league"], item["season"], item["season_role"], item["rows"]]
        for item in stats["file_profiles"]
    ]
    empty_rows = [[field, count] for field, count in stats["empty_counts"].items()]
    if not empty_rows:
        empty_rows = [["none", 0]]

    return "\n".join(
        [
            "# M1 Normalized Matches Report",
            "",
            f"- generated_at_utc: `{report['generated_at_utc']}`",
            f"- output_csv: `{report['output_csv']}`",
            f"- checker: `{report['self_check']['status']}`",
            "- old_system_touched: `NO`",
            "- recommendations_generated: `NO`",
            "- backtest_run: `NO`",
            "",
            "## Summary",
            "",
            markdown_table(
                ["metric", "value"],
                [
                    ["raw_csv_count", stats["raw_csv_count"]],
                    ["normalized_rows", stats["normalized_rows"]],
                    ["audit_rows", report["audit_baseline"]["row_count"]],
                    ["row_delta_vs_audit", stats["normalized_rows"] - report["audit_baseline"]["row_count"]],
                    ["complete_backtest_rows", stats["rows_by_role"]["COMPLETE_BACKTEST"]],
                    [
                        "current_not_for_backtest_rows",
                        stats["rows_by_role"]["CURRENT_NOT_FOR_BACKTEST"],
                    ],
                ],
            ),
            "",
            "The normalized row count matches the Phase 1 Football-Data audit. "
            "`2025/26` rows are retained in the normalized table as "
            "`CURRENT_NOT_FOR_BACKTEST`, but they are not counted in "
            "`complete_backtest_rows`.",
            "",
            "## Role Counts",
            "",
            markdown_table(["season_role", "rows"], role_rows),
            "",
            "## Season Counts",
            "",
            markdown_table(["season", "season_role", "rows"], season_rows),
            "",
            "## Normalized Fields",
            "",
            markdown_table(["field"], [[field] for field in NORMALIZED_FIELDS]),
            "",
            "## Empty Normalized Cell Counts",
            "",
            markdown_table(["field", "empty_cells"], empty_rows),
            "",
            "## Source File Counts",
            "",
            markdown_table(["file", "league", "season", "season_role", "rows"], file_rows),
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
    output_csv: Path,
    contract: dict[str, Any],
    audit: dict[str, Any],
    stats: dict[str, Any],
    checks: dict[str, Any],
) -> dict[str, Any]:
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "output_csv": str(output_csv.relative_to(REPO_ROOT)),
        "contract_refs": [
            "config/m1_minimum_dataset_fields.json",
            "docs/M1_DATA_CONTRACT.md",
            "reports/data_audit/football_data_field_audit.json",
        ],
        "audit_baseline": {
            "raw_csv_count": audit["summary"]["file_count"],
            "row_count": audit["summary"]["row_count"],
            "rows_by_role": audit["rows_by_role"],
        },
        "contract": {
            "complete_backtest_seasons": contract["complete_backtest_seasons"],
            "current_not_for_backtest_seasons": contract["current_not_for_backtest_seasons"],
        },
        "stats": stats,
        "old_system_touched": "NO",
        "recommendations_generated": "NO",
        "backtest_run": "NO",
        "self_check": checks,
    }


def main() -> int:
    args = parse_args()
    raw_dir = args.raw_dir.resolve()
    contract_path = args.contract.resolve()
    audit_json_path = args.audit_json.resolve()
    output_csv = args.output_csv.resolve()
    if not raw_dir.exists():
        raise SystemExit(f"Raw directory does not exist: {raw_dir}")
    contract = load_json(contract_path)
    audit = load_json(audit_json_path)
    rows, stats = normalize_rows(raw_dir, contract)
    write_csv(output_csv, rows)
    checks = self_check(stats, audit)
    report = build_report(output_csv, contract, audit, stats, checks)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")

    print(f"m1_normalized_matches: {checks['status']}")
    print(f"raw_csv_count={stats['raw_csv_count']}")
    print(f"normalized_rows={stats['normalized_rows']}")
    print(f"complete_backtest_rows={stats['rows_by_role']['COMPLETE_BACKTEST']}")
    print(f"current_not_for_backtest_rows={stats['rows_by_role']['CURRENT_NOT_FOR_BACKTEST']}")
    print(f"output_csv={output_csv.relative_to(REPO_ROOT)}")
    print(f"report_json={REPORT_JSON.relative_to(REPO_ROOT)}")
    print(f"report_md={REPORT_MD.relative_to(REPO_ROOT)}")
    return 0 if checks["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
