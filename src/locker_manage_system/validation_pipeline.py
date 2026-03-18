"""Validation pipeline for classifying applications."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .models import NormalizedApplication
from .validation_rules import validate_floor_usage, validate_student_id

ALLOWED_FLOORS = {"2F", "3F", "4F", "5F", "6F"}
ALLOWED_USAGE_TYPES = {"single", "pair"}


@dataclass(frozen=True)
class DuplicateApplication:
    application_id: str
    applicant_id: str
    applicant_timestamp: str
    usage_type: str
    partner_id: str | None = None
    partner_timestamp: str | None = None


@dataclass(frozen=True)
class DuplicateResolution:
    accepted_application_ids: set[str]
    rejected_codes: dict[str, str]


def _has_required_pair_submission(application: NormalizedApplication) -> bool:
    return bool(application.partner_timestamp and application.partner_card_ref)


def _is_blank(value: str | None) -> bool:
    return value is None or not str(value).strip()


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace(" ", "T"))


def _single_sort_key(application: DuplicateApplication) -> tuple[datetime, str]:
    return (_parse_timestamp(application.applicant_timestamp), application.application_id)


def _pair_sort_key(application: DuplicateApplication) -> tuple[datetime, datetime, str]:
    primary_timestamp = application.partner_timestamp or application.applicant_timestamp
    return (
        _parse_timestamp(primary_timestamp),
        _parse_timestamp(application.applicant_timestamp),
        application.application_id,
    )


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

    if not validate_floor_usage(application.requested_floor, application.usage_type):
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


def resolve_duplicate_applications(
    applications: list[DuplicateApplication],
) -> DuplicateResolution:
    accepted_application_ids: set[str] = set()
    rejected_codes: dict[str, str] = {}

    single_applications = [app for app in applications if app.usage_type == "single"]
    pair_applications = [app for app in applications if app.usage_type == "pair"]

    latest_single_by_applicant: dict[str, DuplicateApplication] = {}
    for application in sorted(single_applications, key=_single_sort_key):
        latest_single_by_applicant[application.applicant_id] = application

    accepted_people: set[str] = set()
    for application in latest_single_by_applicant.values():
        accepted_application_ids.add(application.application_id)
        accepted_people.add(application.applicant_id)

    for application in sorted(pair_applications, key=_pair_sort_key):
        if application.applicant_id in accepted_people:
            rejected_codes[application.application_id] = "E4"
            continue
        if application.partner_id and application.partner_id in accepted_people:
            rejected_codes[application.application_id] = "E4"
            continue

        accepted_application_ids.add(application.application_id)
        accepted_people.add(application.applicant_id)
        if application.partner_id:
            accepted_people.add(application.partner_id)

    for application in single_applications:
        if application.application_id not in accepted_application_ids:
            rejected_codes[application.application_id] = "E4"

    return DuplicateResolution(
        accepted_application_ids=accepted_application_ids,
        rejected_codes=rejected_codes,
    )
