from utils.db import load_master

master = load_master()

print(master.columns.tolist())