from locker_manage_system.cli import build_parser
from locker_manage_system.main import main


def test_parser_exposes_validate_and_lottery_commands():
    parser = build_parser()
    subparsers = parser._subparsers._group_actions[0]
    assert {"validate", "lottery"}.issubset(subparsers.choices.keys())


def test_main_dispatches_validate_command(monkeypatch, tmp_path):
    called = {}

    def fake_run_validate(**kwargs):
        called.update(kwargs)
        return None

    monkeypatch.setattr("locker_manage_system.main.run_validate", fake_run_validate)

    exit_code = main(
        [
            "validate",
            "--config",
            str(tmp_path / "config.yml"),
            "--term",
            "term1",
            "--input-dir",
            str(tmp_path / "input"),
            "--state-dir",
            str(tmp_path / "state"),
            "--output-dir",
            str(tmp_path / "output"),
        ]
    )

    assert exit_code == 0
    assert called["term"] == "term1"


def test_main_dispatches_lottery_command(monkeypatch, tmp_path):
    called = {}

    def fake_run_lottery(**kwargs):
        called.update(kwargs)
        return None

    monkeypatch.setattr("locker_manage_system.main.run_lottery", fake_run_lottery)

    exit_code = main(
        [
            "lottery",
            "--config",
            str(tmp_path / "config.yml"),
            "--term",
            "term1",
            "--review-dir",
            str(tmp_path / "review"),
            "--state-dir",
            str(tmp_path / "state"),
            "--output-dir",
            str(tmp_path / "output"),
        ]
    )

    assert exit_code == 0
    assert called["review_dir"] == str(tmp_path / "review")
