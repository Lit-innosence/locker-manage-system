from locker_manage_system.cli import build_parser


def test_parser_exposes_validate_and_lottery_commands():
    parser = build_parser()
    subparsers = parser._subparsers._group_actions[0]
    assert {"validate", "lottery"}.issubset(subparsers.choices.keys())
