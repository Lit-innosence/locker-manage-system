from pathlib import Path
import csv

from locker_manage_system.lottery_command import run_lottery


def _write_review_csv(path: Path) -> None:
    path.write_text(
        "申請者学籍番号,申請者氏名,共同利用者学籍番号,共同利用者氏名,requested_floor,usage_type,manual_status\n"
        "1520001,山田 太郎,,,4F,single,keep\n"
        "1520002,山田 二郎,,,4F,single,reject\n",
        encoding="utf-8",
    )


def _write_state_csv(path: Path) -> None:
    path.write_text(
        "ロッカー番号,割り当て状態\n"
        "4001,\n"
        "4002,\n",
        encoding="utf-8",
    )


def test_run_lottery_uses_only_manual_keep_rows(tmp_path):
    review_dir = tmp_path / "output" / "term1" / "review"
    state_dir = tmp_path / "state"
    output_dir = tmp_path / "output"
    review_dir.mkdir(parents=True)
    state_dir.mkdir()

    _write_review_csv(review_dir / "review_4F.csv")
    _write_state_csv(state_dir / "locker_assignments.csv")

    config_path = tmp_path / "config.yml"
    config_path.write_text(
        "year: 2026\n"
        "floors:\n"
        "  4F:\n"
        "    capacity: 240\n"
        "    occupancy: single_only\n"
        "    locker_start: 4001\n"
        "    locker_end: 4002\n",
        encoding="utf-8",
    )

    result = run_lottery(
        config_path=config_path,
        term="term1",
        review_dir=review_dir,
        state_dir=state_dir,
        output_dir=output_dir,
    )

    assert result.winner_count == 1

    with (tmp_path / "output" / "term1" / "lottery" / "result.csv").open(
        "r", encoding="utf-8", newline=""
    ) as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert [row["申請者学籍番号"] for row in rows] == ["1520001"]
    assert (tmp_path / "output" / "term1" / "lottery" / "locker_assignments.csv").exists()
    assert (tmp_path / "output" / "term1" / "lottery" / "lottery_log.csv").exists()
