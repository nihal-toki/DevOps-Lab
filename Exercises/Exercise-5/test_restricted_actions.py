
import docker
from docker.errors import DockerException

client = docker.from_env()
container = None

try:
    container = client.containers.run(
        "flask-apparmor",
        name="flask-restriction-test",
        security_opt=["apparmor=my-apparmor-profile"],
        detach=True
    )

    print("Container started:", container.short_id)

    info = client.api.inspect_container(container.id)
    print("Reported AppArmor profile:",
          info.get("AppArmorProfile") or "(none)")

    tests = [
        ("Read /etc/passwd", ["cat", "/etc/passwd"]),
        ("Execute /bin/bash", ["/bin/bash", "-c", "echo bash-executed"])
    ]

    for description, command in tests:
        result = container.exec_run(command)
        print(f"\nTest: {description}")
        print("Exit code:", result.exit_code)
        print("Output:", result.output.decode(errors="replace"))

except DockerException as error:
    print("Docker error:", error)

finally:
    if container is not None:
        container.stop()
        container.remove()
        print("\nContainer stopped and removed.")
