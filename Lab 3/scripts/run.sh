#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p evidence
export DOCKER_HOST="$(docker context inspect --format '{{.Endpoints.docker.Host}}')"
.venv/bin/ansible-playbook -i ansible/inventory ansible/playbook.yml -e "ansible_python_interpreter=$PWD/.venv/bin/python" 2>&1 | tee evidence/task1-ansible.log
terraform -chdir=terraform init -no-color 2>&1 | tee evidence/task2-terraform.log
terraform -chdir=terraform validate -no-color 2>&1 | tee -a evidence/task2-terraform.log
terraform -chdir=terraform plan -out=lab3.tfplan -no-color 2>&1 | tee -a evidence/task2-terraform.log
terraform -chdir=terraform apply -no-color lab3.tfplan 2>&1 | tee -a evidence/task2-terraform.log
docker compose -p lab3-elk -f elk/docker-compose.yml up -d 2>&1 | tee evidence/task3-elk.log
docker compose -p lab3-monitoring -f prometheus/docker-compose.yml up -d 2>&1 | tee evidence/task5-monitoring.log
.venv/bin/python feature-flags/test_flags.py 2>&1 | tee evidence/task6-tests.log
python3 scripts/verify.py 2>&1 | tee evidence/live-verification.log
bash devsecops/trivy_scan.sh lab3-flask-app 1.0 2>&1 | tee evidence/task4-security.log
