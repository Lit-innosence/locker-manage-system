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
        floor_winners={"2F": [], "4F": ["4654293"]},
    )

    assert output.exists()
    assert output.stat().st_size > 0


def test_export_lottery_pdf_uses_japanese_font_and_sorts_ids(monkeypatch, tmp_path):
    FakeCanvas.instances.clear()
    monkeypatch.setattr(pdf_export, "Canvas", FakeCanvas)

    pdf_export.export_lottery_pdf(
        tmp_path / "lottery_result.pdf",
        processed_date="2026-04-03",
        floor_winners={"4F": ["4654293", "1500895", "4100001"]},
    )

    canvas = FakeCanvas.instances[0]

    assert ("HeiseiKakuGo-W5", 16) in canvas.font_calls
    assert ("HeiseiKakuGo-W5", 9) in canvas.font_calls

    drawn_ids = [text for _, _, text in canvas.draw_calls if text.isdigit()]
    assert drawn_ids == ["1500895", "4100001", "4654293"]


def test_export_lottery_pdf_fills_columns_top_to_bottom_then_left_to_right(monkeypatch, tmp_path):
    FakeCanvas.instances.clear()
    monkeypatch.setattr(pdf_export, "Canvas", FakeCanvas)

    winners = [f"410000{i}" for i in range(10)]
    pdf_export.export_lottery_pdf(
        tmp_path / "lottery_result.pdf",
        processed_date="2026-04-03",
        floor_winners={"4F": winners},
    )

    canvas = FakeCanvas.instances[0]
    drawn_ids = [(x, y, text) for x, y, text in canvas.draw_calls if text.isdigit()]

    assert [text for _, _, text in drawn_ids] == winners
    assert len({x for x, _, _ in drawn_ids[:10]}) == 1
    assert [y for _, y, _ in drawn_ids[:10]] == sorted((y for _, y, _ in drawn_ids[:10]), reverse=True)
    assert all(x == drawn_ids[0][0] for x, _, _ in drawn_ids)


def test_export_lottery_pdf_moves_to_next_column_after_25_rows(monkeypatch, tmp_path):
    FakeCanvas.instances.clear()
    monkeypatch.setattr(pdf_export, "Canvas", FakeCanvas)

    winners = [f"4100{i:03d}" for i in range(26)]
    pdf_export.export_lottery_pdf(
        tmp_path / "lottery_result.pdf",
        processed_date="2026-04-03",
        floor_winners={"4F": winners},
    )

    canvas = FakeCanvas.instances[0]
    drawn_ids = [(x, y, text) for x, y, text in canvas.draw_calls if text.isdigit()]

    assert drawn_ids[25][0] > drawn_ids[24][0]
    assert drawn_ids[25][1] == drawn_ids[0][1]


def test_export_lottery_pdf_keeps_31_winners_on_one_page(monkeypatch, tmp_path):
    FakeCanvas.instances.clear()
    monkeypatch.setattr(pdf_export, "Canvas", FakeCanvas)

    pdf_export.export_lottery_pdf(
        tmp_path / "lottery_result.pdf",
        processed_date="2026-04-03",
        floor_winners={"4F": [f"4100{i:03d}" for i in range(31)]},
    )

    canvas = FakeCanvas.instances[0]

    assert canvas.show_page_count == 0
    assert [text for _, _, text in canvas.draw_calls].count("4F") == 1


def test_export_lottery_pdf_paginates_after_100_winners(monkeypatch, tmp_path):
    FakeCanvas.instances.clear()
    monkeypatch.setattr(pdf_export, "Canvas", FakeCanvas)

    pdf_export.export_lottery_pdf(
        tmp_path / "lottery_result.pdf",
        processed_date="2026-04-03",
        floor_winners={"4F": [f"4100{i:03d}" for i in range(101)]},
    )

    canvas = FakeCanvas.instances[0]

    assert canvas.show_page_count == 1
    assert [text for _, _, text in canvas.draw_calls].count("4F") == 2
