# Lab 2: Containerization & Kubernetes Orchestration

## Task 2: Implement Kubernetes deployment

Nirdesh Jain | Repository: github.com/jainnirdesh/DevOps | 18 November 2026

Platform: macOS (Apple Silicon), Docker via dedicated Colima profile lab2, Minikube profile lab2, Kubernetes namespace lab2. Figures are rendered from actual saved command output; they are not browser screenshots.

## 1. Objective

Perform a rolling update, rollback, and replica scaling, verifying the image response after each image change.

## 2. Rolling update

Version 2.0 changes the application welcome message. RollingUpdate permits one surge pod and one unavailable pod.

```
docker build -t lab2-python-app:2.0 app-v2
minikube -p lab2 image load --daemon=true lab2-python-app:2.0
kubectl --context lab2 -n lab2 set image deployment/lab2-app web=lab2-python-app:2.0
kubectl --context lab2 -n lab2 rollout status deployment/lab2-app --timeout=180s
kubectl --context lab2 -n lab2 rollout history deployment/lab2-app
```

## 3. Rollback

Undo restores the previous pod template; each surviving ready pod is checked for the VERSION 1.0 response.

```
kubectl --context lab2 -n lab2 rollout undo deployment/lab2-app
kubectl --context lab2 -n lab2 rollout status deployment/lab2-app --timeout=180s
```

## 4. Scaling

Scale to five replicas and wait for readiness, then reduce to three and verify readiness again.

```
kubectl --context lab2 -n lab2 scale deployment/lab2-app --replicas=5
kubectl --context lab2 -n lab2 rollout status deployment/lab2-app --timeout=180s
kubectl --context lab2 -n lab2 scale deployment/lab2-app --replicas=3
kubectl --context lab2 -n lab2 rollout status deployment/lab2-app --timeout=180s
```

Figure 1 — Actual rolling update, rollback and scaling output. Complete transcript: evidence/task2.log.

## 5. Conclusion

Rolling update, rollback and scaling verification: PASS. The later Task 8 reapplies the manifest, returning the desired replica count to two.

## Execution status

Task 2: PASS

Runtime versions and installation details: evidence/environment.log and evidence/install.log. Re-run commands are documented in README.md. All reported outcomes are limited to the evidence retained in this folder.
