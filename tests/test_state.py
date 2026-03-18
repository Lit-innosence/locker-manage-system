from locker_manage_system.state import load_winner_ids


def test_load_winner_ids_reads_both_applicant_and_partner_ids(tmp_path):
    path = tmp_path / "winners.csv"
    path.write_text(
        "申請者氏名,申請者学籍番号,共同利用者氏名,共同利用者学籍番号,処理日,割り当てロッカー\n"
        "吉田 結衣,1556822,中村 稔,4162071,2026-04-01,5001\n",
        encoding="utf-8",
    )

    assert load_winner_ids(path) == {"1556822", "4162071"}
