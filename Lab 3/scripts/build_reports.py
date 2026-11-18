"""Build reports from this run's recorded evidence, without importing reference claims."""
from pathlib import Path
import json
from docx import Document
from docx.shared import Inches
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
E = ROOT / 'evidence'
FIGURES = E / 'figures'
FIGURES.mkdir(exist_ok=True)
RESULTS = json.loads((E / 'results.json').read_text())
TITLES = [
    'Ansible Infrastructure Automation', 'Terraform IaC', 'ELK Centralized Logging',
    'DevSecOps CI/CD Security', 'Prometheus Grafana Monitoring', 'Feature Flags Testing',
    'Monitoring Logging DevSecOps Report',
]
LOGS = ['task1-ansible.log', 'task2-terraform.log', 'live-verification.log',
        'task4-security.log', 'live-verification.log', 'task6-tests.log']
EXPLANATIONS = [
    'Ansible builds the Flask image, starts lab3-app on loopback port 5003, and retries its HTTP health check. Docker uses the existing colima-lab2 context.',
    'The supplied Terraform configuration uses local and null providers. It creates deployment.json and two simulated instance resources; it does not provision cloud machines or run two application containers. A three-instance scaling plan is recorded separately.',
    'Elasticsearch, Logstash and Kibana run in Docker. Flask sends JSON request events over TCP to host port 5002. Verification searches Elasticsearch for actual lab3-flask events, rather than only checking container status.',
    'The local application image is scanned by Trivy. The critical vulnerability gate exits nonzero on findings or scan failure. Jenkinsfile is configured, but no Jenkins job is claimed to have run. An OWASP dependency-check run is not claimed.',
    'Prometheus scrapes the application, itself, and node-exporter. Grafana has a provisioned Prometheus datasource and Lab 3 dashboard. Node-exporter reports its container/VM view; these are not macOS host metrics.',
    'The supplied feature flag module is verified by 17 unit tests covering initialization, mutation, queries, snapshot copying, and lifecycle behavior. This is an in-memory module, not a remote feature management service.',
]
for i, title in enumerate(TITLES, 1):
    doc = Document()
    doc.add_heading('Lab 3: Monitoring, Logging & DevSecOps', 0)
    doc.add_heading(f'Task {i}: {title}', 1)
    doc.add_paragraph('Execution date: 18 November 2026 (Asia/Kolkata)')
    if i <= 6:
        doc.add_paragraph(EXPLANATIONS[i-1])
        entry = RESULTS[str(i)]
        doc.add_heading('Observed result', 2)
        doc.add_paragraph(f"{entry['status']}: {entry['detail']}")
        text = (E / LOGS[i-1]).read_text(errors='replace') if (E / LOGS[i-1]).exists() else 'No execution output recorded.'
        lines = text.splitlines()
        selected = lines[-28:]
        canvas = Image.new('RGB', (1500, max(300, 70 + len(selected)*25)), '#111827')
        draw = ImageDraw.Draw(canvas)
        font = ImageFont.truetype('/System/Library/Fonts/Menlo.ttc', 17)
        draw.text((20, 15), f'Task {i}: actual log excerpt (rendered text, not a UI screenshot)', fill='#93c5fd', font=font)
        for n, line in enumerate(selected):
            draw.text((20, 55+n*25), line[:138], fill='#e5e7eb', font=font)
        path = FIGURES / f'task{i}.png'
        canvas.save(path)
        doc.add_picture(str(path), width=Inches(6.3))
        doc.add_paragraph('Full evidence: evidence/' + LOGS[i-1])
    else:
        doc.add_paragraph('Application -> Ansible/Docker deployment; request logs -> Logstash -> Elasticsearch -> Kibana; metrics -> Prometheus -> Grafana. Terraform supplies simulated local IaC configuration. Trivy scans the built image before deployment in the configured Jenkins pipeline.')
        for task in range(1,7):
            entry = RESULTS[str(task)]
            doc.add_heading(f'Task {task}: {TITLES[task-1]}', 2)
            doc.add_paragraph(f"{entry['status']}: {entry['detail']}")
            doc.add_paragraph(EXPLANATIONS[task-1])
        doc.add_heading('Access and reproduction', 2)
        doc.add_paragraph('Flask localhost:5003; Kibana localhost:5601; Elasticsearch localhost:9200; Prometheus localhost:9090; Grafana localhost:3000 (local lab credentials admin/admin123). Run scripts/run.sh from Lab 3 after installing dependencies. See README.md for exact prerequisites and limitations.')
    existing = sorted((ROOT/'docs').glob(f'Task{i}_*.docx'))
    dest = existing[0] if existing else ROOT/'docs'/f'Task{i}_{title.replace(" ", "_")}.docx'
    doc.save(dest)
print('Generated 7 reports from fresh execution evidence.')
