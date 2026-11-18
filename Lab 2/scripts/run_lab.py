#!/usr/bin/env python3
"""Run the nine reference experiments on the dedicated colima-lab2 / lab2 cluster."""
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import threading
import time
import urllib.request

BASE = Path(__file__).resolve().parents[1]
EVIDENCE = BASE / 'evidence'
EVIDENCE.mkdir(exist_ok=True)
os.environ['DOCKER_CONTEXT'] = 'colima-lab2'
os.environ['DOCKER_HOST'] = 'unix://' + str(Path.home() / '.colima/lab2/docker.sock')
RESULTS = {}
log = None

def record(text):
    print(text, flush=True)
    if log:
        log.write(text + '\n')
        log.flush()

def command(*args, timeout=600):
    record('$ ' + shlex.join(str(a) for a in args))
    p = subprocess.Popen([str(a) for a in args], cwd=BASE, env=os.environ,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    output = []
    def pump():
        for line in p.stdout:
            output.append(line)
            record(line.rstrip('\n'))
    reader = threading.Thread(target=pump, daemon=True)
    reader.start()
    try:
        p.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        p.wait()
        reader.join()
        raise
    reader.join()
    if p.returncode:
        raise RuntimeError(f'Command exited with status {p.returncode}')
    return ''.join(output)

def request(port, path='/', attempts=40):
    url = f'http://127.0.0.1:{port}{path}'
    for _ in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=3) as r:
                data = json.load(r)
            record(f'GET {url}\n{json.dumps(data)}')
            return data
        except Exception:
            time.sleep(1)
    raise RuntimeError(f'Endpoint did not become ready: {url}')

def docker(*args, **kw): return command('docker', *args, **kw)
def kube(*args, **kw): return command('kubectl', '--context', 'lab2', '-n', 'lab2', *args, **kw)

def task4():
    docker('version')
    docker('build', '-t', 'lab2-python-app:1.0', 'app', timeout=1200)
    docker('run', '-d', '--name', 'lab2-app', '-p', '127.0.0.1:5004:5000', 'lab2-python-app:1.0')
    assert request(5004, '/health')['status'] == 'healthy'
    assert 'VERSION 1.0' in request(5004)['message']
    docker('history', 'lab2-python-app:1.0')
    docker('image', 'inspect', 'lab2-python-app:1.0', '--format', '{{json .RootFS.Layers}}')

def task5():
    docker('ps')
    docker('stop', 'lab2-app')
    docker('ps', '-a')
    docker('start', 'lab2-app')
    request(5004, '/health')
    docker('exec', 'lab2-app', 'ls', '/app')
    docker('stop', 'lab2-app')
    docker('rm', 'lab2-app')
    docker('images', 'lab2-python-app')
    docker('run', '-d', '-p', '127.0.0.1:5050:5000', '--name', 'lab2-registry', 'registry:2', timeout=900)
    request(5050, '/v2/')
    docker('tag', 'lab2-python-app:1.0', 'localhost:5050/lab2-python-app:1.0')
    docker('push', 'localhost:5050/lab2-python-app:1.0', timeout=900)
    assert 'lab2-python-app' in request(5050, '/v2/_catalog')['repositories']
    command('docker-compose', '-f', 'compose/compose.yaml', 'up', '-d', '--build', timeout=1200)
    command('docker-compose', '-f', 'compose/compose.yaml', 'ps')
    request(5001, '/health')
    assert request(5001)['visits'] == 1
    assert request(5001)['visits'] == 2
    command('docker-compose', '-f', 'compose/compose.yaml', 'down')

def task6():
    docker('run', '-d', '--name', 'lab2-novol', '-p', '127.0.0.1:5101:5000', 'lab2-python-app:1.0')
    request(5101, '/health')
    for expected in (1, 2, 3): assert request(5101)['visits'] == expected
    docker('rm', '-f', 'lab2-novol')
    docker('run', '-d', '--name', 'lab2-novol', '-p', '127.0.0.1:5101:5000', 'lab2-python-app:1.0')
    request(5101, '/health')
    assert request(5101)['visits'] == 1
    docker('rm', '-f', 'lab2-novol')
    docker('volume', 'create', 'lab2-vol')
    docker('run', '-d', '--name', 'lab2-volume', '-v', 'lab2-vol:/data', '-p', '127.0.0.1:5102:5000', 'lab2-python-app:1.0')
    request(5102, '/health')
    assert request(5102)['visits'] == 1
    assert request(5102)['visits'] == 2
    docker('rm', '-f', 'lab2-volume')
    docker('run', '-d', '--name', 'lab2-volume', '-v', 'lab2-vol:/data', '-p', '127.0.0.1:5102:5000', 'lab2-python-app:1.0')
    request(5102, '/health')
    assert request(5102)['visits'] == 3
    docker('rm', '-f', 'lab2-volume')
    mount = str(BASE / 'storage-demo/bind-data') + ':/data'
    docker('run', '-d', '--name', 'lab2-bind', '-v', mount, '-p', '127.0.0.1:5103:5000', 'lab2-python-app:1.0')
    request(5103, '/health')
    assert request(5103)['visits'] == 1
    docker('rm', '-f', 'lab2-bind')
    assert (BASE / 'storage-demo/bind-data/counter.txt').read_text() == '1'
    docker('run', '-d', '--name', 'lab2-bind', '-v', mount, '-p', '127.0.0.1:5103:5000', 'lab2-python-app:1.0')
    request(5103, '/health')
    assert request(5103)['visits'] == 2
    record('Host counter.txt = ' + (BASE / 'storage-demo/bind-data/counter.txt').read_text())
    docker('rm', '-f', 'lab2-bind')
    docker('volume', 'inspect', 'lab2-vol')

def task7():
    docker('network', 'create', 'lab2-net')
    docker('run', '-d', '--name', 'lab2-net-app', '--network', 'lab2-net', 'lab2-python-app:1.0')
    docker('run', '-d', '--name', 'lab2-net-client', '--network', 'lab2-net', 'lab2-python-app:1.0', 'sleep', '3600')
    ip = docker('inspect', '--format', '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}', 'lab2-net-app').strip()
    time.sleep(2)
    for host in ('lab2-net-app', ip):
        out=docker('exec', 'lab2-net-client', 'python', '-c', f'import urllib.request; print(urllib.request.urlopen("http://{host}:5000/health").read().decode())')
        assert json.loads(out)['status'] == 'healthy'
    docker('network', 'inspect', 'lab2-net')

def task1():
    command('minikube', '-p', 'lab2', 'start', '--driver=docker', '--kubernetes-version=v1.37.0', '--container-runtime=containerd', '--cpus=2', '--memory=3072', '--disk-size=20g', '--base-image=gcr.io/k8s-minikube/kicbase:v0.0.51', '--preload=true', '--cache-images=false', timeout=1500)
    command('minikube', '-p', 'lab2', 'image', 'load', '--daemon=true', 'lab2-python-app:1.0', timeout=900)
    command('kubectl', '--context', 'lab2', 'get', 'nodes', '-o', 'wide')
    kube('apply', '-f', 'k8s/namespace.yaml')
    kube('apply', '-f', 'k8s/')
    kube('rollout', 'status', 'deployment/lab2-app', '--timeout=180s')
    kube('get', 'deployments,pods,svc', '-o', 'wide')
    ready=json.loads(kube('get', 'deployment/lab2-app', '-o', 'json'))['status']['readyReplicas']
    assert ready == 2
    verify_pods('VERSION 1.0')
    out=kube('exec', 'deployment/lab2-app', '--', 'python', '-c', 'import urllib.request;print(urllib.request.urlopen("http://lab2-service/health").read().decode())')
    assert json.loads(out)['status']=='healthy'

def verify_pods(version):
    pods=json.loads(kube('get', 'pods', '-l', 'app=lab2-app', '-o', 'json'))['items']
    for p in pods:
        if p['metadata'].get('deletionTimestamp'):continue
        out=kube('exec', p['metadata']['name'], '--', 'python', '-c', 'import urllib.request;print(urllib.request.urlopen("http://localhost:5000/").read().decode())')
        assert version in json.loads(out)['message']

def task2():
    docker('build', '-t', 'lab2-python-app:2.0', 'app-v2', timeout=1200)
    command('minikube', '-p', 'lab2', 'image', 'load', '--daemon=true', 'lab2-python-app:2.0', timeout=900)
    kube('set', 'image', 'deployment/lab2-app', 'web=lab2-python-app:2.0')
    kube('rollout', 'status', 'deployment/lab2-app', '--timeout=180s')
    verify_pods('VERSION 2.0')
    kube('rollout', 'history', 'deployment/lab2-app')
    kube('rollout', 'undo', 'deployment/lab2-app')
    kube('rollout', 'status', 'deployment/lab2-app', '--timeout=180s')
    verify_pods('VERSION 1.0')
    for count in (5, 3):
        kube('scale', 'deployment/lab2-app', f'--replicas={count}')
        kube('rollout', 'status', 'deployment/lab2-app', '--timeout=180s')
        kube('get', 'deployments,pods', '-o', 'wide')
        d=json.loads(kube('get', 'deployment/lab2-app', '-o', 'json'))
        assert d['status']['readyReplicas'] == count

def task8():
    command('sh', 'scripts/cicd.sh', '3', timeout=1200)
    d=json.loads(kube('get', 'deployment/lab2-app', '-o', 'json'))
    assert d['spec']['template']['spec']['containers'][0]['image'] == 'lab2-python-app:3'
    assert d['status']['readyReplicas']==2
    verify_pods('VERSION 1.0')

def main():
    global log
    results_path=EVIDENCE/'results.json'
    if results_path.exists():RESULTS.update(json.loads(results_path.read_text()))
    selected=sys.argv[1:] or ['4','5','6','7','1','2','8']
    for n in selected:
        with (EVIDENCE/f'task{n}.log').open('w') as stream:
            log=stream
            record(f'Lab 2 Task {n} - actual execution log')
            try:
                globals()['task'+n]()
                RESULTS[n]={'status':'PASS','log':f'evidence/task{n}.log'}
                record('RESULT: PASS')
            except Exception as exc:
                RESULTS[n]={'status':'FAILED','error':str(exc),'log':f'evidence/task{n}.log'}
                record('RESULT: FAILED - '+str(exc))
                results_path.write_text(json.dumps(RESULTS,indent=2))
                raise
            results_path.write_text(json.dumps(RESULTS,indent=2))
    log=None

if __name__=='__main__':main()
