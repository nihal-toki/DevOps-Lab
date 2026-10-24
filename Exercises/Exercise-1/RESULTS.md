# Exercise 1 — Results

Completed by [nihal-toki](https://github.com/nihal-toki) on 19 October 2026.

| Check | Observed result |
| --- | --- |
| Minikube | Host, kubelet, and API server Running; kubeconfig Configured |
| Node | minikube Ready |
| Pod | hello-k8s, 1/1 Ready, Running, 0 restarts |
| Service | hello-k8s, NodePort, 80:31509/TCP |
| Browser | Welcome to nginx! |

## Cluster status
![Minikube status and Ready node](evidence/01-cluster.png)

## Pod and service
![Running pod and NodePort service](evidence/02-pod-service.png)

## Browser output
![Nginx welcome page](evidence/04-browser.png)

The browser used the local Minikube service tunnel. Its temporary localhost port can change between runs.

## Automated verification

Rechecked on 20 October 2026 using `verify.sh`: all five checks passed, including a ready service endpoint and HTTP 200. See [verification.json](evidence/verification.json) for measured values and the image digest, and [nginx-response.html](evidence/nginx-response.html) for the actual response. Ports and addresses are specific to each run.


## GitHub CI recheck — 24 October 2026

[Run 40061489311](https://github.com/nihal-toki/DevOps-Lab/actions/runs/40061489311) successfully deployed the unchanged `hello-k8s.yaml` on a fresh Linux Minikube cluster and passed all five checks: ready pod, Nginx image/port, NodePort configuration, ready endpoint and HTTP 200 with the Nginx welcome page.

The earlier CI attempt on 20 October failed during cluster startup because the default ServiceAccount did not yet exist; its uploaded files were checked-in local reports, not a successful CI measurement. The workflow now waits for that ServiceAccount before applying the manifest and removes checked-in report copies from its disposable workspace before testing. The successful run's newly generated reports are stored separately so the original local results remain unchanged:

- [Fresh CI verification](evidence/ci-verification.json)
- [Actual CI HTML response](evidence/ci-nginx-response.html)
- [Run and artifact provenance](evidence/ci-workflow-run.json)
