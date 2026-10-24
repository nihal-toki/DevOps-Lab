# Exercise 9: Jenkins Multi-Stage Pipeline — Results

## Objective

To execute and verify a Jenkins declarative CI/CD pipeline for a Python Flask application, covering the Build, Test, Deploy, Run Application, and Test Application stages.

## Execution Environment

| Component | Details |
|---|---|
| Operating System | macOS (Apple Silicon) |
| Jenkins | 2.580.1 |
| Jenkins Container | exercise7-jenkins |
| Python (Jenkins Container) | 3.13.5 |
| pip | 25.1.1 |
| Flask | 2.1.2 |
| Werkzeug | 2.1.2 |
| Jenkins Job | Python-MultiStage-Pipeline |
| Git Branch | main |

## Build #1 — Reported Failure (Record Not Retained)

**Reported status:** FAILURE

This history comes from the supplied notes. Jenkins currently retains only build #2, and the supplied screenshot PDF does not show the failed run. The failure and installation transcript below are not independently verified evidence.

The first Jenkins pipeline execution successfully retrieved the Jenkinsfile from GitHub but failed during the Build stage.

### Error

```text
python3: not found
ERROR: script returned exit code 127
Finished: FAILURE
```

### Root Cause

Python 3 was installed on the host Mac but was not available inside the Jenkins Docker container.

### Resolution

Entered the Jenkins container as root:

```bash
docker exec -it -u root exercise7-jenkins bash
```

Updated the package list and installed the required Python packages:

```bash
apt-get update
apt-get install -y python3 python3-pip python3-venv
```

Verified the installation:

```text
Python 3.13.5
pip 25.1.1
```

Python virtual environment support was also verified successfully.

## Build #2 — Successful

**Status:** SUCCESS

After installing Python inside the Jenkins container, the pipeline was executed again.

### Pipeline Stage Results

| Stage | Status | Observed Result |
|---|---|---|
| Build | PASS | Virtual environment created and dependencies installed |
| Test | PASS | One automated unit test passed |
| Deploy | PASS | Application copied to the deployment directory |
| Run Application | PASS | Flask application imported and URL routes displayed |
| Test Application | PASS | Root endpoint returned HTTP 200 and the expected response |

### Unit Test Output

```text
Ran 1 test in 0.010s

OK

Hello, Jenkins Multi-Stage Pipeline!
```

### Deployment Location

```text
/var/jenkins_home/workspace/Python-MultiStage-Pipeline/python-app-deploy/
```

The pipeline copied `app.py` into this directory.

### Application Validation

The deployed Flask application was imported successfully.

The registered routes included:

```text
/
 /static/<filename>
```

The final stage used Flask's test client to verify:

- HTTP status code: 200
- Expected response: `Hello, Jenkins Multi-Stage Pipeline!`

This validation was performed in-process; the pipeline did not launch a persistent HTTP server.

### Final Console Output

```text
Pipeline execution finished.
Pipeline completed successfully!
Finished: SUCCESS
```

## Issues Encountered and Resolved

| Issue | Resolution |
|---|---|
| Python unavailable inside Jenkins Docker | Installed Python 3, pip, and venv |
| Initial Build stage failure | Reran pipeline after installing Python |
| Remaining stages skipped in Build #1 | All required stages completed in Build #2 |

## Evidence

- Jenkins dashboard showing successful Build #2
- Jenkins Stages visualization with green checkmarks
- Actual Jenkins Build #2 console and saved build record captured during the audit
- Supplementary live HTTP response and process cleanup report

The three supplied screenshots show the dashboard, successful job page and green stage visualization. Console and Python-installation screenshots were not supplied. Build #1 and its installation transcript are not retained.

## Final Outcome

**Build/test/mock-deploy pipeline completed successfully.**

The Jenkins pipeline executed all five required stages and verified the deployed Flask application's expected response. Build #2 finished with `SUCCESS`.

Note: Python was installed directly into the running Jenkins container. A custom Jenkins Docker image would make the environment reproducible across container recreation.

## Independent Audit — 24 October 2026

Eight verification groups passed for genuine build #2, which checked out `0cd75b4ee6b9b054ec2d1a3a964139b652b17adb`. Saved configuration confirms Pipeline script from SCM, `*/main`, the separate sample repository and `python-flask-app/Jenkinsfile`. The successful console records all five stages, dependency installation, one passing test, file copying and in-process deployed-app checks. All four local application/pipeline files match that exact GitHub revision byte for byte.

The [supplementary HTTP report](evidence/http-response.json) independently records six passing checks: HTTP 200, exact response, deployed module identity, source/deployment hash equality, child process identity and process cleanup. This audit started a temporary real server inside the existing controller and stopped it afterward. It did not trigger another Jenkins build or rewrite the original pipeline.

**Remaining difference:** server startup and HTTP testing are outside the original Jenkins pipeline. Build #2's Run Application stage only imports Flask. Therefore this is not exact parity with the reference's pipeline-driven live server test. The README records this distinction and the source's conflicting deployment path instructions. The failed build #1 cannot be re-verified because its record is absent. No screenshot or result is invented to fill these gaps.

See the [README evidence table](README.md#evidence-and-verification) for all captured files.
