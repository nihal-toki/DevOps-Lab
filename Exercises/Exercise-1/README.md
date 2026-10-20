# Exercise 1: Kubernetes Getting Started

Run the `nginx` image as a Kubernetes pod, expose it through a NodePort service, and open the Nginx welcome page.

## Objective
Represent the Zepto storefront application with Nginx and make it accessible through a local Kubernetes cluster.

## Prerequisites
Docker Desktop running, Minikube, kubectl, and Python 3. This exercise was completed on macOS with the Docker driver.

## Procedure

```sh
minikube start --driver=docker
kubectl --context=minikube run hello-k8s --image=nginx --port=80
kubectl --context=minikube wait --for=condition=Ready pod/hello-k8s --timeout=180s
kubectl --context=minikube get pods
kubectl --context=minikube expose pod hello-k8s --type=NodePort --port=80
kubectl --context=minikube get service hello-k8s
minikube service hello-k8s
```

Keep the service terminal open while viewing the page on macOS with the Docker driver.

## Configuration alternative
On a clean cluster, `kubectl --context=minikube apply -f hello-k8s.yaml` creates the same pod and service declaratively. The procedure above records the commands used for the lab.

## Verification
In one Terminal, run `minikube -p minikube service hello-k8s -n default --url` and keep it open. In a second Terminal, from this directory, run:

```sh
bash verify.sh http://127.0.0.1:PORT/
```

Replace PORT with the actual port printed by Minikube. The script checks pod readiness, Nginx image and container port, NodePort configuration, the ready service endpoint, and HTTP 200 with the Nginx welcome page. It saves measured results to `evidence/verification.json` and the live HTML to `evidence/nginx-response.html`. Optional `--context` and `--namespace` arguments select another cluster or namespace.

GitHub Actions repeats the deployment and verification in a fresh Linux Minikube cluster and uploads the measured evidence as a run artifact. The local instructions are for macOS.

The standalone pod has no Deployment or ReplicaSet to recreate it if deleted. Stop the local cluster without deleting resources using `minikube stop`.

## Results and screenshots
See [RESULTS.md](RESULTS.md) and the [evidence folder](evidence/).

## Reference
[Instructor’s Exercise 1](https://github.com/SunagP/DevOps-Lab/blob/main/Exercises/1-Kubernetes-Getting-Started.md)
