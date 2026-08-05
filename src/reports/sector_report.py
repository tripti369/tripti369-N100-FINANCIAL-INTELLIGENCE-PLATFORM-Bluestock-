import pandas as pd
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generate_sector_report(sector_name: str, companies_df: pd.DataFrame, output_path: str):
    doc = SimpleDocTemplate(output_path, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
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
    elements.append(Paragraph(f"Sector Report: {sector_name}", header_style))
    elements.append(Spacer(1, 12))

    summary = companies_df.describe().loc[["mean", "min", "max"]].round(2)
    summary_table = Table([summary.columns.tolist()] + summary.reset_index().values.tolist(), hAlign="LEFT")
    summary_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Company metrics:", ParagraphStyle(name="Subheader", fontSize=14, leading=18)))
    rows = [companies_df.columns.tolist()] + companies_df.head(20).values.tolist()
    table = Table(rows, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
    ]))
    elements.append(table)

    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    doc.build(elements)
