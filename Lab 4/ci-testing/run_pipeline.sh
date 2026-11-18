#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export DOCKER_CONTEXT=colima-lab2
export DOCKER_HOST="$(docker context inspect --format '{{.Endpoints.docker.Host}}')"
echo '=== Build ==='
docker build -t lab4-app:1.0 app/
docker build -t lab4-app:2.0 app-v2/
echo '=== Automated tests ==='
.venv/bin/python -m pytest ci-testing/test_app.py -v --tb=short
echo '=== Pipeline secret injection ==='
.venv/bin/python scripts/pipeline_secret.py
echo '=== Deploy ==='
docker compose -p lab4-bg -f blue-green/docker-compose.yml up -d
echo '=== Verify ==='
.venv/bin/python - <<'PY'
import json,time,urllib.request
for attempt in range(30):
    try:
        with urllib.request.urlopen('http://localhost:5300/health',timeout=3) as r:
            assert json.load(r)['status']=='healthy'
        break
    except Exception:
        if attempt==29:raise
        time.sleep(1)
print('PASS: deployed application healthy')
PY
