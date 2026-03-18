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


def _pair_sort_key(application: DuplicateApplication) -> tuple[datetime, datetime, str]:
    primary_timestamp = application.partner_timestamp or application.applicant_timestamp
    return (
        _parse_timestamp(primary_timestamp),
        _parse_timestamp(application.applicant_timestamp),
        application.application_id,
    )


def _submission_key(application: DuplicateApplication) -> tuple[datetime, datetime, str]:
    if application.usage_type == "pair":
        return _pair_sort_key(application)
    applicant_time = _parse_timestamp(application.applicant_timestamp)
    return (applicant_time, applicant_time, application.application_id)


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

    latest_single_by_person: dict[str, DuplicateApplication] = {}
    earliest_pair_by_person: dict[str, DuplicateApplication] = {}

    for application in sorted(applications, key=_submission_key):
        if application.usage_type == "single":
            latest_single_by_person[application.applicant_id] = application
            continue

        involved_people = [application.applicant_id]
        if application.partner_id:
            involved_people.append(application.partner_id)

        for person_id in involved_people:
            earliest_pair_by_person.setdefault(person_id, application)

    chosen_application_by_person: dict[str, DuplicateApplication] = {}
    all_people = set(latest_single_by_person) | set(earliest_pair_by_person)
    for person_id in all_people:
        single_application = latest_single_by_person.get(person_id)
        pair_application = earliest_pair_by_person.get(person_id)

        if single_application and pair_application:
            if _submission_key(single_application) >= _submission_key(pair_application):
                chosen_application_by_person[person_id] = single_application
            else:
                chosen_application_by_person[person_id] = pair_application
        elif single_application:
            chosen_application_by_person[person_id] = single_application
        elif pair_application:
            chosen_application_by_person[person_id] = pair_application

    for application in applications:
        involved_people = [application.applicant_id]
        if application.usage_type == "pair" and application.partner_id:
            involved_people.append(application.partner_id)

        if all(chosen_application_by_person.get(person_id) == application for person_id in involved_people):
            accepted_application_ids.add(application.application_id)
            continue

        rejected_codes[application.application_id] = "E4"

    return DuplicateResolution(
        accepted_application_ids=accepted_application_ids,
        rejected_codes=rejected_codes,
    )
