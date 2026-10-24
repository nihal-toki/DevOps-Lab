# Exercise 8 — Creating a Hello World Jenkins Job

## Aim

To create and execute a Jenkins Freestyle job that retrieves a shell script from a GitHub repository and displays `Hello, Jenkins!` in the Jenkins console output.

## Objectives

- Create and test a Bash shell script.
- Create a public GitHub repository.
- Upload the script to GitHub.
- Configure a Jenkins Freestyle project.
- Connect Jenkins to a GitHub repository using Git.
- Execute the script through Jenkins.
- Verify successful execution using the console output.

## Tools and Technologies

| Tool | Purpose |
|---|---|
| Jenkins | CI automation server |
| Docker Desktop | Runs the Jenkins container |
| GitHub | Hosts the shell script |
| Git | Retrieves source code from GitHub |
| Bash | Executes the shell script |
| PyCharm | Creates and edits project files |
| macOS | Local development environment |

## Project Details

| Property | Value |
|---|---|
| Jenkins Job | `HelloWorld` |
| Job Type | Freestyle project |
| GitHub Repository | https://github.com/nihal-toki/devops-sample-code |
| Repository Visibility | Public |
| Git Branch | `main` |
| Shell Script | `hello-world.sh` |
| Jenkins URL | http://localhost:8080/ |
| Build Number | `#1` |
| Build Result | SUCCESS |

## Introduction

Jenkins is an open-source automation server used in Continuous Integration and Continuous Delivery (CI/CD).

A Jenkins Freestyle project allows users to configure automated tasks such as downloading source code, executing scripts, compiling applications, and running tests.

In this exercise, Jenkins retrieves a Bash script from GitHub and executes it using a shell build step.

## Procedure

### Step 1 — Create the Shell Script

Created a file named `hello-world.sh` inside the `Exercise-8` directory.

```bash
#!/bin/bash
echo "Hello, Jenkins!"
```

### Step 2 — Make the Script Executable

Executed:

```bash
chmod +x hello-world.sh
```

### Step 3 — Test the Script Locally

Executed:

```bash
./hello-world.sh
```

Output:

```text
Hello, Jenkins!
```

The script executed successfully on macOS.

### Step 4 — Create a GitHub Repository

Created a public GitHub repository named `devops-sample-code`.

Repository URL:

https://github.com/nihal-toki/devops-sample-code

Uploaded `hello-world.sh` to the repository's `main` branch using the GitHub web interface.

### Step 5 — Access Jenkins

Opened the Jenkins dashboard:

http://localhost:8080/

Jenkins was running inside the Docker container configured during Exercise 7.

### Step 6 — Create a Jenkins Freestyle Job

Selected **New Item** from the Jenkins dashboard.

Configured:

- Job name: `HelloWorld`
- Project type: Freestyle project
- Description: `Hello World! Jenkins job.`

### Step 7 — Configure Source Code Management

Selected **Git** under Source Code Management.

Repository URL:

```text
https://github.com/nihal-toki/devops-sample-code.git
```

Credentials:

```text
- none -
```

Branch specifier:

```text
*/main
```

Because the GitHub repository is public, no authentication credentials were required for cloning.

### Step 8 — Configure Build Steps

Under **Build Steps**, selected **Add build step → Execute shell**.

Entered:

```bash
sh hello-world.sh
```

Saved the Jenkins job configuration.

### Step 9 — Execute the Jenkins Job

Opened the `HelloWorld` job and selected **Build Now**.

Jenkins started build `#1`.

### Step 10 — Verify Console Output

Opened **Build #1 → Console Output**.

The console confirmed that Jenkins cloned the GitHub repository, checked out the `main` branch, and executed the shell script.

Relevant output:

```text
+ sh hello-world.sh
Hello, Jenkins!
Finished: SUCCESS
```

## Results

| Test | Status |
|---|---|
| Shell script created | PASS |
| Script executable locally | PASS |
| Local script execution | PASS |
| GitHub repository created | PASS |
| Script uploaded to GitHub | PASS |
| Jenkins Freestyle job created | PASS |
| Git repository configured | PASS |
| Main branch checked out | PASS |
| Shell build step executed | PASS |
| Console displayed `Hello, Jenkins!` | PASS |
| Jenkins build #1 completed successfully | PASS |

## Screenshots

The Exercise 8 screenshots PDF contains evidence of:

1. Successful local execution of the Bash script.
2. GitHub repository and uploaded script.
3. Jenkins Freestyle job configuration.
4. Git repository URL and branch settings.
5. Execute shell build step.
6. Successful Jenkins build.
7. Jenkins console output showing the Git checkout and script execution.

## Conclusion

Successfully created and executed a Jenkins Freestyle job named `HelloWorld`.

Jenkins retrieved `hello-world.sh` from the public GitHub repository, executed the Bash script, displayed `Hello, Jenkins!`, and completed build `#1` with a **SUCCESS** status.

This exercise demonstrated basic Jenkins job configuration, Git integration, shell script execution, and build verification.

## Saved Evidence and Repeatable Verification

| Evidence | File |
| --- | --- |
| local execution | [Screenshot](evidence/01-local-execution.png) |
| github repository | [Screenshot](evidence/02-github-repository.png) |
| script upload | [Screenshot](evidence/03-script-upload.png) |
| script committed | [Screenshot](evidence/04-script-committed.png) |
| job configuration | [Screenshot](evidence/05-job-configuration.png) |
| git configuration | [Screenshot](evidence/06-git-configuration.png) |
| shell build step | [Screenshot](evidence/07-shell-build-step.png) |
| build success | [Screenshot](evidence/08-build-success.png) |
| console checkout | [Screenshot](evidence/09-console-checkout.png) |
| console success | [Screenshot](evidence/10-console-success.png) |

- [Actual job configuration](job.xml)
- [Actual Jenkins build record](evidence/build.xml)
- [Console output](evidence/console.txt)
- [Measured verification](evidence/verification.json)
- [Local execution output](evidence/local-execution.txt)
- [PDF provenance and reference revision](evidence/source-provenance.json)

From this folder, run `python3 verify.py` to check the existing build without changing Jenkins. Docker access and GitHub CLI access are required. Use `--save` only when intentionally refreshing the evidence. The verifier checks seven groups: Freestyle job type, Git repository/main checkout, configured and executed shell, expected output, completed SUCCESS, local script matching the public source at the built revision, and local execute permission. It removes encoded Jenkins ConsoleNote metadata from the saved log without changing visible output. No new Jenkins build was triggered by the audit.

To repeat the job, open `http://localhost:8080/job/HelloWorld/`, choose **Build Now**, then inspect the new build's console. Run `python3 verify.py --build NUMBER` to check that build. `job.xml` exports my existing configuration for reference; it does not replace or reconfigure the live job.

## Reference and Question-Sheet Comparison

Compared with [my friend's Exercise 8](https://github.com/Anas2694/DevOps-Lab/tree/main/Exercises/Exercise-8), this folder follows the same README/RESULTS, shell script, job XML and evidence organization. My `verify.py` is a read-only macOS-compatible alternative to the verification part of the reference's Windows job runner. Job creation and triggering remain the manual workflow above. No automated runner or GitHub Actions repetition is claimed.

My friend keeps the script in the lab repository and runs its nested path. I followed the question sheet's separate public `devops-sample-code` repository and run `sh hello-world.sh`. My Jenkins URL uses port 8080; the reference uses 18007. These are intentional configuration differences, not missing lab steps. Existing authenticated GitHub tooling was used; no new personal access token was required or stored. Upload through GitHub's web interface replaces the sheet's local Git push procedure; both publish the script. Build #1 is the genuine user-run build, not the reference's build #3.
