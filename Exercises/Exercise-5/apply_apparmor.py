
import docker
from docker.errors import APIError, DockerException

PROFILE = "my-apparmor-profile"
IMAGE = "flask-apparmor"

client = docker.from_env()

try:
    print("Building Flask Docker image...")
    client.images.build(path=".", tag=IMAGE, rm=True)
    print("Image built successfully.")

    print("\nStarting container with AppArmor profile...")

    container = client.containers.run(
        IMAGE,
        name="flask-apparmor-sdk-test",
        ports={"5000/tcp": 5003},
        security_opt=[f"apparmor={PROFILE}"],
        detach=True
    )

    print(f"Container started: {container.short_id}")

    info = client.api.inspect_container(container.id)

    print("Requested security options:",
          info["HostConfig"].get("SecurityOpt"))

    print("Reported AppArmor profile:",
          info.get("AppArmorProfile"))

    container.stop()
    container.remove()
    print("Container stopped and removed.")

except (APIError, DockerException) as error:
    print("\nDocker error:", error)
    print("AppArmor enforcement has NOT been verified.")
