"""Fetch credentials on demand and inject them into a pipeline child process."""
import json
import os
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
token=(ROOT/'.runtime/pipeline-token').read_text().strip()
result=subprocess.run(['docker','exec','-i','lab4-vault','sh','-c',
    'read -r VAULT_TOKEN; export VAULT_TOKEN VAULT_ADDR=http://127.0.0.1:8200; vault kv get -format=json secret/lab4/app'],
    input=token+'\n',capture_output=True,text=True)
if result.returncode:
    raise RuntimeError('Pipeline secret retrieval failed; initialize Vault and renew the local token.')
values=json.loads(result.stdout)['data']['data']
assert set(values)=={'db_password','api_key'}
environment=os.environ.copy()
environment.update(DB_PASSWORD=values['db_password'],API_KEY=values['api_key'])
subprocess.run(['python3','-c',
    'import os; assert len(os.environ["DB_PASSWORD"])>=32; assert len(os.environ["API_KEY"])>=32; print("[PASS] Pipeline received DB_PASSWORD and API_KEY; values redacted")'],
    env=environment,check=True)
