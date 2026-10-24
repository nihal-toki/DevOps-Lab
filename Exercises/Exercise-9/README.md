# Exercise 9: Jenkins Multi-Stage Pipeline for a Python Flask Application

## Objective

Create and execute a Jenkins CI/CD pipeline that automates building, testing, deploying, and validating a Python Flask application using a declarative Jenkinsfile.

## Tools and Technologies

- Jenkins
- Docker Desktop
- Python 3
- Flask
- Git and GitHub
- Python unittest
- PyCharm

## Project Structure

```text
python-flask-app/
├── app.py
├── requirements.txt
├── test_app.py
├── Jenkinsfile
├── pipeline_runtime.py
└── .gitignore
```

## Application Overview

The Flask application provides a root endpoint (`/`) that returns:

```text
Hello, Jenkins Multi-Stage Pipeline!
```

The application is tested using Python's built-in `unittest` framework and Flask's test client.

## Jenkins Pipeline Configuration

| Setting | Value |
|---|---|
| Job Name | Python-MultiStage-Pipeline |
| Job Type | Pipeline |
| Pipeline Definition | Pipeline script from SCM |
| SCM | Git |
| Repository | https://github.com/nihal-toki/devops-sample-code |
| Branch | main |
| Script Path | python-flask-app/Jenkinsfile |

## Pipeline Stages

### 1. Build

- Creates a Python virtual environment in the Jenkins workspace.
- Installs dependencies from `requirements.txt`.
- Uses Flask 2.1.2 and Werkzeug 2.1.2.

### 2. Test

- Executes automated unit tests using `unittest`.
- Verifies that the Flask application's root endpoint returns the expected response.

### 3. Deploy

- Creates a deployment directory within the Jenkins workspace.
- Copies `app.py` into that directory.

### 4. Run Application

- Starts a real temporary Werkzeug HTTP server from the copied `app.py`.
- Binds only to the controller's loopback interface on an OS-assigned free port.
- Records the deployed module, PID and process start time; disables debug/reload without modifying the Flask application.
- Uses a build-specific Jenkins process cookie so the server survives between stages.

### 5. Test Application

- Sends a real HTTP request to the server started by the preceding stage.
- Requires HTTP 200 and exactly `Hello, Jenkins Multi-Stage Pipeline!`.
- Checks process identity and deployed/source file hashes.

The `post` cleanup verifies process identity before stopping the server and removes its state file. Jenkins archives the HTTP report, cleanup report and real server log. Concurrent builds are disabled to protect the shared mock deployment directory. The Build stage also runs `pip check`.

## Execution Procedure

1. Start Docker Desktop and the Jenkins container.
2. Open Jenkins at `http://localhost:8080`.
3. Create or open the `Python-MultiStage-Pipeline` job.
4. Configure Git SCM and the Jenkinsfile script path.
5. Select **Build Now**.
6. Review the pipeline stages and console output.
7. Confirm successful completion of all stages.

## Troubleshooting

The supplied notes report that the initial pipeline execution failed because `python3` was unavailable inside the Jenkins Docker container. Build #1 is no longer retained, so this historical failure cannot be independently verified from Jenkins or the three supplied screenshot pages.

Python and the required tools were installed inside the running container using:

```bash
apt-get update
apt-get install -y python3 python3-pip python3-venv
```

After installation, Python 3.13.5, pip 25.1.1, and virtual environment support were verified.

The installation applies to the current container and is not guaranteed to persist if the container is recreated.

## Final Result

**Build #3: SUCCESS**

The updated Jenkins pipeline completed all five stages, passed the original unit test and dependency check, started the deployed HTTP server, verified its exact response, and cleaned it up. Fourteen independent audit checks passed. Build #2 remains documented as the earlier in-process implementation.

See `RESULTS.md` for execution evidence and detailed outcomes.

## Evidence and Verification

| Evidence | File |
| --- | --- |
| Jenkins dashboard | [Original screenshot page 1](evidence/01-dashboard.png) |
| Successful build #2 | [Original screenshot page 2](evidence/02-build-success.png) |
| Green pipeline stages | [Original screenshot page 3](evidence/03-pipeline-stages.png) |
| Saved Pipeline-from-SCM configuration | [job.xml](job.xml) |
| Historical build #2 record | [build.xml](evidence/build.xml) |
| Historical build #2 console | [console.txt](evidence/console.txt) |
| Historical build #2 audit | [verification.json](evidence/verification.json) |
| Historical standalone HTTP audit | [http-response.json](evidence/http-response.json) |
| Screenshot source hash and page mapping | [source-provenance.json](evidence/source-provenance.json) |

Run `python3 verify.py --build 3` from this folder to audit the completed HTTP pipeline and compare all five application/pipeline files with its exact built GitHub revision. Docker and GitHub CLI read access are required. Use `--save` only when intentionally refreshing that build’s reports. The audit is read-only: it reads the saved build, console and archived reports without starting a server or triggering a build. Loopback URLs refer to the controller, not a host-published application endpoint; the tested server is stopped after each build.

The original application, test and dependency list are preserved. The Jenkinsfile now invokes `pipeline_runtime.py` in the runtime stages and post-build cleanup. The saved console has only Jenkins's encoded ConsoleNote metadata removed; visible output is retained. The supplied PDF has three screenshot pages; it does not contain console or Python-installation screenshots. Real console and build records supplement it instead. The three supplied screenshot pages remain unchanged. The new build #3 screenshots below are genuine captures of the completed Jenkins run.

## Comparison with the Question Sheet and Reference

Compared with [the reference Exercise 9](https://github.com/Anas2694/DevOps-Lab/tree/main/Exercises/Exercise-9), this submission uses README/RESULTS, application files, an exported job XML and an evidence folder. My application remains under `python-flask-app/` and in the separate sample repository, matching the question sheet's layout; the reference flattens those files into its exercise folder and uses its lab repository. My job reuses Exercise 7's controller at port 8080. The reference uses a dedicated controller at 18009 and a custom image. My manually installed Python environment will need reinstallation if the controller is recreated.

My Build stage actually installs dependencies and pins compatible Werkzeug, correcting the sheet's echo-only Build example. The copy destination follows the sheet's Jenkinsfile workspace path, rather than its contradictory `/tmp` prose. Historical build #2 imported and validated the app in-process. The updated build #3 now starts the deployed server, tests it over HTTP inside Jenkins and performs explicit cleanup, matching the runtime requirement demonstrated in the reference. The separate earlier HTTP audit is retained as historical evidence; it is not substituted for build #3’s archived pipeline reports. Only one source unit test is present; the reference adds a second test. Additional lint, Docker deployment, notifications and a GitHub Actions repetition are not required by the core exercise and are not claimed.

## Completed HTTP Pipeline — Build #3

Build #3 fetched source commit `a202a55a742af6ca469a0e54bdb69b05740485ca` from the sample repository and completed SUCCESS. All 14 audit checks passed. The source update changed only the Jenkinsfile and added the runtime helper; the application, unit test and requirements were not changed.

- [Actual build #3 record](evidence/jenkins-build-3.xml)
- [Actual build #3 console](evidence/jenkins-console-build-3.txt)
- [Jenkins-archived HTTP measurement](evidence/jenkins-http-build-3.json)
- [Jenkins-archived process cleanup](evidence/jenkins-cleanup-build-3.json)
- [Actual server access log](evidence/jenkins-app-build-3.log)
- [Fourteen-check verification](evidence/pipeline-verification.json)
- [Successful build screenshot](evidence/build-3-success.png)
- [Successful stage screenshot](evidence/build-3-stages.png)

The helper imports the copied Flask module and serves it using Werkzeug with debug/reloading disabled. This follows the lab's development-server intent without editing the app or leaving a server running. The process log contains the real HTTP request. Cleanup signals only the recorded process after verifying its command and Linux start time; it refuses an unrelated reused PID. Stage completion is observed from the successful real console and UI; no stage REST API measurement is claimed.
