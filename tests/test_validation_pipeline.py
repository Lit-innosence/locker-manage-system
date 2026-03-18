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


def test_classify_application_returns_e1_when_applicant_name_missing():
    application = NormalizedApplication(
        applicant_id="1556822",
        applicant_name="",
        applicant_timestamp="2026-04-01T00:55:10",
        applicant_card_ref="accept",
        requested_floor="5F",
        usage_type="single",
        partner_id="",
        partner_name="",
        partner_timestamp=None,
        partner_card_ref=None,
    )

    assert classify_application(application, winner_ids=set()) == "E1"


def test_classify_application_prioritizes_e2_over_e3():
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

    assert classify_application(application, winner_ids={"1556822"}) == "E2"


def test_classify_application_returns_e3_for_prior_winner():
    application = NormalizedApplication(
        applicant_id="1556822",
        applicant_name="吉田 結衣",
        applicant_timestamp="2026-04-01T00:55:10",
        applicant_card_ref="accept",
        requested_floor="5F",
        usage_type="single",
        partner_id="",
        partner_name="",
        partner_timestamp=None,
        partner_card_ref=None,
    )

    assert classify_application(application, winner_ids={"1556822"}) == "E3"


def test_classify_application_returns_e1_when_requested_floor_missing():
    application = NormalizedApplication(
        applicant_id="1556822",
        applicant_name="吉田 結衣",
        applicant_timestamp="2026-04-01T00:55:10",
        applicant_card_ref="accept",
        requested_floor="",
        usage_type="single",
        partner_id="",
        partner_name="",
        partner_timestamp=None,
        partner_card_ref=None,
    )

    assert classify_application(application, winner_ids=set()) == "E1"


def test_classify_application_returns_e1_when_pair_usage_has_missing_partner_name():
    application = NormalizedApplication(
        applicant_id="1556822",
        applicant_name="吉田 結衣",
        applicant_timestamp="2026-04-01T00:55:10",
        applicant_card_ref="accept",
        requested_floor="5F",
        usage_type="pair",
        partner_id="4162071",
        partner_name="",
        partner_timestamp="2026-04-01T00:44:40",
        partner_card_ref="accept",
    )

    assert classify_application(application, winner_ids=set()) == "E1"


def test_classify_application_returns_e1_when_usage_type_is_invalid():
    application = NormalizedApplication(
        applicant_id="1556822",
        applicant_name="吉田 結衣",
        applicant_timestamp="2026-04-01T00:55:10",
        applicant_card_ref="accept",
        requested_floor="5F",
        usage_type="group",
        partner_id="",
        partner_name="",
        partner_timestamp=None,
        partner_card_ref=None,
    )

    assert classify_application(application, winner_ids=set()) == "E1"


def test_classify_application_returns_e3_for_prior_partner_winner():
    application = NormalizedApplication(
        applicant_id="1556822",
        applicant_name="吉田 結衣",
        applicant_timestamp="2026-04-01T00:55:10",
        applicant_card_ref="accept",
        requested_floor="5F",
        usage_type="pair",
        partner_id="4162071",
        partner_name="中村 稔",
        partner_timestamp="2026-04-01T00:44:40",
        partner_card_ref="accept",
    )

    assert classify_application(application, winner_ids={"4162071"}) == "E3"
