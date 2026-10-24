# Exercise 5 — Docker Security with AppArmor and Python

## Objective

Understand Docker container security using AppArmor profiles, Python Flask, and the Docker SDK for Python.

## Environment

- Operating system: macOS (Apple Silicon)
- Container platform: Docker Desktop
- Docker Engine: 29.9.1
- Python virtual environment: Python 3.9.6
- Docker SDK for Python: 7.2.0
- Application: Python Flask

## Tasks Performed

### Task 1 — Create Flask Application

Created `app.py`, a simple Flask application that returns:

`Hello, this is a secure Flask application running inside a Docker container!`

### Task 2 — Containerize Flask

Created a Dockerfile and built the application image using:

`docker build -t flask-apparmor .`

The image built successfully.

Ran the Flask container using host port 5002 mapped to container port 5000.

Verified the application with:

`curl http://localhost:5002/`

The expected message was returned.

### Task 3 — Create AppArmor Profile

Created `my-apparmor-profile` to define restrictions on sensitive files, shell execution, and administrative capabilities.

The profile was not loaded into an AppArmor-enabled Linux host. Docker Desktop did not report AppArmor support.

### Task 4 — Docker SDK for Python

Installed the Docker SDK in a Python virtual environment.

Created and executed `apply_apparmor.py`.

The script successfully built the Docker image, started a container with the requested AppArmor security option, inspected its configuration, and removed the temporary container.

Docker recorded the requested option but did not report an active AppArmor profile.

### Task 5 — Test Restricted Actions

Created and executed `test_restricted_actions.py`.

Observed results:

| Test | Exit Code | Result |
|---|---|---|
| Read `/etc/passwd` | 0 | Allowed |
| Execute `/bin/bash` | 0 | Allowed |

The intended restrictions were not enforced in the tested environment.

### Cleanup

Stopped and removed the Flask container and verified that no Exercise 5 test containers remained.

## Assignment Questions and Answers

**1. What is the purpose of using AppArmor with Docker containers?**

AppArmor provides mandatory access control policies that restrict what containerized applications can access or execute, reducing the potential impact of a compromised application.

**2. How do AppArmor profiles help secure a Docker container?**

Profiles define permissions for file access, program execution, network operations, and certain Linux capabilities. The Linux kernel enforces these rules when AppArmor is active and the profile is correctly applied.

**3. Why restrict access to sensitive directories such as `/etc/` and `/var/`?**

These directories may contain configuration files, account information, logs, and application data. Restricting unnecessary access reduces information exposure and unauthorized modification.

**4. What other capabilities can AppArmor restrict?**

AppArmor can restrict executable access, filesystem operations, networking, and privileged capabilities such as `CAP_SYS_ADMIN`, subject to the supported policy rules and kernel configuration.

**5. How can you verify whether an AppArmor profile is applied?**

Inspect Docker's `AppArmorProfile` field, examine the relevant Linux kernel security state, and perform positive and negative tests that confirm the expected operations are allowed or denied.

## Conclusion

The Flask containerization, Docker SDK integration, connectivity tests, restricted-action test execution, and cleanup were completed successfully.

AppArmor enforcement was not demonstrated because the tested Docker Desktop environment did not report an active AppArmor profile. The original macOS run could not verify enforcement. The separate successful Ubuntu run below now completes that requirement.

## Repeat local checks

With Docker Desktop running, use `python3 verify_local.py` from this folder. It builds the unchanged image with a unique tag, runs both route tests, verifies the HTTP response on a temporary localhost port and removes its test container. It records Docker's AppArmor capability separately; route tests alone do not demonstrate confinement.

## Linux enforcement verification

The original `app.py`, Dockerfile, `apply_apparmor.py`, `test_restricted_actions.py` and `my-apparmor-profile` are preserved. The original scripts report observations but do not assert that enforcement occurred. Use the separate `verify_linux.py` for an enforcing test on a supported Linux Docker host.

The GitHub workflow `.github/workflows/exercise-5.yml` uses Ubuntu 24.04. It installs the Docker SDK, loads `my-apparmor-profile-linux`, runs the SDK-based verification, requires kernel denial evidence and unloads only the lab policy. It refuses to replace an existing named profile. Reports are uploaded as the `exercise5-linux-evidence` artifact.

The Linux policy declares the matching profile name, allows Python and shared-library mappings, permits the datagram socket Werkzeug needs during startup, and permits writes in `/app`. It retains denials for `/etc`, `/var`, shell/binary execution and `sys_admin`. It explicitly denies Bash's `libtinfo` library so direct Docker exec cannot start Bash through its loader. This separate corrected policy is used for Linux testing; the original macOS draft is not replaced.

`verify_linux.py` uses the Docker SDK to build the same app image, starts matched unconfined and confined containers, requires Docker's profile field and `/proc/self/attr/current` to report the named profile in enforce mode, and checks HTTP before and after restriction tests. Direct Python file reads are tested separately from `cat` execution, preventing an execution denial from being mistaken for a file-read denial. It requires `/etc/passwd` reads, `/var` writes and Python-spawned Bash/cat to fail while the same operations succeed in the control. Direct Docker exec of Bash and cat must also fail; an `/app` write and both Flask route tests must pass. Test containers are removed in a `finally` block.

The broad network rules do not filter specifically to port 5000. This is a lab confinement policy, not protection against an administrator controlling the Docker daemon. Loading, inspecting and auditing the profile follows [Docker's AppArmor guidance](https://docs.docker.com/engine/security/apparmor/).

Linux enforcement passed in [GitHub Actions run 40060739413](https://github.com/nihal-toki/DevOps-Lab/actions/runs/40060739413), testing commit `bcd09b6`. The genuine artifact reports are saved in `evidence/`. No Linux result is inferred from the macOS screenshots.

## Evidence organization

Saved local reports: [host capability](evidence/macos-host.json), [build](evidence/local-build.txt), [two passing tests](evidence/unit-tests.txt), [HTTP response](evidence/local-http.json), and [cleanup](evidence/local-cleanup.json).

The ten screenshots in `evidence/` are unchanged page captures of the supplied `Exercise_5_Screenshots.pdf`, preserving the actual local observations. Source pages 1, 3, 5, 8, 10, 11, 15, 16, 18 and 19 cover capability, image, response, SDK connection, baseline inspection, requested profile, allowed restricted actions and cleanup. None is presented as Linux enforcement evidence.


## Completion status

The local build, HTTP and unit tests passed. On Ubuntu 24.04 the named profile was confirmed in enforce mode, all four negative operations were denied while the unconfined controls succeeded, direct Bash/cat attempts failed, `/app` writes remained allowed, and Flask returned HTTP 200 before and after testing. Both containers were removed and the workflow unloaded the profile.

[RESULTS.md](RESULTS.md) records the observed exit codes and the kernel audit evidence. The first workflow attempt passed the enforcement checks but lacked the required Bash audit entry after bytecode-cache denials filled the audit burst. Disabling bytecode writes in disposable containers and spacing direct tests produced the fully successful rerun without relaxing assertions.
