import pandas as pd
from pathlib import Path
from utils.db import load_master, load_cash_flow, load_balance_sheet

OUTPUT_PATH = Path("output/cashflow_intelligence.xlsx")
DISTRESS_PATH = Path("output/distress_alerts.csv")


def safe_float(value):
    try:
        return float(value)
    except Exception:
        return None


def compute_cagr(start, end, periods):
    try:
        start = float(start)
        end = float(end)
        if start <= 0 or periods <= 0:
            return None
        return (end / start) ** (1.0 / periods) - 1
    except Exception:
        return None


def classify_cfo_quality(ratios):
    if not ratios:
        return "Unknown"
    avg = sum(ratios) / len(ratios)
    if avg > 1.0:
        return "High Quality"
    if avg >= 0.5:
        return "Moderate"
    return "Accrual Risk"


def classify_capex(intensity):
    if intensity is None:
        return "Unknown"
    if intensity < 3:
        return "Asset Light"
    if intensity <= 8:
        return "Moderate"
    return "Capital Intensive"


def compute_capital_allocation_label(cfo_quality_label, distress_flag, capex_label):
    if distress_flag:
        return "Distress Signal"
    if cfo_quality_label == "High Quality" and capex_label == "Asset Light":
        return "Capital Preserver"
    if cfo_quality_label == "Moderate" and capex_label == "Moderate":
        return "Growth Investor"
    if cfo_quality_label == "Accrual Risk" and capex_label == "Capital Intensive":
        return "Aggressive Builder"
    return "Balanced Allocator"


def generate_cashflow_intelligence():
    master = load_master()
    cash = load_cash_flow()
    balance = load_balance_sheet()

    master["company_id"] = master["company_id"].astype(str).str.strip().str.upper()
    cash["company_id"] = cash["company_id"].astype(str).str.strip().str.upper()
    balance["company_id"] = balance["company_id"].astype(str).str.strip().str.upper()

    rows = []
    distress_rows = []

    for _, company in master.iterrows():
        cid = str(company.get("company_id") or company.get("id")).strip().upper()
        if not cid:
            continue

        company_cash = cash[cash["company_id"] == cid].copy()
        company_balance = balance[balance["company_id"] == cid].copy()

        if company_cash.empty or company_balance.empty:
            continue

        company_cash["year"] = pd.to_numeric(company_cash["year"], errors="coerce")
        company_balance["year"] = pd.to_numeric(company_balance["year"], errors="coerce")

        company_cash = company_cash.sort_values("year")
        company_balance = company_balance.sort_values("year")

        years = len(company_cash)
        if years < 3:
            continue

        cfo_pat = []
        fcf_values = []
        for _, row in company_cash.iterrows():
            cfo = safe_float(row.get("operating_activity"))
            net_profit = safe_float(row.get("net_cash_flow"))
            if cfo is not None and net_profit is not None and net_profit != 0:
                cfo_pat.append(cfo / net_profit)
            fcf_values.append(cfo)

        cfo_quality_label = classify_cfo_quality([v for v in cfo_pat if v is not None])
        cfo_quality_score = round(sum([v for v in cfo_pat if v is not None]) / len([v for v in cfo_pat if v is not None]), 2) if cfo_pat else None

        latest_cash = company_cash.iloc[-1]
        latest_balance = company_balance.iloc[-1]

        sales = safe_float(company_cash.iloc[-1].get("sales")) if "sales" in company_cash.columns else None
        investing = safe_float(latest_cash.get("investing_activity"))
        capex_intensity = None
        if sales is not None and sales != 0 and investing is not None:
            capex_intensity = abs(investing) / sales * 100

        capex_label = classify_capex(capex_intensity)

        if len(company_cash) >= 6:
            fcf_cagr = compute_cagr(company_cash.iloc[0].get("operating_activity"), company_cash.iloc[-1].get("operating_activity"), len(company_cash) - 1)
        else:
            fcf_cagr = None

        fcf_conversion_pct = None
        if safe_float(latest_cash.get("operating_activity")) is not None and safe_float(latest_cash.get("net_cash_flow")) not in (None, 0):
            fcf_conversion_pct = safe_float(latest_cash.get("operating_activity")) / safe_float(latest_cash.get("net_cash_flow")) * 100

        distress_flag = False
        if safe_float(latest_cash.get("operating_activity")) is not None and safe_float(latest_cash.get("investing_activity")) is not None:
            distress_flag = safe_float(latest_cash.get("operating_activity")) < 0 and safe_float(latest_cash.get("financing_activity")) > 0

        deleveraging_flag = False
        if len(company_cash) >= 2 and safe_float(latest_cash.get("financing_activity")) is not None and safe_float(company_cash.iloc[-2].get("financing_activity")) is not None:
            deleveraging_flag = latest_cash.get("financing_activity") < company_cash.iloc[-2].get("financing_activity")

        capital_allocation_label = compute_capital_allocation_label(cfo_quality_label, distress_flag, capex_label)

        rows.append({
            "company_id": cid,
            "sector": company.get("sector") if "sector" in company else None,
            "cfo_quality_score": cfo_quality_score,
            "cfo_quality_label": cfo_quality_label,
            "capex_intensity_pct": round(capex_intensity, 2) if capex_intensity is not None else None,
            "capex_label": capex_label,
            "fcf_cagr_5yr": round(fcf_cagr * 100, 2) if fcf_cagr is not None else None,
            "fcf_conversion_pct": round(fcf_conversion_pct, 2) if fcf_conversion_pct is not None else None,
            "distress_flag": distress_flag,
            "deleveraging_flag": deleveraging_flag,
            "capital_allocation_label": capital_allocation_label,
        })

        if distress_flag:
            distress_rows.append({
                "company_id": cid,
                "cfo_value": latest_cash.get("operating_activity"),
                "cff_value": latest_cash.get("financing_activity"),
                "latest_net_profit": latest_cash.get("net_cash_flow"),
            })

    df = pd.DataFrame(rows)
    df.to_excel(OUTPUT_PATH, index=False)
    distress_df = pd.DataFrame(distress_rows)
    distress_df.to_csv(DISTRESS_PATH, index=False)
    return df
