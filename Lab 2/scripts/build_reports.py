#!/usr/bin/env python3
"""Rebuild Word reports using reference styles and this lab's saved evidence."""
from pathlib import Path
import json
import os
import re
import textwrap
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from PIL import Image, ImageDraw, ImageFont

B=Path(__file__).resolve().parents[1]
REF=Path(os.environ.get('LAB2_REFERENCE_DIR', str(Path.home()/'Downloads/DevOps_and_Automation-Lab_2301420022-main/Lab2/docs')))
E=B/'evidence'
FIG=E/'figures';FIG.mkdir(exist_ok=True)
RESULTS=json.loads((E/'results.json').read_text()) if (E/'results.json').exists() else {}

def read(p):return (B/p).read_text() if (B/p).exists() else '(No execution output recorded.)'
def status(n):
 r=RESULTS.get(str(n),{})
 return 'PASS' if r.get('status')=='PASS' else 'NOT COMPLETED: '+r.get('error','execution pending')

def figure(n):
 raw=read(f'evidence/task{n}.log')
 # Render selected unmodified log lines. The complete command transcript is retained separately.
 candidates=[]
 for line in raw.splitlines():
  compact_json=line.startswith('{') and line.endswith('}') and len(line)<500
  common=line.startswith(('GET ', 'RESULT: PASS', '===', 'Host counter.txt =')) or compact_json
  if n==2:
   keep=compact_json or line.startswith(('deployment.apps/lab2-app', 'deployment "lab2-app" successfully', 'RESULT: PASS')) or (line.startswith('$ kubectl') and any(x in line for x in (' set image ', ' rollout undo ', ' scale ')))
  elif n==8:
   keep=common or line.startswith(('deployment.apps/lab2-app', 'deployment "lab2-app" successfully', 'service/lab2-service'))
  elif n==1:
   keep=common or line.startswith(('* ', 'lab2 ', 'deployment.apps/lab2-app', 'pod/lab2-app', 'service/lab2-service', 'deployment "lab2-app" successfully'))
  else:
   keep=common or (line.startswith('$ docker ') and any(x in line for x in (' build ', ' run ', ' history ', ' exec '))) or line.startswith('lab2-compose-')
  if keep:candidates.append(line)
 selected=candidates[-30:] if candidates else raw.splitlines()[-24:]
 lines=[]
 for s in selected:lines.extend(textwrap.wrap(s,106,replace_whitespace=False,drop_whitespace=False) or [''])
 font=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',18)
 im=Image.new('RGB',(1280,90+27*len(lines)),'#111827');d=ImageDraw.Draw(im)
 d.text((22,20),f'Lab 2 / Task {n} - actual saved console output (selected lines)',font=font,fill='#93c5fd')
 for i,s in enumerate(lines):d.text((22,65+27*i),s,font=font,fill='#e5e7eb')
 p=FIG/f'task{n}.png';im.save(p);return p

class Report:
 def __init__(self,n):
  self.n=n;self.ref=next(REF.glob(f'Task{n}_*.docx'));self.doc=Document(self.ref);self.md=[]
  self.title=self.doc.paragraphs[0].text
  self.subtitle=self.doc.paragraphs[1].text
  for ch in list(self.doc._element.body):
   if not ch.tag.endswith('}sectPr'):self.doc._element.body.remove(ch)
  self.heading(self.title,1);self.heading(self.subtitle,2)
  self.par('Nirdesh Jain | Repository: github.com/jainnirdesh/DevOps | 18 November 2026')
  self.par('Platform: macOS (Apple Silicon), Docker via dedicated Colima profile lab2, Minikube profile lab2, Kubernetes namespace lab2. Figures are rendered from actual saved command output; they are not browser screenshots.')
 def heading(self,s,level=2):
  p=self.doc.add_paragraph(s);style=OxmlElement('w:pStyle');style.set(qn('w:val'),f'Heading{level}');p._p.get_or_add_pPr().append(style)
  self.md.append('#'*level+' '+s)
 def par(self,s):self.doc.add_paragraph(s);self.md.append(s)
 def code(self,s):
  self.md.append('```\n'+s.rstrip()+'\n```')
  for line in s.rstrip().splitlines():
   p=self.doc.add_paragraph();p.paragraph_format.space_after=Pt(0)
   r=p.add_run(line or ' ');r.font.name='Consolas';r.font.size=Pt(9)
   sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'F2F2F2');p._p.get_or_add_pPr().append(sh)
 def source(self,p):self.par(p);self.code(read(p))
 def fig(self,n,caption):
  if (E/f'task{n}.log').exists():
   self.doc.add_picture(str(figure(n)),width=Inches(6));self.par(caption+f' Complete transcript: evidence/task{n}.log.')
 def finish(self):
  self.heading('Execution status')
  if self.n in (3,9):
   self.par('; '.join(f'Task {n}: {status(n)}' for n in (1,2,4,5,6,7,8)))
  else:self.par(f'Task {self.n}: {status(self.n)}')
  self.par('Runtime versions and installation details: evidence/environment.log and evidence/install.log. Re-run commands are documented in README.md. All reported outcomes are limited to the evidence retained in this folder.')
  self.doc.core_properties.author='Nirdesh Jain';self.doc.core_properties.last_modified_by='Nirdesh Jain'
  self.doc.core_properties.title=self.subtitle
  used={e.get(qn('r:embed')) for e in self.doc._element.iter() if e.get(qn('r:embed'))}
  for rid,rel in list(self.doc.part.rels.items()):
   if rel.reltype.endswith('/image') and rid not in used:self.doc.part.drop_rel(rid)
  name=re.sub(r'_2301420022(?=\.docx$)','',self.ref.name)
  self.doc.save(B/'docs'/name)
  (B/'docs'/Path(name).with_suffix('.md')).write_text('\n\n'.join(self.md)+'\n')

def section(r,title,text=None,code=None):
 r.heading(title)
 if text:r.par(text)
 if code:r.code(code)

r=Report(1)
section(r,'1. Objective','Deploy the containerized Flask app to Minikube using Deployment and Service manifests and verify ready pods and HTTP responses.')
section(r,'2. Start the cluster','A dedicated Minikube profile uses the Docker engine inside the lab2 Colima VM. Image 1.0 must be loaded before starting pods with imagePullPolicy Never.', 'export DOCKER_CONTEXT=colima-lab2\nexport DOCKER_HOST="unix://$HOME/.colima/lab2/docker.sock"\nminikube -p lab2 start --driver=docker --kubernetes-version=v1.37.0 --container-runtime=containerd --cpus=2 --memory=3072 --disk-size=20g --base-image=gcr.io/k8s-minikube/kicbase:v0.0.51 --preload=true --cache-images=false\nminikube -p lab2 image load --daemon=true lab2-python-app:1.0\nkubectl --context lab2 get nodes -o wide')
r.par('Setup observation: slow external downloads were replaced with checksum-verified local caches. The CNI image was loaded locally after an external pull failure. Explicit --daemon=true and DOCKER_HOST select the local Colima engine for image loading; bootstrap attempt logs are retained as setup evidence.')
section(r,'3. Manifests and deployment','The namespace isolates this lab. The Deployment starts two replicas, readiness checks /health, and the NodePort service maps port 80 to container port 5000 using node port 30080.')
for p in ('k8s/namespace.yaml','k8s/deployment.yaml','k8s/service.yaml'):r.source(p)
section(r,'4. Verify running pods','The execution script checks readyReplicas equals 2, tests each pod directly and tests /health through the Service DNS name.', 'kubectl --context lab2 -n lab2 get deployments,pods,svc -o wide\nkubectl --context lab2 -n lab2 rollout status deployment/lab2-app --timeout=180s')
r.fig(1,'Figure 1 — Cluster deployment and endpoint verification.')
section(r,'5. Conclusion',f'Deployment verification result: {status(1)}. The full transcript records actual node versions and pod names; reference versions are not copied.')
r.finish()

r=Report(2)
section(r,'1. Objective','Perform a rolling update, rollback, and replica scaling, verifying the image response after each image change.')
section(r,'2. Rolling update','Version 2.0 changes the application welcome message. RollingUpdate permits one surge pod and one unavailable pod.', 'docker build -t lab2-python-app:2.0 app-v2\nminikube -p lab2 image load --daemon=true lab2-python-app:2.0\nkubectl --context lab2 -n lab2 set image deployment/lab2-app web=lab2-python-app:2.0\nkubectl --context lab2 -n lab2 rollout status deployment/lab2-app --timeout=180s\nkubectl --context lab2 -n lab2 rollout history deployment/lab2-app')
section(r,'3. Rollback','Undo restores the previous pod template; each surviving ready pod is checked for the VERSION 1.0 response.', 'kubectl --context lab2 -n lab2 rollout undo deployment/lab2-app\nkubectl --context lab2 -n lab2 rollout status deployment/lab2-app --timeout=180s')
section(r,'4. Scaling','Scale to five replicas and wait for readiness, then reduce to three and verify readiness again.', 'kubectl --context lab2 -n lab2 scale deployment/lab2-app --replicas=5\nkubectl --context lab2 -n lab2 rollout status deployment/lab2-app --timeout=180s\nkubectl --context lab2 -n lab2 scale deployment/lab2-app --replicas=3\nkubectl --context lab2 -n lab2 rollout status deployment/lab2-app --timeout=180s')
r.fig(2,'Figure 1 — Actual rolling update, rollback and scaling output.')
section(r,'5. Conclusion',f'Rolling update, rollback and scaling verification: {status(2)}. The later Task 8 reapplies the manifest, returning the desired replica count to two.')
r.finish()

r=Report(3)
section(r,'1. Introduction','This report describes Docker containerization and Kubernetes orchestration of a Flask application on this Mac. Task-specific reports contain reproducible commands and actual evidence.')
section(r,'2. Architecture',code='Dockerfile -> lab2-python-app:1.0 / 2.0 / 3\n                    | minikube image load\n                    v\nColima Docker VM -> Minikube node -> Deployment -> Pods\n                                         ^\n                        NodePort Service 30080 -> port 5000')
r.par('The app serves / and /health. A file counter under /data demonstrates container-layer storage, named volumes and bind mounts. Docker Compose uses a separate Redis-backed counter. A dedicated namespace and explicit contexts isolate all Kubernetes commands.')
r.fig(1,'Figure 1 — Kubernetes deployment verification.')
section(r,'3. Deployment strategy','RollingUpdate uses maxSurge 1 and maxUnavailable 1. A readiness probe controls endpoint readiness. Rollback restores the preceding revision; HTTP responses verify that the expected application version is running.')
r.fig(2,'Figure 2 — Deployment strategy and scaling evidence.')
section(r,'4. Scaling results',f'The test asserts five ready replicas, then three. Actual result: {status(2)}. No timing from the reference is reused.')
section(r,'5. Observations','Local images are loaded into Minikube and imagePullPolicy Never prevents external pulls for the application. Pod-local counters are independent and ephemeral. Named volumes and bind mounts persist beyond container deletion, until their external data is removed. Dockerfile filesystem layers and metadata instructions are distinguished by docker history and RootFS.Layers.')
r.fig(8,'Figure 3 — Continuous deployment script execution.')
section(r,'6. Conclusion','The status table below reports only completed experiments. The shell pipeline is executed separately from Jenkins; the Jenkinsfile is supplied for a local agent with access to these Docker and Kubernetes contexts.')
r.finish()

r=Report(4)
section(r,'1. Objective','Build and run a Docker image for the Flask app, verify both HTTP endpoints and inspect image history.')
section(r,'2. Application','GET / returns the welcome message, hostname and visit count persisted to /data/counter.txt. GET /health returns healthy without changing the counter. A lock serializes counter updates within the demo process.')
r.source('app/app.py');r.source('app/requirements.txt')
section(r,'3. Dockerfile and build','Dependencies are copied and installed before app.py so source changes can reuse the dependency layer.')
r.source('app/Dockerfile');r.code('docker build -t lab2-python-app:1.0 app')
section(r,'4. Run, layers and behaviour',code='docker run -d --name lab2-app -p 127.0.0.1:5004:5000 lab2-python-app:1.0\ncurl http://127.0.0.1:5004/\ncurl http://127.0.0.1:5004/health\ndocker history lab2-python-app:1.0\ndocker image inspect lab2-python-app:1.0 --format "{{json .RootFS.Layers}}"')
r.fig(4,'Figure 1 — Actual Docker build and HTTP verification output.')
section(r,'5. Layer description','FROM supplies the base filesystem. COPY and RUN create filesystem changes; WORKDIR also sets image configuration and may create its directory. EXPOSE and CMD are image metadata. docker history includes metadata-only entries, so every listed instruction must not be counted as a filesystem layer. Actual layer digests and sizes are in the task log.')
section(r,'6. Conclusion',f'Docker image build and endpoint checks: {status(4)}. Flask development server is used for this local lab.')
r.finish()

r=Report(5)
section(r,'1. Objective','Manage container lifecycle, tag and push an image to a local registry, and run a two-service Compose stack.')
section(r,'2. Container management',code='docker ps\ndocker stop lab2-app\ndocker ps -a\ndocker start lab2-app\ndocker exec lab2-app ls /app\ndocker stop lab2-app\ndocker rm lab2-app\ndocker images lab2-python-app')
r.par('A running container is stopped before normal removal. All these resources belong to the dedicated lab Docker engine.')
section(r,'3. Tag and push to a registry','A loopback-bound local registry avoids publishing the image to an external account.', 'docker run -d -p 127.0.0.1:5050:5000 --name lab2-registry registry:2\ndocker tag lab2-python-app:1.0 localhost:5050/lab2-python-app:1.0\ndocker push localhost:5050/lab2-python-app:1.0\ncurl http://127.0.0.1:5050/v2/_catalog')
section(r,'4. Docker Compose','Redis has a health check, and the web service waits for Redis readiness. Two requests must produce visits 1 and 2 before teardown.')
if (E/'task5-attempt1.log').exists():r.par('Observation: the first Compose build hit a Docker Hub TLS handshake timeout while resolving the Python base image. Retrying the build succeeded. The first attempt is preserved in evidence/task5-attempt1.log; the completed verification is recorded in evidence/task5.log.')
r.source('compose/compose.yaml');r.source('compose/web/app.py');r.code('docker-compose -f compose/compose.yaml up -d --build\ndocker-compose -f compose/compose.yaml ps\ndocker-compose -f compose/compose.yaml down')
r.fig(5,'Figure 1 — Actual registry, Compose and lifecycle output.')
section(r,'5. Conclusion',f'Container lifecycle, registry push and Compose verification: {status(5)}. Registry publication is local only.')
r.finish()

r=Report(6)
section(r,'1. Objective','Demonstrate container writable-layer loss and persistence outside the container using a named volume and bind mount.')
section(r,'2. Data loss without a volume','The experiment asserts counts 1, 2 and 3. After deleting and recreating the container without a mount, it asserts count 1.', 'docker run -d --name lab2-novol -p 127.0.0.1:5101:5000 lab2-python-app:1.0\n# Request / three times\ndocker rm -f lab2-novol\ndocker run -d --name lab2-novol -p 127.0.0.1:5101:5000 lab2-python-app:1.0\n# Request / and verify visits=1')
section(r,'3. Named volume and bind mount','The named volume is reused by a new container; visits continue from 2 to 3. The bind mount creates a host counter.txt and is also reused by a replacement container; visits continue from 1 to 2.', 'docker volume create lab2-vol\ndocker run -d --name lab2-volume -v lab2-vol:/data -p 127.0.0.1:5102:5000 lab2-python-app:1.0\ndocker run -d --name lab2-bind -v "$PWD/storage-demo/bind-data:/data" -p 127.0.0.1:5103:5000 lab2-python-app:1.0')
r.fig(6,'Figure 1 — Actual counter reset and persistence assertions.')
section(r,'4. Conclusion',f'Storage assertions: {status(6)}. Volumes and bind mounts persist independently of a container, but are not permanent backups: deleting the volume or host data removes the stored content.')
r.finish()

r=Report(7)
section(r,'1. Objective','Verify container-to-container HTTP communication using Docker DNS and the dynamically discovered container IP.')
section(r,'2. Create network and containers','The client uses the same Python image with a sleep command; Python urllib performs the HTTP requests.', 'docker network create lab2-net\ndocker run -d --name lab2-net-app --network lab2-net lab2-python-app:1.0\ndocker run -d --name lab2-net-client --network lab2-net lab2-python-app:1.0 sleep 3600')
section(r,'3. Communication by name and by IP','The server IP is inspected at runtime, rather than copying the reference IP. Both responses must contain status=healthy.', 'docker inspect --format "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}" lab2-net-app\ndocker exec lab2-net-client python -c \'import urllib.request; print(urllib.request.urlopen("http://lab2-net-app:5000/health").read().decode())\'\n# Repeat with the inspected IP in place of lab2-net-app\ndocker network inspect lab2-net')
r.fig(7,'Figure 1 — Actual DNS and IP communication output.')
section(r,'4. Conclusion',f'Both name and IP communication checks: {status(7)}. Container names provide a stable discovery mechanism while IP assignments can change.')
r.finish()

r=Report(8)
section(r,'1. Objective','Automate image build, Minikube image loading, manifest application, image update and rollout verification in one command.')
section(r,'2. Pipeline definition','The reference PowerShell/bat pipeline is adapted to macOS shell/sh while preserving its five stages. The Jenkinsfile is intended for an agent on this machine with access to the dedicated contexts.')
r.source('Jenkinsfile');r.source('scripts/cicd.sh')
section(r,'3. Pipeline run','The equivalent shell pipeline is executed locally; the verification asserts image tag 3 and two ready replicas.', 'sh scripts/cicd.sh 3')
r.fig(8,'Figure 1 — Actual five-stage shell pipeline output.')
section(r,'4. Note','The executed pipeline is scripts/cicd.sh. No Jenkins job, remote webhook, polling trigger or automatic GitHub deployment is claimed for Lab 2. Reapplying the base manifests resets replicas to two before the new image is deployed.')
section(r,'5. Conclusion',f'Continuous deployment script result: {status(8)}. Jenkinsfile execution remains unverified unless separately configured and run.')
r.finish()

r=Report(9)
section(r,'1. Overview','This report records the lab source, Docker and Kubernetes configuration, actual command transcripts, output figures and observations. All source files are under Lab 2.')
section(r,'2. Dockerfile (app)');r.source('app/Dockerfile');r.source('app/requirements.txt')
section(r,'3. Docker Compose file');r.source('compose/compose.yaml')
section(r,'4. Kubernetes manifests')
for p in ('k8s/namespace.yaml','k8s/deployment.yaml','k8s/service.yaml'):r.source(p)
section(r,'5. Pipeline files');r.source('Jenkinsfile');r.source('scripts/cicd.sh')
section(r,'6. Commands used','The complete commands and outputs are retained in evidence/task1.log, task2.log, task4.log through task8.log. scripts/run_lab.py executes the experiments with assertions and records results.json. Runtime versions:');r.code(read('evidence/environment.log'))
for n in (4,5,6,7,1,2,8):
 raw=read(f'evidence/task{n}.log')
 r.par(f'Task {n}: {status(n)}')
 r.code('\n'.join(s for s in raw.splitlines() if s.startswith('$ ')))
section(r,'7. Screenshots and observations','Figures below are excerpts rendered from actual execution logs. Screenshots in the supplied reference documents are not submitted as this run’s evidence.')
for n,caption in ((4,'Image build and HTTP endpoints'),(5,'Lifecycle, registry and Compose'),(6,'Ephemeral and persistent storage'),(7,'Network DNS and IP'),(1,'Kubernetes deployment'),(2,'Rolling update, rollback and scaling'),(8,'Deployment pipeline')):r.fig(n,f'Task {n} — {caption}.')
r.par('Image history includes metadata entries as well as filesystem changes. Counter storage in a container or pod is ephemeral. External storage survives recreation until explicitly deleted. Names on a custom Docker network resolve through Docker DNS. Kubernetes readiness and rollout status are verified before proceeding. Exact versions and outcomes are derived from saved local evidence.')
r.finish()

for p in (B/'docs').glob('*.docx'):
 d=Document(p);txt='\n'.join(x.text for x in d.paragraphs)
 assert 'Nirdesh Jain' in txt and 'Yatharth Chopra' not in txt and '2301420022' not in txt,p
 print(p.name, len(d.paragraphs), 'paragraphs,', len(d.inline_shapes), 'figures')
