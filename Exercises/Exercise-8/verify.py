"""Verify an existing local Jenkins build without changing the job or credentials.

Run: python3 verify.py [--build 1] [--save]
Requires Docker access and authenticated GitHub CLI for read-only public-source checks.
"""
import argparse, datetime, hashlib, json, re, subprocess
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
REPOSITORY = "https://github.com/nihal-toki/devops-sample-code.git"

def run(*args):
    return subprocess.check_output(args)

def controller_file(path):
    return run("docker", "exec", "exercise7-jenkins", "cat", path)

def xml(data):
    # Jenkins writes XML 1.1; these records use the XML 1.0 character subset.
    return ET.fromstring(data.replace(b"version='1.1'", b"version='1.0'"))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", type=int, default=1)
    parser.add_argument("--save", action="store_true", help="Save measured reports under evidence/")
    args = parser.parse_args()
    if args.build < 1:
        parser.error("build must be positive")
    base = "/var/jenkins_home/jobs/HelloWorld"
    config_bytes = controller_file(base + "/config.xml")
    config = xml(config_bytes)
    build_bytes = controller_file(base + f"/builds/{args.build}/build.xml")
    build = xml(build_bytes)
    raw_log = controller_file(base + f"/builds/{args.build}/log")
    # Remove Jenkins's encoded ConsoleNote metadata; preserve visible output.
    console = re.sub(rb"\x1b\[8mha:.*?\x1b\[0m", b"", raw_log, flags=re.S).decode("utf-8")
    revision = build.findtext(".//hudson.plugins.git.util.Build/marked/sha1")
    if not revision or not re.fullmatch("[0-9a-f]{40}", revision):
        raise RuntimeError("No valid checked-out revision in build record")
    source = run("gh", "api", f"repos/nihal-toki/devops-sample-code/contents/hello-world.sh?ref={revision}", "-H", "Accept: application/vnd.github.raw+json")
    local = (ROOT / "hello-world.sh").read_bytes()
    metadata = json.loads(run("gh", "api", "repos/nihal-toki/devops-sample-code"))
    local_output = run("bash", str(ROOT / "hello-world.sh")).decode()
    scm = config.find("scm")
    checks = {
        "freestyle_job": config.tag == "project",
        "git_repository_and_main_checkout": (
            scm is not None and scm.get("class") == "hudson.plugins.git.GitSCM"
            and scm.findtext(".//url") == REPOSITORY
            and scm.findtext(".//hudson.plugins.git.BranchSpec/name") == "*/main"
            and build.findtext(".//remoteUrls/string") == REPOSITORY
            and f"Checking out Revision {revision} (refs/remotes/origin/main)" in console
        ),
        "configured_and_executed_shell": (
            config.findtext("builders/hudson.tasks.Shell/command") == "sh hello-world.sh"
            and "+ sh hello-world.sh" in console
        ),
        "expected_console_and_local_output": "Hello, Jenkins!" in console.splitlines() and local_output == "Hello, Jenkins!\n",
        "completed_success": build.findtext("result") == "SUCCESS" and console.rstrip().endswith("Finished: SUCCESS"),
        "local_script_matches_built_public_source": local == source and not metadata["private"],
        "local_script_executable": bool((ROOT / "hello-world.sh").stat().st_mode & 0o111),
    }
    report = {
        "verified_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "job": "HelloWorld", "build_number": args.build,
        "build_started_at": datetime.datetime.fromtimestamp(int(build.findtext("timestamp"))/1000, datetime.timezone.utc).isoformat(),
        "result": build.findtext("result"), "duration_ms": int(build.findtext("duration")),
        "checked_out_revision": revision, "repository": REPOSITORY,
        "script_sha256": hashlib.sha256(local).hexdigest(),
        "checks": checks, "all_passed": all(checks.values()),
        "method": "Read-only saved Jenkins config/build/log via Docker; GitHub source at built revision; local Bash execution. No new build triggered.",
        "console_note": "Encoded Jenkins ConsoleNote metadata removed; visible console output retained.",
    }
    if args.save:
        if not all(checks.values()):
            raise RuntimeError("Verification failed; saved evidence was not overwritten")
        evidence = ROOT / "evidence"
        evidence.mkdir(exist_ok=True)
        (ROOT / "job.xml").write_bytes(config_bytes)
        (evidence / "build.xml").write_bytes(build_bytes)
        (evidence / "console.txt").write_text(console)
        (evidence / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
        (evidence / "local-execution.txt").write_text(local_output)
    print(json.dumps(report, indent=2))
    return 0 if all(checks.values()) else 1

if __name__ == "__main__":
    raise SystemExit(main())
