import sqlite3
import pandas as pd

DB_PATH = 'nifty100.db'

tables = ['peer_groups', 'sectors']

with sqlite3.connect(DB_PATH) as conn:
    for table in tables:
        try:
            df = pd.read_sql(f'SELECT * FROM {table}', conn)
            print('TABLE', table)
            print('columns:', list(df.columns))
            print(df.head(3).to_dict(orient='records'))
            print('---')
        except Exception as exc:
            print('ERROR', table, exc)
