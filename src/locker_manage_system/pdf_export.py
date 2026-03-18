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
BODY_FONT_SIZE = 12
LINES_PER_PAGE = 30


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
        y = _draw_page_header(canvas, title=title, floor=floor)

        if sorted_winners:
            lines_on_page = 0
            for winner in sorted_winners:
                if lines_on_page == LINES_PER_PAGE:
                    canvas.showPage()
                    y = _draw_page_header(canvas, title=title, floor=floor)
                    lines_on_page = 0
                canvas.drawString(72, y, str(winner))
                y -= 18
                lines_on_page += 1
        else:
            canvas.drawString(72, y, "該当なし")
            y -= 18

        if index < len(items) - 1:
            canvas.showPage()

    canvas.save()
    return output
