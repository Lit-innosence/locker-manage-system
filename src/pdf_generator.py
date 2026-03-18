import pandas as pd
import datetime
from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import config
from data_io import sanitize_id

def generate_pdf(term: str):
    print(f"\n[{term}] PDF出力処理を開始します...")

    result_csv_path = config.OUTPUT_DIR / term / "result.csv"
    output_pdf_path = config.OUTPUT_DIR / term / "locker_result.pdf"

    if result_csv_path.exists():
        df = pd.read_csv(result_csv_path)
        for col in ["申請者学籍番号", "割り当てロッカー"]:
            if col in df.columns:
                df[col] = sanitize_id(df[col])
    else:
        df = pd.DataFrame(columns=["申請者学籍番号", "割り当てロッカー"])

    pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='Title_JP', fontName='HeiseiKakuGo-W5', fontSize=18,
        alignment=1, spaceAfter=20
    ))
    styles.add(ParagraphStyle(
        name='Heading_JP', fontName='HeiseiKakuGo-W5', fontSize=14,
        spaceBefore=15, spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        name='Normal_JP', fontName='HeiseiKakuGo-W5', fontSize=11,
        spaceAfter=5
    ))

    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(output_pdf_path), pagesize=A4)
    elements = []

    today_str = datetime.date.today().strftime("%Y年%m月%d日")
    title_text = f"ロッカー抽選結果（{today_str}）"
    elements.append(Paragraph(title_text, styles['Title_JP']))

    for floor in ['2', '3', '4', '5', '6']:
        elements.append(Paragraph(f"■ {floor}階", styles['Heading_JP']))

        if not df.empty and "割り当てロッカー" in df.columns:
            floor_df = df[df["割り当てロッカー"].str.startswith(floor)]
        else:
            floor_df = pd.DataFrame()

        if floor_df.empty:
            elements.append(Paragraph("該当なし", styles['Normal_JP']))
        else:
            winners = floor_df["申請者学籍番号"].sort_values().tolist()

            cols = 5
            table_data = []
            for i in range(0, len(winners), cols):
                row = winners[i:i+cols]
                row += [""] * (cols - len(row))
                table_data.append(row)

            t = Table(table_data, colWidths=[90]*cols)
            t.setStyle(TableStyle([
                ('FONT', (0,0), (-1,-1), 'HeiseiKakuGo-W5', 11),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ]))
            elements.append(t)

        elements.append(Spacer(1, 10))

    try:
        doc.build(elements)
        print(f">> PDFの生成が完了しました。出力先: {output_pdf_path}")
    except Exception as e:
        print(f">> PDFの生成中にエラーが発生しました: {e}")

if __name__ == "__main__":
    generate_pdf("term1")