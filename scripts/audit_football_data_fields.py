#!/usr/bin/env python3
"""Audit Football-Data CSV fields for the M1 minimum dataset contract."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = REPO_ROOT / "data" / "raw" / "football_data"
ALT_DATA_DIR = REPO_ROOT / "data" / "raw" / "football_data_sample"
REPORT_DIR = REPO_ROOT / "reports" / "data_audit"
JSON_REPORT = REPORT_DIR / "football_data_field_audit.json"
MD_REPORT = REPORT_DIR / "football_data_field_audit.md"
MINIMUM_CONTRACT = REPO_ROOT / "config" / "m1_minimum_dataset_fields.json"

EXPECTED_FILE_COUNT = 30
COMPLETE_BACKTEST_SEASONS = {"2020/21", "2021/22", "2022/23", "2023/24", "2024/25"}
CURRENT_NOT_FOR_BACKTEST_SEASONS = {"2025/26"}

LEAGUE_NAMES = {
    "E0": "England Premier League",
    "D1": "Germany Bundesliga",
    "SP1": "Spain La Liga",
    "I1": "Italy Serie A",
    "F1": "France Ligue 1",
}

FIELD_GROUPS = {
    "result": ["FTHG", "FTAG", "FTR"],
    "one_x_two_opening": ["B365H", "B365D", "B365A"],
    "one_x_two_closing": ["B365CH", "B365CD", "B365CA"],
    "ah_opening": ["AHh", "B365AHH", "B365AHA"],
    "ah_closing": ["AHCh", "B365CAHH", "B365CAHA"],
    "ou_opening": ["B365>2.5", "B365<2.5"],
    "ou_closing": ["B365C>2.5", "B365C<2.5"],
    "b365": [
        "B365H",
        "B365D",
        "B365A",
        "B365CH",
        "B365CD",
        "B365CA",
        "B365>2.5",
        "B365<2.5",
        "B365C>2.5",
        "B365C<2.5",
        "B365AHH",
        "B365AHA",
        "B365CAHH",
        "B365CAHA",
    ],
    "pinnacle_ps": [
        "PSH",
        "PSD",
        "PSA",
        "PSCH",
        "PSCD",
        "PSCA",
        "P>2.5",
        "P<2.5",
        "PC>2.5",
        "PC<2.5",
        "PAHH",
        "PAHA",
        "PCAHH",
        "PCAHA",
    ],
    "ah_line_replacement": ["AHh", "AHCh"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR if DEFAULT_DATA_DIR.exists() else ALT_DATA_DIR,
        help="Directory containing Football-Data CSV files.",
    )
    parser.add_argument(
        "--expected-file-count",
        type=int,
        default=EXPECTED_FILE_COUNT,
        help="Expected CSV count for self-check.",
    )
    return parser.parse_args()


def season_from_code(code: str) -> str:
    if code == "2021":
        return "2020/21"
    if re.fullmatch(r"\d{4}", code):
        start = int(code[:2])
        end = int(code[2:])
        return f"20{start:02d}/{end:02d}"
    raise ValueError(f"Unsupported season code: {code}")


def parse_filename(path: Path) -> tuple[str, str]:
    match = re.fullmatch(r"([A-Z0-9]+)_(\d{4})\.csv", path.name)
    if not match:
        raise ValueError(f"Unexpected Football-Data filename: {path.name}")
    return match.group(1), season_from_code(match.group(2))


def read_csv_profile(path: Path) -> tuple[list[str], int]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        row_count = sum(1 for row in reader if any(cell.strip() for cell in row))
    return header, row_count


def coverage_for(header: list[str], fields: list[str]) -> dict[str, Any]:
    present = [field for field in fields if field in header]
    missing = [field for field in fields if field not in header]
    return {
        "status": "PASS" if not missing else "FAIL",
        "present": present,
        "missing": missing,
        "coverage": len(present) / len(fields) if fields else 1.0,
    }


def season_role(season: str) -> str:
    if season in COMPLETE_BACKTEST_SEASONS:
        return "COMPLETE_BACKTEST"
    if season in CURRENT_NOT_FOR_BACKTEST_SEASONS:
        return "CURRENT_NOT_FOR_BACKTEST"
    return "OUT_OF_SCOPE"


def audit_files(data_dir: Path) -> dict[str, Any]:
    csv_files = sorted(data_dir.glob("*.csv"))
    files = []
    leagues: dict[str, dict[str, Any]] = {}
    seasons: dict[str, dict[str, Any]] = {}
    totals_by_role: dict[str, int] = defaultdict(int)

    for path in csv_files:
        league_code, season = parse_filename(path)
        header, row_count = read_csv_profile(path)
        group_coverage = {
            group: coverage_for(header, fields) for group, fields in FIELD_GROUPS.items()
        }
        role = season_role(season)
        file_profile = {
            "file": str(path.relative_to(REPO_ROOT)),
            "league_code": league_code,
            "league_name": LEAGUE_NAMES.get(league_code, "Unknown"),
            "season": season,
            "season_role": role,
            "rows": row_count,
            "field_count": len(header),
            "coverage": group_coverage,
        }
        files.append(file_profile)

        league_entry = leagues.setdefault(
            league_code,
            {
                "league_name": LEAGUE_NAMES.get(league_code, "Unknown"),
                "files": 0,
                "rows": 0,
                "seasons": [],
            },
        )
        league_entry["files"] += 1
        league_entry["rows"] += row_count
        league_entry["seasons"].append(season)

        season_entry = seasons.setdefault(
            season,
            {"files": 0, "rows": 0, "season_role": role, "leagues": []},
        )
        season_entry["files"] += 1
        season_entry["rows"] += row_count
        season_entry["leagues"].append(league_code)
        totals_by_role[role] += row_count

    for league_entry in leagues.values():
        league_entry["seasons"] = sorted(set(league_entry["seasons"]))
    for season_entry in seasons.values():
        season_entry["leagues"] = sorted(set(season_entry["leagues"]))

    overall_coverage = {}
    for group, fields in FIELD_GROUPS.items():
        missing_files = [
            item["file"] for item in files if item["coverage"][group]["status"] != "PASS"
        ]
        overall_coverage[group] = {
            "status": "PASS" if not missing_files else "FAIL",
            "required_fields": fields,
            "files_passed": len(files) - len(missing_files),
            "files_total": len(files),
            "missing_files": missing_files,
        }

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": {
            "name": "football_data",
            "data_dir": str(data_dir.relative_to(REPO_ROOT)),
        },
        "summary": {
            "file_count": len(files),
            "league_count": len(leagues),
            "season_count": len(seasons),
            "row_count": sum(item["rows"] for item in files),
            "usable_for_m1": "YES",
            "old_system_touched": "NO",
            "current_season_policy": "2025/26 is CURRENT_NOT_FOR_BACKTEST and excluded from COMPLETE_BACKTEST.",
        },
        "leagues": dict(sorted(leagues.items())),
        "seasons": dict(sorted(seasons.items())),
        "rows_by_role": dict(sorted(totals_by_role.items())),
        "overall_coverage": overall_coverage,
        "files": files,
        "ah_line_note": (
            "Football-Data files in this sample expose AHh and AHCh as the Asian "
            "Handicap opening and closing line fields. M1 treats AHh/AHCh as the "
            "minimum line contract instead of legacy BbAH/BbAHh naming."
        ),
        "backtest_policy": {
            "complete_backtest_seasons": sorted(COMPLETE_BACKTEST_SEASONS),
            "current_not_for_backtest_seasons": sorted(CURRENT_NOT_FOR_BACKTEST_SEASONS),
        },
    }


def build_minimum_contract(audit: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": "m1_minimum_dataset_fields",
        "version": "0.1.0",
        "source": "football_data",
        "usable_for_m1": "YES",
        "old_system_touched": "NO",
        "complete_backtest_seasons": sorted(COMPLETE_BACKTEST_SEASONS),
        "current_not_for_backtest_seasons": sorted(CURRENT_NOT_FOR_BACKTEST_SEASONS),
        "season_role_field": "season_role",
        "required_fields": {
            "identity": ["Div", "Date", "HomeTeam", "AwayTeam"],
            "result": FIELD_GROUPS["result"],
            "one_x_two_opening": FIELD_GROUPS["one_x_two_opening"],
            "one_x_two_closing": FIELD_GROUPS["one_x_two_closing"],
            "ah_opening": FIELD_GROUPS["ah_opening"],
            "ah_closing": FIELD_GROUPS["ah_closing"],
            "ou_opening": FIELD_GROUPS["ou_opening"],
            "ou_closing": FIELD_GROUPS["ou_closing"],
            "b365": FIELD_GROUPS["b365"],
            "pinnacle_ps": FIELD_GROUPS["pinnacle_ps"],
        },
        "line_fields": {
            "asian_handicap_opening": "AHh",
            "asian_handicap_closing": "AHCh",
            "legacy_not_required": ["BbAH", "BbAHh"],
            "note": audit["ah_line_note"],
        },
        "current_season_policy": {
            "label": "CURRENT_NOT_FOR_BACKTEST",
            "allowed_use": "current-season field validation and forward research only",
            "disallowed_use": "complete-season historical backtest",
        },
    }


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def render_markdown(audit: dict[str, Any], self_check: dict[str, Any]) -> str:
    summary = audit["summary"]
    season_rows = [
        [
            season,
            item["season_role"],
            item["files"],
            item["rows"],
            ", ".join(item["leagues"]),
        ]
        for season, item in audit["seasons"].items()
    ]
    league_rows = [
        [
            code,
            item["league_name"],
            item["files"],
            item["rows"],
            ", ".join(item["seasons"]),
        ]
        for code, item in audit["leagues"].items()
    ]
    coverage_rows = [
        [
            group,
            item["status"],
            f"{item['files_passed']}/{item['files_total']}",
            ", ".join(item["required_fields"]),
        ]
        for group, item in audit["overall_coverage"].items()
    ]
    file_rows = [
        [
            item["file"],
            item["league_code"],
            item["season"],
            item["season_role"],
            item["rows"],
            item["field_count"],
        ]
        for item in audit["files"]
    ]

    return "\n".join(
        [
            "# Football-Data Field Audit",
            "",
            f"- generated_at_utc: `{audit['generated_at_utc']}`",
            f"- data_dir: `{audit['source']['data_dir']}`",
            f"- usable_for_m1: `{summary['usable_for_m1']}`",
            f"- old_system_touched: `{summary['old_system_touched']}`",
            f"- checker: `{self_check['status']}`",
            "",
            "## Summary",
            "",
            markdown_table(
                ["metric", "value"],
                [
                    ["file_count", summary["file_count"]],
                    ["league_count", summary["league_count"]],
                    ["season_count", summary["season_count"]],
                    ["row_count", summary["row_count"]],
                    ["complete_backtest_rows", audit["rows_by_role"].get("COMPLETE_BACKTEST", 0)],
                    [
                        "current_not_for_backtest_rows",
                        audit["rows_by_role"].get("CURRENT_NOT_FOR_BACKTEST", 0),
                    ],
                ],
            ),
            "",
            "## Season Classification",
            "",
            markdown_table(["season", "label", "files", "rows", "leagues"], season_rows),
            "",
            "Policy: `2020/21`-`2024/25` are `COMPLETE_BACKTEST`; `2025/26` is "
            "`CURRENT_NOT_FOR_BACKTEST` and must not be mixed into complete-season backtests.",
            "",
            "## League Coverage",
            "",
            markdown_table(["code", "league", "files", "rows", "seasons"], league_rows),
            "",
            "## Field Coverage",
            "",
            markdown_table(["group", "status", "files_passed", "required_fields"], coverage_rows),
            "",
            "## AH Line Field Note",
            "",
            audit["ah_line_note"],
            "",
            "## File Inventory",
            "",
            markdown_table(["file", "league", "season", "label", "rows", "fields"], file_rows),
            "",
            "## Self Check",
            "",
            markdown_table(
                ["check", "status"],
                [[name, status] for name, status in self_check["checks"].items()],
            ),
            "",
        ]
    )


def run_self_check(audit: dict[str, Any], expected_file_count: int) -> dict[str, Any]:
    seasons = audit["seasons"]
    checks = {
        "file_count_is_30": audit["summary"]["file_count"] == expected_file_count,
        "usable_for_m1_yes": audit["summary"]["usable_for_m1"] == "YES",
        "old_system_touched_no": audit["summary"]["old_system_touched"] == "NO",
        "all_coverage_pass": all(
            item["status"] == "PASS" for item in audit["overall_coverage"].values()
        ),
        "complete_backtest_2020_21_to_2024_25": all(
            seasons.get(season, {}).get("season_role") == "COMPLETE_BACKTEST"
            for season in COMPLETE_BACKTEST_SEASONS
        ),
        "current_2025_26_not_for_backtest": all(
            seasons.get(season, {}).get("season_role") == "CURRENT_NOT_FOR_BACKTEST"
            for season in CURRENT_NOT_FOR_BACKTEST_SEASONS
        ),
        "current_not_mixed_into_complete_backtest": not any(
            item["season"] in CURRENT_NOT_FOR_BACKTEST_SEASONS
            and item["season_role"] == "COMPLETE_BACKTEST"
            for item in audit["files"]
        ),
    }
    rendered = {name: "PASS" if passed else "FAIL" for name, passed in checks.items()}
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": rendered,
    }


def main() -> int:
    args = parse_args()
    data_dir = args.data_dir.resolve()
    if not data_dir.exists():
        raise SystemExit(f"Data directory does not exist: {data_dir}")

    audit = audit_files(data_dir)
    self_check = run_self_check(audit, args.expected_file_count)
    audit["self_check"] = self_check
    contract = build_minimum_contract(audit)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MINIMUM_CONTRACT.parent.mkdir(parents=True, exist_ok=True)

    JSON_REPORT.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MINIMUM_CONTRACT.write_text(
        json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MD_REPORT.write_text(render_markdown(audit, self_check), encoding="utf-8")

    print(f"football_data_field_audit: {self_check['status']}")
    print(f"csv_files={audit['summary']['file_count']} rows={audit['summary']['row_count']}")
    print(f"markdown={MD_REPORT.relative_to(REPO_ROOT)}")
    print(f"json={JSON_REPORT.relative_to(REPO_ROOT)}")
    print(f"contract={MINIMUM_CONTRACT.relative_to(REPO_ROOT)}")
    return 0 if self_check["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
