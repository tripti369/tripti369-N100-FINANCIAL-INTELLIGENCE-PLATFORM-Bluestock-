from utils.db import load_table

tables = [
    "companies",
    "profitandloss",
    "balancesheet",
    "cashflow",
    "financial_ratios",
    "peer_groups",
    "market_cap",
    "stock_prices",
    "sectors"
]

for table in tables:
    print("\n" + "=" * 60)
    print(table.upper())

    try:
        df = load_table(table)
        print(df.columns.tolist())
    except Exception as e:
        print("ERROR:", e)