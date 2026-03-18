"""PDF export helpers for public lottery results."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping, Sequence

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen.canvas import Canvas


def export_lottery_pdf(
    output_path: str | Path,
    *,
    processed_date: str,
    floor_winners: Mapping[str, Sequence[str]],
) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    canvas = Canvas(str(output), pagesize=A4)
    width, height = A4
    y = height - 48

    canvas.setFont("Helvetica-Bold", 16)
    canvas.drawString(48, y, f"ロッカー抽選結果 ({processed_date})")
    y -= 32

    canvas.setFont("Helvetica", 12)
    for floor, winners in floor_winners.items():
        canvas.drawString(48, y, floor)
        y -= 20

        if winners:
            for winner in winners:
                canvas.drawString(72, y, str(winner))
                y -= 18
        else:
            canvas.drawString(72, y, "該当なし")
            y -= 18

        y -= 8
        if y < 64:
            canvas.showPage()
            canvas.setFont("Helvetica", 12)
            y = height - 48

    canvas.save()
    return output
