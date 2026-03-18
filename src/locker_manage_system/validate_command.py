"""Validation workflow for weekly locker applications."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .config import AppConfig, load_config
from .models import ApplicantRow, NormalizedApplication
from .state import load_winner_ids
from .validation_pipeline import (
    DuplicateApplication,
    classify_application,
    resolve_duplicate_applications,
)


VALIDATION_COLUMNS = [
    "申請者学籍番号",
    "申請者氏名",
    "共同利用者学籍番号",
    "共同利用者氏名",
]

REVIEW_COLUMNS = [
    "申請者学籍番号",
    "申請者氏名",
    "共同利用者学籍番号",
    "共同利用者氏名",
    "requested_floor",
    "usage_type",
    "manual_status",
]

@dataclass(frozen=True)
class ValidationResult:
    term: str
    validation_dir: Path
    review_dir: Path


@dataclass(frozen=True)
class _Candidate:
    application_id: str
    normalized: NormalizedApplication
    raw_input_row: dict[str, str]


@dataclass(frozen=True)
class _ApplicantInput:
    raw_row: dict[str, str]
    model: ApplicantRow


def _load_applicant_inputs(path: Path) -> tuple[list[str], list[_ApplicantInput]]:
    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = list(reader.fieldnames or [])
        inputs: list[_ApplicantInput] = []
        for row in reader:
            floor = row["階数希望選択（共同利用者なし）"] or row["階数希望選択（共同利用者あり）"]
            inputs.append(
                _ApplicantInput(
                    raw_row=row,
                    model=ApplicantRow(
                        timestamp=row["タイムスタンプ"],
                        applicant_id=row["申請者の学籍番号"],
                        applicant_name=row["申請者の氏名"],
                        applicant_card_ref=row["申請者の学生証写真"],
                        usage_label=row["共同利用者の有無"],
                        partner_id=row["共同利用者の学籍番号"],
                        partner_name=row["共同利用者の氏名"],
                        requested_floor=floor.replace("階", "F").strip(),
                    ),
                )
            )

    return fieldnames, inputs


def _load_partner_inputs(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        return [], []

    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = list(reader.fieldnames or [])
        partner_rows = [row for row in reader]

    return fieldnames, partner_rows


def _normalize_application(
    row: ApplicantRow,
    partner_rows: dict[str, dict[str, str]],
) -> NormalizedApplication:
    is_pair = "共同利用者あり" in row.usage_label
    partner_row = partner_rows.get(row.partner_id, {}) if is_pair else {}

    return NormalizedApplication(
        applicant_id=row.applicant_id,
        applicant_name=row.applicant_name,
        applicant_timestamp=row.timestamp,
        applicant_card_ref=row.applicant_card_ref,
        requested_floor=row.requested_floor,
        usage_type="pair" if is_pair else "single",
        partner_id=row.partner_id if is_pair else "",
        partner_name=row.partner_name if is_pair else "",
        partner_timestamp=partner_row.get("タイムスタンプ") if is_pair else None,
        partner_card_ref=partner_row.get("共同利用者の学生証写真") if is_pair else None,
    )


def _load_state_winner_ids(state_dir: Path, year: int) -> set[str]:
    for candidate in (
        state_dir / str(year) / "winners.csv",
        state_dir / "winners.csv",
    ):
        if candidate.exists():
            return load_winner_ids(candidate)
    return set()


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _valid_row(application: NormalizedApplication) -> dict[str, str]:
    return {
        "申請者学籍番号": application.applicant_id,
        "申請者氏名": application.applicant_name,
        "共同利用者学籍番号": application.partner_id if application.usage_type == "pair" else "",
        "共同利用者氏名": application.partner_name if application.usage_type == "pair" else "",
    }


def _review_row(application: NormalizedApplication) -> dict[str, str]:
    return {
        "申請者学籍番号": application.applicant_id,
        "申請者氏名": application.applicant_name,
        "共同利用者学籍番号": application.partner_id if application.usage_type == "pair" else "",
        "共同利用者氏名": application.partner_name if application.usage_type == "pair" else "",
        "requested_floor": application.requested_floor,
        "usage_type": application.usage_type,
        "manual_status": "",
    }


def _floor_from_application(application: NormalizedApplication) -> str:
    return application.requested_floor


def run_validate(
    *,
    config_path: str | Path,
    term: str,
    input_dir: str | Path,
    state_dir: str | Path,
    output_dir: str | Path,
) -> ValidationResult:
    config: AppConfig = load_config(config_path)
    input_path = Path(input_dir)
    state_path = Path(state_dir)
    output_path = Path(output_dir) / term

    applicant_fieldnames, applicant_inputs = _load_applicant_inputs(input_path / "applicant_data.csv")
    partner_fieldnames, partner_inputs = _load_partner_inputs(input_path / "partner_data.csv")
    partner_lookup = {
        row.get("共同利用者の学籍番号", "").strip(): row
        for row in partner_inputs
        if row.get("共同利用者の学籍番号", "").strip()
    }
    winner_ids = _load_state_winner_ids(state_path, config.year)

    candidates: list[_Candidate] = []
    for index, applicant_input in enumerate(applicant_inputs, start=1):
        row = applicant_input.model
        candidates.append(
            _Candidate(
                application_id=f"{term}-{index}",
                normalized=_normalize_application(row, partner_lookup),
                raw_input_row=applicant_input.raw_row,
            )
        )

    duplicate_resolution = resolve_duplicate_applications(
        [
            DuplicateApplication(
                application_id=candidate.application_id,
                applicant_id=candidate.normalized.applicant_id,
                applicant_timestamp=candidate.normalized.applicant_timestamp,
                usage_type=candidate.normalized.usage_type,
                partner_id=candidate.normalized.partner_id or None,
                partner_timestamp=candidate.normalized.partner_timestamp,
            )
            for candidate in candidates
        ]
    )

    validation_rows_by_floor: dict[str, list[dict[str, str]]] = {floor: [] for floor in config.floors}
    review_rows_by_floor: dict[str, list[dict[str, str]]] = {floor: [] for floor in config.floors}
    applicant_output_rows: list[dict[str, str]] = []
    partner_result_by_id: dict[str, str] = {}

    for candidate in candidates:
        result_code = classify_application(candidate.normalized, winner_ids)
        if result_code == "S0" and candidate.application_id in duplicate_resolution.rejected_codes:
            result_code = duplicate_resolution.rejected_codes[candidate.application_id]

        if candidate.normalized.usage_type == "pair" and candidate.normalized.partner_id:
            partner_result_by_id.setdefault(candidate.normalized.partner_id, result_code)

        applicant_output_rows.append({**candidate.raw_input_row, "結果": result_code})

        if result_code == "S0":
            floor = _floor_from_application(candidate.normalized)
            validation_rows_by_floor[floor].append(_valid_row(candidate.normalized))
            review_rows_by_floor[floor].append(_review_row(candidate.normalized))

    for floor in config.floors:
        validation_rows_by_floor[floor].sort(key=lambda row: row["申請者学籍番号"])
        review_rows_by_floor[floor].sort(key=lambda row: row["申請者学籍番号"])
        _write_csv(
            output_path / "validation" / f"valid_{floor}.csv",
            VALIDATION_COLUMNS,
            validation_rows_by_floor[floor],
        )
        _write_csv(
            output_path / "review" / f"review_{floor}.csv",
            REVIEW_COLUMNS,
            review_rows_by_floor[floor],
        )

    invalid_app_rows = sorted(applicant_output_rows, key=lambda row: row.get("タイムスタンプ", ""))
    invalid_par_rows = [
        {
            **row,
            "結果": partner_result_by_id.get(row.get("共同利用者の学籍番号", "").strip(), "E2"),
        }
        for row in sorted(partner_inputs, key=lambda row: row.get("タイムスタンプ", ""))
    ]

    _write_csv(
        output_path / "validation" / "invalid_app.csv",
        applicant_fieldnames + ["結果"],
        invalid_app_rows,
    )
    _write_csv(
        output_path / "validation" / "invalid_par.csv",
        partner_fieldnames + ["結果"],
        invalid_par_rows,
    )

    return ValidationResult(term=term, validation_dir=output_path / "validation", review_dir=output_path / "review")
