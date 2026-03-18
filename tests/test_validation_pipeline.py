from locker_manage_system.models import NormalizedApplication
from locker_manage_system.validation_pipeline import classify_application


def test_classify_application_returns_e2_when_partner_submission_missing():
    application = NormalizedApplication(
        applicant_id="1556822",
        applicant_name="吉田 結衣",
        applicant_timestamp="2026-04-01T00:55:10",
        applicant_card_ref="accept",
        requested_floor="5F",
        usage_type="pair",
        partner_id="4162071",
        partner_name="中村 稔",
        partner_timestamp=None,
        partner_card_ref=None,
    )

    assert classify_application(application, winner_ids=set()) == "E2"
