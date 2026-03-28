"""Shared data models for normalized input rows."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ApplicantRow:
    timestamp: str
    applicant_id: str
    applicant_name: str
    applicant_card_ref: str
    usage_label: str
    partner_id: str
    partner_name: str
    requested_floor: str


@dataclass(frozen=True)
class NormalizedApplication:
    applicant_id: str
    applicant_name: str
    applicant_timestamp: str
    applicant_card_ref: str
    requested_floor: str
    usage_type: str
    partner_id: str
    partner_name: str
    partner_timestamp: str | None
    partner_card_ref: str | None
