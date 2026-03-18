"""Validation helper rules used by the application pipeline."""

from __future__ import annotations

import re

STUDENT_ID_PATTERN = re.compile(r"^(15\d{5}|[48][1-6]\d{5})$")


def validate_student_id(student_id: str) -> bool:
    return bool(STUDENT_ID_PATTERN.fullmatch(student_id))
