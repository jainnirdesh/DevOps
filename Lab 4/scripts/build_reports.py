"""Generate task-wise Markdown and DOCX from this lab's recorded execution."""
from pathlib import Path
import json
import re
from docx import Document
from docx.shared import Inches, Pt
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'evidence'
RESULTS=json.loads((E/'results.json').read_text())
if any(RESULTS.get(str(n), {}).get('status') != 'PASS' for n in [1,2,3,4,6,7]):
    raise RuntimeError('Generate final reports only after all six execution tasks pass.')
PROBES=len(json.loads((E/'task3-cutover.json').read_text())['samples'])
FIG=E/'figures';FIG.mkdir(exist_ok=True)
DOCS=ROOT/'docs';DOCS.mkdir(exist_ok=True)
SPECS={
1:('Disaster_Recovery_Mechanism','Design and demonstrate disaster recovery',
'Protect Docker volume state using a verified backup and restore it after simulated loss of the original volume.',
'''1. Create `lab4-dr-vol` and start the primary application on loopback port 5200.
2. Make two requests and verify counters 1 and 2.
3. Create a compressed snapshot with `disaster-recovery/backup.sh` and verify its counter before deletion.
4. Remove only the experiment's primary container and volume.
5. Restore into `lab4-dr-vol-restored`, start failover on port 5201, and verify counter 3.''',
'''bash disaster-recovery/backup.sh
bash disaster-recovery/restore.sh
curl -fsS http://localhost:5201/health''',
'''The saved snapshot contained counter 2 and the first failover request returned counter 3. The archive SHA-256 and before/after responses are retained in [task1-recovery.json](../evidence/task1-recovery.json).

This proves recovery to the saved snapshot. Writes after a snapshot would not be recovered by this method. No automatic failover controller or production recovery-time objective was demonstrated. The runner refuses to overwrite pre-existing disaster-recovery volumes.''',
['disaster-recovery/backup.sh','disaster-recovery/restore.sh']),
2:('Automated_Testing_CICD_Pipeline','Implement automated testing in a CI/CD pipeline',
'Run application tests as a quality gate before deployment and verify the deployed service.',
'''1. Build application images 1.0 and 2.0.
2. Execute seven pytest tests against the Flask application.
3. Retrieve credentials using a scoped Vault token and inject them into a child process.
4. Deploy the Blue-Green stack only after the previous stages succeed.
5. Verify `/health` through the reverse proxy.''',
'''bash ci-testing/run_pipeline.sh
.venv/bin/python -m pytest ci-testing/test_app.py -v --tb=short''',
'''The local shell pipeline passed all stages. **7 tests passed**, covering response status, message/version/hostname fields, health, and an unknown route. Each test uses a temporary state directory. `set -euo pipefail` propagates test failures and stops subsequent stages.

A Jenkinsfile is provided for an appropriately prepared local agent. The existing Jenkins server requires authentication, so no Lab 4 Jenkins server build or remote SCM execution is claimed. The successful evidence is from the local pipeline, which also verified on-demand secret injection.''',
['ci-testing/run_pipeline.sh','ci-testing/Jenkinsfile','ci-testing/test_app.py']),
3:('Blue_Green_Deployment_Strategy','Implement Blue-Green deployment',
'Run two application versions behind Nginx, verify traffic cutover, and demonstrate rollback.',
'''1. Start Blue (`1.0-blue`), Green (`2.0-green`), and the Nginx proxy on port 5300.
2. Confirm the initial Blue response.
3. Copy the Green upstream configuration, validate it with `nginx -t`, and reload Nginx.
4. Verify Green, roll back to Blue, then restore the final Green route.
5. Run HTTP probes throughout the switching sequence and retain every result.''',
'''docker compose -p lab4-bg -f blue-green/docker-compose.yml up -d
cp blue-green/nginx-green.conf blue-green/conf/default.conf
docker exec lab4-bg-nginx nginx -t
docker exec lab4-bg-nginx nginx -s reload
curl -fsS http://localhost:5300/''',
'''The saved run verified Blue -> Green -> Blue rollback -> Green. **47 HTTP probe requests had zero observed failures**. Both versions appeared in the probe sample. Final routing is Green.

Full samples: [task3-cutover.json](../evidence/task3-cutover.json). This finite local sample is evidence of the observed cutover, not a guarantee of zero downtime under every workload. Blue-Green needs parallel capacity; application schema compatibility and database migration were outside this demonstration.''',
['blue-green/docker-compose.yml','blue-green/nginx-blue.conf','blue-green/nginx-green.conf']),
4:('GitOps_Based_Delivery','Implement Git-backed desired-state delivery',
'Fetch versioned desired state from Git and reconcile local Docker containers, including drift and rollback.',
'''1. Create an isolated local bare Git remote and author/controller repositories under `.runtime/gitops`.
2. Commit the desired YAML and push to that local remote.
3. Fetch and check out its revision, then create the application and Nginx sidecar.
4. Reconcile again to confirm zero drift; stop the app and repair it in the next cycle.
5. Commit and push v2, reconcile, and verify the new app version.
6. Use `git revert`, push to the local remote, reconcile, and verify rollback to v1.''',
'''.venv/bin/python gitops/controller.py --repository "$PWD/.runtime/gitops/remote.git" --checkout "$PWD/.runtime/gitops/controller"
curl -fsS http://localhost:5500/
curl -I http://localhost:5501/''',
'''All six steps passed. The reconciler checks container ownership, running state, image reference/content, desired environment values, and loopback port mappings. It returns failure on Docker errors and fixes the Nginx sidecar's container port to 80.

The Git repositories and pushes are local sandbox resources; the user's main repository was not committed or pushed. Controller cycles were invoked explicitly. No hosted Git remote, Argo CD, Flux, or continuously polling controller was used. One instance per declared service is supported; unsupported replica counts are rejected.''',
['gitops/desired-state.yml','gitops/deploy.py','gitops/controller.py']),
6:('Secret_Management_Pipeline','Implement secret management for the pipeline',
'Store generated credentials in Vault and let the pipeline retrieve them with restricted read access.',
'''1. Start Vault on loopback port 8200 using a generated development token from an ignored local file.
2. Generate a database password and API key, write them to `secret/lab4/app`, and verify retrieval without printing values.
3. Create a policy that only reads `secret/data/lab4/app` and issue a token with a one-hour TTL.
4. Verify that the restricted token cannot write to an unauthorized path.
5. Fetch the credentials on demand and pass them as environment variables to a pipeline child process.''',
'''docker compose --env-file .runtime/vault.env -p lab4-vault -f vault/docker-compose.yml up -d
bash vault/init-vault.sh
.venv/bin/python scripts/pipeline_secret.py''',
'''Vault initialization, write/read verification, policy enforcement, and pipeline injection all passed. Evidence prints status and key names; credential values are redacted. Local token files have mode 0600 and are excluded from Git.

This is **Vault development mode**: storage is ephemeral, the local endpoint uses HTTP, and it is not a production Vault deployment. The pipeline token expires after one hour; repeat Task 6 to issue a fresh one. The environment file is used for the local dev server, while application credentials are retrieved from Vault.''',
['vault/docker-compose.yml','scripts/vault_demo.py','scripts/pipeline_secret.py']),
7:('Canary_Deployment_Strategy','Implement a Canary deployment strategy',
'Route weighted traffic to a new version, progressively promote it, and demonstrate stable rollback.',
'''1. Start stable v1, canary v2, and Nginx on loopback port 5400.
2. Configure upstream weights 9:1 and send 100 sequential requests.
3. Repeat with 3:1 and 1:1 weights.
4. Mark stable `down` to promote all traffic to canary.
5. Mark canary `down` to roll back all traffic to stable.
6. Restore the final 9:1 configuration.''',
'''docker compose -p lab4-canary -f canary/docker-compose.yml up -d
docker exec lab4-canary-nginx nginx -t
docker exec lab4-canary-nginx nginx -s reload
curl -fsS http://localhost:5400/''',
'''Each stage used 100 requests. Recorded distributions are below. Nginx round-robin worker behavior can produce small differences from nominal percentages in a finite sample. Zero is represented by `down`, since Nginx weights must be positive. Final routing is restored to 90/10.

These are local sequential requests, not a load test or automatic latency/error-driven rollout policy. Full counts are retained in [task7-distribution.json](../evidence/task7-distribution.json).''',
['canary/docker-compose.yml','canary/nginx-canary.conf'])}


def make_figure(n):
    lines=(E/f'task{n}.log').read_text(errors='replace').splitlines()[-27:]
    canvas=Image.new('RGB',(1550,max(220,65+len(lines)*24)),'#111827')
    draw=ImageDraw.Draw(canvas)
    font=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',16)
    draw.text((18,12),f'Lab 4 Task {n}: actual saved command output (rendered excerpt)',font=font,fill='#93c5fd')
    for i,line in enumerate(lines):draw.text((18,50+i*24),line[:150],font=font,fill='#e5e7eb')
    canvas.save(FIG/f'task{n}.png')


def docx(markdown,path):
    document=Document()
    in_code=False
    table_rows=[]
    def flush_table():
        if table_rows:
            table=document.add_table(rows=0, cols=len(table_rows[0]));table.style='Table Grid'
            for row in table_rows:
                cells=table.add_row().cells
                for i,value in enumerate(row):cells[i].text=value.strip().replace('**','').replace('`','')
            table_rows.clear()
    for line in markdown.splitlines():
        if line.startswith('```'):
            flush_table();in_code=not in_code;continue
        if in_code:
            p=document.add_paragraph();run=p.add_run(line);run.font.name='Menlo';run.font.size=Pt(8)
            continue
        image=re.fullmatch(r'!\[.*?\]\((.*?)\)',line)
        if image:
            flush_table();document.add_picture(str(DOCS/image.group(1)),width=Inches(6.3));continue
        if line.startswith('|'):
            if re.fullmatch(r'[| :\-]+',line):continue
            table_rows.append(line.strip('|').split('|'));continue
        flush_table()
        if not line.strip():continue
        if line.startswith('#'):
            level=len(line)-len(line.lstrip('#'));document.add_heading(line[level:].strip(),min(level,3));continue
        clean=re.sub(r'\[([^]]+)\]\([^)]+\)',r'\1',line).replace('**','').replace('`','')
        document.add_paragraph(clean)
    flush_table();document.save(path)


HEADER='# Lab 4: Advanced Deployment Strategies & Enterprise DevOps\n\n'
META='Nirdesh Jain | 18 November 2026 | macOS Apple Silicon, Docker context `colima-lab2`\n\nCommands run from `Lab 4`. Results belong to the saved local execution. Figures are rendered log excerpts, not GUI screenshots.\n\n'
links=[]
for n,(slug,title,objective,steps,commands,observations,files) in sorted(SPECS.items()):
    make_figure(n)
    text=HEADER+f'## Task {n}: {title}\n\n'+META
    text+='## 1. Objective\n\n'+objective+'\n\n## 2. Procedure\n\n'+steps+'\n\n'
    text+='## 3. Commands\n\n```sh\n'+commands+'\n```\n\n'
    text+='## 4. Observations\n\n'+observations+'\n\n'
    if n==7:
        counts=json.loads((E/'task7-distribution.json').read_text())
        text+='| Stage | Stable responses | Canary responses |\n| --- | ---: | ---: |\n'
        for stage,c in counts.items():text+=f'| {stage} | {c.get("1.0-stable",0)} | {c.get("2.0-canary",0)} |\n'
        text+='\n'
    text+=f'![Task {n} execution](../evidence/figures/task{n}.png)\n\nFull transcript: [task{n}.log](../evidence/task{n}.log).\n\n'
    text+='## 5. Implementation files\n\n'+'\n'.join(f'- [{f}](../{f})' for f in files)+'\n\n'
    result=RESULTS.get(str(n),{'status':'NOT RUN','detail':'No recorded result.'})
    text=text.replace('47',str(PROBES))
    text+=f'## Execution status\n\n**{result["status"]}**: {result["detail"]}\n'
    filename=f'Task{n}_{slug}'
    (DOCS/f'{filename}.md').write_text(text)
    docx(text,DOCS/f'{filename}.docx')
    links.append((n,title,filename+'.md'))

summary=HEADER+'## Task 5: Advanced deployment strategies report\n\n'+META
summary+='## 1. Architecture\n\n```text\nBuild -> Automated tests -> Vault injection -> Deploy -> Health verification\nBlue v1 + Green v2 -> Nginx cutover and rollback\nStable v1 + Canary v2 -> Nginx weighted routing\nLocal Git remote -> fetched desired revision -> Docker reconciliation\nDocker volume -> verified archive -> restored failover volume\n```\n\n'
summary+='## 2. Verified outcomes\n\n| Task | Status | Observed scope |\n| --- | --- | --- |\n'
for n in [1,2,3,4,6,7]:
    result=RESULTS.get(str(n),{'status':'NOT RUN','detail':'No recorded result.'})
    summary+=f'| {n} | {result["status"]} | {result["detail"]} |\n'
summary+='\n## 3. Strategy comparison\n\n| Approach | Change mechanism | Demonstrated rollback | Main tradeoff |\n| --- | --- | --- | --- |\n| Blue-Green | Switch Nginx between parallel versions | Route back to Blue | Parallel application capacity |\n| Canary | Adjust Nginx weights | Route all requests to stable | Sample-based checks; automatic policy not implemented |\n| Git-backed delivery | Fetch a committed manifest and reconcile | Git revert followed by reconciliation | Controller cycles manually invoked |\n| Disaster recovery | Backup and restore volume state | Restore a verified snapshot | Changes after the snapshot are outside recovery |\n\n'
summary+='## 4. Execution evidence\n\n'
for n in [1,2,3,4,6,7]:summary+=f'![Task {n} evidence](../evidence/figures/task{n}.png)\n\n'
summary+='## 5. Limitations and conclusion\n\nThe local pipeline passed seven tests and verified deployment. No Lab 4 Jenkins server job ran because the existing server requires authentication. Blue-Green had zero failures in 47 observed probes; this is a measured sample rather than a universal downtime guarantee. Canary checks used 100 requests at each stage. GitOps used an isolated local Git remote and explicit reconciliation cycles. Vault ran in ephemeral development mode over local HTTP with scoped read-only pipeline access. Disaster recovery restored the saved counter state, without claiming recovery of later writes.\n\n'
summary+='All six implementation experiments passed within those local scopes. This seventh artifact documents the outcomes. Full statuses: [results.json](../evidence/results.json). Reproduction: [README.md](../README.md).\n'
filename='Task5_Advanced_Deployment_Strategies_Report'
summary=summary.replace('47',str(PROBES))
(DOCS/f'{filename}.md').write_text(summary)
docx(summary,DOCS/f'{filename}.docx')
RESULTS['5']={'status':'PASS','detail':'Seven task-wise Markdown and DOCX reports generated from actual execution logs and measured results.'}
(E/'task5-result.json').write_text(json.dumps(RESULTS['5'],indent=2))
(E/'results.json').write_text(json.dumps(RESULTS,indent=2))
links.append((5,'Advanced deployment strategies report',filename+'.md'))
index='\n'.join(f'- [Task {n}: {title}](docs/{file})' for n,title,file in sorted(links))
(ROOT/'README.md').write_text('''# Lab 4: Advanced Deployment Strategies & Enterprise DevOps

Local execution: 18 November 2026. Six implementation tasks passed; Task 5 records the results. Actual logs and responses are in `evidence/`. Reference reports, screenshots, and backup archives were not reused as execution evidence.

## Task-wise reports

'''+index+'''

Matching DOCX files are alongside the Markdown reports in `docs/`. Evidence figures render real saved output, not browser screenshots.

## Verified results

- Recovery: snapshot at counter 2 restored; first failover request returned 3.
- Testing: local build/test/secret-injection/deploy/verify pipeline passed all 7 tests.
- Blue-Green: cutover and rollback; 47 HTTP probes, zero observed failures; final route Green.
- GitOps: committed local desired state, no-drift check, repair of stopped app, v2 promotion, and Git-revert rollback.
- Vault: generated credentials stored and fetched, read-only policy enforced, credentials injected into pipeline process without printing values.
- Canary: measured stable/canary counts 90/10, 76/24, 52/48, 0/100, and 100/0. Final split restored to 90/10.

## Services

| Service | URL |
| --- | --- |
| Recovered application | http://localhost:5201 |
| Blue-Green proxy (Green) | http://localhost:5300 |
| Canary proxy (90/10) | http://localhost:5400 |
| GitOps app (rolled back v1) | http://localhost:5500 |
| GitOps Nginx sidecar | http://localhost:5501 |
| Vault dev server | http://localhost:8200 |

All host bindings are loopback. The deleted primary app port 5200 is intentionally inactive. Docker context `colima-lab2` is shared with Labs 2 and 3; only Lab 4 resources were managed.

## Prerequisites and reproduction

```sh
cd 'Lab 4'
python3 -m venv .venv
.venv/bin/pip install -r requirements-tools.txt
export DOCKER_CONTEXT=colima-lab2
docker build -t lab4-app:1.0 app/
docker build -t lab4-app:2.0 app-v2/
docker pull nginx:alpine
docker pull hashicorp/vault:latest
.venv/bin/python scripts/run_lab.py
.venv/bin/python scripts/build_reports.py
```

The experiment runner is intended for a fresh Lab 4 setup. It refuses to overwrite existing DR volumes and an existing GitOps sandbox, preserving earlier data. The full runner orders Vault before the local pipeline. Individual tasks can be selected, for example `.venv/bin/python scripts/run_lab.py 6 2`; running Task 6 issues a fresh one-hour pipeline token. Repeating Task 1 requires separately inspecting/preserving existing recovery data. Do not delete recovery volumes merely to rerun reports.

For non-destructive checks against existing services:

```sh
.venv/bin/python scripts/verify.py
```

## Scope

The successful CI run used the local shell pipeline. The Jenkinsfile is prepared, but no Lab 4 Jenkins server job ran; the existing server requires authentication. GitOps uses an isolated local bare Git remote and explicit controller cycles, with no main-repository commit or external push. Blue-Green and Canary outcomes describe finite local samples. Vault development mode is ephemeral and uses local HTTP; it is not a production secret service. Local tokens stay under ignored `.runtime/` with restrictive permissions. Vault restarts may require Task 6 to initialize fresh secrets and tokens.

## Stop Lab 4 only

```sh
docker compose -p lab4-bg -f blue-green/docker-compose.yml stop
docker compose -p lab4-canary -f canary/docker-compose.yml stop
docker compose --env-file .runtime/vault.env -p lab4-vault -f vault/docker-compose.yml stop
docker stop lab4-dr-failover lab4-gitops-app lab4-gitops-sidecar
```

Do not stop the shared Colima VM when the other labs are in use. The backup archive and restored volume are retained. Tokens and the isolated Git sandbox are excluded from Git; keep the local `.runtime/` directory to reproduce the current sandbox.
''')
readme=ROOT/'README.md'
readme.write_text(readme.read_text().replace('47',str(PROBES)))
print('Created 7 Markdown reports, 7 DOCX reports, and README from verified local evidence.')
