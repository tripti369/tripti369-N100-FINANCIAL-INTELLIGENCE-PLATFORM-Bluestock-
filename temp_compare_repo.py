import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

repo = "tripti369/N100-FINANCIAL-INTELLIGENCE-PLATFORM-upgraded-"
api_url = f"https://api.github.com/repos/{repo}/git/trees/HEAD?recursive=1"

print('Fetching remote tree', api_url)
req = Request(api_url, headers={'User-Agent': 'repo-check'})
try:
    with urlopen(req, timeout=30) as resp:
        data = json.load(resp)
except HTTPError as e:
    print('HTTPError', e.code, e.reason)
    sys.exit(1)
except URLError as e:
    print('URLError', e.reason)
    sys.exit(1)

remote_files = [item['path'] for item in data.get('tree', []) if item['type'] == 'blob']
print('Remote file count:', len(remote_files))
remote_dirs = sorted({os.path.dirname(p) for p in remote_files if os.path.dirname(p)})
print('Remote dir count:', len(remote_dirs))

root = os.path.abspath(os.path.dirname(__file__))
local_files = []
for dirpath, dirnames, filenames in os.walk(root):
    if dirpath.startswith(os.path.join(root, '.git')):
        continue
    rel = os.path.relpath(dirpath, root)
    for fn in filenames:
        if fn == os.path.basename(__file__):
            continue
        local_files.append(os.path.normpath(os.path.join(rel, fn)).replace('\\', '/'))
local_files = sorted(local_files)
print('Local file count:', len(local_files))

remote_set = set(remote_files)
local_set = set(local_files)

missing_locally = sorted(remote_set - local_set)
extra_locally = sorted(local_set - remote_set)

print('Missing locally:', len(missing_locally))
print('Extra locally:', len(extra_locally))
if missing_locally:
    print('\n--- MISSING LOCALLY ---')
    for p in missing_locally[:100]:
        print(p)
if extra_locally:
    print('\n--- EXTRA LOCALLY ---')
    for p in extra_locally[:100]:
        print(p)
