# Lab 2: Containerization & Kubernetes Orchestration

## Task 1: Deploy an application to Kubernetes

Nirdesh Jain | Repository: github.com/jainnirdesh/DevOps | 18 November 2026

Platform: macOS (Apple Silicon), Docker via dedicated Colima profile lab2, Minikube profile lab2, Kubernetes namespace lab2. Figures are rendered from actual saved command output; they are not browser screenshots.

## 1. Objective

Deploy the containerized Flask app to Minikube using Deployment and Service manifests and verify ready pods and HTTP responses.

## 2. Start the cluster

A dedicated Minikube profile uses the Docker engine inside the lab2 Colima VM. Image 1.0 must be loaded before starting pods with imagePullPolicy Never.

```
export DOCKER_CONTEXT=colima-lab2
export DOCKER_HOST="unix://$HOME/.colima/lab2/docker.sock"
minikube -p lab2 start --driver=docker --kubernetes-version=v1.37.0 --container-runtime=containerd --cpus=2 --memory=3072 --disk-size=20g --base-image=gcr.io/k8s-minikube/kicbase:v0.0.51 --preload=true --cache-images=false
minikube -p lab2 image load --daemon=true lab2-python-app:1.0
kubectl --context lab2 get nodes -o wide
```

Setup observation: slow external downloads were replaced with checksum-verified local caches. The CNI image was loaded locally after an external pull failure. Explicit --daemon=true and DOCKER_HOST select the local Colima engine for image loading; bootstrap attempt logs are retained as setup evidence.

## 3. Manifests and deployment

The namespace isolates this lab. The Deployment starts two replicas, readiness checks /health, and the NodePort service maps port 80 to container port 5000 using node port 30080.

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

## 4. Verify running pods

The execution script checks readyReplicas equals 2, tests each pod directly and tests /health through the Service DNS name.

```
kubectl --context lab2 -n lab2 get deployments,pods,svc -o wide
kubectl --context lab2 -n lab2 rollout status deployment/lab2-app --timeout=180s
```

Figure 1 — Cluster deployment and endpoint verification. Complete transcript: evidence/task1.log.

## 5. Conclusion

Deployment verification result: PASS. The full transcript records actual node versions and pod names; reference versions are not copied.

## Execution status

Task 1: PASS

Runtime versions and installation details: evidence/environment.log and evidence/install.log. Re-run commands are documented in README.md. All reported outcomes are limited to the evidence retained in this folder.
