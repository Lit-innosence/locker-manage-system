"""Validation pipeline for classifying applications."""

from __future__ import annotations

from .models import NormalizedApplication
from .validation_rules import validate_student_id


def _has_required_pair_submission(application: NormalizedApplication) -> bool:
    return bool(application.partner_timestamp and application.partner_card_ref)


def classify_application(
    application: NormalizedApplication,
    winner_ids: set[str],
) -> str:
    if not validate_student_id(application.applicant_id):
        return "E1"

    if application.usage_type == "pair":
        if not validate_student_id(application.partner_id):
            return "E1"
        if not _has_required_pair_submission(application):
            return "E2"

    if application.applicant_id in winner_ids:
        return "E3"

    if application.usage_type == "pair" and application.partner_id in winner_ids:
        return "E3"

    return "S0"
