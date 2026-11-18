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
