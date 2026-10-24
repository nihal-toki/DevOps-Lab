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

### Step 1: Reset Minikube

```bash
minikube stop
minikube delete
```

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

See [RESULTS.md](RESULTS.md) for observed results and the `evidence/` directory for saved Kubernetes outputs and API responses.

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