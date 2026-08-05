import math
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from utils.db import load_master, load_profit_loss


def arrow_symbol(current, previous):
    try:
        current = float(current)
        previous = float(previous)
    except Exception:
        return "→"
    if previous == 0:
        return "→"
    delta = current - previous
    if abs(delta) <= abs(previous) * 0.02:
        return "→"
    return "↑" if delta > 0 else "↓"


def create_portfolio_summary(output_path: str = "reports/portfolio/portfolio_summary.pdf"):
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    master = load_master()
    profit = load_profit_loss()
    profit["company_id"] = profit["company_id"].astype(str).str.strip().str.upper()
    master["company_id"] = master["company_id"].astype(str).str.strip().str.upper()

    sorted_master = master.sort_values("company_name")
    doc = SimpleDocTemplate(str(output_file), pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
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
    elements.append(Paragraph("Portfolio Summary", header_style))

    for _, row in sorted_master.iterrows():
        company_name = row.get("company_name")
        cid = row.get("company_id")
        if not company_name or not cid:
            continue

        company_profit = profit[profit["company_id"] == cid].sort_values("year")
        if company_profit.empty:
            continue

        latest = company_profit.iloc[-1]
        previous = company_profit.iloc[-2] if len(company_profit) >= 2 else latest

        metrics = [
            ("ROE", row.get("roe_percentage")),
            ("ROCE", row.get("roce_percentage")),
            ("Sales", latest.get("sales")),
            ("Net Profit", latest.get("net_profit")),
            ("EPS", latest.get("eps")),
            ("Operating Profit", latest.get("operating_profit")),
        ]

        elements.append(Paragraph(f"<b>{company_name}</b>", ParagraphStyle(name="CompanyHeader", fontSize=14, leading=18)))
        table_data = [["Metric", "Value", "Trend"]]
        for name, value in metrics:
            symbol = arrow_symbol(value, previous.get(name.lower().replace(" ", "_") if name != "ROE" else "roe_percentage"))
            table_data.append([name, f"{value}", symbol])

        table = Table(table_data, colWidths=[5 * cm, 5 * cm, 2 * cm])
        table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))

    doc.build(elements)
    return str(output_file)
