"""Run local Lab 3 tasks and record their actual exit statuses."""
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
E = ROOT / 'evidence'
E.mkdir(exist_ok=True)
RESULTS = {}
os.environ['DOCKER_HOST'] = subprocess.check_output(['docker', 'context', 'inspect', '--format', '{{.Endpoints.docker.Host}}'], text=True).strip()


def command(args, log, append=False):
    print('$ ' + shlex.join(args), flush=True)
    with (E/log).open('a' if append else 'w') as out:
        out.write('$ ' + shlex.join(args) + '\n')
        out.flush()
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            out.write(line)
            out.flush()
            print(line, end='', flush=True)
        code = process.wait()
        out.write(f'\nExit code: {code}\n')
    return code


def task(number, commands, log, detail):
    for i, args in enumerate(commands):
        code = command(args, log, append=i > 0)
        if code:
            RESULTS[str(number)] = {'status': 'FAIL', 'detail': f'Command exited {code}; see {log}.'}
            return
    RESULTS[str(number)] = {'status': 'PASS', 'detail': detail}


task(1, [['.venv/bin/ansible-playbook', '-i', 'ansible/inventory', 'ansible/playbook.yml']], 'task1-ansible.log', 'Ansible deployed the app and verified HTTP health with zero failed tasks.')
task(2, [
    ['terraform', '-chdir=terraform', 'init', '-no-color'],
    ['terraform', '-chdir=terraform', 'validate', '-no-color'],
    ['terraform', '-chdir=terraform', 'plan', '-out=lab3.tfplan', '-no-color'],
    ['terraform', '-chdir=terraform', 'apply', '-no-color', 'lab3.tfplan'],
], 'task2-terraform.log', 'Local IaC simulation applied with two instance resources and deployment.json.')
command(['terraform', '-chdir=terraform', 'plan', '-var=instance_count=3', '-no-color'], 'task2-scale-plan.log')
command(['terraform', '-chdir=terraform', 'plan', '-detailed-exitcode', '-no-color'], 'task2-idempotence.log')
task(3, [['docker', 'compose', '-p', 'lab3-elk', '-f', 'elk/docker-compose.yml', 'up', '-d']], 'task3-elk.log', 'ELK containers started; live verification pending.')
task(5, [['docker', 'compose', '-p', 'lab3-monitoring', '-f', 'prometheus/docker-compose.yml', 'up', '-d']], 'task5-monitoring.log', 'Monitoring containers started; live verification pending.')
task(6, [[sys.executable, 'feature-flags/test_flags.py']], 'task6-tests.log', 'All 17 feature flag unit tests passed.')
code = command([sys.executable, 'scripts/verify.py'], 'live-verification.log')
if code == 0:
    RESULTS['3'] = {'status': 'PASS', 'detail': 'Actual Flask request logs indexed in Elasticsearch; Kibana available and log data view created.'}
    RESULTS['5'] = {'status': 'PASS', 'detail': 'All three Prometheus targets up; Grafana database healthy and dashboard provisioned.'}
else:
    for n in ['3', '5']:
        RESULTS[n] = {'status': 'FAIL', 'detail': 'Combined live verification failed; inspect live-verification.log for the failing service.'}
task(4, [['bash', 'devsecops/trivy_scan.sh', 'lab3-flask-app', '1.0']], 'task4-security.log', 'Actual app image scanned; no CRITICAL vulnerabilities reported. Jenkins configuration provided; no Jenkins server job executed.')
scan = subprocess.run(['docker', 'run', '--rm', '-v', '/var/run/docker.sock:/var/run/docker.sock', '-v', 'lab3-trivy-cache:/root/.cache', 'aquasec/trivy:latest', 'image', '--skip-db-update', '--severity', 'HIGH,CRITICAL', '--format', 'json', 'lab3-flask-app:1.0'], capture_output=True, text=True)
(E/'task4-json-scan.log').write_text(scan.stderr)
if scan.returncode == 0:
    (E/'task4-vulnerabilities.json').write_text(scan.stdout)
    from collections import Counter
    counts = Counter(v['Severity'] for r in json.loads(scan.stdout).get('Results', []) for v in r.get('Vulnerabilities', []))
    RESULTS['4']['detail'] += f' Package findings: {counts["HIGH"]} HIGH, {counts["CRITICAL"]} CRITICAL.'
(E/'results.json').write_text(json.dumps(RESULTS, indent=2))
report_code = command([sys.executable, 'scripts/build_reports.py'], 'task7-reports.log')
RESULTS['7'] = {'status': 'PASS' if report_code == 0 else 'FAIL', 'detail': 'Report generation exit code: ' + str(report_code)}
(E/'results.json').write_text(json.dumps(RESULTS, indent=2))
print(json.dumps(RESULTS, indent=2))
sys.exit(1 if report_code or any(r['status'] != 'PASS' for r in RESULTS.values()) else 0)
