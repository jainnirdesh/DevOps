"""Verify current Lab 4 endpoints without altering counter state."""
import json
import subprocess
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
results={}
for port,version in [(5201,'1.0'),(5300,'2.0-green'),(5500,'1.0-gitops')]:
    with urllib.request.urlopen(f'http://localhost:{port}/health',timeout=5) as response:
        data=json.load(response)
    assert data=={'status':'healthy','version':version},data
    results[str(port)]=data
with urllib.request.urlopen('http://localhost:5400/health',timeout=5) as response:
    data=json.load(response)
assert data['status']=='healthy' and data['version'] in ['1.0-stable','2.0-canary']
results['5400']=data
with urllib.request.urlopen('http://localhost:5501',timeout=5) as response:assert response.status==200
with urllib.request.urlopen('http://localhost:8200/v1/sys/health',timeout=5) as response:
    data=json.load(response)
assert data['initialized'] and not data['sealed']
results['vault']={'initialized':data['initialized'],'sealed':data['sealed']}
subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts/pipeline_secret.py')],check=True)
(ROOT/'evidence/live-verification.json').write_text(json.dumps(results,indent=2))
print('PASS: recovery, Green routing, Canary health, GitOps app/sidecar, Vault and scoped secret injection')
