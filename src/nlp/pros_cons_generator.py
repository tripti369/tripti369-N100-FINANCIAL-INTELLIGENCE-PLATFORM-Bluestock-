import math
from pathlib import Path

import pandas as pd
from utils.db import load_master, load_profit_loss, load_balance_sheet, load_cash_flow

PRO_RULES = [
    (1, "ROE > 20% sustained for 3+ years", "Consistently high return on equity above 20% demonstrates exceptional capital efficiency"),
    (2, "FCF positive 5+ years", "Strong free cash flow generation over 5 years signals healthy business fundamentals"),
    (3, "Debt free latest year", "Debt-free balance sheet provides financial flexibility and eliminates interest burden"),
    (4, "Revenue CAGR >15% 5yr", "Revenue growing at above 15% CAGR over 5 years reflects strong business momentum"),
    (5, "OPM >25% latest year", "Operating profit margin above 25% indicates strong pricing power and cost discipline"),
    (6, "PAT CAGR >20% 5yr", "Net profit compounding at above 20% over 5 years creates significant shareholder value"),
    (7, "ICR >10 or debt free", "Very high interest coverage ratio reflects negligible financial stress from debt servicing"),
    (8, "Dividend yield >2% and FCF positive", "Consistent dividend yield above 2% backed by positive free cash flow"),
    (9, "EPS CAGR >15% 5yr", "Earnings per share growing above 15% CAGR indicates strong earnings quality and compounding"),
    (10, "ROE improving 3 years", "Return on equity improving for 3 consecutive years shows strengthening business quality"),
    (11, "Revenue CAGR > PAT CAGR", "Revenue growing slower than profits shows improving operating leverage and scale benefits"),
    (12, "Assets growing and debt declining", "Growing asset base funded by internal accruals reflects self-sustaining growth"),
]

CON_RULES = [
    (1, "D/E >2 non-financial", "Debt-to-equity ratio of {ratio:.2f} is elevated for a non-financial company and warrants monitoring"),
    (2, "FCF negative 3 years", "Free cash flow negative for 3 consecutive years raises concern about cash generation quality"),
    (3, "OPM declining 3 years", "Operating margins declining for 3 consecutive years suggest pricing or cost pressure"),
    (4, "Net profit negative latest year", "Company reported a net loss in the most recent financial year"),
    (5, "Revenue declining 2 years", "Revenue contraction over 2 consecutive years indicates demand weakness or market share loss"),
    (6, "ICR <1.5", "Interest coverage ratio below 1.5x indicates the company is at risk of not meeting its debt obligations"),
    (7, "Dividend payout >100%", "Dividend payout ratio above 100% means the company is paying dividends from reserves, which is unsustainable"),
    (8, "D/E rising 3 years", "Rising debt-to-equity ratio over 3 years suggests increasing financial leverage risk"),
    (9, "EPS declining 3 years", "Earnings per share declining for 3 consecutive years reflects deteriorating profitability"),
    (10, "ROCE <10%", "Return on capital employed below 10% suggests the business is not generating sufficient returns on invested capital"),
    (11, "Net Debt >3x EBITDA", "Net debt exceeding 3 times EBITDA is a high leverage ratio and limits financial flexibility"),
    (12, "Revenue CAGR <5% 5yr", "Revenue growing at below 5% over 5 years lags inflation and suggests limited business momentum"),
]

OUTPUT_PATH = Path("output/pros_cons_generated.csv")


def safe_pct(value):
    try:
        return float(value)
    except Exception:
        return None


def normalize_id(value):
    if pd.isna(value):
        return None
    return str(value).strip().upper()


def score_confidence(base_score, signal_strength=1.0):
    score = base_score * signal_strength
    return min(100, max(0, round(score)))


def compute_cagr(start, end, periods):
    try:
        start = float(start)
        end = float(end)
        if start <= 0 or periods <= 0:
            return None
        return (end / start) ** (1.0 / periods) - 1
    except Exception:
        return None


def generate_pros_cons():
    master = load_master()
    profit = load_profit_loss()
    balance = load_balance_sheet()
    cash = load_cash_flow()

    master["company_id"] = master["company_id"].astype(str).str.strip().str.upper()
    profit["company_id"] = profit["company_id"].astype(str).str.strip().str.upper()
    balance["company_id"] = balance["company_id"].astype(str).str.strip().str.upper()
    cash["company_id"] = cash["company_id"].astype(str).str.strip().str.upper()

    out_rows = []

    for _, company in master.iterrows():
        cid = normalize_id(company.get("company_id") or company.get("id"))
        if not cid:
            continue

        prof = profit[profit["company_id"] == cid].copy()
        bal = balance[balance["company_id"] == cid].copy()
        cf = cash[cash["company_id"] == cid].copy()

        if prof.empty or bal.empty or cf.empty:
            continue

        prof["year"] = pd.to_numeric(prof["year"], errors="coerce")
        bal["year"] = pd.to_numeric(bal["year"], errors="coerce")
        cf["year"] = pd.to_numeric(cf["year"], errors="coerce")

        prof = prof.sort_values("year")
        bal = bal.sort_values("year")
        cf = cf.sort_values("year")

        latest = prof.iloc[-1]
        latest_bal = bal.iloc[-1]
        latest_cf = cf.iloc[-1]

        # Pro rule 1
        roes = prof["net_profit"] / prof["sales"] * 100
        if len(roes) >= 3 and (roes.tail(3) > 20).all():
            out_rows.append({
                "company_id": cid,
                "type": "pro",
                "rule_id": 1,
                "text": PRO_RULES[0][2],
                "confidence_pct": score_confidence(90, roes.tail(3).mean() / 20),
            })

        # Pro rule 2
        fcf = cf["operating_activity"] + cf["investing_activity"] + cf["financing_activity"]
        if len(fcf) >= 5 and (fcf.tail(5) > 0).all():
            out_rows.append({
                "company_id": cid,
                "type": "pro",
                "rule_id": 2,
                "text": PRO_RULES[1][2],
                "confidence_pct": score_confidence(85, fcf.tail(5).mean() / (fcf.tail(5).mean() + 1)),
            })

        # Pro rule 3
        if pd.notna(latest_bal.get("borrowings")) and float(latest_bal.get("borrowings")) == 0:
            out_rows.append({
                "company_id": cid,
                "type": "pro",
                "rule_id": 3,
                "text": PRO_RULES[2][2],
                "confidence_pct": 80,
            })

        # Pro rule 4
        if len(prof) >= 6:
            recent = prof.tail(6)
            cagr = compute_cagr(recent.iloc[0]["sales"], recent.iloc[-1]["sales"], 5)
            if cagr is not None and cagr > 0.15:
                out_rows.append({
                    "company_id": cid,
                    "type": "pro",
                    "rule_id": 4,
                    "text": PRO_RULES[3][2],
                    "confidence_pct": score_confidence(85, cagr / 0.15),
                })

        # Pro rule 5
        opm = pd.to_numeric(latest.get("opm_percentage"), errors="coerce")
        if opm is not None and opm > 25:
            out_rows.append({
                "company_id": cid,
                "type": "pro",
                "rule_id": 5,
                "text": PRO_RULES[4][2],
                "confidence_pct": score_confidence(80, opm / 25),
            })

        # Pro rule 6
        if len(prof) >= 6:
            recent = prof.tail(6)
            cagr_pat = compute_cagr(recent.iloc[0]["net_profit"], recent.iloc[-1]["net_profit"], 5)
            if cagr_pat is not None and cagr_pat > 0.20:
                out_rows.append({
                    "company_id": cid,
                    "type": "pro",
                    "rule_id": 6,
                    "text": PRO_RULES[5][2],
                    "confidence_pct": score_confidence(85, cagr_pat / 0.20),
                })

        # Pro rule 7
        interest = pd.to_numeric(latest.get("interest"), errors="coerce")
        ebit = pd.to_numeric(latest.get("operating_profit"), errors="coerce")
        icr = None
        if interest is not None and interest != 0 and ebit is not None:
            icr = ebit / abs(interest)
        if icr is not None and icr > 10:
            out_rows.append({
                "company_id": cid,
                "type": "pro",
                "rule_id": 7,
                "text": PRO_RULES[6][2],
                "confidence_pct": score_confidence(80, min(1.0, icr / 10)),
            })
        elif latest_bal.get("borrowings") == 0:
            out_rows.append({
                "company_id": cid,
                "type": "pro",
                "rule_id": 7,
                "text": PRO_RULES[6][2],
                "confidence_pct": 80,
            })

        # Pro rule 8
        dividend_yield = pd.to_numeric(latest.get("dividend_payout"), errors="coerce")
        if dividend_yield is not None and dividend_yield > 2 and (fcf.tail(1).iloc[0] > 0):
            out_rows.append({
                "company_id": cid,
                "type": "pro",
                "rule_id": 8,
                "text": PRO_RULES[7][2],
                "confidence_pct": 75,
            })

        # Pro rule 9
        if len(prof) >= 6:
            recent = prof.tail(6)
            eps_cagr = compute_cagr(recent.iloc[0]["eps"], recent.iloc[-1]["eps"], 5)
            if eps_cagr is not None and eps_cagr > 0.15:
                out_rows.append({
                    "company_id": cid,
                    "type": "pro",
                    "rule_id": 9,
                    "text": PRO_RULES[8][2],
                    "confidence_pct": score_confidence(80, eps_cagr / 0.15),
                })

        # Pro rule 10
        if len(roes) >= 3 and roes.tail(3).is_monotonic_increasing:
            out_rows.append({
                "company_id": cid,
                "type": "pro",
                "rule_id": 10,
                "text": PRO_RULES[9][2],
                "confidence_pct": 75,
            })

        # Pro rule 11
        rev_cagr = None
        pat_cagr = None
        if len(prof) >= 6:
            recent = prof.tail(6)
            rev_cagr = compute_cagr(recent.iloc[0]["sales"], recent.iloc[-1]["sales"], 5)
            pat_cagr = compute_cagr(recent.iloc[0]["net_profit"], recent.iloc[-1]["net_profit"], 5)
        if rev_cagr is not None and pat_cagr is not None and rev_cagr < pat_cagr:
            out_rows.append({
                "company_id": cid,
                "type": "pro",
                "rule_id": 11,
                "text": PRO_RULES[10][2],
                "confidence_pct": 80,
            })

        # Pro rule 12
        if len(bal) >= 2:
            assets_growth = compute_cagr(bal.iloc[0]["total_assets"], bal.iloc[-1]["total_assets"], len(bal) - 1)
            debt_trend = bal["borrowings"].diff().tail(3)
            if assets_growth is not None and assets_growth > 0 and debt_trend.max() < 0:
                out_rows.append({
                    "company_id": cid,
                    "type": "pro",
                    "rule_id": 12,
                    "text": PRO_RULES[11][2],
                    "confidence_pct": 80,
                })

        # Con rule 1
        de_ratio = None
        equity = pd.to_numeric(latest_bal.get("equity_capital"), errors="coerce") + pd.to_numeric(latest_bal.get("reserves"), errors="coerce")
        borrowings = pd.to_numeric(latest_bal.get("borrowings"), errors="coerce")
        if equity and equity != 0 and borrowings is not None:
            de_ratio = borrowings / equity
        if de_ratio is not None and de_ratio > 2:
            out_rows.append({
                "company_id": cid,
                "type": "con",
                "rule_id": 1,
                "text": CON_RULES[0][2].format(ratio=de_ratio),
                "confidence_pct": score_confidence(80, min(1.0, de_ratio / 2)),
            })

        # Con rule 2
        if len(fcf) >= 3 and (fcf.tail(3) < 0).all():
            out_rows.append({
                "company_id": cid,
                "type": "con",
                "rule_id": 2,
                "text": CON_RULES[1][2],
                "confidence_pct": 80,
            })

        # Con rule 3
        oprops = prof["opm_percentage"].astype(float, errors="ignore")
        if len(oprops) >= 3 and oprops.tail(3).is_monotonic_decreasing:
            out_rows.append({
                "company_id": cid,
                "type": "con",
                "rule_id": 3,
                "text": CON_RULES[2][2],
                "confidence_pct": 75,
            })

        # Con rule 4
        if pd.to_numeric(latest.get("net_profit"), errors="coerce") < 0:
            out_rows.append({
                "company_id": cid,
                "type": "con",
                "rule_id": 4,
                "text": CON_RULES[3][2],
                "confidence_pct": 85,
            })

        # Con rule 5
        if len(prof) >= 3 and prof["sales"].tail(2).is_monotonic_decreasing:
            out_rows.append({
                "company_id": cid,
                "type": "con",
                "rule_id": 5,
                "text": CON_RULES[4][2],
                "confidence_pct": 75,
            })

        # Con rule 6
        if icr is not None and icr < 1.5:
            out_rows.append({
                "company_id": cid,
                "type": "con",
                "rule_id": 6,
                "text": CON_RULES[5][2],
                "confidence_pct": 85,
            })

        # Con rule 7
        payout = pd.to_numeric(latest.get("dividend_payout"), errors="coerce")
        if payout is not None and payout > 100:
            out_rows.append({
                "company_id": cid,
                "type": "con",
                "rule_id": 7,
                "text": CON_RULES[6][2],
                "confidence_pct": 90,
            })

        # Con rule 8
        if len(bal) >= 3:
            debt_trend = bal["borrowings"].astype(float).diff().tail(3)
            if debt_trend.gt(0).all():
                out_rows.append({
                    "company_id": cid,
                    "type": "con",
                    "rule_id": 8,
                    "text": CON_RULES[7][2],
                    "confidence_pct": 80,
                })

        # Con rule 9
        if len(prof) >= 3 and prof["eps"].tail(3).is_monotonic_decreasing:
            out_rows.append({
                "company_id": cid,
                "type": "con",
                "rule_id": 9,
                "text": CON_RULES[8][2],
                "confidence_pct": 80,
            })

        # Con rule 10
        if pd.to_numeric(latest.get("roce_percentage"), errors="coerce") < 10:
            out_rows.append({
                "company_id": cid,
                "type": "con",
                "rule_id": 10,
                "text": CON_RULES[9][2],
                "confidence_pct": 85,
            })

        # Con rule 11
        # EBITDA is approximated as operating_profit + depreciation
        ebitda = pd.to_numeric(latest.get("operating_profit"), errors="coerce") + pd.to_numeric(latest.get("depreciation"), errors="coerce")
        net_debt = pd.to_numeric(latest_bal.get("borrowings"), errors="coerce")
        if ebitda is not None and ebitda > 0 and net_debt is not None and net_debt > 3 * ebitda:
            out_rows.append({
                "company_id": cid,
                "type": "con",
                "rule_id": 11,
                "text": CON_RULES[10][2],
                "confidence_pct": 90,
            })

        # Con rule 12
        if rev_cagr is not None and rev_cagr < 0.05:
            out_rows.append({
                "company_id": cid,
                "type": "con",
                "rule_id": 12,
                "text": CON_RULES[11][2],
                "confidence_pct": score_confidence(70, 0.05 / (rev_cagr + 1e-9)),
            })

    df = pd.DataFrame(out_rows)
    df = df[df["confidence_pct"] > 60]
    output_dir = OUTPUT_PATH.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    return df
