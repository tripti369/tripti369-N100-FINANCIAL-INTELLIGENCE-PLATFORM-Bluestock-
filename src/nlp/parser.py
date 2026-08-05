import re
from pathlib import Path

import pandas as pd
from utils.db import load_analysis, load_master

PATTERN = re.compile(r"(\d+)\s*Years?:?\s*([\d.]+)%", re.IGNORECASE)
METRIC_COLUMNS = [
    "compounded_sales_growth",
    "compounded_profit_growth",
    "stock_price_cagr",
    "roe",
]


def parse_metric_text(text):
    if not isinstance(text, str):
        return None
    match = PATTERN.search(text)
    if not match:
        return None
    years = int(match.group(1))
    value = float(match.group(2))
    return years, value


def normalize_company_id(value):
    if pd.isna(value):
        return None
    return str(value).strip().upper()


def parse_analysis_excel(
    source_path: str = "analysis.xlsx",
    output_path: str = "output/analysis_parsed.csv",
    failures_path: str = "output/parse_failures.csv",
    divergence_path: str = "output/analysis_divergences.csv",
):
    source_file = Path(source_path)
    if not source_file.exists():
        raise FileNotFoundError(f"Source file not found: {source_file}")

    df = pd.read_excel(source_file)
    parsed = []
    failures = []

    for _, row in df.iterrows():
        company_id = normalize_company_id(row.get("company_id") or row.get("company_id_pl") or row.get("id"))
        for metric in METRIC_COLUMNS:
            raw_value = row.get(metric)
            if pd.isna(raw_value):
                continue

            result = parse_metric_text(raw_value)
            if result is None:
                failures.append({
                    "company_id": company_id,
                    "metric_type": metric,
                    "raw_value": raw_value,
                })
            else:
                years, value = result
                parsed.append({
                    "company_id": company_id,
                    "metric_type": metric,
                    "period_years": years,
                    "value_pct": value,
                })

    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    parsed_df = pd.DataFrame(parsed)
    parsed_df.to_csv(output_path, index=False)

    failures_df = pd.DataFrame(failures)
    failures_df.to_csv(failures_path, index=False)

    if divergence_path:
        divergences = compare_with_declared_values(parsed_df)
        divergences.to_csv(divergence_path, index=False)

    return parsed_df


def compare_with_declared_values(parsed_df: pd.DataFrame):
    master = load_master()
    master = master.copy()
    master["company_id"] = master["company_id"].astype(str).str.strip().str.upper()
    cluster = []

    for _, row in parsed_df.iterrows():
        cid = row["company_id"]
        metric = row["metric_type"]
        source_value = None
        master_row = master[master["company_id"] == cid]
        if not master_row.empty and metric in master_row.columns:
            source_top = master_row.iloc[0][metric]
            try:
                source_value = float(source_top)
            except Exception:
                source_value = None

        if source_value is not None and source_value != 0:
            divergence_pct = abs(row["value_pct"] - source_value) / abs(source_value) * 100
            if divergence_pct > 5:
                cluster.append({
                    "company_id": cid,
                    "metric_type": metric,
                    "parsed_value_pct": row["value_pct"],
                    "declared_value": source_value,
                    "divergence_pct": divergence_pct,
                })

    return pd.DataFrame(cluster)
