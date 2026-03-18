"""CSV readers for Google Form exports."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .models import ApplicantRow

APPLICANT_REQUIRED_COLUMNS = {
    "タイムスタンプ",
    "申請者の学籍番号",
    "申請者の氏名",
    "申請者の学生証写真",
    "共同利用者の有無",
    "共同利用者の学籍番号",
    "共同利用者の氏名",
    "階数希望選択（共同利用者なし）",
    "階数希望選択（共同利用者あり）",
}

PARTNER_REQUIRED_COLUMNS = {
    "タイムスタンプ",
    "共同利用者の学籍番号",
    "共同利用者の氏名",
    "共同利用者の学生証写真",
}


@dataclass(frozen=True)
class ApplicantInput:
    raw_row: dict[str, str]
    model: ApplicantRow


def _normalize_floor(value: str) -> str:
    return value.replace("階", "F").strip()


def load_applicant_inputs(path: str | Path) -> tuple[list[str], list[ApplicantInput]]:
    csv_path = Path(path)
    with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        missing_columns = APPLICANT_REQUIRED_COLUMNS.difference(reader.fieldnames or [])
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"Applicant CSV is missing required columns: {missing}")

        rows: list[ApplicantInput] = []
        for row in reader:
            floor = row["階数希望選択（共同利用者なし）"] or row["階数希望選択（共同利用者あり）"]
            rows.append(
                ApplicantInput(
                    raw_row=row,
                    model=ApplicantRow(
                        timestamp=row["タイムスタンプ"],
                        applicant_id=row["申請者の学籍番号"],
                        applicant_name=row["申請者の氏名"],
                        applicant_card_ref=row["申請者の学生証写真"],
                        usage_label=row["共同利用者の有無"],
                        partner_id=row["共同利用者の学籍番号"],
                        partner_name=row["共同利用者の氏名"],
                        requested_floor=_normalize_floor(floor),
                    ),
                )
            )

    return list(reader.fieldnames or []), rows


def load_applicants_csv(path: str | Path) -> list[ApplicantRow]:
    return [item.model for item in load_applicant_inputs(path)[1]]


def load_partner_inputs(path: str | Path) -> tuple[list[str], list[dict[str, str]]]:
    csv_path = Path(path)
    with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        missing_columns = PARTNER_REQUIRED_COLUMNS.difference(reader.fieldnames or [])
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"Partner CSV is missing required columns: {missing}")

        rows = [row for row in reader]

    return list(reader.fieldnames or []), rows
