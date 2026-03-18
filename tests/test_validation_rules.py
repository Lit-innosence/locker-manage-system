from locker_manage_system.validation_rules import validate_student_id


def test_validate_student_id_accepts_allowed_patterns():
    assert validate_student_id("1588184") is True
    assert validate_student_id("4654293") is True
    assert validate_student_id("8654293") is True
    assert validate_student_id("2032044") is False
