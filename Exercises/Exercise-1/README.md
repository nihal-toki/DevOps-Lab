# Exercise 1: Kubernetes Getting Started

Run the `nginx` image as a Kubernetes pod, expose it through a NodePort service, and open the Nginx welcome page.

## Objective
Represent the Zepto storefront application with Nginx and make it accessible through a local Kubernetes cluster.

## Prerequisites
Docker Desktop running, Minikube, and kubectl. This exercise was completed on macOS with the Docker driver.

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
Run `bash verify.sh` from this directory. It checks the Minikube cluster, pod readiness, and service type. Open the service URL to verify the browser output.

## Results and screenshots
See [RESULTS.md](RESULTS.md) and the [evidence folder](evidence/).

## Reference
[Instructor’s Exercise 1](https://github.com/SunagP/DevOps-Lab/blob/main/Exercises/1-Kubernetes-Getting-Started.md)
