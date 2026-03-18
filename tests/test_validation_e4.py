from locker_manage_system.validation_pipeline import (
    DuplicateApplication,
    resolve_duplicate_applications,
)


def test_resolve_duplicate_applications_prefers_earliest_conflicting_pair():
    applications = [
        DuplicateApplication(
            application_id="pair-a",
            applicant_id="1000001",
            applicant_timestamp="2026-04-01T09:00:00",
            usage_type="pair",
            partner_id="2000001",
            partner_timestamp="2026-04-01T09:05:00",
        ),
        DuplicateApplication(
            application_id="pair-b",
            applicant_id="1000001",
            applicant_timestamp="2026-04-01T09:10:00",
            usage_type="pair",
            partner_id="2000002",
            partner_timestamp="2026-04-01T09:15:00",
        ),
    ]

    resolved = resolve_duplicate_applications(applications)

    assert resolved.accepted_application_ids == {"pair-a"}
    assert resolved.rejected_codes["pair-b"] == "E4"


def test_resolve_duplicate_applications_prefers_latest_single_submission():
    applications = [
        DuplicateApplication(
            application_id="single-a",
            applicant_id="3000001",
            applicant_timestamp="2026-04-01T09:00:00",
            usage_type="single",
        ),
        DuplicateApplication(
            application_id="single-b",
            applicant_id="3000001",
            applicant_timestamp="2026-04-01T10:00:00",
            usage_type="single",
        ),
    ]

    resolved = resolve_duplicate_applications(applications)

    assert resolved.accepted_application_ids == {"single-b"}
    assert resolved.rejected_codes["single-a"] == "E4"


def test_resolve_duplicate_applications_prefers_latest_submission_across_types():
    applications = [
        DuplicateApplication(
            application_id="single-a",
            applicant_id="3000001",
            applicant_timestamp="2026-04-01T09:00:00",
            usage_type="single",
        ),
        DuplicateApplication(
            application_id="pair-b",
            applicant_id="3000001",
            applicant_timestamp="2026-04-01T10:00:00",
            usage_type="pair",
            partner_id="4000001",
            partner_timestamp="2026-04-01T10:05:00",
        ),
    ]

    resolved = resolve_duplicate_applications(applications)

    assert resolved.accepted_application_ids == {"pair-b"}
    assert resolved.rejected_codes["single-a"] == "E4"


def test_resolve_duplicate_applications_prefers_latest_identical_pair_resubmission():
    applications = [
        DuplicateApplication(
            application_id="pair-a",
            applicant_id="1000001",
            applicant_timestamp="2026-04-01T09:00:00",
            usage_type="pair",
            partner_id="2000001",
            partner_timestamp="2026-04-01T09:05:00",
        ),
        DuplicateApplication(
            application_id="pair-b",
            applicant_id="1000001",
            applicant_timestamp="2026-04-01T10:00:00",
            usage_type="pair",
            partner_id="2000001",
            partner_timestamp="2026-04-01T10:05:00",
        ),
    ]

    resolved = resolve_duplicate_applications(applications)

    assert resolved.accepted_application_ids == {"pair-b"}
    assert resolved.rejected_codes["pair-a"] == "E4"
