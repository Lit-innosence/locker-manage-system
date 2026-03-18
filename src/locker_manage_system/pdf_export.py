"""PDF export helpers for public lottery results."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping, Sequence

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.pdfmetrics import registerFont


JAPANESE_FONT_NAME = "HeiseiKakuGo-W5"
TITLE_FONT_SIZE = 16
BODY_FONT_SIZE = 9
MAX_COLUMNS = 4
LINES_PER_PAGE = 100
ROWS_PER_COLUMN = 25
LEFT_MARGIN = 72
TOP_LINE_HEIGHT = 10


def _register_japanese_font() -> str:
    registerFont(UnicodeCIDFont(JAPANESE_FONT_NAME))
    return JAPANESE_FONT_NAME


def _draw_page_header(canvas: Canvas, *, title: str, floor: str | None = None) -> float:
    _, height = A4
    y = height - 48

    canvas.setFont(JAPANESE_FONT_NAME, TITLE_FONT_SIZE)
    canvas.drawString(48, y, title)
    y -= 32

    canvas.setFont(JAPANESE_FONT_NAME, BODY_FONT_SIZE)
    if floor is not None:
        canvas.drawString(48, y, floor)
        y -= 20

    return y


def _column_x_positions() -> list[float]:
    width, _ = A4
    usable_width = width - (LEFT_MARGIN * 2)
    column_width = usable_width / MAX_COLUMNS
    return [LEFT_MARGIN + (column_width * index) for index in range(MAX_COLUMNS)]


def _draw_winner_page(canvas: Canvas, *, title: str, floor: str, winners: Sequence[str]) -> None:
    y_start = _draw_page_header(canvas, title=title, floor=floor)
    x_positions = _column_x_positions()

    for index, winner in enumerate(winners):
        column_index = index // ROWS_PER_COLUMN
        row_index = index % ROWS_PER_COLUMN
        x = x_positions[column_index]
        y = y_start - (row_index * TOP_LINE_HEIGHT)
        canvas.drawString(x, y, winner)


def export_lottery_pdf(
    output_path: str | Path,
    *,
    processed_date: str,
    floor_winners: Mapping[str, Sequence[str]],
) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    _register_japanese_font()

    canvas = Canvas(str(output), pagesize=A4)
    title = f"ロッカー抽選結果 ({processed_date})"

    items = list(floor_winners.items())
    for index, (floor, winners) in enumerate(items):
        sorted_winners = sorted(str(winner) for winner in winners)

        if sorted_winners:
            for page_start in range(0, len(sorted_winners), LINES_PER_PAGE):
                if page_start > 0:
                    canvas.showPage()
                page_winners = sorted_winners[page_start : page_start + LINES_PER_PAGE]
                _draw_winner_page(canvas, title=title, floor=floor, winners=page_winners)
        else:
            y = _draw_page_header(canvas, title=title, floor=floor)
            canvas.drawString(72, y, "該当なし")

        if index < len(items) - 1:
            canvas.showPage()

    canvas.save()
    return output
