from utils.db import load_table, load_master

# Inspect peer_groups and profit_loss loads
for name in ['peer_groups', 'profit_loss', 'sectors', 'companies']:
    df = load_table(name)
    print('TABLE', name)
    print('columns', list(df.columns))
    print(df.head(3).to_dict(orient='records'))
    print('---')

master = load_master()
print('MASTER columns', list(master.columns))
print(master.head(3).to_dict(orient='records'))
