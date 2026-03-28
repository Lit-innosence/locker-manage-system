from locker_manage_system.csv_io import load_applicants_csv


def test_load_applicants_csv_resolves_floor_from_either_column(tmp_path):
    path = tmp_path / "applicants.csv"
    path.write_text(
        "\ufeffタイムスタンプ,申請者の学籍番号,申請者の氏名,申請者の学生証写真,共同利用者の有無,共同利用者の学籍番号,共同利用者の氏名,階数希望選択（共同利用者なし）,階数希望選択（共同利用者あり）\n"
        "2026-04-01 00:00:00,4654293,藤田 治,accept,共同利用者なし,,,,4階,\n",
        encoding="utf-8",
    )

    rows = load_applicants_csv(path)

    assert rows[0].requested_floor == "4F"
