# Lab 2: Containerization & Kubernetes Orchestration

## Task 9: Record all tools documents

Nirdesh Jain | Repository: github.com/jainnirdesh/DevOps | 18 November 2026

Platform: macOS (Apple Silicon), Docker via dedicated Colima profile lab2, Minikube profile lab2, Kubernetes namespace lab2. Figures are rendered from actual saved command output; they are not browser screenshots.

## 1. Overview

This report records the lab source, Docker and Kubernetes configuration, actual command transcripts, output figures and observations. All source files are under Lab 2.

## 2. Dockerfile (app)

app/Dockerfile

```
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
RUN mkdir -p /data
EXPOSE 5000
CMD ["python", "app.py"]
```

app/requirements.txt

```
Flask==3.1.2
```

## 3. Docker Compose file

compose/compose.yaml

```
name: lab2-compose
services:
  web:
    build: ./web
    image: lab2-compose-web:1.0
    ports:
      - "127.0.0.1:5001:5000"
    environment:
      REDIS_HOST: redis
    depends_on:
      redis:
        condition: service_healthy
  redis:
    image: redis:7-alpine
    expose:
      - "6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 2s
      timeout: 2s
      retries: 30
```

## 4. Kubernetes manifests

k8s/namespace.yaml

```
apiVersion: v1
kind: Namespace
metadata:
  name: lab2
```

k8s/deployment.yaml

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lab2-app
  namespace: lab2
spec:
  replicas: 2
  selector:
    matchLabels:
      app: lab2-app
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  template:
    metadata:
      labels:
        app: lab2-app
    spec:
      containers:
        - name: web
          image: lab2-python-app:1.0
          imagePullPolicy: Never
          ports:
            - containerPort: 5000
          readinessProbe:
            httpGet:
              path: /health
              port: 5000
            initialDelaySeconds: 2
            periodSeconds: 2
          resources:
            requests:
              cpu: 50m
              memory: 64Mi
            limits:
              cpu: 500m
              memory: 128Mi
```

k8s/service.yaml

```
apiVersion: v1
kind: Service
metadata:
  name: lab2-service
  namespace: lab2
spec:
  type: NodePort
  selector:
    app: lab2-app
  ports:
    - port: 80
      targetPort: 5000
      nodePort: 30080
```

## 5. Pipeline files

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

## 6. Commands used

The complete commands and outputs are retained in evidence/task1.log, task2.log, task4.log through task8.log. scripts/run_lab.py executes the experiments with assertions and records results.json. Runtime versions:

```
$ uname -sm
Darwin arm64

$ docker --version
Docker version 29.10.0, build fdd4b8e5da

$ docker-compose version
Docker Compose version 5.8.0

$ docker buildx version
github.com/docker/buildx v0.39.0 Homebrew

$ colima version
colima version 0.10.3
git commit: 00f6c297e92a82c04a4ab507db0a61435650d7e8

$ minikube version
minikube version: v1.39.0
commit: 7a9f6a841470a207de8cf4bafcccee0969d8ba10

$ kubectl version --client=true
Client Version: v1.37.2
Kustomize Version: v5.8.1
$ docker --context colima-lab2 version
Client: Docker Engine - Community
 Version:           29.10.0
 API version:       1.54 (downgraded from 1.57)
 Go version:        go1.27.4
 Git commit:        fdd4b8e5da
 Built:             Fri Nov 13 13:30:47 2026
 OS/Arch:           darwin/arm64
 Context:           colima-lab2

Server: Docker Engine - Community
 Engine:
  Version:          29.5.2
  API version:      1.54 (minimum version 1.40)
  Go version:       go1.26.3
  Git commit:       568f755
  Built:            Wed May 20 14:39:25 2026
  OS/Arch:          linux/arm64
  Experimental:     false
 containerd:
  Version:          v2.2.4
  GitCommit:        193637f7ee8ae5f5aa5248f49e7baa3e6164966e
 runc:
  Version:          1.3.5
  GitCommit:        v1.3.5-0-g488fc13e
 docker-init:
  Version:          0.19.0
  GitCommit:        de40ad0

$ kubectl --context lab2 version
Client Version: v1.37.2
Kustomize Version: v5.8.1
Server Version: v1.37.0

$ kubectl --context lab2 get nodes -o wide
NAME   STATUS   ROLES           AGE   VERSION   INTERNAL-IP    EXTERNAL-IP   OS-IMAGE                         KERNEL-VERSION              CONTAINER-RUNTIME
lab2   Ready    control-plane   3m    v1.37.0   192.168.49.2   <none>        Debian GNU/Linux 12 (bookworm)   6.8.0-117-generic (arm64)   containerd://2.3.4

$ kubectl --context lab2 -n lab2 get deployment,pods,svc -o wide
NAME                       READY   UP-TO-DATE   AVAILABLE   AGE   CONTAINERS   IMAGES              SELECTOR
deployment.apps/lab2-app   2/2     2            2           67s   web          lab2-python-app:3   app=lab2-app

NAME                           READY   STATUS    RESTARTS   AGE   IP            NODE   NOMINATED NODE   READINESS GATES
pod/lab2-app-6979d9457-lmhn9   1/1     Running   0          41s   10.244.0.12   lab2   <none>           <none>
pod/lab2-app-6979d9457-nzq8z   1/1     Running   0          41s   10.244.0.13   lab2   <none>           <none>

NAME                   TYPE       CLUSTER-IP       EXTERNAL-IP   PORT(S)        AGE   SELECTOR
service/lab2-service   NodePort   10.105.198.215   <none>        80:30080/TCP   67s   app=lab2-app
```

Task 4: PASS

```
$ docker version
$ docker build -t lab2-python-app:1.0 app
$ docker run -d --name lab2-app -p 127.0.0.1:5004:5000 lab2-python-app:1.0
$ docker history lab2-python-app:1.0
$ docker image inspect lab2-python-app:1.0 --format '{{json .RootFS.Layers}}'
```

Task 5: PASS

```
$ docker ps
$ docker stop lab2-app
$ docker ps -a
$ docker start lab2-app
$ docker exec lab2-app ls /app
$ docker stop lab2-app
$ docker rm lab2-app
$ docker images lab2-python-app
$ docker run -d -p 127.0.0.1:5050:5000 --name lab2-registry registry:2
$ docker tag lab2-python-app:1.0 localhost:5050/lab2-python-app:1.0
$ docker push localhost:5050/lab2-python-app:1.0
$ docker-compose -f compose/compose.yaml up -d --build
$ docker-compose -f compose/compose.yaml ps
$ docker-compose -f compose/compose.yaml down
```

Task 6: PASS

```
$ docker run -d --name lab2-novol -p 127.0.0.1:5101:5000 lab2-python-app:1.0
$ docker rm -f lab2-novol
$ docker run -d --name lab2-novol -p 127.0.0.1:5101:5000 lab2-python-app:1.0
$ docker rm -f lab2-novol
$ docker volume create lab2-vol
$ docker run -d --name lab2-volume -v lab2-vol:/data -p 127.0.0.1:5102:5000 lab2-python-app:1.0
$ docker rm -f lab2-volume
$ docker run -d --name lab2-volume -v lab2-vol:/data -p 127.0.0.1:5102:5000 lab2-python-app:1.0
$ docker rm -f lab2-volume
$ docker run -d --name lab2-bind -v '/Users/nirdeshjain/Documents/DevOps-Lab-1/Lab 2/storage-demo/bind-data:/data' -p 127.0.0.1:5103:5000 lab2-python-app:1.0
$ docker rm -f lab2-bind
$ docker run -d --name lab2-bind -v '/Users/nirdeshjain/Documents/DevOps-Lab-1/Lab 2/storage-demo/bind-data:/data' -p 127.0.0.1:5103:5000 lab2-python-app:1.0
$ docker rm -f lab2-bind
$ docker volume inspect lab2-vol
```

Task 7: PASS

```
$ docker network create lab2-net
$ docker run -d --name lab2-net-app --network lab2-net lab2-python-app:1.0
$ docker run -d --name lab2-net-client --network lab2-net lab2-python-app:1.0 sleep 3600
$ docker inspect --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' lab2-net-app
$ docker exec lab2-net-client python -c 'import urllib.request; print(urllib.request.urlopen("http://lab2-net-app:5000/health").read().decode())'
$ docker exec lab2-net-client python -c 'import urllib.request; print(urllib.request.urlopen("http://172.18.0.2:5000/health").read().decode())'
$ docker network inspect lab2-net
```

Task 1: PASS

```
$ minikube -p lab2 start --driver=docker --kubernetes-version=v1.37.0 --container-runtime=containerd --cpus=2 --memory=3072 --disk-size=20g --base-image=gcr.io/k8s-minikube/kicbase:v0.0.51 --preload=true --cache-images=false
$ minikube -p lab2 image load --daemon=true lab2-python-app:1.0
$ kubectl --context lab2 get nodes -o wide
$ kubectl --context lab2 -n lab2 apply -f k8s/namespace.yaml
$ kubectl --context lab2 -n lab2 apply -f k8s/
$ kubectl --context lab2 -n lab2 rollout status deployment/lab2-app --timeout=180s
$ kubectl --context lab2 -n lab2 get deployments,pods,svc -o wide
$ kubectl --context lab2 -n lab2 get deployment/lab2-app -o json
$ kubectl --context lab2 -n lab2 get pods -l app=lab2-app -o json
$ kubectl --context lab2 -n lab2 exec lab2-app-5cc8f65945-8lh68 -- python -c 'import urllib.request;print(urllib.request.urlopen("http://localhost:5000/").read().decode())'
$ kubectl --context lab2 -n lab2 exec lab2-app-5cc8f65945-jk4h2 -- python -c 'import urllib.request;print(urllib.request.urlopen("http://localhost:5000/").read().decode())'
$ kubectl --context lab2 -n lab2 exec deployment/lab2-app -- python -c 'import urllib.request;print(urllib.request.urlopen("http://lab2-service/health").read().decode())'
```

Task 2: PASS

```
$ docker build -t lab2-python-app:2.0 app-v2
$ minikube -p lab2 image load --daemon=true lab2-python-app:2.0
$ kubectl --context lab2 -n lab2 set image deployment/lab2-app web=lab2-python-app:2.0
$ kubectl --context lab2 -n lab2 rollout status deployment/lab2-app --timeout=180s
$ kubectl --context lab2 -n lab2 get pods -l app=lab2-app -o json
$ kubectl --context lab2 -n lab2 exec lab2-app-84759957f8-26cjb -- python -c 'import urllib.request;print(urllib.request.urlopen("http://localhost:5000/").read().decode())'
$ kubectl --context lab2 -n lab2 exec lab2-app-84759957f8-q9tnm -- python -c 'import urllib.request;print(urllib.request.urlopen("http://localhost:5000/").read().decode())'
$ kubectl --context lab2 -n lab2 rollout history deployment/lab2-app
$ kubectl --context lab2 -n lab2 rollout undo deployment/lab2-app
$ kubectl --context lab2 -n lab2 rollout status deployment/lab2-app --timeout=180s
$ kubectl --context lab2 -n lab2 get pods -l app=lab2-app -o json
$ kubectl --context lab2 -n lab2 exec lab2-app-5cc8f65945-22m99 -- python -c 'import urllib.request;print(urllib.request.urlopen("http://localhost:5000/").read().decode())'
$ kubectl --context lab2 -n lab2 exec lab2-app-5cc8f65945-f2745 -- python -c 'import urllib.request;print(urllib.request.urlopen("http://localhost:5000/").read().decode())'
$ kubectl --context lab2 -n lab2 scale deployment/lab2-app --replicas=5
$ kubectl --context lab2 -n lab2 rollout status deployment/lab2-app --timeout=180s
$ kubectl --context lab2 -n lab2 get deployments,pods -o wide
$ kubectl --context lab2 -n lab2 get deployment/lab2-app -o json
$ kubectl --context lab2 -n lab2 scale deployment/lab2-app --replicas=3
$ kubectl --context lab2 -n lab2 rollout status deployment/lab2-app --timeout=180s
$ kubectl --context lab2 -n lab2 get deployments,pods -o wide
$ kubectl --context lab2 -n lab2 get deployment/lab2-app -o json
```

Task 8: PASS

```
$ sh scripts/cicd.sh 3
$ kubectl --context lab2 -n lab2 get deployment/lab2-app -o json
$ kubectl --context lab2 -n lab2 get pods -l app=lab2-app -o json
$ kubectl --context lab2 -n lab2 exec lab2-app-6979d9457-lmhn9 -- python -c 'import urllib.request;print(urllib.request.urlopen("http://localhost:5000/").read().decode())'
$ kubectl --context lab2 -n lab2 exec lab2-app-6979d9457-nzq8z -- python -c 'import urllib.request;print(urllib.request.urlopen("http://localhost:5000/").read().decode())'
```

## 7. Screenshots and observations

Figures below are excerpts rendered from actual execution logs. Screenshots in the supplied reference documents are not submitted as this run’s evidence.

Task 4 — Image build and HTTP endpoints. Complete transcript: evidence/task4.log.

Task 5 — Lifecycle, registry and Compose. Complete transcript: evidence/task5.log.

Task 6 — Ephemeral and persistent storage. Complete transcript: evidence/task6.log.

Task 7 — Network DNS and IP. Complete transcript: evidence/task7.log.

Task 1 — Kubernetes deployment. Complete transcript: evidence/task1.log.

Task 2 — Rolling update, rollback and scaling. Complete transcript: evidence/task2.log.

Task 8 — Deployment pipeline. Complete transcript: evidence/task8.log.

Image history includes metadata entries as well as filesystem changes. Counter storage in a container or pod is ephemeral. External storage survives recreation until explicitly deleted. Names on a custom Docker network resolve through Docker DNS. Kubernetes readiness and rollout status are verified before proceeding. Exact versions and outcomes are derived from saved local evidence.

## Execution status

Task 1: PASS; Task 2: PASS; Task 4: PASS; Task 5: PASS; Task 6: PASS; Task 7: PASS; Task 8: PASS

Runtime versions and installation details: evidence/environment.log and evidence/install.log. Re-run commands are documented in README.md. All reported outcomes are limited to the evidence retained in this folder.
