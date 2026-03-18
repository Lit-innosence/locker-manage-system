from locker_manage_system import pdf_export


class FakeCanvas:
    instances: list["FakeCanvas"] = []

    def __init__(self, *args, **kwargs):
        self.font_calls: list[tuple[str, int]] = []
        self.draw_calls: list[tuple[int, int, str]] = []
        self.show_page_count = 0
        self.saved = False
        FakeCanvas.instances.append(self)

    def setFont(self, name, size):
        self.font_calls.append((name, size))

    def drawString(self, x, y, text):
        self.draw_calls.append((x, y, text))

    def showPage(self):
        self.show_page_count += 1

    def save(self):
        self.saved = True


def test_export_lottery_pdf_creates_single_file(tmp_path):
    output = tmp_path / "lottery_result.pdf"
    pdf_export.export_lottery_pdf(
        output,
        processed_date="2026-04-03",
        floor_winners={"2F": [], "4F": [("4654293", "4001")]},
    )

    assert output.exists()
    assert output.stat().st_size > 0


def test_export_lottery_pdf_uses_japanese_font_and_sorts_ids(monkeypatch, tmp_path):
    FakeCanvas.instances.clear()
    monkeypatch.setattr(pdf_export, "Canvas", FakeCanvas)

    pdf_export.export_lottery_pdf(
        tmp_path / "lottery_result.pdf",
        processed_date="2026-04-03",
        floor_winners={"4F": [("4654293", "4003"), ("1500895", "4001"), ("4100001", "4002")]},
    )

    canvas = FakeCanvas.instances[0]

    assert ("HeiseiKakuGo-W5", 16) in canvas.font_calls
    assert ("HeiseiKakuGo-W5", 9) in canvas.font_calls

    drawn_items = [text for _, _, text in canvas.draw_calls if "（" in text]
    assert drawn_items == ["1500895（4001）", "4100001（4002）", "4654293（4003）"]


def test_export_lottery_pdf_fills_columns_top_to_bottom_then_left_to_right(monkeypatch, tmp_path):
    FakeCanvas.instances.clear()
    monkeypatch.setattr(pdf_export, "Canvas", FakeCanvas)

    winners = [(f"410000{i}", f"40{i:02d}") for i in range(10)]
    pdf_export.export_lottery_pdf(
        tmp_path / "lottery_result.pdf",
        processed_date="2026-04-03",
        floor_winners={"4F": winners},
    )

    canvas = FakeCanvas.instances[0]
    drawn_ids = [(x, y, text) for x, y, text in canvas.draw_calls if "（" in text]

    assert [text for _, _, text in drawn_ids] == [f"{student_id}（{locker_number}）" for student_id, locker_number in winners]
    assert len({x for x, _, _ in drawn_ids[:10]}) == 1
    assert [y for _, y, _ in drawn_ids[:10]] == sorted((y for _, y, _ in drawn_ids[:10]), reverse=True)
    assert all(x == drawn_ids[0][0] for x, _, _ in drawn_ids)


def test_export_lottery_pdf_moves_to_next_column_after_50_rows(monkeypatch, tmp_path):
    FakeCanvas.instances.clear()
    monkeypatch.setattr(pdf_export, "Canvas", FakeCanvas)

    winners = [(f"4100{i:03d}", f"40{i:02d}") for i in range(51)]
    pdf_export.export_lottery_pdf(
        tmp_path / "lottery_result.pdf",
        processed_date="2026-04-03",
        floor_winners={"4F": winners},
    )

    canvas = FakeCanvas.instances[0]
    drawn_ids = [(x, y, text) for x, y, text in canvas.draw_calls if "（" in text]

    assert drawn_ids[50][0] > drawn_ids[49][0]
    assert drawn_ids[50][1] == drawn_ids[0][1]


def test_export_lottery_pdf_keeps_31_winners_on_one_page(monkeypatch, tmp_path):
    FakeCanvas.instances.clear()
    monkeypatch.setattr(pdf_export, "Canvas", FakeCanvas)

    pdf_export.export_lottery_pdf(
        tmp_path / "lottery_result.pdf",
        processed_date="2026-04-03",
        floor_winners={"4F": [(f"4100{i:03d}", f"40{i:02d}") for i in range(31)]},
    )

    canvas = FakeCanvas.instances[0]

    assert canvas.show_page_count == 0
    assert [text for _, _, text in canvas.draw_calls].count("4F") == 1


def test_export_lottery_pdf_paginates_after_150_winners(monkeypatch, tmp_path):
    FakeCanvas.instances.clear()
    monkeypatch.setattr(pdf_export, "Canvas", FakeCanvas)

    pdf_export.export_lottery_pdf(
        tmp_path / "lottery_result.pdf",
        processed_date="2026-04-03",
        floor_winners={"4F": [(f"4100{i:03d}", f"40{i:02d}") for i in range(151)]},
    )

    canvas = FakeCanvas.instances[0]

    assert canvas.show_page_count == 1
    assert [text for _, _, text in canvas.draw_calls].count("4F") == 2
