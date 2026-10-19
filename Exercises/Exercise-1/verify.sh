#!/usr/bin/env bash
set -euo pipefail
export PATH="/opt/homebrew/bin:/Applications/Docker.app/Contents/Resources/bin:$PATH"
minikube status
kubectl --context=minikube wait --for=condition=Ready node/minikube --timeout=60s
kubectl --context=minikube wait --for=condition=Ready pod/hello-k8s --timeout=60s
kubectl --context=minikube get nodes
kubectl --context=minikube get pod hello-k8s -o wide
kubectl --context=minikube get service hello-k8s
service_type=$(kubectl --context=minikube get service hello-k8s -o jsonpath='{.spec.type}')
[ "$service_type" = "NodePort" ] || { echo "Expected a NodePort service" >&2; exit 1; }
printf '\nChecks passed. Open the app using: minikube service hello-k8s\n'
