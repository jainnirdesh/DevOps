# Lab 2: Containerization & Kubernetes Orchestration

## Task 3: Containerization and orchestration report

Nirdesh Jain | Repository: github.com/jainnirdesh/DevOps | 18 November 2026

Platform: macOS (Apple Silicon), Docker via dedicated Colima profile lab2, Minikube profile lab2, Kubernetes namespace lab2. Figures are rendered from actual saved command output; they are not browser screenshots.

## 1. Introduction

This report describes Docker containerization and Kubernetes orchestration of a Flask application on this Mac. Task-specific reports contain reproducible commands and actual evidence.

## 2. Architecture

```
Dockerfile -> lab2-python-app:1.0 / 2.0 / 3
                    | minikube image load
                    v
Colima Docker VM -> Minikube node -> Deployment -> Pods
                                         ^
                        NodePort Service 30080 -> port 5000
```

The app serves / and /health. A file counter under /data demonstrates container-layer storage, named volumes and bind mounts. Docker Compose uses a separate Redis-backed counter. A dedicated namespace and explicit contexts isolate all Kubernetes commands.

Figure 1 — Kubernetes deployment verification. Complete transcript: evidence/task1.log.

## 3. Deployment strategy

RollingUpdate uses maxSurge 1 and maxUnavailable 1. A readiness probe controls endpoint readiness. Rollback restores the preceding revision; HTTP responses verify that the expected application version is running.

Figure 2 — Deployment strategy and scaling evidence. Complete transcript: evidence/task2.log.

## 4. Scaling results

The test asserts five ready replicas, then three. Actual result: PASS. No timing from the reference is reused.

## 5. Observations

Local images are loaded into Minikube and imagePullPolicy Never prevents external pulls for the application. Pod-local counters are independent and ephemeral. Named volumes and bind mounts persist beyond container deletion, until their external data is removed. Dockerfile filesystem layers and metadata instructions are distinguished by docker history and RootFS.Layers.

Figure 3 — Continuous deployment script execution. Complete transcript: evidence/task8.log.

## 6. Conclusion

The status table below reports only completed experiments. The shell pipeline is executed separately from Jenkins; the Jenkinsfile is supplied for a local agent with access to these Docker and Kubernetes contexts.

## Execution status

Task 1: PASS; Task 2: PASS; Task 4: PASS; Task 5: PASS; Task 6: PASS; Task 7: PASS; Task 8: PASS

Runtime versions and installation details: evidence/environment.log and evidence/install.log. Re-run commands are documented in README.md. All reported outcomes are limited to the evidence retained in this folder.
