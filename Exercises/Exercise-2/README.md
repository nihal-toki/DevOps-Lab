# Exercise 2: Flask on Minikube

Deploy the Flask app with a Kubernetes Deployment and expose it through a NodePort Service.

The app returns `Hello from Flask on Kubernetes!` on `/` and listens on port `15000`. The Deployment uses two replicas of `flask-k8s-app:v1` with `imagePullPolicy: Never`.

## Run

Start Docker Desktop and a local Minikube cluster. From this folder, use the following commands to repeat the deployment; these are instructions, not a record of a new run:

```sh
minikube start
docker build -t flask-k8s-app:v1 .
minikube image load flask-k8s-app:v1
kubectl -n default apply -f flask-deployment.yaml
kubectl -n default rollout status deployment/flask-deployment --timeout=180s
kubectl -n default get deployments,pods -l app=flask -o wide
kubectl -n default describe deployment flask-deployment
kubectl -n default logs deployment/flask-deployment
kubectl -n default apply -f flask-service.yaml
kubectl -n default describe service flask-service
minikube service flask-service --namespace default --url
```

Use the current exercise cluster context and its Minikube profile. The manifests do not set a namespace; the recorded deployment used `default`. Apply them with that context's namespace set to `default`.

Open the URL printed by `minikube service` in a browser. Keep that command running if it establishes a tunnel. In another terminal, verify the response with the actual printed URL:

```sh
curl --fail --show-error 'http://127.0.0.1:PRINTED_PORT/'
```

Replace `PRINTED_PORT` with the tunnel port printed for this run. The expected body is `Hello from Flask on Kubernetes!`; the saved [curl response](evidence/curl-response.txt) contains that exact message. The saved [Kubernetes logs](evidence/kubernetes-logs.txt) also record a successful `GET /` with status 200.

## Notes

The Dockerfile uses `python:3.9-slim` and installs Flask 3.1.3. Loading the locally built image into Minikube is required because `imagePullPolicy: Never` prevents a registry pull.

The Deployment and Service remain in separate YAML files. The Deployment keeps two pod replicas available; the Service selects pods with `app: flask` and forwards requests to their port `15000`.

Service port `15000` forwards to target port `15000`; NodePort `30080` exposes the Service on a node. Declaring `containerPort` alone does not publish a port on the laptop. With the Docker driver on macOS, use the URL printed by `minikube service` when direct node access is unavailable.

Implementation differences from the question sheet:

- This Deployment runs **two replicas**, rather than the requested one.
- The resource names are `flask-deployment` and `flask-service`; the image is `flask-k8s-app:v1`. These are the names used in this implementation rather than the question sheet's names.
- The Service is defined separately in `flask-service.yaml` and applied after `flask-deployment.yaml`.

The original 20 October evidence did not demonstrate a pre-Service failure. A supplementary isolated run on 24 October now records that failure and the subsequent successful Service request; see RESULTS.md.

The Flask development server is retained for this lab. Existing application code and container/Kubernetes settings have been preserved.

See [RESULTS.md](RESULTS.md) for the recorded results and available evidence. The original deployment evidence is preserved alongside a supplementary isolated verification run on 24 October 2026.

The saved evidence is organized in this exercise's `evidence/` folder:

- [Deployment description](evidence/deployment-description.txt): two available replicas of `flask-k8s-app:v1`.
- [Flask startup logs](evidence/flask-startup.txt): the application listening on port `15000`.
- [Service description](evidence/service-description.txt): NodePort `30080` and two pod endpoints.

- [Kubernetes pod logs](evidence/kubernetes-logs.txt): Flask startup inside the pods and HTTP request results.
- [Curl response](evidence/curl-response.txt): the required response body.
- Screenshots: [Deployment](evidence/deployment.png), [Service](evidence/service.png), [Pods](evidence/pods.png), [Browser response](evidence/flask-response.png).

The screenshots are unchanged full-page PNG captures of pages 4, 5, 7 and 6 respectively of the supplied `DevOps_Exercise_2_Final.pdf`. They preserve the original screenshot contents and page labels; no terminal output was generated or reconstructed.

## Verify

The missing before/after checks were completed on 24 October 2026. With the existing `minikube` profile running and `flask-k8s-app:v1` already loaded, repeat them from this folder:

```sh
python3 verify.py
kubectl --context minikube -n default exec -i deployment/flask-deployment -- python - < test_app.py
```

`verify.py` creates a unique temporary namespace, applies the existing Deployment, confirms zero Services and curl connection refusal at `127.0.0.1:15000`, then creates a temporary copy of the Service and checks its tunnel response. It allocates a free NodePort instead of reusing `30080`, which remains assigned to the original Service. It records seven Kubernetes/HTTP check groups, checks both manifests with the API server, closes its tunnel and deletes its temporary namespace. It updates its evidence files on each run. A process listening on host port 15000 will cause the refusal check to fail.

`test_app.py` checks the home route's status/body and an unknown route's 404 using Flask's test client. The command above runs it in a separate process inside the existing application container without editing the server. The saved [unit-test output](evidence/unit-tests.txt) records both tests passing.

Supplementary evidence: [before-Service measurement](evidence/before-service.json), [deployment/pod listing](evidence/deployment.txt), [Service/endpoints](evidence/service.txt), [curl command, headers and body](evidence/service-http-response.txt), [verification report](evidence/verification.json), and [temporary namespace cleanup](evidence/verification-cleanup.json).
