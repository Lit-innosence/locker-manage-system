"""CSV readers for Google Form exports."""

from __future__ import annotations

import csv
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


def _normalize_floor(value: str) -> str:
    return value.replace("階", "F").strip()


def load_applicants_csv(path: str | Path) -> list[ApplicantRow]:
    csv_path = Path(path)
    with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        missing_columns = APPLICANT_REQUIRED_COLUMNS.difference(reader.fieldnames or [])
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"Applicant CSV is missing required columns: {missing}")

        rows: list[ApplicantRow] = []
        for row in reader:
            floor = row["階数希望選択（共同利用者なし）"] or row["階数希望選択（共同利用者あり）"]
            rows.append(
                ApplicantRow(
                    timestamp=row["タイムスタンプ"],
                    applicant_id=row["申請者の学籍番号"],
                    applicant_name=row["申請者の氏名"],
                    applicant_card_ref=row["申請者の学生証写真"],
                    usage_label=row["共同利用者の有無"],
                    partner_id=row["共同利用者の学籍番号"],
                    partner_name=row["共同利用者の氏名"],
                    requested_floor=_normalize_floor(floor),
                )
            )

    return rows
