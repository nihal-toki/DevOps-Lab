# Exercise 7 — Introduction to Continuous Integration (CI) and Jenkins Installation

## Aim

To understand Continuous Integration (CI) and successfully install and configure Jenkins using Docker.

## Objectives

- Understand the concept and benefits of Continuous Integration.
- Learn the basic architecture and components of Jenkins.
- Install Jenkins using Docker.
- Configure Jenkins plugins and administrator access.
- Verify that the Jenkins dashboard is accessible.

## Tools and Technologies

| Tool | Purpose |
|---|---|
| Docker Desktop | Run Jenkins in a container |
| Jenkins LTS | Continuous Integration automation server |
| PyCharm | Project documentation and terminal |
| Web Browser | Access the Jenkins dashboard |
| macOS | Host operating system |

## Introduction to Continuous Integration

Continuous Integration (CI) is a software development practice where developers frequently integrate code changes into a shared repository.

CI systems automatically build and test code to identify errors early.

### Benefits of CI

- Early detection of bugs
- Automated builds and testing
- Faster development cycles
- Improved collaboration
- Consistent software quality

### CI Workflow

1. Developer writes code.
2. Changes are pushed to a Git repository.
3. CI server detects changes.
4. Automated builds and tests execute.
5. Developers receive build results.

## Introduction to Jenkins

Jenkins is an open-source automation server used for Continuous Integration and Continuous Delivery.

### Key Jenkins Concepts

- **Job:** A task configured in Jenkins.
- **Build:** An execution of a job.
- **Pipeline:** A sequence of automated stages.
- **Plugin:** An extension that adds functionality.
- **Node/Agent:** A machine that executes Jenkins tasks.

## Jenkins Installation Using Docker

### Step 1 — Verify Docker

```bash
docker info --format '{{.ServerVersion}}'
```

Docker Engine version verified: `29.9.1`.

### Step 2 — Install Jenkins

```bash
docker run -d \
  --name exercise7-jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts
```

The container uses a persistent Docker volume to preserve Jenkins configuration.

### Step 3 — Verify Container

```bash
docker ps --filter "name=exercise7-jenkins"
```

Result: Jenkins container running successfully.

### Step 4 — Access Jenkins

Open:

`http://localhost:8080/`

The Jenkins Unlock screen appeared successfully.

### Step 5 — Retrieve Initial Administrator Password

```bash
docker exec exercise7-jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

The password was used locally to unlock Jenkins. It is intentionally excluded from documentation.

### Step 6 — Install Plugins

Selected **Install suggested plugins** and completed plugin installation.

### Step 7 — Create Administrator Account

Created an administrator account through the Jenkins setup wizard.

### Step 8 — Configure Jenkins URL

Configured the Jenkins instance URL as:

`http://localhost:8080/`

### Step 9 — Complete Installation

Jenkins displayed the **Jenkins is ready!** confirmation screen.

### Step 10 — Verify Dashboard

Successfully opened the Jenkins dashboard.

The dashboard displayed:

- New Item
- Build History
- Build Queue
- Build Executor Status
- Create a Job

## Verification Results

| Verification | Result |
|---|---|
| Docker Engine running | PASS |
| Jenkins image downloaded | PASS |
| Jenkins container running | PASS |
| Jenkins accessible on port 8080 | PASS |
| Administrator unlock | PASS |
| Suggested plugins installed | PASS |
| Administrator account created | PASS |
| Jenkins URL configured | PASS |
| Jenkins dashboard accessible | PASS |

## Conclusion

Jenkins was successfully installed and configured using Docker on macOS. The Jenkins dashboard is accessible through port 8080, and the installation is ready for future Continuous Integration exercises.

**Note:** Jenkins installation was verified. No automated CI pipeline or build was executed as part of this exercise.

## Evidence

The following are unchanged page renders from my supplied screenshot PDF:

| Evidence | File |
| --- | --- |
| jenkins installation | [Screenshot](evidence/jenkins-installation.png) |
| jenkins container | [Screenshot](evidence/jenkins-container.png) |
| jenkins unlock | [Screenshot](evidence/jenkins-unlock.png) |
| jenkins plugins | [Screenshot](evidence/jenkins-plugins.png) |
| jenkins admin form | [Screenshot](evidence/jenkins-admin-form.png) |
| jenkins instance url | [Screenshot](evidence/jenkins-instance-url.png) |
| jenkins ready | [Screenshot](evidence/jenkins-ready.png) |
| jenkins dashboard | [Screenshot](evidence/jenkins-dashboard.png) |

[Source provenance](evidence/installation.json) records the PDF hash and page mapping.
[Live verification](evidence/verification-installed.json) records nine read-only checks.

## Reproduce and compare with the reference

Compared with [the reference Exercise 7](https://github.com/Anas2694/DevOps-Lab/tree/main/Exercises/Exercise-7), this folder uses README, RESULTS, Compose and an evidence folder. `start.sh` and `verify.py` provide macOS equivalents of its Windows helper scripts. The documented manual wizard replaces its automated setup script. Ports 8080/50000 and the existing `jenkins_home` volume preserve my actual installation; the reference uses different host ports and a different volume name.

Run `sh start.sh` to reuse the existing container or create it if absent. The Compose file uses the existing external volume. Do not run another Jenkins instance on these same ports. Follow the wizard steps above for a fresh installation; no password is saved in this repository. Run `python3 verify.py` for read-only checks. Stop with `docker stop exercise7-jenkins`; this retains the volume.

The persistent mount is verified, but restart survival and authenticated API checks were not tested. The screenshots show the completed wizard and dashboard; the admin-form screenshot alone shows only an empty form. No password screenshot is needed. No build or pipeline execution is required by this installation exercise.
