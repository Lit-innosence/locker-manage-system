"""Workflow for running the floor lotteries from review outputs."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .config import AppConfig, load_config
from .lottery import FloorLotteryWinner, run_floor_lottery
from .review_io import ReviewApplication, load_review_applications


RESULT_COLUMNS = [
    "申請者氏名",
    "申請者学籍番号",
    "共同利用者氏名",
    "共同利用者学籍番号",
    "処理日",
    "割り当てロッカー",
]

LOCKER_STATE_COLUMNS = ["ロッカー番号", "割り当て状態"]
LOG_COLUMNS = ["floor", "application_id", "申請者学籍番号", "割り当てロッカー"]


@dataclass(frozen=True)
class LotteryRunResult:
    winner_count: int
    result_path: Path
    locker_state_path: Path
    log_path: Path


@dataclass(frozen=True)
class LockerAssignment:
    locker_number: str
    assignment_state: str = ""


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _floor_locker_numbers(config: AppConfig, floor: str) -> list[str]:
    floor_config = config.floors[floor]
    if floor_config.locker_start is None or floor_config.locker_end is None:
        return []
    return [str(number) for number in range(floor_config.locker_start, floor_config.locker_end + 1)]


def _load_locker_state(config: AppConfig, state_dir: str | Path) -> dict[str, LockerAssignment]:
    state_path = Path(state_dir)
    candidates = [
        state_path / str(config.year) / "locker_assignments.csv",
        state_path / "locker_assignments.csv",
    ]

    for candidate in candidates:
        if candidate.exists():
            with candidate.open("r", encoding="utf-8", newline="") as csv_file:
                reader = csv.DictReader(csv_file)
                state: dict[str, LockerAssignment] = {}
                for row in reader:
                    locker_number = row.get("ロッカー番号", "").strip()
                    if locker_number:
                        state[locker_number] = LockerAssignment(
                            locker_number=locker_number,
                            assignment_state=row.get("割り当て状態", "").strip(),
                        )
                return state

    state: dict[str, LockerAssignment] = {}
    for floor in config.floors:
        for locker_number in _floor_locker_numbers(config, floor):
            state[locker_number] = LockerAssignment(locker_number=locker_number)
    return state


def _update_locker_state(
    locker_state: dict[str, LockerAssignment],
    winners_by_locker: dict[str, ReviewApplication],
) -> dict[str, LockerAssignment]:
    updated_state = dict(locker_state)
    for locker_number, application in winners_by_locker.items():
        updated_state[locker_number] = LockerAssignment(
            locker_number=locker_number,
            assignment_state=application.applicant_id,
        )
    return updated_state


def _locker_rows(locker_state: dict[str, LockerAssignment]) -> list[dict[str, str]]:
    return [
        {"ロッカー番号": locker_number, "割り当て状態": locker_state[locker_number].assignment_state}
        for locker_number in sorted(locker_state)
    ]


def _open_lockers_for_floor(
    config: AppConfig,
    locker_state: dict[str, LockerAssignment],
    floor: str,
) -> list[str]:
    floor_lockers = set(_floor_locker_numbers(config, floor))
    return [
        locker_number
        for locker_number in sorted(floor_lockers)
        if not locker_state.get(locker_number, LockerAssignment(locker_number)).assignment_state
    ]


def _result_row(application: ReviewApplication, processing_date: str, locker_number: str) -> dict[str, str]:
    return {
        "申請者氏名": application.applicant_name,
        "申請者学籍番号": application.applicant_id,
        "共同利用者氏名": application.partner_name if application.usage_type == "pair" else "",
        "共同利用者学籍番号": application.partner_id if application.usage_type == "pair" else "",
        "処理日": processing_date,
        "割り当てロッカー": locker_number,
    }


def _log_row(application: ReviewApplication, locker_number: str) -> dict[str, str]:
    return {
        "floor": application.floor,
        "application_id": application.application_id,
        "申請者学籍番号": application.applicant_id,
        "割り当てロッカー": locker_number,
    }


def run_lottery(
    *,
    config_path: str | Path,
    term: str,
    review_dir: str | Path,
    state_dir: str | Path,
    output_dir: str | Path,
    seed: int | None = None,
) -> LotteryRunResult:
    config: AppConfig = load_config(config_path)
    review_applications = load_review_applications(review_dir)
    locker_state = _load_locker_state(config, state_dir)
    processing_date = date.today().isoformat()

    result_rows: list[dict[str, str]] = []
    log_rows: list[dict[str, str]] = []
    winners_by_locker: dict[str, ReviewApplication] = {}

    applications_by_floor: dict[str, list[ReviewApplication]] = {floor: [] for floor in config.floors}
    for application in review_applications:
        if application.manual_status == "keep":
            applications_by_floor.setdefault(application.floor, []).append(application)

    for floor in config.floors:
        floor_applications = applications_by_floor.get(floor, [])
        open_lockers = _open_lockers_for_floor(config, locker_state, floor)
        floor_winners: list[FloorLotteryWinner] = run_floor_lottery(
            applications=floor_applications,
            open_lockers=open_lockers,
            seed=seed,
        )
        winners_by_application_id = {application.application_id: application for application in floor_applications}

        for winner in floor_winners:
            application = winners_by_application_id[winner.application_id]
            winners_by_locker[winner.locker_number] = application
            result_rows.append(_result_row(application, processing_date, winner.locker_number))
            log_rows.append(_log_row(application, winner.locker_number))

    result_rows.sort(key=lambda row: (row["処理日"], row["割り当てロッカー"]))
    updated_locker_state = _update_locker_state(locker_state, winners_by_locker)

    output_path = Path(output_dir) / term / "lottery"
    result_path = output_path / "result.csv"
    locker_state_path = output_path / "locker_assignments.csv"
    log_path = output_path / "lottery_log.csv"

    _write_csv(result_path, RESULT_COLUMNS, result_rows)
    _write_csv(locker_state_path, LOCKER_STATE_COLUMNS, _locker_rows(updated_locker_state))
    _write_csv(log_path, LOG_COLUMNS, log_rows)

    return LotteryRunResult(
        winner_count=len(result_rows),
        result_path=result_path,
        locker_state_path=locker_state_path,
        log_path=log_path,
    )
