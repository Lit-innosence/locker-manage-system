"""Validation helper rules used by the application pipeline."""

from __future__ import annotations

import re

STUDENT_ID_PATTERN = re.compile(r"^(15\d{5}|[48][1-6]\d{5})$")
PAIR_ONLY_FLOORS = {"2F", "3F"}
SINGLE_ONLY_FLOORS = {"4F", "5F", "6F"}


def validate_student_id(student_id: str) -> bool:
    return bool(STUDENT_ID_PATTERN.fullmatch(student_id))


def validate_floor_usage(requested_floor: str, usage_type: str) -> bool:
    if requested_floor in PAIR_ONLY_FLOORS:
        return usage_type == "pair"
    if requested_floor in SINGLE_ONLY_FLOORS:
        return usage_type == "single"
    return False
