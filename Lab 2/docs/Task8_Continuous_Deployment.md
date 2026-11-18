# Lab 2: Containerization & Kubernetes Orchestration

## Task 8: Configure continuous deployment

Nirdesh Jain | Repository: github.com/jainnirdesh/DevOps | 18 November 2026

Platform: macOS (Apple Silicon), Docker via dedicated Colima profile lab2, Minikube profile lab2, Kubernetes namespace lab2. Figures are rendered from actual saved command output; they are not browser screenshots.

## 1. Objective

Automate image build, Minikube image loading, manifest application, image update and rollout verification in one command.

## 2. Pipeline definition

The reference PowerShell/bat pipeline is adapted to macOS shell/sh while preserving its five stages. The Jenkinsfile is intended for an agent on this machine with access to the dedicated contexts.

Jenkinsfile

```
pipeline {
  agent any
  options { disableConcurrentBuilds() }
  environment {
    PATH = "/opt/homebrew/bin:${env.PATH}"
    DOCKER_CONTEXT = 'colima-lab2'
    DOCKER_HOST = "unix://${env.HOME}/.colima/lab2/docker.sock"
  }
  stages {
    stage('Build Image') {
      steps { dir('Lab 2') { sh 'docker build -t lab2-python-app:$BUILD_NUMBER app' } }
    }
    stage('Load to Minikube') {
      steps { sh 'minikube -p lab2 image load --daemon=true lab2-python-app:$BUILD_NUMBER' }
    }
    stage('Apply Manifests') {
      steps { dir('Lab 2') { sh 'kubectl --context lab2 apply -f k8s/namespace.yaml && kubectl --context lab2 apply -f k8s/' } }
    }
    stage('Deploy New Image') {
      steps { sh 'kubectl --context lab2 -n lab2 set image deployment/lab2-app web=lab2-python-app:$BUILD_NUMBER' }
    }
    stage('Verify') {
      steps { sh 'kubectl --context lab2 -n lab2 rollout status deployment/lab2-app --timeout=180s' }
    }
  }
  post {
    success { echo 'Lab 2 deployment successful' }
    failure { echo 'Lab 2 deployment failed' }
  }
}
```

scripts/cicd.sh

```
#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
export DOCKER_CONTEXT="${DOCKER_CONTEXT:-colima-lab2}"
export DOCKER_HOST="${DOCKER_HOST:-unix://$HOME/.colima/lab2/docker.sock}"
profile="${MINIKUBE_PROFILE:-lab2}"
build="${1:-3}"
case "$build" in ''|*[!a-zA-Z0-9_.-]*) echo 'Invalid image tag' >&2; exit 2;; esac
echo '=== Build Image ==='
docker build -t "lab2-python-app:$build" app
echo '=== Load to Minikube ==='
minikube -p "$profile" image load --daemon=true "lab2-python-app:$build"
echo '=== Apply Manifests ==='
kubectl --context "$profile" apply -f k8s/namespace.yaml
kubectl --context "$profile" apply -f k8s/
echo '=== Deploy New Image ==='
kubectl --context "$profile" -n lab2 set image deployment/lab2-app "web=lab2-python-app:$build"
echo '=== Verify ==='
kubectl --context "$profile" -n lab2 rollout status deployment/lab2-app --timeout=180s
kubectl --context "$profile" -n lab2 get deployments,pods,svc -o wide
kubectl --context "$profile" -n lab2 exec deployment/lab2-app -- python -c 'import urllib.request; print(urllib.request.urlopen("http://lab2-service/health").read().decode())'
```

## 3. Pipeline run

The equivalent shell pipeline is executed locally; the verification asserts image tag 3 and two ready replicas.

```
sh scripts/cicd.sh 3
```

Figure 1 — Actual five-stage shell pipeline output. Complete transcript: evidence/task8.log.

## 4. Note

The executed pipeline is scripts/cicd.sh. No Jenkins job, remote webhook, polling trigger or automatic GitHub deployment is claimed for Lab 2. Reapplying the base manifests resets replicas to two before the new image is deployed.

## 5. Conclusion

Continuous deployment script result: PASS. Jenkinsfile execution remains unverified unless separately configured and run.

## Execution status

Task 8: PASS

Runtime versions and installation details: evidence/environment.log and evidence/install.log. Re-run commands are documented in README.md. All reported outcomes are limited to the evidence retained in this folder.
