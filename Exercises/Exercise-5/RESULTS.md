# Exercise 5 — Results and Verification

## Environment

| Component | Observed value |
|---|---|
| Operating system | macOS (Apple Silicon) |
| Docker platform | Docker Desktop |
| Docker Engine | 29.9.1 |
| Python | 3.9.6 |
| Docker SDK | 7.2.0 |
| Flask image | `flask-apparmor` |
| Host port | 5002 |
| Container port | 5000 |

## 1. Docker Security Support

Command:

```bash
docker info --format '{{json .SecurityOptions}}'
```

Observed output:

```text
["name=seccomp,profile=builtin","name=cgroupns"]
```

**Result:** Docker did not report AppArmor support.

## 2. Flask Docker Image Build

Command:

```bash
docker build -t flask-apparmor .
```

**Result:** Successful.

The image was built using `python:3.8-slim`, with Flask 2.2.5 and Werkzeug 2.2.3.

## 3. Flask Container Verification

Command:

```bash
docker run -d --name flask-security-test -p 5002:5000 flask-apparmor
```

**Result:** Container started successfully.

Command:

```bash
curl http://localhost:5002/
```

Observed output:

```text
Hello, this is a secure Flask application running inside a Docker container!
```

**Result:** Passed.

## 4. AppArmor Profile Inspection

Command:

```bash
docker inspect flask-security-test --format 'AppArmor Profile: {{.AppArmorProfile}}'
```

Observed output:

```text
AppArmor Profile:
```

Command:

```bash
docker inspect flask-security-test --format '{{json .HostConfig.SecurityOpt}}'
```

Observed output:

```text
null
```

**Result:** The baseline container did not report an active AppArmor profile or custom security options.

A separate container was started with the requested AppArmor option, but this did not establish that the profile was enforced.

## 5. Docker SDK Verification

Command:

```bash
python -c "import docker; client = docker.from_env(); print('Docker SDK connection:', client.ping()); print('Docker Engine:', client.version()['Version'])"
```

Observed output:

```text
Docker SDK connection: True
Docker Engine: 29.9.1
```

**Result:** Passed.

## 6. Apply AppArmor Using Python SDK

Command:

```bash
python apply_apparmor.py
```

Observed output:

```text
Building Flask Docker image...
Image built successfully.

Starting container with AppArmor profile...
Container started: a2bf1ed82570
Requested security options: ['apparmor=my-apparmor-profile']
Reported AppArmor profile:
Container stopped and removed.
```

**Result:** Docker SDK execution passed, but AppArmor enforcement was not verified.

## 7. Restricted Actions

Command:

```bash
python test_restricted_actions.py
```

Observed results:

| Action | Exit code | Outcome |
|---|---|---|
| Read `/etc/passwd` | 0 | Allowed |
| Execute `/bin/bash` | 0 | Allowed |

The shell test printed:

```text
bash-executed
```

**Result:** Both restricted actions succeeded. The custom AppArmor restrictions were not enforced in the tested environment.

## 8. Cleanup

Commands:

```bash
docker stop flask-security-test
docker rm flask-security-test
```

Both commands succeeded.

Final verification:

```bash
docker ps -a --filter "name=flask-security-test" --filter "name=flask-restriction-test" --filter "name=flask-apparmor-sdk-test"
```

**Observed result:** Only Docker table headers appeared; no matching containers remained.

**Result:** Passed.

## Final Summary

| Requirement | Status |
|---|---|
| Flask application created | Passed |
| Docker image built | Passed |
| Flask HTTP response verified | Passed |
| AppArmor profile file created | Completed |
| Docker SDK integration | Passed |
| AppArmor profile enforcement | Not verified |
| Restricted-action tests executed | Passed |
| Intended restrictions enforced | No |
| Cleanup | Passed |

## Conclusion

Exercise 5 demonstrated Flask containerization, Docker SDK security-option configuration, container inspection, restricted-action testing, and cleanup.

The requested AppArmor security option was recorded, but Docker did not report an active AppArmor profile. Both restricted actions succeeded. Actual AppArmor policy enforcement must be tested separately on a compatible Linux host.

## Supplementary local verification — 24 October 2026

The unchanged Dockerfile built successfully. Both `test_app.py` route tests passed, and the temporary Flask container returned HTTP 200 with the exact expected message. Docker again reported seccomp and cgroup namespaces without AppArmor; no local confinement result is claimed. The temporary test container was removed.

- [macOS host capability](evidence/macos-host.json)
- [Build output](evidence/local-build.txt)
- [Two passing unit tests](evidence/unit-tests.txt)
- [HTTP status and response](evidence/local-http.json)
- [Cleanup](evidence/local-cleanup.json)

## Original screenshot evidence

| PDF page | Screenshot |
| --- | --- |
| 1 | [No reported AppArmor support](evidence/macos-security-options.png) |
| 3 | [Built image](evidence/flask-image.png) |
| 5 | [Expected Flask response](evidence/flask-response.png) |
| 8 | [Docker SDK connected](evidence/docker-sdk-connection.png) |
| 10 | [Empty baseline AppArmor profile](evidence/baseline-profile.png) |
| 11 | [Baseline security options](evidence/baseline-security-options.png) |
| 15 | [Requested SDK option without active profile](evidence/sdk-profile-request.png) |
| 16 | [Restricted operations allowed on macOS](evidence/macos-restrictions-not-enforced.png) |
| 18 | [Container removal](evidence/containers-cleanup.png) |
| 19 | [No remaining lab containers](evidence/cleanup-confirmation.png) |

These genuine full-page captures are preserved unchanged. A separate Linux policy and Ubuntu workflow have been prepared for the missing enforcement checks; the result is pending the actual run and will be documented from its artifact.
