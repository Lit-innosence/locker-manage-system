"""Persistent state helpers for winners and locker assignments."""

from __future__ import annotations

import csv
from pathlib import Path


def load_winner_ids(path: str | Path) -> set[str]:
    csv_path = Path(path)
    with csv_path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        winner_ids: set[str] = set()
        for row in reader:
            applicant_id = row.get("申請者学籍番号", "").strip()
            partner_id = row.get("共同利用者学籍番号", "").strip()
            if applicant_id:
                winner_ids.add(applicant_id)
            if partner_id:
                winner_ids.add(partner_id)

    return winner_ids
