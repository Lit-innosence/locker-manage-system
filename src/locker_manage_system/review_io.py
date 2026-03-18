"""Readers for human-reviewed validation outputs."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ReviewApplication:
    application_id: str
    floor: str
    applicant_id: str
    applicant_name: str
    partner_id: str
    partner_name: str
    requested_floor: str
    usage_type: str
    manual_status: str
    source_row: dict[str, str]


def _normalize_floor_name(path: Path) -> str:
    stem = path.stem
    if stem.startswith("review_"):
        return stem.removeprefix("review_")
    return stem


def load_review_applications(review_dir: str | Path) -> list[ReviewApplication]:
    review_path = Path(review_dir)
    applications: list[ReviewApplication] = []

    for csv_path in sorted(review_path.glob("review_*.csv")):
        floor = _normalize_floor_name(csv_path)
        with csv_path.open("r", encoding="utf-8", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for index, row in enumerate(reader, start=1):
                applications.append(
                    ReviewApplication(
                        application_id=f"{floor}-{index}",
                        floor=floor,
                        applicant_id=row.get("申請者学籍番号", "").strip(),
                        applicant_name=row.get("申請者氏名", "").strip(),
                        partner_id=row.get("共同利用者学籍番号", "").strip(),
                        partner_name=row.get("共同利用者氏名", "").strip(),
                        requested_floor=row.get("requested_floor", floor).strip() or floor,
                        usage_type=row.get("usage_type", "").strip(),
                        manual_status=row.get("manual_status", "").strip(),
                        source_row=row,
                    )
                )

    return applications
