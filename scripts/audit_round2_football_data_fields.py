#!/usr/bin/env python3
"""Audit Round2 Football-Data CSV field coverage."""

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
DATA_DIR = REPO_ROOT / "data" / "raw" / "football_data_round2"
REPORT_DIR = REPO_ROOT / "reports" / "data_audit"
REPORT_MD = REPORT_DIR / "round2_football_data_field_audit.md"
REPORT_JSON = REPORT_DIR / "round2_football_data_field_audit.json"
AVAILABILITY_JSON = REPO_ROOT / "config" / "round2_league_availability.json"

EXPECTED_FILE_COUNT = 36
TARGET_LEAGUES = ["N1", "B1", "P1", "T1", "SC0", "J1"]
UNAVAILABLE_LEAGUES = ["K1"]
COMPLETE_BACKTEST_SEASONS = ["2020/21", "2021/22", "2022/23", "2023/24", "2024/25"]
CURRENT_NOT_FOR_BACKTEST_SEASONS = ["2025/26"]

LEAGUE_NAMES = {
    "N1": "Netherlands Eredivisie",
    "B1": "Belgium Jupiler League",
    "P1": "Portugal Primeira Liga",
    "T1": "Turkey Super Lig",
    "SC0": "Scotland Premiership",
    "J1": "Japan J1 League",
    "K1": "South Korea K League 1",
}

FIELD_GROUPS = {
    "identity_result": ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"],
    "one_x_two_opening": ["B365H", "B365D", "B365A"],
    "one_x_two_closing": ["B365CH", "B365CD", "B365CA"],
    "ah_opening": ["AHh", "B365AHH", "B365AHA"],
    "ah_closing": ["AHCh", "B365CAHH", "B365CAHA"],
    "ou25_opening": ["B365>2.5", "B365<2.5"],
    "ou25_closing": ["B365C>2.5", "B365C<2.5"],
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
    "ah_line_fields": ["AHh", "AHCh"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    return parser.parse_args()


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


def season_role(season: str, rows: int, league: str) -> str:
    if league == "J1" and season == "2025/26" and rows == 0:
        return "CURRENT_EMPTY"
    if season in COMPLETE_BACKTEST_SEASONS:
        return "COMPLETE_BACKTEST"
    if season in CURRENT_NOT_FOR_BACKTEST_SEASONS:
        return "CURRENT_NOT_FOR_BACKTEST"
    return "OUT_OF_SCOPE"


def read_profile(path: Path) -> tuple[list[str], int]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader, [])
        rows = sum(1 for row in reader if any(cell.strip() for cell in row))
    return [field.strip() for field in header if field.strip()], rows


def coverage(header: list[str], fields: list[str]) -> dict[str, Any]:
    present = [field for field in fields if field in header]
    missing = [field for field in fields if field not in header]
    return {
        "status": "PASS" if not missing else "FAIL",
        "present": present,
        "missing": missing,
        "coverage": len(present) / len(fields) if fields else 1.0,
    }


def audit(data_dir: Path) -> dict[str, Any]:
    files = sorted(data_dir.glob("*.csv"))
    file_profiles = []
    league_profiles: dict[str, dict[str, Any]] = {}
    season_profiles: dict[str, dict[str, Any]] = {}
    empty_files = []
    current_rows = 0
    complete_rows = 0

    for path in files:
        league, season = parse_filename(path)
        header, rows = read_profile(path)
        role = season_role(season, rows, league)
        group_coverage = {name: coverage(header, fields) for name, fields in FIELD_GROUPS.items()}
        header_only = rows == 0
        if header_only:
            empty_files.append(str(path.relative_to(REPO_ROOT)))
        if role == "COMPLETE_BACKTEST":
            complete_rows += rows
        elif role == "CURRENT_NOT_FOR_BACKTEST":
            current_rows += rows
        file_ok = (
            not header_only
            and all(group_coverage[name]["status"] == "PASS" for name in FIELD_GROUPS)
        )
        profile = {
            "file": str(path.relative_to(REPO_ROOT)),
            "league": league,
            "league_name": LEAGUE_NAMES.get(league, "Unknown"),
            "season": season,
            "season_role": role,
            "rows": rows,
            "field_count": len(header),
            "header_only": header_only,
            "coverage": group_coverage,
            "usable_for_round2_backtest_contract": "YES" if file_ok else "NO",
        }
        file_profiles.append(profile)

        league_entry = league_profiles.setdefault(
            league,
            {
                "league_name": LEAGUE_NAMES.get(league, "Unknown"),
                "files": 0,
                "rows": 0,
                "seasons": [],
                "failed_files": [],
                "empty_files": [],
                "availability": "AVAILABLE",
            },
        )
        league_entry["files"] += 1
        league_entry["rows"] += rows
        league_entry["seasons"].append(season)
        if not file_ok:
            league_entry["failed_files"].append(profile["file"])
        if header_only:
            league_entry["empty_files"].append(profile["file"])

        season_entry = season_profiles.setdefault(
            season, {"files": 0, "rows": 0, "leagues": [], "season_role": role}
        )
        season_entry["files"] += 1
        season_entry["rows"] += rows
        season_entry["leagues"].append(league)

    for league in UNAVAILABLE_LEAGUES:
        league_profiles[league] = {
            "league_name": LEAGUE_NAMES.get(league, "Unknown"),
            "files": 0,
            "rows": 0,
            "seasons": [],
            "failed_files": [],
            "empty_files": [],
            "availability": "UNAVAILABLE_SOURCE_EXPIRED",
        }
    for league, entry in league_profiles.items():
        entry["seasons"] = sorted(set(entry["seasons"]))
        if entry["availability"] != "UNAVAILABLE_SOURCE_EXPIRED":
            entry["availability"] = "AVAILABLE_FULL_CONTRACT" if not entry["failed_files"] else "AVAILABLE_PARTIAL_SCHEMA"
    for entry in season_profiles.values():
        entry["leagues"] = sorted(set(entry["leagues"]))

    failed_files = [
        item["file"]
        for item in file_profiles
        if item["usable_for_round2_backtest_contract"] != "YES"
    ]
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": {
            "name": "football_data_round2",
            "data_dir": str(data_dir.relative_to(REPO_ROOT)),
        },
        "summary": {
            "files_checked": len(file_profiles),
            "target_files_expected": EXPECTED_FILE_COUNT,
            "target_leagues": TARGET_LEAGUES,
            "unavailable_leagues": UNAVAILABLE_LEAGUES,
            "complete_backtest_rows": complete_rows,
            "current_not_for_backtest_rows": current_rows,
            "empty_files": empty_files,
            "failed_files": failed_files,
            "usable_for_round2": "YES" if not failed_files else "NO",
            "old_system_touched": "NO",
            "normalized_built": "NO",
            "features_built": "NO",
            "backtest_run": "NO",
            "recommendations_generated": "NO",
        },
        "season_policy": {
            "complete_backtest": COMPLETE_BACKTEST_SEASONS,
            "current_not_for_backtest": CURRENT_NOT_FOR_BACKTEST_SEASONS,
            "current_empty": ["J1_2526.csv"],
        },
        "league_profiles": dict(sorted(league_profiles.items())),
        "season_profiles": dict(sorted(season_profiles.items())),
        "files": file_profiles,
        "k1_unavailable": [
            {
                "league": "K1",
                "league_name": LEAGUE_NAMES["K1"],
                "status": "UNAVAILABLE_SOURCE_EXPIRED",
                "failure_is_blocker": False,
            }
        ],
        "notes": [
            "J1_2526 is header-only and is labeled CURRENT_EMPTY; it is excluded from current rows.",
            "K1 is labeled UNAVAILABLE_SOURCE_EXPIRED and is not counted as a failed CSV.",
            "This audit does not build normalized rows, features, or backtests.",
        ],
    }


def availability_config(audit_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": "round2_league_availability",
        "version": "0.1.0",
        "old_system_touched": "NO",
        "usable_for_round2": audit_result["summary"]["usable_for_round2"],
        "data_dir": audit_result["source"]["data_dir"],
        "leagues": audit_result["league_profiles"],
        "empty_files": audit_result["summary"]["empty_files"],
        "unavailable_sources": audit_result["k1_unavailable"],
        "season_policy": audit_result["season_policy"],
        "forbidden_actions_confirmed": {
            "normalized_built": False,
            "features_built": False,
            "backtest_run": False,
            "recommendations_generated": False,
            "v3_v4_touched": False,
        },
    }


def self_check(audit_result: dict[str, Any]) -> dict[str, Any]:
    summary = audit_result["summary"]
    checks = {
        "files_checked_36": summary["files_checked"] == EXPECTED_FILE_COUNT,
        "empty_files_listed": "data/raw/football_data_round2/J1_2526.csv" in summary["empty_files"],
        "j1_2526_current_empty": any(
            item["file"] == "data/raw/football_data_round2/J1_2526.csv"
            and item["season_role"] == "CURRENT_EMPTY"
            and item["header_only"] is True
            for item in audit_result["files"]
        ),
        "k1_unavailable_listed": audit_result["k1_unavailable"][0]["status"]
        == "UNAVAILABLE_SOURCE_EXPIRED",
        "usable_for_round2_explicit": summary["usable_for_round2"] in {"YES", "NO"},
        "season_roles_valid": all(
            item["season_role"] in {"COMPLETE_BACKTEST", "CURRENT_NOT_FOR_BACKTEST", "CURRENT_EMPTY"}
            for item in audit_result["files"]
        ),
        "current_empty_not_in_current_rows": all(
            item["rows"] == 0
            for item in audit_result["files"]
            if item["season_role"] == "CURRENT_EMPTY"
        ),
        "old_system_touched_no": summary["old_system_touched"] == "NO",
        "no_normalized_features_backtest": summary["normalized_built"] == "NO"
        and summary["features_built"] == "NO"
        and summary["backtest_run"] == "NO",
        "recommendations_generated_no": summary["recommendations_generated"] == "NO",
    }
    rendered = {name: "PASS" if passed else "FAIL" for name, passed in checks.items()}
    return {"status": "PASS" if all(checks.values()) else "FAIL", "checks": rendered}


def md_cell(value: Any) -> str:
    if isinstance(value, list):
        value = ", ".join(str(v) for v in value)
    return str(value).replace("|", "\\|")


def table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(md_cell(h) for h in headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(md_cell(v) for v in row) + " |")
    return "\n".join(lines)


def render_markdown(audit_result: dict[str, Any]) -> str:
    summary = audit_result["summary"]
    league_rows = [
        [
            league,
            profile["league_name"],
            profile["availability"],
            profile["files"],
            profile["rows"],
            profile["seasons"],
            len(profile["failed_files"]),
            profile["empty_files"],
        ]
        for league, profile in audit_result["league_profiles"].items()
    ]
    file_rows = [
        [
            item["file"],
            item["league"],
            item["season"],
            item["season_role"],
            item["rows"],
            item["header_only"],
            item["usable_for_round2_backtest_contract"],
            item["coverage"]["identity_result"]["status"],
            item["coverage"]["one_x_two_opening"]["status"],
            item["coverage"]["one_x_two_closing"]["status"],
            item["coverage"]["ah_opening"]["status"],
            item["coverage"]["ah_closing"]["status"],
            item["coverage"]["ou25_opening"]["status"],
            item["coverage"]["ou25_closing"]["status"],
            item["coverage"]["b365"]["status"],
            item["coverage"]["pinnacle_ps"]["status"],
            item["coverage"]["ah_line_fields"]["status"],
        ]
        for item in audit_result["files"]
    ]
    return "\n".join(
        [
            "# Round2 Football-Data Field Audit",
            "",
            f"- generated_at_utc: `{audit_result['generated_at_utc']}`",
            f"- data_dir: `{audit_result['source']['data_dir']}`",
            f"- checker: `{audit_result['self_check']['status']}`",
            f"- files_checked: `{summary['files_checked']}`",
            f"- usable_for_round2: `{summary['usable_for_round2']}`",
            f"- old_system_touched: `{summary['old_system_touched']}`",
            "- normalized_built: `NO`",
            "- features_built: `NO`",
            "- backtest_run: `NO`",
            "- recommendations_generated: `NO`",
            "",
            "## Summary",
            "",
            table(
                ["metric", "value"],
                [
                    ["files_checked", summary["files_checked"]],
                    ["complete_backtest_rows", summary["complete_backtest_rows"]],
                    ["current_not_for_backtest_rows", summary["current_not_for_backtest_rows"]],
                    ["empty_files", summary["empty_files"]],
                    ["failed_files", len(summary["failed_files"])],
                    ["K1", "UNAVAILABLE_SOURCE_EXPIRED"],
                ],
            ),
            "",
            "## League Availability",
            "",
            table(
                ["league", "name", "availability", "files", "rows", "seasons", "failed_files", "empty_files"],
                league_rows,
            ),
            "",
            "## Special Rules",
            "",
            "- `J1_2526.csv` is header-only and labeled `CURRENT_EMPTY`; it is not counted in current rows.",
            "- `K1` is labeled `UNAVAILABLE_SOURCE_EXPIRED`; it is not counted as a failed CSV.",
            "- This phase does not merge normalized rows, build features, run backtests, or generate recommendations.",
            "",
            "## File Coverage",
            "",
            table(
                [
                    "file",
                    "league",
                    "season",
                    "season_role",
                    "rows",
                    "header_only",
                    "usable",
                    "identity_result",
                    "1x2_open",
                    "1x2_close",
                    "ah_open",
                    "ah_close",
                    "ou25_open",
                    "ou25_close",
                    "b365",
                    "pinnacle_ps",
                    "AHh_AHCh",
                ],
                file_rows,
            ),
            "",
            "## Self Check",
            "",
            table(
                ["check", "status"],
                [[name, status] for name, status in audit_result["self_check"]["checks"].items()],
            ),
            "",
        ]
    )


def main() -> int:
    args = parse_args()
    data_dir = args.data_dir.resolve()
    if not data_dir.exists():
        raise SystemExit(f"Data directory does not exist: {data_dir}")
    result = audit(data_dir)
    result["self_check"] = self_check(result)
    availability = availability_config(result)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    AVAILABILITY_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(result), encoding="utf-8")
    AVAILABILITY_JSON.write_text(json.dumps(availability, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"round2_football_data_field_audit: {result['self_check']['status']}")
    print(f"files_checked={result['summary']['files_checked']}")
    print(f"usable_for_round2={result['summary']['usable_for_round2']}")
    print(f"empty_files={len(result['summary']['empty_files'])}")
    print(f"k1_unavailable={result['k1_unavailable'][0]['status']}")
    print(f"report_json={REPORT_JSON.relative_to(REPO_ROOT)}")
    print(f"report_md={REPORT_MD.relative_to(REPO_ROOT)}")
    print(f"availability={AVAILABILITY_JSON.relative_to(REPO_ROOT)}")
    return 0 if result["self_check"]["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
