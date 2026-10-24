# Exercise 4: Docker Networking

Run Flask, MySQL and Redis on a user-defined bridge network. The `/about` route returns API metadata on container port 5001; the application does not query MySQL or use Redis caching. Network and server connectivity are tested separately.

## Build and run

The original macOS run built `flask-api:latest`, created `my-bridge-net`, and launched containers named `flask`, `mysql` and `redis`. Flask published host port 5001; MySQL 8.4 and Redis 7 were reachable internally. The original containers and network were removed at the end of the exercise.

To repeat the full lab with Docker Desktop running, from this folder use:

```sh
python3 verify.py
```

This builds the unchanged Dockerfile under a unique temporary image tag, tests a standalone Flask container, creates a temporary bridge network and starts the three containers. Network aliases `mysql`, `redis` and `flask` retain Docker DNS names while unique container names avoid collisions with other work.

The MySQL root password is generated for the temporary database and supplied through an ephemeral environment file. It is not printed or saved as evidence. Flask binds a dynamically allocated localhost host port to container port 5001; MySQL and Redis publish no host ports. The printed port is captured in `evidence/verification.json`.

## Inspect and test

The repeatable script verifies:

- Standalone and networked `/about` responses return HTTP 200 with the exact expected JSON.
- All three containers are running and connected to the bridge.
- From Flask, Docker DNS resolves MySQL and Redis to their network addresses.
- Both servers accept TCP connections; MySQL sends a protocol-10 handshake.
- Three ICMP pings to each server succeed with zero packet loss.
- Redis answers `PING` with `PONG`, both through its protocol and `redis-cli`.
- An authenticated MySQL query returns its version and database list, including the temporary `devopsdb`.
- Three Flask tests pass: `/about`, unknown-route 404 and POST rejection.

The ping utility is installed only inside the disposable Flask container for diagnostics. The project Dockerfile and application remain unchanged. Repeat verification needs network access to the package repository and enough resources for MySQL; images may be pulled if absent.

`verify_network.py` performs the container-side DNS, ping and server tests. `test_app.py` uses Flask's test client. `verify.py` runs both in the temporary application container and saves measured output under `evidence/`. Evidence files from the supplementary run are updated when repeating the script.

Expected response:

```json
{"description":"This is a simple REST API built with Flask.","name":"Simple REST API","version":"1.0"}
```

The original host URL was `http://localhost:5001/about`. The supplementary run uses a different free localhost port, recorded in the verification report. Addresses, ports and IDs are specific to each run.

## Clean up

`verify.py` removes its temporary containers and their disposable volumes, then its temporary network, even when a check fails. It records cleanup and verifies previously existing networks remain. Images are retained; no global prune is performed.

## Lab questions

1. `--net`/`--network` selects the container's Docker network.
2. Containers on a user-defined bridge communicate through their internal addresses and Docker DNS names or aliases.
3. Bridge networking gives containers separate network namespaces on a virtual network. Host networking shares the host network namespace instead; Docker Desktop support depends on its configuration.
4. `-p HOST_PORT:CONTAINER_PORT` publishes a port, for example `-p 5001:5001`. `EXPOSE` alone does not publish it.

## Implementation differences

The app binds to `0.0.0.0`, allowing published-port access, with debug mode disabled. Werkzeug 2.0.3 is pinned alongside Flask 2.0.1 for compatibility. The original run uses `mysql:8.4` and `redis:7` instead of unpinned `latest` images. MySQL receives initialization credentials rather than the incomplete launch command in the question sheet.

The supplementary run uses unique names, network aliases and a dynamic localhost port while preserving the original code and files. Python scripts provide the macOS verification workflow instead of the reference repository's PowerShell orchestration. Python 3.9, these dependency versions and the Flask development server are retained for the lab.

See [RESULTS.md](RESULTS.md) for the original screenshot evidence and the supplementary measured run.
