"""Run isolated Lab 4 experiments and retain actual command transcripts."""
import collections
import hashlib
import json
import os
from pathlib import Path
import secrets
import shlex
import shutil
import subprocess
import sys
import threading
import time
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
E=ROOT/'evidence'
E.mkdir(exist_ok=True)
RUNTIME=ROOT/'.runtime'
RUNTIME.mkdir(exist_ok=True)
os.environ['DOCKER_CONTEXT']='colima-lab2'
os.environ['DOCKER_HOST']=subprocess.check_output(['docker','context','inspect','--format','{{.Endpoints.docker.Host}}'],text=True).strip()
RESULTS=json.loads((E/'results.json').read_text()) if (E/'results.json').exists() else {}
LOG=None


def note(value):
    print(value,flush=True)
    if LOG: LOG.write(value+'\n');LOG.flush()


def cmd(args):
    note('$ '+shlex.join(map(str,args)))
    result=subprocess.run(list(map(str,args)),capture_output=True,text=True)
    if result.stdout:note(result.stdout.rstrip())
    if result.stderr:note(result.stderr.rstrip())
    if result.returncode:raise RuntimeError(f'Command failed (exit {result.returncode})')
    return result.stdout.strip()


def request(port,path='/'):
    with urllib.request.urlopen(f'http://localhost:{port}{path}',timeout=5) as r:
        return json.load(r)


def ready(port):
    for attempt in range(60):
        try:
            assert request(port,'/health')['status']=='healthy'
            return
        except Exception:
            if attempt==59:raise
            time.sleep(1)


def compose(folder,project,*args):
    return cmd(['docker','compose','-p',project,'-f',f'{folder}/docker-compose.yml',*args])


def task1():
    # Only destroy the volume created during this experiment, after verifying its archive.
    for name in ['lab4-dr-vol','lab4-dr-vol-restored']:
        found=subprocess.run(['docker','volume','inspect',name],capture_output=True)
        if found.returncode==0:raise RuntimeError(f'{name} already exists; preserve or inspect previous DR data before rerunning')
    cmd(['docker','volume','create','--label','lab=lab4','lab4-dr-vol'])
    cmd(['docker','run','-d','--name','lab4-dr-app','--label','lab=lab4','-v','lab4-dr-vol:/data','-p','127.0.0.1:5200:5000','lab4-app:1.0'])
    ready(5200)
    before=[request(5200),request(5200)]
    assert [v['stateful_counter'] for v in before]==[1,2]
    note('Primary counters: 1, 2')
    cmd(['bash','disaster-recovery/backup.sh'])
    archive=ROOT/'disaster-recovery/backup_snapshot.tar.gz'
    archive_hash=hashlib.sha256(archive.read_bytes()).hexdigest()
    counter=cmd(['docker','run','--rm','-v',f'{archive.parent}:/backup:ro','lab4-app:1.0','python','-c',
        'import tarfile; t=tarfile.open("/backup/backup_snapshot.tar.gz"); print(t.extractfile("./counter.txt").read().decode())'])
    assert counter=='2'
    cmd(['docker','rm','-f','lab4-dr-app'])
    cmd(['docker','volume','rm','lab4-dr-vol'])
    cmd(['bash','disaster-recovery/restore.sh'])
    cmd(['docker','run','-d','--name','lab4-dr-failover','--label','lab=lab4','-v','lab4-dr-vol-restored:/data','-p','127.0.0.1:5201:5000','lab4-app:1.0'])
    ready(5201)
    after=request(5201)
    assert after['stateful_counter']==3
    data={'before':before,'after':after,'archive_sha256':archive_hash}
    (E/'task1-recovery.json').write_text(json.dumps(data,indent=2))
    note('[PASS] Primary volume deleted; restored counter resumed at 3')
    return 'Backup verified at counter 2; original volume deleted; failover resumed at 3. Recovery covers the saved snapshot.'


def task2():
    cmd(['bash','ci-testing/run_pipeline.sh'])
    return 'Local Build -> 7 pytest tests -> scoped Vault injection -> Deploy -> Verify pipeline passed. Jenkinsfile prepared; Jenkins server requires authentication and no server build is claimed.'


def switch_bg(color):
    shutil.copyfile(ROOT/f'blue-green/nginx-{color}.conf',ROOT/'blue-green/conf/default.conf')
    cmd(['docker','exec','lab4-bg-nginx','nginx','-t'])
    cmd(['docker','exec','lab4-bg-nginx','nginx','-s','reload'])


def wait_version(port,version):
    for attempt in range(100):
        value=request(port)
        if value['version']==version:return value
        time.sleep(.05)
    raise AssertionError('Expected version was not routed: '+version)


def task3():
    shutil.copyfile(ROOT/'blue-green/nginx-blue.conf',ROOT/'blue-green/conf/default.conf')
    compose('blue-green','lab4-bg','up','-d')
    ready(5300)
    switch_bg('blue')
    initial=wait_version(5300,'1.0-blue')
    samples=[]
    stop=threading.Event()
    def probe():
        while not stop.is_set():
            try:samples.append({'version':request(5300)['version'],'ok':True})
            except Exception as error:samples.append({'ok':False,'error':str(error)})
            stop.wait(.025)
    worker=threading.Thread(target=probe);worker.start()
    try:
        time.sleep(.2)
        switch_bg('green')
        green=wait_version(5300,'2.0-green')
        time.sleep(.3)
        switch_bg('blue')
        rollback=wait_version(5300,'1.0-blue')
        switch_bg('green')
        wait_version(5300,'2.0-green')
        time.sleep(.2)
    finally:stop.set();worker.join()
    assert samples and all(v['ok'] for v in samples),samples
    assert {'1.0-blue','2.0-green'} <= {v['version'] for v in samples}
    (E/'task3-cutover.json').write_text(json.dumps({'initial':initial,'green':green,'rollback':rollback,'samples':samples},indent=2))
    note(f'[PASS] Blue -> Green -> Blue rollback -> Green; {len(samples)} probe requests, zero observed failures')
    return f'Cutover and rollback verified; {len(samples)} probe requests had zero observed failures. Final route: Green. This sample does not prove universal zero downtime.'


def task4():
    base=RUNTIME/'gitops'
    if base.exists():raise RuntimeError('GitOps sandbox already exists; preserve earlier evidence before rerunning')
    base.mkdir()
    remote=base/'remote.git';source=base/'author';checkout=base/'controller'
    cmd(['git','init','--bare','--initial-branch=main',remote])
    cmd(['git','init','--initial-branch=main',source])
    cmd(['git','-C',source,'config','user.name','Lab 4 Demo'])
    cmd(['git','-C',source,'config','user.email','lab4@localhost'])
    manifest=source/'desired-state.yml'
    shutil.copyfile(ROOT/'gitops/desired-state.yml',manifest)
    cmd(['git','-C',source,'add','desired-state.yml'])
    cmd(['git','-C',source,'commit','-m','Declare Lab 4 v1 desired state'])
    cmd(['git','-C',source,'remote','add','origin',remote])
    cmd(['git','-C',source,'push','-u','origin','main'])
    def reconcile():return cmd([sys.executable,'gitops/controller.py','--repository',remote,'--checkout',checkout])
    reconcile();ready(5500)
    assert request(5500)['version']=='1.0-gitops'
    with urllib.request.urlopen('http://localhost:5501/',timeout=5) as r:assert r.status==200
    assert 'changed=0' in reconcile()
    cmd(['docker','stop','lab4-gitops-app'])
    assert 'stopped' in reconcile();ready(5500)
    original=manifest.read_text()
    manifest.write_text(original.replace('lab4-app:1.0','lab4-app:2.0').replace('1.0-gitops','2.0-gitops'))
    cmd(['git','-C',source,'add','desired-state.yml'])
    cmd(['git','-C',source,'commit','-m','Promote GitOps app to v2'])
    cmd(['git','-C',source,'push','origin','main'])
    assert 'image' in reconcile();ready(5500)
    assert request(5500)['version']=='2.0-gitops'
    cmd(['git','-C',source,'revert','--no-edit','HEAD'])
    cmd(['git','-C',source,'push','origin','main'])
    reconcile();ready(5500)
    assert request(5500)['version']=='1.0-gitops'
    assert 'changed=0' in reconcile()
    note('[PASS] Git-backed create, no-drift, stopped-container repair, v2 promotion, and Git-revert rollback verified')
    return 'Isolated local Git remote: desired state fetched by revision, drift repaired, v2 promoted and Git revert rolled back to v1. Controller cycles invoked explicitly; no hosted GitOps controller.'


def task6():
    env=RUNTIME/'vault.env'
    if not env.exists():
        env.write_text('LAB4_VAULT_TOKEN='+secrets.token_hex(32)+'\n');env.chmod(0o600)
    cmd(['docker','compose','--env-file',env,'-p','lab4-vault','-f','vault/docker-compose.yml','up','-d'])
    for attempt in range(60):
        try:
            with urllib.request.urlopen('http://localhost:8200/v1/sys/health',timeout=3) as response:
                assert json.load(response)['sealed'] is False
            break
        except Exception:
            if attempt==59:raise
            time.sleep(1)
    cmd([sys.executable,'scripts/vault_demo.py'])
    cmd([sys.executable,'scripts/pipeline_secret.py'])
    return 'Generated credentials stored and read back; scoped read-only token injected credentials into a pipeline child process; unauthorized write denied. Vault dev mode is ephemeral and uses local HTTP.'


def canary_config(stable,canary):
    text=(ROOT/'canary/nginx-canary.conf').read_text()
    text=text.replace('server lab4-stable:5000 weight=9;', 'server lab4-stable:5000 down;' if stable==0 else f'server lab4-stable:5000 weight={stable};')
    text=text.replace('server lab4-canary:5000 weight=1;', 'server lab4-canary:5000 down;' if canary==0 else f'server lab4-canary:5000 weight={canary};')
    (ROOT/'canary/conf/default.conf').write_text(text)
    cmd(['docker','exec','lab4-canary-nginx','nginx','-t'])
    cmd(['docker','exec','lab4-canary-nginx','nginx','-s','reload'])
    time.sleep(.3)


def task7():
    shutil.copyfile(ROOT/'canary/nginx-canary.conf',ROOT/'canary/conf/default.conf')
    compose('canary','lab4-canary','up','-d');ready(5400)
    distributions={}
    for label,stable,canary in [('90-10',9,1),('75-25',3,1),('50-50',1,1),('100-canary',0,1),('rollback-stable',1,0)]:
        canary_config(stable,canary)
        counts=collections.Counter(request(5400)['version'] for _ in range(100))
        distributions[label]=dict(counts)
        note(label+': '+json.dumps(dict(counts)))
        if stable and canary:
            assert set(counts)=={'1.0-stable','2.0-canary'}
            assert abs(counts['2.0-canary']-100*canary/(stable+canary))<=5
        elif stable:assert counts=={'1.0-stable':100}
        else:assert counts=={'2.0-canary':100}
    canary_config(9,1)
    (E/'task7-distribution.json').write_text(json.dumps(distributions,indent=2))
    note('[PASS] Weighted rollout, full promotion, rollback verified; final split restored to 90/10')
    return '100-request samples verified 90/10, 75/25, 50/50, full canary promotion and stable rollback. Final configuration: 90/10. Requests are a local sequential sample.'


TASKS={1:task1,2:task2,3:task3,4:task4,6:task6,7:task7}
if __name__=='__main__':
    selected=[int(v) for v in sys.argv[1:]] if len(sys.argv)>1 else [1,3,4,7,6,2]
    for number in selected:
        with (E/f'task{number}.log').open('w') as handle:
            LOG=handle
            try:
                detail=TASKS[number]()
                RESULTS[str(number)]={'status':'PASS','detail':detail}
            except Exception as error:
                note('[FAIL] '+str(error))
                RESULTS[str(number)]={'status':'FAIL','detail':str(error)}
            finally:
                LOG=None
                (E/f'task{number}-result.json').write_text(json.dumps(RESULTS[str(number)],indent=2))
                merged={f.stem.split('-')[0][4:]: json.loads(f.read_text()) for f in E.glob('task*-result.json')}
                (E/'results.json').write_text(json.dumps(merged,indent=2))
    print(json.dumps(RESULTS,indent=2))
    sys.exit(1 if any(v['status']=='FAIL' for v in RESULTS.values()) else 0)
