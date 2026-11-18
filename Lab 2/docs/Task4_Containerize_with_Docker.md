# Lab 2: Containerization & Kubernetes Orchestration

## Task 4: Containerize a sample application using Docker

Nirdesh Jain | Repository: github.com/jainnirdesh/DevOps | 18 November 2026

Platform: macOS (Apple Silicon), Docker via dedicated Colima profile lab2, Minikube profile lab2, Kubernetes namespace lab2. Figures are rendered from actual saved command output; they are not browser screenshots.

## 1. Objective

Build and run a Docker image for the Flask app, verify both HTTP endpoints and inspect image history.

## 2. Application

GET / returns the welcome message, hostname and visit count persisted to /data/counter.txt. GET /health returns healthy without changing the counter. A lock serializes counter updates within the demo process.

app/app.py

```
import os
import socket
from pathlib import Path
from threading import Lock
from flask import Flask, jsonify

app = Flask(__name__)
lock = Lock()
counter_path = Path(os.environ.get("DATA_DIR", "/data")) / "counter.txt"

@app.get("/")
def index():
    with lock:
        counter_path.parent.mkdir(parents=True, exist_ok=True)
        count = int(counter_path.read_text()) + 1 if counter_path.exists() else 1
        counter_path.write_text(str(count))
    return jsonify(message=os.environ.get("APP_MESSAGE", "Welcome to Lab 2 - VERSION 1.0"), hostname=socket.gethostname(), visits=count)

@app.get("/health")
def health():
    return jsonify(status="healthy")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

app/requirements.txt

```
Flask==3.1.2
```

## 3. Dockerfile and build

Dependencies are copied and installed before app.py so source changes can reuse the dependency layer.

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

```
docker build -t lab2-python-app:1.0 app
```

## 4. Run, layers and behaviour

```
docker run -d --name lab2-app -p 127.0.0.1:5004:5000 lab2-python-app:1.0
curl http://127.0.0.1:5004/
curl http://127.0.0.1:5004/health
docker history lab2-python-app:1.0
docker image inspect lab2-python-app:1.0 --format "{{json .RootFS.Layers}}"
```

Figure 1 — Actual Docker build and HTTP verification output. Complete transcript: evidence/task4.log.

## 5. Layer description

FROM supplies the base filesystem. COPY and RUN create filesystem changes; WORKDIR also sets image configuration and may create its directory. EXPOSE and CMD are image metadata. docker history includes metadata-only entries, so every listed instruction must not be counted as a filesystem layer. Actual layer digests and sizes are in the task log.

## 6. Conclusion

Docker image build and endpoint checks: PASS. Flask development server is used for this local lab.

## Execution status

Task 4: PASS

Runtime versions and installation details: evidence/environment.log and evidence/install.log. Re-run commands are documented in README.md. All reported outcomes are limited to the evidence retained in this folder.
