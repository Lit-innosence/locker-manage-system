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
    assert ("HeiseiKakuGo-W5", 12) in canvas.font_calls

    drawn_ids = [text for _, _, text in canvas.draw_calls if text.isdigit()]
    assert drawn_ids == ["1500895", "4100001", "4654293"]


def test_export_lottery_pdf_paginates_every_30_winners(monkeypatch, tmp_path):
    FakeCanvas.instances.clear()
    monkeypatch.setattr(pdf_export, "Canvas", FakeCanvas)

    pdf_export.export_lottery_pdf(
        tmp_path / "lottery_result.pdf",
        processed_date="2026-04-03",
        floor_winners={"4F": [f"4100{i:03d}" for i in range(31)]},
    )

    canvas = FakeCanvas.instances[0]

    assert canvas.show_page_count == 1
    assert [text for _, _, text in canvas.draw_calls].count("4F") == 2
