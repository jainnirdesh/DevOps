# Lab 2: Containerization & Kubernetes Orchestration

## Task 7: Docker Network

Nirdesh Jain | Repository: github.com/jainnirdesh/DevOps | 18 November 2026

Platform: macOS (Apple Silicon), Docker via dedicated Colima profile lab2, Minikube profile lab2, Kubernetes namespace lab2. Figures are rendered from actual saved command output; they are not browser screenshots.

## 1. Objective

Verify container-to-container HTTP communication using Docker DNS and the dynamically discovered container IP.

## 2. Create network and containers

The client uses the same Python image with a sleep command; Python urllib performs the HTTP requests.

```
docker network create lab2-net
docker run -d --name lab2-net-app --network lab2-net lab2-python-app:1.0
docker run -d --name lab2-net-client --network lab2-net lab2-python-app:1.0 sleep 3600
```

## 3. Communication by name and by IP

The server IP is inspected at runtime, rather than copying the reference IP. Both responses must contain status=healthy.

```
docker inspect --format "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}" lab2-net-app
docker exec lab2-net-client python -c 'import urllib.request; print(urllib.request.urlopen("http://lab2-net-app:5000/health").read().decode())'
# Repeat with the inspected IP in place of lab2-net-app
docker network inspect lab2-net
```

Figure 1 — Actual DNS and IP communication output. Complete transcript: evidence/task7.log.

## 4. Conclusion

Both name and IP communication checks: PASS. Container names provide a stable discovery mechanism while IP assignments can change.

## Execution status

Task 7: PASS

Runtime versions and installation details: evidence/environment.log and evidence/install.log. Re-run commands are documented in README.md. All reported outcomes are limited to the evidence retained in this folder.
