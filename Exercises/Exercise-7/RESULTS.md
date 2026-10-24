# Exercise 7 — Results

## Aim

To install, configure, and verify Jenkins using Docker on macOS.

## Environment

| Component | Details |
|---|---|
| Operating System | macOS |
| Docker Engine | 29.9.1 |
| Jenkins Version | 2.580.1 |
| Jenkins Image | jenkins/jenkins:lts |
| Container Name | exercise7-jenkins |
| Jenkins URL | http://localhost:8080/ |
| Persistent Storage | jenkins_home Docker volume |

## Installation Results

### 1. Docker Verification — PASS

Docker Engine was verified to be running successfully.

### 2. Jenkins Container Installation — PASS

The Jenkins LTS Docker image was downloaded and the container was started successfully.

### 3. Container Status — PASS

The `exercise7-jenkins` container was confirmed to be running, with port 8080 exposed.

### 4. Jenkins Unlock — PASS

The initial administrator password was retrieved from the container and used to unlock Jenkins.

The password is excluded from this report for security reasons.

### 5. Plugin Installation — PASS

The suggested Jenkins plugins were installed successfully.

### 6. Administrator Account — PASS

An administrator account was created using the Jenkins setup wizard.

### 7. Instance Configuration — PASS

The Jenkins instance URL was configured as `http://localhost:8080/`.

### 8. Jenkins Dashboard — PASS

The Jenkins dashboard was opened successfully and displayed the available job management and build options.

## Final Verification

| Test | Status |
|---|---|
| Docker running | PASS |
| Jenkins image downloaded | PASS |
| Jenkins container running | PASS |
| Jenkins accessible on port 8080 | PASS |
| Jenkins unlocked | PASS |
| Suggested plugins installed | PASS |
| Administrator account created | PASS |
| Jenkins instance configured | PASS |
| Dashboard accessible | PASS |
| Automated CI pipeline executed | NOT TESTED |

## Conclusion

Jenkins was successfully installed and configured using Docker. The Jenkins dashboard is accessible and ready for future Continuous Integration exercises.

This exercise covered Jenkins installation and initial setup; no CI pipeline was created or executed.

## Independent live checks

On 24 October 2026, all nine checks in [verification-installed.json](evidence/verification-installed.json) passed: running official-image container, persistent volume mount, login HTTP 200, anonymous API HTTP 403, enabled security, local-user realm, matching setup version records, and installed plugin presence (92 plugin archives). Setup version: 2.580.1. Plugin presence does not independently prove every suggested plugin is active; the wizard completion and dashboard screenshots provide the installation evidence.

See [README evidence links](README.md#evidence) for eight original screenshot pages and source provenance. Unlike the reference, no restart or authenticated API verification is claimed. No required installation screenshot is missing. The initial password is deliberately excluded. CI job execution belongs to later exercises.
