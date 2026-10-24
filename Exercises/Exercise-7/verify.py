"""Read-only checks of the existing Exercise 7 controller; never read passwords."""
import datetime, json, subprocess, urllib.request, urllib.error
import xml.etree.ElementTree as ET

def docker(*args):
    return subprocess.check_output(["docker", *args], text=True)
def status(path):
    try:
        with urllib.request.urlopen("http://localhost:8080" + path, timeout=10) as response:
            return response.status
    except urllib.error.HTTPError as error:
        return error.code
container = json.loads(docker("inspect", "--type", "container", "exercise7-jenkins"))[0]
config = ET.fromstring(docker("exec", "exercise7-jenkins", "cat", "/var/jenkins_home/config.xml"))
version = docker("exec", "exercise7-jenkins", "cat", "/var/jenkins_home/jenkins.install.InstallUtil.lastExecVersion").strip()
wizard = docker("exec", "exercise7-jenkins", "cat", "/var/jenkins_home/jenkins.install.UpgradeWizard.state").strip()
plugins = docker("exec", "exercise7-jenkins", "sh", "-c", "ls /var/jenkins_home/plugins/*.jpi").splitlines()
checks = {
    "container_running": container["State"]["Running"],
    "official_image": container["Config"]["Image"] == "jenkins/jenkins:lts",
    "persistent_volume": any(m.get("Name") == "jenkins_home" and m["Destination"] == "/var/jenkins_home" for m in container["Mounts"]),
    "login_http_200": status("/login") == 200,
    "anonymous_api_denied": status("/api/json") == 403,
    "security_enabled": config.findtext("useSecurity") == "true",
    "local_user_realm": config.find("securityRealm").get("class") == "hudson.security.HudsonPrivateSecurityRealm",
    "setup_version_recorded": bool(version) and wizard == version,
    "plugins_present": len(plugins) > 0,
}
print(json.dumps({"checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "jenkins_version": version, "plugin_count": len(plugins), "checks": checks, "all_passed": all(checks.values()), "limitations": ["No authenticated API check or restart test performed", "Screenshots separately demonstrate completed wizard and dashboard"]}, indent=2))
raise SystemExit(0 if all(checks.values()) else 1)
