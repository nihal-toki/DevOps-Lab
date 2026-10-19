# Exercise 1 — Hello Pod

Student GitHub: https://github.com/nihal-toki

Reference: https://github.com/SunagP/DevOps-Lab/blob/main/Exercises/1-Kubernetes-Getting-Started.md

## Objective
Run Nginx in a Kubernetes pod using Minikube and access it in a browser. Nginx represents the storefront application in the exercise's Zepto scenario.

## Procedure

Start Docker Desktop and wait until its engine is running. Then run:

```sh
minikube start --driver=docker
minikube status
kubectl --context=minikube get nodes
kubectl --context=minikube run hello-k8s --image=nginx --port=80
kubectl --context=minikube wait --for=condition=Ready pod/hello-k8s --timeout=180s
kubectl --context=minikube get pods
kubectl --context=minikube expose pod hello-k8s --type=NodePort --port=80
kubectl --context=minikube get service hello-k8s
minikube service hello-k8s
```

Keep the service terminal open while viewing the page on macOS with the Docker driver.

## Submission screenshots

### Cluster running
![Minikube running and node Ready](screenshots/01-cluster.png)

### Pod and service
![Nginx pod Running and NodePort service](screenshots/02-pod-service.png)

### Application in browser
![Nginx welcome page](screenshots/04-browser.png)

## Execution status
Verified on 19 October 2026: Minikube node Ready; hello-k8s pod 1/1 Running with zero restarts; NodePort service created on port 31509; HTTP request through the Minikube service tunnel returned the Nginx welcome page. All three submission screenshots are included above.

The YAML files provide an alternative declarative way to reproduce the pod and service. The executed lab used the imperative commands above.

Run `show-results.command` to display live cluster, pod, and service results for screenshots, then press Enter to open the service in your browser.
