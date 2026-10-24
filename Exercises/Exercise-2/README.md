# Exercise 2: Flask on Minikube

Deploy the Flask app with a Kubernetes Deployment and expose it through a NodePort Service.

The app returns `Hello from Flask on Kubernetes!` on `/` and listens on port `15000`. The Deployment uses two replicas of `flask-k8s-app:v1` with `imagePullPolicy: Never`.

## Run

Start Docker Desktop and a local Minikube cluster. From this folder, use the following commands to repeat the deployment; these are instructions, not a record of a new run:

```sh
minikube start
docker build -t flask-k8s-app:v1 .
minikube image load flask-k8s-app:v1
kubectl apply -f flask-deployment.yaml
kubectl -n default rollout status deployment/flask-deployment --timeout=180s
kubectl -n default get deployments,pods -l app=flask -o wide
kubectl -n default describe deployment flask-deployment
kubectl -n default logs deployment/flask-deployment
kubectl apply -f flask-service.yaml
kubectl -n default describe service flask-service
minikube service flask-service --namespace default --url
```

Use the current exercise cluster context and its Minikube profile. The manifests do not set a namespace; the recorded deployment used `default`. Apply them with that context's namespace set to `default`.

Open the URL printed by `minikube service` in a browser. Keep that command running if it establishes a tunnel. The expected response is `Hello from Flask on Kubernetes!`.

## Notes

The Dockerfile uses `python:3.9-slim` and installs Flask 3.1.3. Loading the locally built image into Minikube is required because `imagePullPolicy: Never` prevents a registry pull.

The Deployment and Service remain in separate YAML files. The Deployment keeps two pod replicas available; the Service selects pods with `app: flask` and forwards requests to their port `15000`.

Service port `15000` forwards to target port `15000`; NodePort `30080` exposes the Service on a node. Declaring `containerPort` alone does not publish a port on the laptop. With the Docker driver on macOS, use the URL printed by `minikube service` when direct node access is unavailable.

The Flask development server is retained for this lab. Existing application code and container/Kubernetes settings have been preserved.

See [RESULTS.md](RESULTS.md) for the recorded results and available evidence. No new deployment or automated execution results were generated while organizing this exercise.

The saved evidence is organized in this exercise's `evidence/` folder:

- [Deployment description](evidence/deployment-description.txt): two available replicas of `flask-k8s-app:v1`.
- [Flask startup logs](evidence/flask-startup.txt): the application listening on port `15000`.
- [Service description](evidence/service-description.txt): NodePort `30080` and two pod endpoints.

No screenshot files are currently present in `evidence/`; the browser response is recorded in RESULTS.md as confirmed by the repository owner.
