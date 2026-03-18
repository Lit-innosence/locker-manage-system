"""Validation pipeline for classifying applications."""

from __future__ import annotations

from .models import NormalizedApplication
from .validation_rules import validate_student_id

ALLOWED_FLOORS = {"2F", "3F", "4F", "5F", "6F"}
ALLOWED_USAGE_TYPES = {"single", "pair"}


def _has_required_pair_submission(application: NormalizedApplication) -> bool:
    return bool(application.partner_timestamp and application.partner_card_ref)


def _is_blank(value: str | None) -> bool:
    return value is None or not str(value).strip()


def classify_application(
    application: NormalizedApplication,
    winner_ids: set[str],
) -> str:
    if any(
        _is_blank(value)
        for value in (
            application.applicant_id,
            application.applicant_name,
            application.applicant_timestamp,
            application.applicant_card_ref,
            application.requested_floor,
            application.usage_type,
        )
    ):
        return "E1"

    if not validate_student_id(application.applicant_id):
        return "E1"

    if application.requested_floor not in ALLOWED_FLOORS:
        return "E1"

    if application.usage_type not in ALLOWED_USAGE_TYPES:
        return "E1"

    if application.usage_type == "pair":
        if _is_blank(application.partner_id) or _is_blank(application.partner_name):
            return "E1"
        if not validate_student_id(application.partner_id):
            return "E1"
        if not _has_required_pair_submission(application):
            return "E2"

    if application.applicant_id in winner_ids:
        return "E3"

    if application.usage_type == "pair" and application.partner_id in winner_ids:
        return "E3"

    return "S0"
