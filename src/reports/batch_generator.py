from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from utils.db import load_master, load_balance_sheet, load_cash_flow, load_profit_loss
from src.reports.tearsheet import generate_tearsheet
from src.reports.sector_report import generate_sector_report


def build_company_tearsheets(output_dir: str = "reports/tearsheets"):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    master = load_master()
    profit = load_profit_loss()
    cash = load_cash_flow()
    balance = load_balance_sheet()

    generated = []
    skipped = []

    for _, row in master.iterrows():
        cid = str(row.get("company_id") or row.get("id")).strip().upper()
        company_name = row.get("company_name")
        ticker = row.get("id")

        company_profit = profit[profit["company_id"].astype(str).str.strip().str.upper() == cid]
        company_balance = balance[balance["company_id"].astype(str).str.strip().str.upper() == cid]
        company_cash = cash[cash["company_id"].astype(str).str.strip().str.upper() == cid]

        if len(company_profit) < 3 or len(company_balance) < 3 or len(company_cash) < 3:
            skipped.append({"company_id": cid, "company_name": company_name})
            continue

        output_path = output_dir / f"{ticker}_{company_name.replace(' ', '_')}_tearsheet.pdf"
        generate_tearsheet(company_name, ticker, str(output_path))
        generated.append(output_path)

    skipped_path = Path("output/skipped_tearsheets.csv")
    skipped_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(skipped).to_csv(skipped_path, index=False)
    return generated


def build_sector_reports(output_dir: str = "reports/sector"):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    master = load_master()
    if "sector" not in master.columns:
        raise ValueError("Sector column not found in master table.")

    for sector, group in master.groupby("sector"):
        sector_file = output_dir / f"{sector.replace(' ', '_')}_report.pdf"
        summary_df = group[["company_name", "roe_percentage", "roce_percentage"]].copy()
        generate_sector_report(sector, summary_df, str(sector_file))

    return list(output_dir.glob("*.pdf"))
