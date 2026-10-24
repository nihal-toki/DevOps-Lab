# Exercise 2 Results

The saved Deployment description records creation on 20 October 2026 at 10:30:44 +0530. The exact verification time and tool versions were not captured in the supplied evidence.

The deployment ran in namespace `default`. Results below use the existing terminal evidence and the deployment details supplied by the repository owner; this documentation update did not rerun the exercise.

## Image and deployment

The preserved Dockerfile uses `python:3.9-slim` and pins Flask 3.1.3. The Deployment uses image `flask-k8s-app:v1`, two replicas and `imagePullPolicy: Never`.

The [Deployment description](evidence/deployment-description.txt) records two desired, updated, total and available replicas, with zero unavailable. Both `Available` and `Progressing` conditions are `True`. The repository owner confirmed both pods were running successfully; a separate pod listing was not supplied.

The [Flask startup logs](evidence/flask-startup.txt) show the app listening on all addresses at port `15000`. The Deployment description records container port `15000/TCP` and host port `0/TCP`.

## Before and after the Service

A separate before-Service request or absence-of-Service check was not captured, so no before-Service execution result is claimed here.

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

The two endpoint addresses show where the Service forwards traffic to the Flask application. The repository owner confirmed the browser displayed:

```text
Hello from Flask on Kubernetes!
```

A browser screenshot and a captured HTTP response were not available locally. No HTTP status code or automated test pass is claimed. Obtain a current access URL with `minikube service flask-service --namespace default --url` when repeating the exercise.

## Recorded output

- [Deployment description](evidence/deployment-description.txt)
- [Flask startup logs](evidence/flask-startup.txt)
- [Service description and endpoints](evidence/service-description.txt)

Missing evidence compared with the reference: browser screenshot (`evidence/flask-response.png`), separate deployment/pod listing, Service listing, before-Service measurement, unit-test output and automated verification report. These were not fabricated or copied. The reference's Windows verification script and test implementation were not added as completed work.
