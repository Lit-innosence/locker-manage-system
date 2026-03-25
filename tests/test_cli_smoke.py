from locker_manage_system.cli import build_parser
from locker_manage_system.main import main


def test_parser_exposes_validate_and_lottery_commands():
    parser = build_parser()
    subparsers = parser._subparsers._group_actions[0]
    assert {"validate", "lottery"}.issubset(subparsers.choices.keys())


def test_parser_uses_default_paths_for_validate():
    parser = build_parser()

    args = parser.parse_args(["validate", "--term", "2026-04-01..2026-04-07"])

    assert args.config == "config/default.yml"
    assert args.input_dir == "input"
    assert args.output_dir == "output"
    assert args.state_dir is None


def test_parser_uses_default_paths_for_lottery():
    parser = build_parser()

    args = parser.parse_args(["lottery", "--term", "2026-04-01..2026-04-07"])

    assert args.config == "config/default.yml"
    assert args.output_dir == "output"
    assert args.review_dir is None
    assert args.state_dir is None


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


def test_main_resolves_default_validate_paths_from_term(monkeypatch):
    called = {}

    def fake_run_validate(**kwargs):
        called.update(kwargs)
        return None

    monkeypatch.setattr("locker_manage_system.main.run_validate", fake_run_validate)

    exit_code = main(["validate", "--term", "2026-04-01..2026-04-07"])

    assert exit_code == 0
    assert called == {
        "config_path": "config/default.yml",
        "term": "2026-04-01..2026-04-07",
        "input_dir": "input",
        "state_dir": "output/state/2026",
        "output_dir": "output",
    }


def test_main_resolves_default_lottery_paths_from_term(monkeypatch):
    called = {}

    def fake_run_lottery(**kwargs):
        called.update(kwargs)
        return None

    monkeypatch.setattr("locker_manage_system.main.run_lottery", fake_run_lottery)

    exit_code = main(["lottery", "--term", "2026-04-01..2026-04-07"])

    assert exit_code == 0
    assert called == {
        "config_path": "config/default.yml",
        "term": "2026-04-01..2026-04-07",
        "review_dir": "output/2026-04-01..2026-04-07/review",
        "state_dir": "output/state/2026",
        "output_dir": "output",
        "seed": None,
    }


def test_main_interactively_dispatches_validate_when_no_args(monkeypatch):
    called = {}
    answers = iter(["validate", "2026-04-01", "2026-04-07"])

    def fake_input(prompt):
        return next(answers)

    def fake_run_validate(**kwargs):
        called.update(kwargs)
        return None

    monkeypatch.setattr("builtins.input", fake_input)
    monkeypatch.setattr("locker_manage_system.main.run_validate", fake_run_validate)

    exit_code = main([])

    assert exit_code == 0
    assert called == {
        "config_path": "config/default.yml",
        "term": "2026-04-01..2026-04-07",
        "input_dir": "input",
        "state_dir": "output/state/2026",
        "output_dir": "output",
    }


def test_main_interactively_retries_on_invalid_entries(monkeypatch, capsys):
    called = {}
    answers = iter(
        ["bad", "lottery", "2026/04/01", "2026-04-01", "2026-03-31", "2026-04-01", "2026-04-07"]
    )

    def fake_input(prompt):
        return next(answers)

    def fake_run_lottery(**kwargs):
        called.update(kwargs)
        return None

    monkeypatch.setattr("builtins.input", fake_input)
    monkeypatch.setattr("locker_manage_system.main.run_lottery", fake_run_lottery)

    exit_code = main([])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "validate または lottery" in captured.out
    assert "YYYY-MM-DD" in captured.out
    assert "終了日は開始日以降" in captured.out
    assert called["term"] == "2026-04-01..2026-04-07"
