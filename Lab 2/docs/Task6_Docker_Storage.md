# Lab 2: Containerization & Kubernetes Orchestration

## Task 6: Docker Storage

Nirdesh Jain | Repository: github.com/jainnirdesh/DevOps | 18 November 2026

Platform: macOS (Apple Silicon), Docker via dedicated Colima profile lab2, Minikube profile lab2, Kubernetes namespace lab2. Figures are rendered from actual saved command output; they are not browser screenshots.

## 1. Objective

Demonstrate container writable-layer loss and persistence outside the container using a named volume and bind mount.

## 2. Data loss without a volume

The experiment asserts counts 1, 2 and 3. After deleting and recreating the container without a mount, it asserts count 1.

```
docker run -d --name lab2-novol -p 127.0.0.1:5101:5000 lab2-python-app:1.0
# Request / three times
docker rm -f lab2-novol
docker run -d --name lab2-novol -p 127.0.0.1:5101:5000 lab2-python-app:1.0
# Request / and verify visits=1
```

## 3. Named volume and bind mount

The named volume is reused by a new container; visits continue from 2 to 3. The bind mount creates a host counter.txt and is also reused by a replacement container; visits continue from 1 to 2.

```
docker volume create lab2-vol
docker run -d --name lab2-volume -v lab2-vol:/data -p 127.0.0.1:5102:5000 lab2-python-app:1.0
docker run -d --name lab2-bind -v "$PWD/storage-demo/bind-data:/data" -p 127.0.0.1:5103:5000 lab2-python-app:1.0
```

Figure 1 — Actual counter reset and persistence assertions. Complete transcript: evidence/task6.log.

## 4. Conclusion

Storage assertions: PASS. Volumes and bind mounts persist independently of a container, but are not permanent backups: deleting the volume or host data removes the stored content.

## Execution status

Task 6: PASS

Runtime versions and installation details: evidence/environment.log and evidence/install.log. Re-run commands are documented in README.md. All reported outcomes are limited to the evidence retained in this folder.
