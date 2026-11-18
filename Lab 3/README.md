# Lab 3: Monitoring, Logging & DevSecOps

Working implementation adapted from the seven supplied reference reports. Reference success claims and screenshots are not execution evidence. Fresh output is saved in `evidence/`; updated reports are in `docs/`.

## Run

Docker must be running. This Mac uses existing context `colima-lab2` (shared with Lab 2). Lab 3 only manages containers prefixed `lab3-`.

```sh
cd 'Lab 3'
python3 -m venv .venv
.venv/bin/pip install ansible-core docker requests python-docx pillow
.venv/bin/ansible-galaxy collection install community.docker
brew install hashicorp/tap/terraform
bash scripts/run.sh
```

The tools use `ansible-core` and the `community.docker` collection. The playbook selects its active virtual environment automatically, including when the workspace path contains spaces.

| Service | URL |
| --- | --- |
| Flask application | http://localhost:5003 |
| Elasticsearch | http://localhost:9200 |
| Kibana | http://localhost:5601 |
| Prometheus | http://localhost:9090/targets |
| Grafana dashboard | http://localhost:3000/d/lab3 |

Grafana local lab login: `admin` / `admin123`. Logstash receives TCP JSON on loopback port 5002. Port 5003 avoids the macOS AirPlay listener on 5000; port 5002 avoids Lab 2's port 5001. Observability services bind to loopback.

## What each task verifies

1. Ansible builds and deploys the app, then checks `/health`.
2. Terraform initializes, validates, plans and applies the supplied **simulation** using `null_resource` and `local_file`. Two simulated instances are not two real running servers. The three-instance scale plan is in `evidence/task2-scale-plan.log`.
3. Flask forwards real JSON request events to Logstash. Verification confirms indexed events in Elasticsearch and checks Kibana availability.
4. Trivy scans the actual app image and enforces a **CRITICAL** vulnerability gate. A finding produces a failed security task, not a false success. Jenkins configuration is provided; local execution is not a Jenkins server run. The pipeline includes build, tests, a security gate and deployment.
5. All three Prometheus targets must be up; Grafana datasource and a four-panel dashboard are provisioned automatically. Node-exporter reports a Docker VM/container view.
6. Run the 17 feature flag unit tests.
7. Reports summarize recorded results, including incomplete or failed tasks.

`python3 scripts/verify.py` repeats the live service checks. `.venv/bin/python scripts/build_reports.py` regenerates reports after `evidence/results.json` has been written. Figures render real log excerpts; they are not GUI screenshots.

## Stop just Lab 3

```sh
docker compose -p lab3-monitoring -f prometheus/docker-compose.yml stop
docker compose -p lab3-elk -f elk/docker-compose.yml stop
docker stop lab3-app
```

Do not stop the shared Colima VM if Lab 2 is in use. Restart Compose with `up -d` and the app with `docker start lab3-app`.

## Verified execution: 18 November 2026

All seven local lab tasks completed. Ansible recap: 9 OK, 0 failed. Terraform applied its two simulated instances and the repeat plan found no changes. The application logs were indexed and the Kibana data view was created. All three Prometheus targets were UP, and Grafana datasource and dashboard checks passed. All 17 feature flag tests passed.

Trivy recorded **48 HIGH package findings and 0 CRITICAL**. The CRITICAL-only gate passed; this does not mean the image has no vulnerabilities. Full findings are in `evidence/task4-vulnerabilities.json` and the scan transcript is in `evidence/task4-security.log`.

Initial download timeouts, Logstash's original 128 MB heap error, and the corrected final execution are retained in evidence. The final Logstash configuration uses a 512 MB heap and one pipeline worker. Terraform remains a local simulation; Jenkinsfile is configured but no Jenkins server job was run.
