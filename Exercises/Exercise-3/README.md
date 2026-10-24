# Exercise 3: Scaling Flask App on Single Node Using ReplicaSets

## Real-Life Tech Use Case: E-commerce Flash Sale

During an e-commerce flash sale, a website can experience a sudden increase in customer traffic.

Kubernetes ReplicaSets help maintain multiple identical application Pods. When more replicas are required, Kubernetes creates additional Pods. If a Pod is deleted, the ReplicaSet automatically replaces it.

## Objective

- Understand Kubernetes ReplicaSets and Pods.
- Deploy a Flask-based Flash Sale application.
- Scale the ReplicaSet from 3 to 5 Pods.
- Observe automatic Pod replacement.
- Verify Pod distribution on a single-node Minikube cluster.

## Environment

- Operating System: macOS (Apple Silicon)
- Minikube: v1.39.0
- Kubernetes: v1.37.0
- Container Runtime: containerd
- Docker Desktop
- Python: 3.11
- Framework: Flask
- Application Server: Gunicorn

## Application Endpoints

| Endpoint | Purpose |
|---|---|
| `/` | Displays the Flash Sale welcome message |
| `/buy?user=123` | Simulates a product purchase |
| `/health` | Returns the application's health status |

## Steps Performed

### Step 1: Original cluster reset

The original run reset Minikube as directed by the sheet. This deletes cluster resources, including previous exercises; it is not needed to repeat the verification below. Reuse the running single-node cluster for subsequent checks.

### Step 2: Start Single-Node Minikube

```bash
minikube start --nodes=1 --driver=docker
kubectl wait --for=condition=Ready node/minikube --timeout=180s
kubectl get nodes
```

The single Minikube node reached `Ready` status.

### Step 3: Create Flask Application

Created `app.py` with three routes: `/`, `/buy`, and `/health`.

### Step 4: Create Dockerfile

Used Python 3.11, Flask, and Gunicorn to serve the application on port 5000.

### Step 5: Build Docker Image

```bash
docker build -t flashsale:1.0 .
docker images flashsale
minikube image load flashsale:1.0
```

The image was built using Docker Desktop and loaded into Minikube.

### Step 6: Create ReplicaSet and Service

Created `flashsale-replicaset.yaml` containing:

- ReplicaSet: `flashsale-rs`
- Initial replicas: 3
- Container image: `flashsale:1.0`
- Readiness and liveness probes: `/health`
- ClusterIP Service: `flashsale-svc`

### Step 7: Deploy and Verify

```bash
kubectl apply -f flashsale-replicaset.yaml
kubectl get rs
kubectl get pods
```

All three Pods reached `1/1 Running`.

### Step 8: Scale to Five Replicas

```bash
kubectl scale rs flashsale-rs --replicas=5
kubectl get rs
kubectl get pods
```

The ReplicaSet reached five ready Pods.

### Step 9: Delete a Pod

```bash
kubectl delete pod flashsale-rs-mgk5d
kubectl get pods
kubectl get pods -o wide
```

Kubernetes created replacement Pod `flashsale-rs-66b59` and maintained five running Pods on the single Minikube node.

### Step 10: Test Flask Endpoints

```bash
kubectl port-forward service/flashsale-svc 8080:80
```

In another Terminal:

```bash
curl http://127.0.0.1:8080/
curl "http://127.0.0.1:8080/buy?user=123"
curl http://127.0.0.1:8080/health
```

All three endpoints returned the expected JSON responses.

### Step 11: Inspect ReplicaSet

```bash
kubectl describe rs flashsale-rs
kubectl get rs
```

Final state: 5 desired, 5 current, 5 ready replicas.

## Results and Evidence

See [RESULTS.md](RESULTS.md) for the original screenshots, saved terminal outputs, API responses and a separate automated verification run.

## Q&A

**Q1. What is the initial number of replicas?**

3.

**Q2. How many Pods run after applying the ReplicaSet?**

3.

**Q3. What happens when scaling to 5 replicas?**

Kubernetes creates 2 additional Pods.

**Q4. What happens when one Pod is deleted?**

The ReplicaSet automatically creates a replacement Pod.

**Q5. How does Kubernetes maintain the desired replicas?**

The ReplicaSet controller continuously reconciles the actual Pod count with the desired replica count.

**Q6. How many nodes are running?**

1.

**Q7. Where are the Pods running?**

All 5 Pods are running on the single `minikube` node.

## Repeat the verification

With the `minikube` profile running on one node and `flashsale:1.0` loaded, run from this folder:

```sh
python3 verify.py
```

The script creates a unique temporary namespace and applies the unchanged manifest there. It checks three ready pods, scaling to five while retaining the initial pod UIDs, replacement of a deleted pod with a new UID, single-node placement, image/probes/resources, five ready Service endpoints, all three routes and 100 simulated purchases through Service DNS. It also runs the five tests in `test_app.py` inside a running application container and checks the manifest with a server-side dry run.

Measured results, unit-test output, final resources and cleanup are saved under `evidence/`. The script updates these supplementary evidence files on repeat runs. It deletes only its temporary namespace; the original `default` namespace ReplicaSet is left intact. The observed purchase counts demonstrate Service traffic distribution, not a load benchmark or a guarantee of equal counts.

A port-forward targets a single pod. Use it for browser access; use the Service DNS requests from the verification script to demonstrate traffic distribution.

## Source corrections and implementation differences

The question sheet copies `ex3-flash-sale.py` but starts `app:app`; this implementation consistently uses `app.py`. Its commands alternate between `flask-app-rs` and `flashsale-rs`; this implementation uses `flashsale-rs`, matching the manifest. The image tag is consistently `flashsale:1.0`, rather than the unrelated `flask-app` build tag in one sheet command.

The local image is loaded into Minikube and uses `imagePullPolicy: Never`. No Docker Hub publication or registry digest verification is claimed. The sheet and the reference repository also include publishing an image; that is a separate remaining step if required by the instructor. The existing application, Dockerfile and ReplicaSet/Service manifest are preserved.

## Screenshot evidence

These are unchanged full-page PNG captures from the supplied `Exercise_3_Screenshots.pdf`; the original screenshot content is preserved:

| PDF page | Evidence |
| --- | --- |
| 3 | [Ready node](evidence/nodes.png) |
| 6 | [Successful Docker build](evidence/docker-build.png) |
| 7 | [Initial three pods](evidence/initial-three-pods.png) |
| 8 | [Scaled five pods](evidence/scaled-five-pods.png) |
| 9 | [Replacement and node placement](evidence/pod-replacement.png) |
| 10 | [Homepage and purchase curl responses](evidence/buy-response.png) |
| 11 | [Health curl response](evidence/health-response.png) |
| 12 | [ReplicaSet configuration](evidence/replicaset-description.png) |
| 13 | [Controller events and five ready replicas](evidence/replicaset-events.png) |
