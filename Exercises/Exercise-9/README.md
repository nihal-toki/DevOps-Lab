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

- Imports the deployed Flask application.
- Prints and verifies the registered Flask URL routes.
- This stage does not start a persistent HTTP server.

### 5. Test Application

- Uses Flask's test client against the deployed application.
- Checks that the root endpoint returns HTTP status `200`.
- Verifies the response text.

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

**Build #2: SUCCESS**

The Jenkins pipeline successfully completed all five stages. One unit test passed, and the deployed Flask application returned the expected response during in-process validation.

See `RESULTS.md` for execution evidence and detailed outcomes.

## Evidence and Verification

| Evidence | File |
| --- | --- |
| Jenkins dashboard | [Original screenshot page 1](evidence/01-dashboard.png) |
| Successful build #2 | [Original screenshot page 2](evidence/02-build-success.png) |
| Green pipeline stages | [Original screenshot page 3](evidence/03-pipeline-stages.png) |
| Saved Pipeline-from-SCM configuration | [job.xml](job.xml) |
| Actual build #2 record | [build.xml](evidence/build.xml) |
| Actual build #2 console | [console.txt](evidence/console.txt) |
| Eight measured audit checks | [verification.json](evidence/verification.json) |
| Supplementary HTTP and process cleanup | [http-response.json](evidence/http-response.json) |
| Screenshot source hash and page mapping | [source-provenance.json](evidence/source-provenance.json) |

Run `python3 verify.py` from this folder to check the existing build and compare application files with the exact built GitHub revision. Docker and GitHub CLI read access are required. Run `python3 verify.py --http` to additionally start a temporary Werkzeug server from the deployed file inside Jenkins, request its OS-assigned loopback port, verify the response and stop it. Use `--save` only when intentionally refreshing the reports. No credentials are read and no job configuration or build is changed. Loopback here means inside the controller, not a host-published application URL.

The original application, test, dependency list and Jenkinsfile are preserved. The saved console has only Jenkins's encoded ConsoleNote metadata removed; visible output is retained. The supplied PDF has three screenshot pages; it does not contain console or Python-installation screenshots. Real console and build records supplement it instead. No screenshots were generated or altered.

## Comparison with the Question Sheet and Reference

Compared with [the reference Exercise 9](https://github.com/Anas2694/DevOps-Lab/tree/main/Exercises/Exercise-9), this submission uses README/RESULTS, application files, an exported job XML and an evidence folder. My application remains under `python-flask-app/` and in the separate sample repository, matching the question sheet's layout; the reference flattens those files into its exercise folder and uses its lab repository. My job reuses Exercise 7's controller at port 8080. The reference uses a dedicated controller at 18009 and a custom image. My manually installed Python environment will need reinstallation if the controller is recreated.

My Build stage actually installs dependencies and pins compatible Werkzeug, correcting the sheet's echo-only Build example. The copy destination follows the sheet's Jenkinsfile workspace path, rather than its contradictory `/tmp` prose. My successful pipeline imports and validates the deployed app in-process. The sheet's Run Application stage and my friend's implementation instead start a server. The separate live HTTP audit closes the missing runtime evidence, but does not change what build #2 did: server startup and HTTP verification remain outside my original Jenkins pipeline. Exact parity with that part of the reference would require updating and rerunning the Jenkinsfile. Only one source unit test is present; the reference adds a second test. Additional lint, Docker deployment, notifications and a GitHub Actions repetition are not required by the core exercise and are not claimed.
