import pandas as pd
from utils.db import load_master, load_table

master = load_master()
peer = load_table('peer_groups')
profit = load_table('profit_loss')
sectors = load_table('sectors')
companies = load_table('companies')

print('master columns', list(master.columns))
print('peer', list(peer.columns), peer.head(3).to_dict(orient='records'))
print('profit', list(profit.columns), profit.head(3).to_dict(orient='records'))
print('sectors', list(sectors.columns), sectors.head(3).to_dict(orient='records'))
print('companies', list(companies.columns), companies.head(3).to_dict(orient='records'))

# Check sample company mappings
for comp in ['Abbott India Ltd', 'Adani Energy Solutions Ltd', 'Axis Bank Ltd']:
    row = master[master['company_name'] == comp]
    print('COMP', comp, 'rows', len(row))
    if not row.empty:
        cid = str(row.iloc[0]['id']).strip().upper()
        print(' id', cid)
        print(' profit count', len(profit[profit['company_id'].astype(str).str.strip().str.upper() == cid]))
        print(' sector count', len(sectors[sectors['company_id'].astype(str).str.strip().str.upper() == cid]))
        print(' peer count', len(peer[peer['company_id'].astype(str).str.strip().str.upper() == cid]))

# Check if any company_name in master has profit data and sector data
profit_ids = profit['company_id'].astype(str).str.strip().str.upper().unique()
sector_ids = sectors['company_id'].astype(str).str.strip().str.upper().unique()
print('master without profit sample', master[~master['id'].astype(str).str.upper().isin(profit_ids)]['company_name'].head(10).tolist())
print('master without sector sample', master[~master['id'].astype(str).str.upper().isin(sector_ids)]['company_name'].head(10).tolist())

# Check if broad_sector exists as expected
print('broad_sector unique', sectors['broad_sector'].dropna().unique()[:20])
print('sector merge sample', companies.merge(sectors[['company_id','broad_sector']], left_on='id', right_on='company_id', how='left')[['id','company_name','broad_sector']].head(10).to_dict(orient='records'))
