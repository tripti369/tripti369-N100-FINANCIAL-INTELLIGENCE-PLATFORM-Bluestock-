import pandas as pd
from utils.db import load_table, load_master

master = load_master()
peer = load_table('peer_groups')
sectors = load_table('sectors')
profit = load_table('profit_loss')
companies = load_table('companies')

print('master id sample', master['id'].astype(str).head(5).tolist())
print('peer columns', list(peer.columns))
print('peer sample', peer.head(5).to_dict(orient='records'))
print('sector columns', list(sectors.columns))
print('sector sample', sectors.head(5).to_dict(orient='records'))
print('profit cols', list(profit.columns))
print('profit sample', profit.head(5).to_dict(orient='records'))
print('company ids in master count', master['id'].nunique())
print('company_ids in peer count', peer['company_id'].nunique())
print('merged count', master.merge(peer[['company_id','peer_group']], left_on='id', right_on='company_id', how='left')['peer_group'].notna().sum())
print('Companies with peer group sample', master[master['id'].isin(peer['company_id'].unique())]['company_name'].head(10).tolist())
print('profit company ids count', profit['company_id'].nunique())
print('profit rows for ABB', profit[profit['company_id'].astype(str).str.upper()=='ABB'].shape)
print('sector merged count', companies.merge(sectors[['company_id','broad_sector']], left_on='id', right_on='company_id', how='left')['broad_sector'].notna().sum())
print('companies with sectors', companies[companies['id'].isin(sectors['company_id'].unique())]['company_name'].head(10).tolist())
