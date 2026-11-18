# Lab 2: Containerization & Kubernetes Orchestration

## Task 5: Manage Docker containers and images

Nirdesh Jain | Repository: github.com/jainnirdesh/DevOps | 18 November 2026

Platform: macOS (Apple Silicon), Docker via dedicated Colima profile lab2, Minikube profile lab2, Kubernetes namespace lab2. Figures are rendered from actual saved command output; they are not browser screenshots.

## 1. Objective

Manage container lifecycle, tag and push an image to a local registry, and run a two-service Compose stack.

## 2. Container management

```
docker ps
docker stop lab2-app
docker ps -a
docker start lab2-app
docker exec lab2-app ls /app
docker stop lab2-app
docker rm lab2-app
docker images lab2-python-app
```

A running container is stopped before normal removal. All these resources belong to the dedicated lab Docker engine.

## 3. Tag and push to a registry

A loopback-bound local registry avoids publishing the image to an external account.

```
docker run -d -p 127.0.0.1:5050:5000 --name lab2-registry registry:2
docker tag lab2-python-app:1.0 localhost:5050/lab2-python-app:1.0
docker push localhost:5050/lab2-python-app:1.0
curl http://127.0.0.1:5050/v2/_catalog
```

## 4. Docker Compose

Redis has a health check, and the web service waits for Redis readiness. Two requests must produce visits 1 and 2 before teardown.

Observation: the first Compose build hit a Docker Hub TLS handshake timeout while resolving the Python base image. Retrying the build succeeded. The first attempt is preserved in evidence/task5-attempt1.log; the completed verification is recorded in evidence/task5.log.

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

compose/web/app.py

```
import os
import socket
import redis
from flask import Flask, jsonify

app = Flask(__name__)
store = redis.Redis(host=os.environ.get("REDIS_HOST", "redis"), port=6379, decode_responses=True)

@app.get("/")
def index():
    return jsonify(message="Lab 2 Compose with Redis", hostname=socket.gethostname(), visits=store.incr("visits"))

@app.get("/health")
def health():
    store.ping()
    return jsonify(status="healthy")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

```
docker-compose -f compose/compose.yaml up -d --build
docker-compose -f compose/compose.yaml ps
docker-compose -f compose/compose.yaml down
```

Figure 1 — Actual registry, Compose and lifecycle output. Complete transcript: evidence/task5.log.

## 5. Conclusion

Container lifecycle, registry push and Compose verification: PASS. Registry publication is local only.

## Execution status

Task 5: PASS

Runtime versions and installation details: evidence/environment.log and evidence/install.log. Re-run commands are documented in README.md. All reported outcomes are limited to the evidence retained in this folder.
