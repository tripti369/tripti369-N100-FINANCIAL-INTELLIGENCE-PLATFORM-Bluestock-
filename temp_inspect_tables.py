import sqlite3
import pandas as pd
from pathlib import Path
root = Path(__file__).resolve().parent
db_path = root / 'nifty100.db'
conn = sqlite3.connect(db_path)
for table in ['master_company_data', 'cash_flow', 'market_cap', 'profit_loss', 'balance_sheet']:
    print('TABLE', table)
    try:
        df = pd.read_sql(f'SELECT * FROM "{table}" LIMIT 5', conn)
        print('columns:', list(df.columns))
        print(df.head(5).to_dict(orient='records'))
    except Exception as exc:
        print('ERROR', exc)
    print('---')
conn.close()
