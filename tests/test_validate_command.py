from pathlib import Path
import csv

from locker_manage_system.validate_command import run_validate


def _write_applicant_csv(path: Path) -> None:
    path.write_text(
        "タイムスタンプ,メールアドレス,規約への同意,申請者の学籍番号,申請者の氏名,申請者の学生証写真,共同利用者の有無,共同利用者の学籍番号,共同利用者の氏名,階数希望選択（共同利用者なし）,階数希望選択（共同利用者あり）\n"
        "2026-04-01 00:00:00,test@example.com,利用規約に同意する,1520001,山田 太郎,accept,共同利用者なし (2階・3階のロッカーは使用できません),,,4階,\n",
        encoding="utf-8",
    )


def _write_partner_csv(path: Path) -> None:
    path.write_text(
        "タイムスタンプ,メールアドレス,規約への同意,共同利用者の学籍番号,共同利用者の氏名,共同利用者の学生証写真\n"
        "2026-04-01 00:30:00,partner@example.com,利用規約に同意する,1620001,佐藤 花子,accept\n",
        encoding="utf-8",
    )


def test_run_validate_writes_validation_and_review_outputs(tmp_path):
    input_dir = tmp_path / "input"
    state_dir = tmp_path / "state"
    output_dir = tmp_path / "output"
    term = "term1"
    input_dir.mkdir()
    state_dir.mkdir()

    _write_applicant_csv(input_dir / "applicant_data.csv")
    _write_partner_csv(input_dir / "partner_data.csv")

    config_path = tmp_path / "config.yml"
    config_path.write_text(
        "year: 2026\n"
        "paths:\n"
        "  input_dir: input\n"
        "  state_dir: state\n"
        "  output_dir: output\n"
        "floors:\n"
        "  2F:\n"
        "    capacity: 420\n"
        "    occupancy: pair_only\n"
        "    locker_start: 2001\n"
        "    locker_end: 2420\n"
        "  3F:\n"
        "    capacity: 240\n"
        "    occupancy: pair_only\n"
        "    locker_start: 3001\n"
        "    locker_end: 3240\n"
        "  4F:\n"
        "    capacity: 240\n"
        "    occupancy: single_only\n"
        "    locker_start: 4001\n"
        "    locker_end: 4240\n"
        "  5F:\n"
        "    capacity: 240\n"
        "    occupancy: single_only\n"
        "    locker_start: 5001\n"
        "    locker_end: 5240\n"
        "  6F:\n"
        "    capacity: 240\n"
        "    occupancy: single_only\n"
        "    locker_start: 6001\n"
        "    locker_end: 6240\n",
        encoding="utf-8",
    )

    result = run_validate(
        config_path=config_path,
        term=term,
        input_dir=input_dir,
        state_dir=state_dir,
        output_dir=output_dir,
    )

    assert result.term == term
    assert (tmp_path / "output/term1/validation/valid_4F.csv").exists()
    assert (tmp_path / "output/term1/review/review_4F.csv").exists()


def test_run_validate_sorts_valid_rows_by_applicant_id(tmp_path):
    input_dir = tmp_path / "input"
    state_dir = tmp_path / "state"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    state_dir.mkdir()

    input_dir.joinpath("applicant_data.csv").write_text(
        "タイムスタンプ,メールアドレス,規約への同意,申請者の学籍番号,申請者の氏名,申請者の学生証写真,共同利用者の有無,共同利用者の学籍番号,共同利用者の氏名,階数希望選択（共同利用者なし）,階数希望選択（共同利用者あり）\n"
        "2026-04-01 00:00:00,test@example.com,利用規約に同意する,1520002,山田 二郎,accept,共同利用者なし (2階・3階のロッカーは使用できません),,,4階,\n"
        "2026-04-01 00:01:00,test@example.com,利用規約に同意する,1520001,山田 太郎,accept,共同利用者なし (2階・3階のロッカーは使用できません),,,4階,\n",
        encoding="utf-8",
    )
    _write_partner_csv(input_dir / "partner_data.csv")
    config_path = tmp_path / "config.yml"
    config_path.write_text(
        "year: 2026\n"
        "paths:\n"
        "  input_dir: input\n"
        "  state_dir: state\n"
        "  output_dir: output\n"
        "floors:\n"
        "  4F:\n"
        "    capacity: 240\n"
        "    occupancy: single_only\n"
        "    locker_start: 4001\n"
        "    locker_end: 4240\n",
        encoding="utf-8",
    )

    run_validate(
        config_path=config_path,
        term="term1",
        input_dir=input_dir,
        state_dir=state_dir,
        output_dir=output_dir,
    )

    with (tmp_path / "output/term1/validation/valid_4F.csv").open(
        "r", encoding="utf-8", newline=""
    ) as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert [row["申請者学籍番号"] for row in rows] == ["1520001", "1520002"]


def test_run_validate_preserves_invalid_columns(tmp_path):
    input_dir = tmp_path / "input"
    state_dir = tmp_path / "state"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    state_dir.mkdir()

    _write_applicant_csv(input_dir / "applicant_data.csv")
    _write_partner_csv(input_dir / "partner_data.csv")

    config_path = tmp_path / "config.yml"
    config_path.write_text(
        "year: 2026\n"
        "paths:\n"
        "  input_dir: input\n"
        "  state_dir: state\n"
        "  output_dir: output\n"
        "floors:\n"
        "  4F:\n"
        "    capacity: 240\n"
        "    occupancy: single_only\n"
        "    locker_start: 4001\n"
        "    locker_end: 4240\n",
        encoding="utf-8",
    )

    run_validate(
        config_path=config_path,
        term="term1",
        input_dir=input_dir,
        state_dir=state_dir,
        output_dir=output_dir,
    )

    with (tmp_path / "output/term1/validation/invalid_app.csv").open(
        "r", encoding="utf-8", newline=""
    ) as csv_file:
        app_rows = list(csv.DictReader(csv_file))

    with (tmp_path / "output/term1/validation/invalid_par.csv").open(
        "r", encoding="utf-8", newline=""
    ) as csv_file:
        par_rows = list(csv.DictReader(csv_file))

    assert "メールアドレス" in app_rows[0]
    assert "規約への同意" in app_rows[0]
    assert "結果" in app_rows[0]
    assert "メールアドレス" in par_rows[0]
    assert "規約への同意" in par_rows[0]
    assert "結果" in par_rows[0]
