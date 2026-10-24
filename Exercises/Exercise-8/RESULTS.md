# Exercise 8 — Results

## Experiment

Creating and Executing a Hello World Jenkins Job

## Aim

To configure a Jenkins Freestyle job that retrieves a Bash script from GitHub, executes it, and verifies successful execution.

## Environment

| Component | Details |
|---|---|
| Operating System | macOS |
| Jenkins Version | 2.580.1 |
| Jenkins Job | HelloWorld |
| Job Type | Freestyle Project |
| GitHub Repository | https://github.com/nihal-toki/devops-sample-code |
| Repository Branch | main |
| Script | hello-world.sh |
| Build Number | #1 |
| Build Status | SUCCESS |

## Execution Results

### 1. Shell Script Creation — PASS

Created `hello-world.sh` with the following content:

```bash
#!/bin/bash
echo "Hello, Jenkins!"
```

### 2. Local Execution — PASS

Made the script executable and ran it locally.

**Command:**

```bash
./hello-world.sh
```

**Output:**

```text
Hello, Jenkins!
```

### 3. GitHub Repository — PASS

Created the public GitHub repository `devops-sample-code` and uploaded `hello-world.sh` to its `main` branch.

### 4. Jenkins Job Configuration — PASS

Created the Jenkins Freestyle job `HelloWorld`.

Configured Source Code Management:

- Repository URL: `https://github.com/nihal-toki/devops-sample-code.git`
- Credentials: None
- Branch: `*/main`

### 5. Build Step Configuration — PASS

Added an **Execute shell** build step.

**Command:**

```bash
sh hello-world.sh
```

### 6. Jenkins Build Execution — PASS

Triggered build `#1` using **Build Now**.

Jenkins successfully cloned the GitHub repository, checked out the `main` branch, and executed the shell script.

### 7. Console Output Verification — PASS

The Jenkins console displayed:

```text
+ sh hello-world.sh
Hello, Jenkins!
Finished: SUCCESS
```

## Final Verification

| Test Case | Result |
|---|---|
| Bash script created | PASS |
| Local execution successful | PASS |
| GitHub repository created | PASS |
| Script uploaded to GitHub | PASS |
| Jenkins Freestyle job created | PASS |
| Git repository connected | PASS |
| Main branch checked out | PASS |
| Shell command executed | PASS |
| Expected output displayed | PASS |
| Jenkins build #1 successful | PASS |

## Final Result

**SUCCESS**

Jenkins successfully executed `hello-world.sh` from the GitHub repository and displayed `Hello, Jenkins!` in the console output.

## Conclusion

Exercise 8 was completed successfully. The experiment demonstrated Jenkins Freestyle job creation, GitHub integration, shell script execution, and verification of a successful build.

## Independent Verification

All seven verification groups passed on 24 October 2026. The saved Jenkins record and console independently confirm build #1 fetched `8f9793b69b53013b9ccb5de1cb07ec7717ee862c` from the sample repository's `main` branch, invoked `sh hello-world.sh`, printed the required greeting and finished SUCCESS. The local script matches that exact GitHub revision byte for byte and was executed again successfully during this audit. Its original bytes and executable permission were preserved.

See [verification.json](evidence/verification.json), [build.xml](evidence/build.xml), [console.txt](evidence/console.txt) and [job.xml](job.xml). Ten genuine screenshot pages are linked in the [README](README.md#saved-evidence-and-repeatable-verification). No required execution evidence is missing. No additional build, automatic trigger, webhook, or CI workflow run is claimed. Configuration and publication-method differences from the reference and question sheet are documented in the README.
