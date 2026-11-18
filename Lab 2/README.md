# Lab 2: Containerization and Kubernetes Orchestration

Student: Nirdesh Jain  
Repository: https://github.com/jainnirdesh/DevOps

This folder implements all nine tasks from the supplied reference documents. Reports in `docs/` follow the reference task order and styles. The original reference documents remain at their supplied Downloads location; their screenshots and results are not evidence for this run.

## Local runtime

On this Mac, Docker runs inside a dedicated Colima VM. Commands explicitly select Docker context `colima-lab2`, Minikube profile/context `lab2`, and Kubernetes namespace `lab2`.

```sh
brew install colima docker docker-buildx docker-compose kubectl minikube
colima start --profile lab2 --cpu 4 --memory 6 --disk 30 --vm-type vz --mount-type virtiofs
export DOCKER_CONTEXT=colima-lab2
export DOCKER_HOST="unix://$HOME/.colima/lab2/docker.sock"
```

The standalone Flask demo uses host port **5004** because macOS Control Center already occupies port 5000. The container port remains 5000.

## Run the experiments

From `Lab 2`, on a fresh lab runtime:

```sh
python3 scripts/run_lab.py
```

Order: Task 4 (image) → 5 (management, registry, Compose) → 6 (storage) → 7 (network) → 1 (Kubernetes) → 2 (update, rollback, scale) → 8 (deployment pipeline). Tasks 3 and 9 document those experiments. The runner stops on a failed command or assertion and records the failure. It creates named lab resources; do not rerun a partially completed task without checking its log and existing resources first.

Individual experiment: `python3 scripts/run_lab.py 4`. Completed task status and full command transcripts are under `evidence/`. `evidence/host-validation.log` checks Flask responses and YAML syntax outside containers; it does not count as Docker/Kubernetes execution.

## Continuous deployment

```sh
sh scripts/cicd.sh 3
```

The five stages build the image, load it into Minikube, apply manifests, update the Deployment image, and verify readiness and Service DNS. This local shell execution is separate from Jenkins. The supplied `Jenkinsfile` preserves the same stage structure and uses macOS `sh` commands. An SCM job should use Script Path `Lab 2/Jenkinsfile` and a local agent with access to the Docker/Kubernetes contexts. No external GitHub push or automatic remote trigger is performed by the runner.

The base Deployment declares two replicas, so applying it in Task 8 resets the three replicas left by Task 2 to two.

## Evidence and reports

- `app/`, `app-v2/`: Flask versions 1.0 and 2.0, Dockerfiles and pinned dependencies.
- `compose/`: Flask and Redis stack on loopback port 5001.
- `k8s/`: namespace, Deployment and NodePort Service.
- `evidence/task*.log`: actual commands and output.
- `evidence/results.json`: verified task results.
- `evidence/figures/`: selected real log lines rendered as figures, not GUI screenshots.
- `docs/Task*.docx`: updated reports without the reference student's roll number.

To regenerate the reports in an environment with `python-docx` and Pillow:

```sh
python3 -m pip install -r scripts/requirements-docs.txt
python3 scripts/build_reports.py
```

## Stop and resume

After reviewing the running cluster, release its resources without deleting its data:

```sh
export DOCKER_CONTEXT=colima-lab2
minikube -p lab2 stop
colima stop --profile lab2
```

Resume with `colima start --profile lab2`, followed by `minikube -p lab2 start`. Named volume `lab2-vol` and `storage-demo/bind-data/counter.txt` are retained as storage evidence.

## Official setup references

- [Colima installation](https://colima.run/docs/installation/)
- [Minikube Docker driver](https://minikube.sigs.k8s.io/docs/drivers/docker/)


Runtime setup observations: official VM image and Kubernetes binaries were checksum verified and cached after slow host downloads. Minikube uses Kubernetes v1.37.0 with containerd, the cached preload, and explicit `--daemon=true` for loading local application images. The CNI image was loaded locally after an external pull failed. Bootstrap attempts and the recovered Compose TLS timeout are retained in evidence.

Verified final result: Tasks 1, 2, 4, 5, 6, 7 and 8 PASS. Tasks 3 and 9 are the corresponding reports. Final deployment uses image `lab2-python-app:3` with two ready replicas. The application is forwarded to http://localhost:5080/ while the recorded port-forward process is running. Restart forwarding with:

```sh
kubectl --context lab2 -n lab2 port-forward --address 127.0.0.1 service/lab2-service 5080:80
```

Report regeneration reads the original Downloads reference location. Set `LAB2_REFERENCE_DIR` to a different reference-documents directory if needed.
