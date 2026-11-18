# Lab 4: Advanced Deployment Strategies & Enterprise DevOps

Local execution: 18 November 2026. Six implementation tasks passed; Task 5 records the results. Actual logs and responses are in `evidence/`. Reference reports, screenshots, and backup archives were not reused as execution evidence.

## Task-wise reports

- [Task 1: Design and demonstrate disaster recovery](docs/Task1_Disaster_Recovery_Mechanism.md)
- [Task 2: Implement automated testing in a CI/CD pipeline](docs/Task2_Automated_Testing_CICD_Pipeline.md)
- [Task 3: Implement Blue-Green deployment](docs/Task3_Blue_Green_Deployment_Strategy.md)
- [Task 4: Implement Git-backed desired-state delivery](docs/Task4_GitOps_Based_Delivery.md)
- [Task 5: Advanced deployment strategies report](docs/Task5_Advanced_Deployment_Strategies_Report.md)
- [Task 6: Implement secret management for the pipeline](docs/Task6_Secret_Management_Pipeline.md)
- [Task 7: Implement a Canary deployment strategy](docs/Task7_Canary_Deployment_Strategy.md)

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
