# Exercise 3 Results

**Exercise:** Scaling Flask App on Single Node Using ReplicaSets  
**Platform:** macOS (Apple Silicon)  
**Date:** 24 October 2026

## 1. Minikube Cluster

Minikube v1.39.0 was started with Docker Desktop using a single node.

Kubernetes version: v1.37.0.

The node initially reported `NotReady` during startup and subsequently reached `Ready`.

Command:

```bash
kubectl get nodes
```

**Observed result:** One `minikube` control-plane node in `Ready` state.

Evidence: [nodes.txt](evidence/nodes.txt)

## 2. Initial ReplicaSet Deployment

The Flask application was packaged as Docker image `flashsale:1.0` and loaded into Minikube.

The ReplicaSet `flashsale-rs` was created with 3 replicas.

**Observed result:** 3 desired, 3 current, and 3 ready Pods, with zero restarts.

## 3. Scaling from 3 to 5 Replicas

Command:

```bash
kubectl scale rs flashsale-rs --replicas=5
```

**Observed result:** 5 desired, 5 current, and 5 ready Pods.

Kubernetes created two additional Pods without deleting the original three.

Evidence: [replicaset.txt](evidence/replicaset.txt)

## 4. Automatic Pod Replacement

The Pod `flashsale-rs-mgk5d` was deleted.

Kubernetes automatically created replacement Pod `flashsale-rs-66b59`.

**Observed result:** The ReplicaSet returned to five running Pods, demonstrating self-healing.

The ReplicaSet description includes `SuccessfulCreate` events.

Evidence: [replicaset-description.txt](evidence/replicaset-description.txt)

## 5. Pod Distribution

All five Pods were scheduled on the single `minikube` node.

| Pod | IP address | Status |
|---|---|---|
| flashsale-rs-66b59 | 10.244.0.8 | Running |
| flashsale-rs-sfpnb | 10.244.0.4 | Running |
| flashsale-rs-vj9wt | 10.244.0.6 | Running |
| flashsale-rs-xqb4j | 10.244.0.7 | Running |
| flashsale-rs-zh9q8 | 10.244.0.5 | Running |

All Pods reported `1/1` readiness and zero restarts.

Evidence: [pods-distribution.txt](evidence/pods-distribution.txt)

## 6. Kubernetes Service

Service name: `flashsale-svc`

Service type: `ClusterIP`

Service port: `80`

Container target port: `5000`

The Service was accessed from macOS using:

```bash
kubectl port-forward service/flashsale-svc 8080:80
```

Evidence: [service.txt](evidence/service.txt)

## 7. Flask Application Verification

The following endpoints were tested successfully.

| Endpoint | Observed result |
|---|---|
| `/` | Welcome to Big Sale! |
| `/buy?user=123` | Successful simulated purchase of a Smartphone |
| `/health` | Healthy |

The recorded requests were served by Pod `flashsale-rs-sfpnb`.

Evidence:

- [Homepage response](evidence/homepage-response.json)
- [Purchase response](evidence/buy-response.json)
- [Health response](evidence/health-response.json)

## 8. Resource Configuration

The ReplicaSet uses the following resource configuration per container.

| Resource | Request | Limit |
|---|---|---|
| CPU | 100m | 500m |
| Memory | 128Mi | 256Mi |

Both readiness and liveness probes use the `/health` endpoint on port 5000.

## 9. Final Verification

| Check | Result |
|---|---|
| Single-node Minikube | Passed |
| Initial 3 replicas | Passed |
| Scaling to 5 replicas | Passed |
| Automatic Pod replacement | Passed |
| Five Pods running on one node | Passed |
| Flask homepage | Passed |
| Flash Sale purchase endpoint | Passed |
| Health endpoint | Passed |
| ReplicaSet description | Verified |

## Conclusion

Exercise 3 successfully demonstrated Kubernetes ReplicaSet scaling and self-healing on a single-node Minikube cluster running on macOS.

The ReplicaSet was scaled from three to five replicas. After one Pod was deleted, Kubernetes automatically created a replacement to maintain the desired replica count.

All three Flask endpoints returned the expected responses.