from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generate_tearsheet(company_name: str, ticker: str, output_path: str):
    doc = SimpleDocTemplate(output_path, pagesize=landscape(A4), topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    elements = []

    header_style = ParagraphStyle(
        name="Header",
        fontSize=18,
        leading=22,
        textColor=colors.white,
        alignment=1,
        backColor=colors.HexColor("#0B3D91"),
        spaceAfter=12,
    )

    elements.append(Paragraph(f"{company_name} ({ticker})", header_style))

    kpi_data = [
        ["ROE", "ROCE", "Revenue CAGR"],
        ["EPS CAGR", "FCF Yield", "Debt/Equity"],
    ]
    table = Table(kpi_data, colWidths=[6 * cm, 6 * cm, 6 * cm], hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B3D91")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    facts_data = [
        ["Revenue (10Y)", "Net Profit (10Y)"],
        ["ROE Trend", "ROCE Trend"],
    ]
    facts_table = Table(facts_data, colWidths=[9 * cm, 9 * cm], hAlign="LEFT")
    facts_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(facts_table)

    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Pros:", ParagraphStyle(name="Subheader", fontSize=14, leading=18, textColor=colors.green)))
    pros_list = [Paragraph("• Strong free cash flow generation.", ParagraphStyle(name="Normal", fontSize=10, leading=12))]
    for item in pros_list:
        elements.append(item)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Cons:", ParagraphStyle(name="Subheader", fontSize=14, leading=18, textColor=colors.red)))
    cons_list = [Paragraph("• Elevated leverage relative to equity.", ParagraphStyle(name="Normal", fontSize=10, leading=12))]
    for item in cons_list:
        elements.append(item)

    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    doc.build(elements)
