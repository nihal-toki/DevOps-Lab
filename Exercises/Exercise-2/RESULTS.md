# Exercise 2 Results

The saved Deployment description records creation on 20 October 2026 at 10:30:44 +0530. The exact verification time and tool versions were not captured in the supplied evidence.

The deployment ran in namespace `default`. Results below use the existing terminal evidence and the deployment details supplied by the repository owner; this documentation update did not rerun the exercise.

## Image and deployment

The preserved Dockerfile uses `python:3.9-slim` and pins Flask 3.1.3. The Deployment uses image `flask-k8s-app:v1`, two replicas and `imagePullPolicy: Never`.

The [Deployment description](evidence/deployment-description.txt) records two desired, updated, total and available replicas, with zero unavailable. Both `Available` and `Progressing` conditions are `True`. The [pod screenshot](evidence/pods.png) shows both Flask pods `1/1 Running` with zero restarts, at `10.244.0.5` and `10.244.0.4`. The [deployment screenshot](evidence/deployment.png) shows `2/2` ready and two available replicas.

The [Flask startup logs](evidence/flask-startup.txt) show the app listening on all addresses at port `15000`. The Deployment description records container port `15000/TCP` and host port `0/TCP`.

## Before and after the Service

A pre-Service connection failure was **not demonstrated**. No saved request establishes a connection refusal or the absence of a Service before exposure; the evidence below records successful access after deployment.

The [Service description](evidence/service-description.txt) records:

| Setting | Recorded value |
| --- | --- |
| Service | `flask-service` |
| Type | `NodePort` |
| ClusterIP | `10.101.226.195` |
| Service port | `15000/TCP` |
| Target port | `15000/TCP` |
| NodePort | `30080/TCP` |
| Endpoints | `10.244.0.4:15000`, `10.244.0.5:15000` |

The two endpoint addresses match the Flask pod addresses in the screenshot. The [Service screenshot](evidence/service.png) also shows `flask-service` exposed as `15000:30080/TCP`. The saved [curl response](evidence/curl-response.txt) and [browser response screenshot](evidence/flask-response.png) contain:

```text
Hello from Flask on Kubernetes!
```

The [Kubernetes logs](evidence/kubernetes-logs.txt) show Flask listening at `10.244.0.5:15000` and `10.244.0.4:15000`. They record `GET / HTTP/1.1` with status **200** at `20/Oct/2026 05:03:20`. A separate favicon request returned 404; that does not indicate failure of the home route.

`curl-response.txt` records the successful response body, but contains neither the invocation URL nor HTTP headers/status. The 200 status above comes from the application log, not from a fabricated curl transcript. No automated unit-test result is claimed. Obtain a current access URL with `minikube service flask-service --namespace default --url` when repeating the exercise.

![Flask response recorded in the supplied PDF](evidence/flask-response.png)

Implementation differences from the question sheet: this run uses **two replicas instead of one**, names its resources `flask-deployment` and `flask-service`, and defines the Service in a separate `flask-service.yaml`. The saved implementation uses `flask-k8s-app:v1` and namespace `default`. These settings and the application were preserved during evidence organization.

## Recorded output

- [Deployment description](evidence/deployment-description.txt)
- [Flask startup logs](evidence/flask-startup.txt)
- [Service description and endpoints](evidence/service-description.txt)

- [Kubernetes pod logs and HTTP status](evidence/kubernetes-logs.txt)
- [Curl response body](evidence/curl-response.txt)
- [Deployment screenshot](evidence/deployment.png)
- [Service screenshot](evidence/service.png)
- [Pod screenshot](evidence/pods.png)
- [Browser response screenshot](evidence/flask-response.png)

The four images are unchanged full-page PNG captures from the owner's supplied `DevOps_Exercise_2_Final.pdf`: pages 4, 5, 7 and 6 respectively. The PDF's pod capture clips the bottom of an unrelated Exercise 1 row; both Exercise 2 pod rows are visible. The browser-response capture contains the message but no address bar, so its URL is not inferred.

Missing evidence: the pre-Service failure test, curl invocation/URL and headers, unit-test output, and an automated verification report. No results or screenshots were invented to fill these gaps.
