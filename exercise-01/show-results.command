#!/bin/zsh
export PATH="/opt/homebrew/bin:/Applications/Docker.app/Contents/Resources/bin:$PATH"
clear
printf 'EXERCISE 1 — HELLO POD\nStudent: nihal-toki\n\n'
printf '$ minikube status\n'
minikube status
printf '\n$ kubectl --context=minikube get nodes\n'
kubectl --context=minikube get nodes
printf '\n$ kubectl --context=minikube get pods hello-k8s -o wide\n'
kubectl --context=minikube get pods hello-k8s -o wide
printf '\n$ kubectl --context=minikube get service hello-k8s\n'
kubectl --context=minikube get service hello-k8s
printf '\nTake your Terminal screenshot now.\nPress Enter to open the Nginx page; leave this window open.\n'
read answer
minikube service hello-k8s
