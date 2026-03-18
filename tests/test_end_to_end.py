from __future__ import annotations

import csv
import shutil
from pathlib import Path

from locker_manage_system.lottery_command import run_lottery
from locker_manage_system.validate_command import run_validate


REPO_ROOT = Path(__file__).resolve().parents[1]
DEMO_INPUT_DIR = REPO_ROOT / "demo-input"
FIXTURE_STATE_DIR = Path(__file__).resolve().parent / "fixtures" / "demo_state"


def _write_config(path: Path) -> None:
    path.write_text(
        "year: 2026\n"
        "paths:\n"
        "  input_dir: input\n"
        "  state_dir: state\n"
        "  output_dir: output\n"
        "floors:\n"
        "  2F:\n"
        "    capacity: 420\n"
        "    occupancy: pair_only\n"
        "    locker_start: 2001\n"
        "    locker_end: 2420\n"
        "  3F:\n"
        "    capacity: 240\n"
        "    occupancy: pair_only\n"
        "    locker_start: 3001\n"
        "    locker_end: 3240\n"
        "  4F:\n"
        "    capacity: 240\n"
        "    occupancy: single_only\n"
        "    locker_start: 4001\n"
        "    locker_end: 4240\n"
        "  5F:\n"
        "    capacity: 240\n"
        "    occupancy: single_only\n"
        "    locker_start: 5001\n"
        "    locker_end: 5240\n"
        "  6F:\n"
        "    capacity: 240\n"
        "    occupancy: single_only\n"
        "    locker_start: 6001\n"
        "    locker_end: 6240\n",
        encoding="utf-8",
    )


def _copy_demo_state_fixture(state_dir: Path) -> None:
    shutil.copyfile(FIXTURE_STATE_DIR / "winners.csv", state_dir / "winners.csv")
    shutil.copyfile(FIXTURE_STATE_DIR / "lockers.csv", state_dir / "locker_assignments.csv")


def _mark_review_row_keep(review_csv: Path, applicant_id: str) -> None:
    with review_csv.open("r", encoding="utf-8", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))
        fieldnames = list(rows[0].keys()) if rows else []

    for row in rows:
        row["manual_status"] = "keep" if row["申請者学籍番号"] == applicant_id else "reject"

    with review_csv.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_validate_then_lottery_with_demo_input(tmp_path):
    input_dir = tmp_path / "input"
    state_dir = tmp_path / "state"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    state_dir.mkdir()

    shutil.copyfile(DEMO_INPUT_DIR / "applicant_data.csv", input_dir / "applicant_data.csv")
    shutil.copyfile(DEMO_INPUT_DIR / "partner_data.csv", input_dir / "partner_data.csv")
    _copy_demo_state_fixture(state_dir)

    config_path = tmp_path / "config.yml"
    _write_config(config_path)

    validate_result = run_validate(
        config_path=config_path,
        term="term1",
        input_dir=input_dir,
        state_dir=state_dir,
        output_dir=output_dir,
    )

    _mark_review_row_keep(validate_result.review_dir / "review_4F.csv", "4654293")

    lottery_result = run_lottery(
        config_path=config_path,
        term="term1",
        review_dir=validate_result.review_dir,
        state_dir=state_dir,
        output_dir=output_dir,
    )

    result_csv = tmp_path / "output" / "term1" / "lottery" / "result.csv"
    locker_state_csv = tmp_path / "output" / "term1" / "lottery" / "locker_assignments.csv"
    log_csv = tmp_path / "output" / "term1" / "lottery" / "lottery_log.csv"

    assert lottery_result.winner_count == 1
    assert result_csv.exists()
    assert locker_state_csv.exists()
    assert log_csv.exists()

    with result_csv.open("r", encoding="utf-8", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert rows[0]["申請者学籍番号"] == "4654293"
    assert rows[0]["割り当てロッカー"] == "4001"
