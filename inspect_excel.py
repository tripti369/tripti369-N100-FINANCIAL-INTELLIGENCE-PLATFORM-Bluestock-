import pandas as pd

for filename in ['peer_groups.xlsx', 'sectors.xlsx', 'companies.xlsx', 'profitandloss.xlsx']:
    try:
        df = pd.read_excel(filename)
        print('FILE', filename)
        print('columns:', list(df.columns))
        print(df.head(5).to_dict(orient='records'))
        print('---')
    except Exception as exc:
        print('ERROR', filename, exc)
