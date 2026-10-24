# Exercise 5 — Results and Verification

The original macOS run below did not enforce AppArmor. A separate successful Ubuntu workflow, recorded at the end, completes the enforcement requirement while preserving these observations.

## Overall completion

| Question-sheet task | Verified evidence | Status |
| --- | --- | --- |
| Create the Flask application | Preserved `app.py`; expected HTTP response and two passing route tests | Complete |
| Build the Docker image | Local build output and successful Linux SDK image build | Complete |
| Create and load an AppArmor policy | Separate Linux policy loaded; named profile and process enforce mode recorded | Complete on Ubuntu |
| Apply the profile through the Docker SDK | Successful Linux SDK run; Docker inspection and process profile agree | Complete on Ubuntu |
| Test restricted actions | Matched controls, denied file access/execution, allowed app write, kernel denial evidence | Complete on Ubuntu |
| Cleanup | Both Linux test containers removed; workflow profile unload passed | Complete |

The original task filenames remain present. Linux corrections are kept in `my-apparmor-profile-linux` and strict execution checks in `verify_linux.py` to preserve the owner's original files. The profile name remains `my-apparmor-profile`; its installed runner filename and temporary container names/host ports differ from the sheet. Direct Bash returned the measured 127 rather than the example 126. These adaptations are documented and do not remove the required checks.

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

## Original macOS run summary

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

## Original macOS outcome

Exercise 5 demonstrated Flask containerization, Docker SDK security-option configuration, container inspection, restricted-action testing, and cleanup.

The requested AppArmor security option was recorded, but Docker did not report an active AppArmor profile. Both restricted actions succeeded. Actual AppArmor enforcement was subsequently verified on Ubuntu, as recorded below.

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

These genuine full-page captures are preserved unchanged. The separate Linux policy and Ubuntu workflow completed the enforcement checks; their genuine downloaded artifact reports are linked below.


## Linux enforcement run — completed

[GitHub Actions run 40060739413](https://github.com/nihal-toki/DevOps-Lab/actions/runs/40060739413) passed on Ubuntu 24.04 using commit `bcd09b60f37b0fe44de038d6d800a45a1cc7c2db`. The Linux SDK verifier built the unchanged application image and started matched unconfined and confined containers.

Docker reported `my-apparmor-profile`, and the Python process reported `my-apparmor-profile (enforce)`. Flask returned HTTP 200 with the required message before and after the restriction tests. Both route tests passed under confinement.

| Operation | Unconfined exit code | Confined exit code | Confined result |
| --- | ---: | ---: | --- |
| Python reads `/etc/passwd` | 0 | 1 | Permission denied |
| Python writes `/var/lab-test` | 0 | 1 | Permission denied |
| Python spawns `/bin/bash` | 0 | 1 | Permission denied |
| Python spawns `/usr/bin/cat` | 0 | 1 | Permission denied |
| Direct `/bin/bash` | 0 | 127 | Loader blocked by denied `libtinfo` access |
| Direct `/bin/bash -c 'exit 0'` | 0 | 127 | Loader blocked by denied `libtinfo` access |
| Direct `/usr/bin/cat /etc/passwd` | 0 | 1 | Permission denied |

A write to `/app/allowed-test` succeeded with exit code 0. The kernel audit log records `apparmor="DENIED"`, `profile="my-apparmor-profile"` and the blocked Bash `libtinfo.so.6.4` read. Thus direct Bash failure is supported by real kernel evidence, not merely an assumed error message. The measured direct Bash exit code is 127; the sheet's sample 126 is not substituted.

The original `my-apparmor-profile`, `apply_apparmor.py` and `test_restricted_actions.py` remain unchanged as the owner's work. The separate `my-apparmor-profile-linux` includes Python/runtime mappings, the matching profile name, the socket allowances needed for Flask, the source's broader path restrictions and an explicit Bash-library denial. `verify_linux.py` performs strict positive and negative tests rather than relying only on requested Docker security options.

Cleanup removed both Linux test containers, with no owned containers left. The workflow's unload step succeeded. Local Minikube and the other exercises were not modified.

Downloaded original workflow artifacts:

- [Linux Docker capability](evidence/linux-host.json)
- [Loaded AppArmor status](evidence/linux-aa-status.txt)
- [Profile identity, enforce mode and HTTP](evidence/profile-application.json)
- [Controls, denied operations and direct exec](evidence/restricted-actions.json)
- [Kernel audit proof](evidence/apparmor-denials.log)
- [Two passing tests under confinement](evidence/linux-unit-tests.txt)
- [Linux container cleanup](evidence/linux-cleanup.json)
- [Run and artifact provenance](evidence/linux-workflow-run.json)

The first workflow attempt passed the SDK enforcement tests but failed the additional Bash kernel-log requirement because the audit log captured bytecode-cache write denials instead. The subsequent run disabled bytecode-cache writes in its disposable containers and spaced direct attempts; it passed the same assertions and the kernel-evidence check. The original failed run remains visible in GitHub history.

All required practical steps now have evidence: image build, Docker SDK operation, named profile loading, active enforce mode, denied restricted actions, allowed application behavior and cleanup. The macOS limitations remain recorded honestly alongside the successful Linux result.
