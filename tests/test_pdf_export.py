from locker_manage_system.pdf_export import export_lottery_pdf


def test_export_lottery_pdf_creates_single_file(tmp_path):
    output = tmp_path / "lottery_result.pdf"
    export_lottery_pdf(
        output,
        processed_date="2026-04-03",
        floor_winners={"2F": [], "4F": ["4654293"]},
    )

    assert output.exists()
    assert output.stat().st_size > 0
