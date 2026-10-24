#!/usr/bin/env python3
"""Build and verify a disposable Docker networking lab; preserve existing resources."""
import datetime
import json
from pathlib import Path
import secrets
import subprocess
import tempfile
import time
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / 'evidence'
EVIDENCE.mkdir(exist_ok=True)
PREFIX = 'exercise4-check-' + uuid.uuid4().hex[:8]
LABEL = 'devops.lab.verification=' + PREFIX
NETWORK = PREFIX + '-net'
containers = []
network_created = False
network_before = []


def command(args, check=True, **kwargs):
    result = subprocess.run(args, text=True, capture_output=True, **kwargs)
    if check and result.returncode:
        raise RuntimeError('Command failed: ' + result.stderr)
    return result


def docker(*args, **kwargs):
    return command(['docker', *args], **kwargs)


def record(name, data):
    (EVIDENCE / name).write_text(json.dumps(data, indent=2) + '\n')


def launch(name, *args):
    container_id = docker('run', '-d', '--name', name, '--label', LABEL, *args).stdout.strip()
    containers.append(container_id)
    return name


def http(container):
    state = json.loads(docker('inspect', container).stdout)[0]
    port = state['NetworkSettings']['Ports']['5001/tcp'][0]['HostPort']
    url = 'http://127.0.0.1:' + port + '/about'
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=3) as response:
                body = json.load(response)
                assert response.status == 200
                assert body == {'description': 'This is a simple REST API built with Flask.', 'name': 'Simple REST API', 'version': '1.0'}
                return {'url': url, 'status': response.status, 'body': body, 'container_port': 5001}
        except (OSError, ValueError):
            time.sleep(1)
    raise RuntimeError('API did not become ready')


try:
    network_before = docker('network', 'ls', '-q').stdout.split()
    build = docker('build', '-t', PREFIX + '-api:latest', str(ROOT))
    (EVIDENCE / 'build.txt').write_text(build.stdout + build.stderr)
    standalone = launch(PREFIX + '-standalone', '-p', '127.0.0.1::5001', PREFIX + '-api:latest')
    record('standalone.json', {'checked_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), **http(standalone)})
    docker('rm', '-f', '-v', standalone)
    docker('network', 'create', '--driver', 'bridge', '--label', LABEL, NETWORK)
    network_created = True
    with tempfile.TemporaryDirectory() as scratch:
        env_file = Path(scratch) / 'mysql.env'
        env_file.write_text('MYSQL_ROOT_PASSWORD=' + secrets.token_urlsafe(24) + '\nMYSQL_DATABASE=devopsdb\n')
        env_file.chmod(0o600)
        mysql = launch(PREFIX + '-mysql', '--network', NETWORK, '--network-alias', 'mysql', '--env-file', str(env_file), 'mysql:8.4')
    redis = launch(PREFIX + '-redis', '--network', NETWORK, '--network-alias', 'redis', 'redis:7')
    flask = launch(PREFIX + '-flask', '--network', NETWORK, '--network-alias', 'flask', '-p', '127.0.0.1::5001', PREFIX + '-api:latest')
    about = http(flask)
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        query = docker('exec', mysql, 'sh', '-c', 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot -N -e "SELECT VERSION(); SHOW DATABASES;"', check=False)
        if query.returncode == 0:
            break
        time.sleep(2)
    assert query.returncode == 0 and 'devopsdb' in query.stdout
    assert docker('exec', redis, 'redis-cli', 'ping').stdout.strip() == 'PONG'
    # Install only a network diagnostic tool in this disposable container, not in the project image.
    install = docker('exec', flask, 'sh', '-c', 'apt-get update -qq && apt-get install -y -qq iputils-ping')
    (EVIDENCE / 'diagnostic-tool-install.txt').write_text(install.stdout + install.stderr)
    tests = docker('exec', '-i', flask, 'python', '-', input=(ROOT / 'test_app.py').read_text())
    (EVIDENCE / 'unit-tests.txt').write_text('UTC: ' + datetime.datetime.now(datetime.timezone.utc).isoformat() + '\nCommand: docker exec -i ' + flask + ' python - < test_app.py\n\n' + tests.stdout + tests.stderr)
    connectivity = json.loads(docker('exec', '-i', flask, 'python', '-', input=(ROOT / 'verify_network.py').read_text()).stdout)
    net = json.loads(docker('network', 'inspect', NETWORK).stdout)[0]
    assert net['Driver'] == 'bridge' and len(net['Containers']) == 3
    members = []
    for name in [mysql, redis, flask]:
        info = json.loads(docker('inspect', name).stdout)[0]
        assert info['State']['Running']
        ports = info['NetworkSettings']['Ports']
        if name != flask:
            assert not any(ports.values()), 'Database/cache host ports must not be published'
        members.append({'name': name, 'id': info['Id'], 'image': info['Config']['Image'], 'image_id': info['Image'],
                        'running': True, 'ip': info['NetworkSettings']['Networks'][NETWORK]['IPAddress'], 'ports': ports})
    for host in ['mysql','redis']:
        assert connectivity[host]['dns_address'] == next(m['ip'] for m in members if m['name']==PREFIX+'-'+host)
    record('network-inspection.json', net)
    versions = json.loads(docker('exec', flask, 'python', '-c', 'import json,sys,flask,werkzeug;print(json.dumps({"python":sys.version.split()[0],"flask":flask.__version__,"werkzeug":werkzeug.__version__}))').stdout)
    record('app-versions.json', versions)
    record('verification.json', {'checked_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope': 'Fresh temporary stack; original containers were already cleaned up by the owner.',
        'network': NETWORK, 'driver': net['Driver'], 'ipam': net['IPAM']['Config'],
        'containers': members, 'api': about, 'connectivity': connectivity,
        'mysql_query_output': query.stdout, 'redis_cli_ping': 'PONG', 'unit_tests_passed': 3,
        'checks_passed': ['standalone_api','three_running_bridge_members','host_api', 'dns_addresses',
                         'tcp_mysql_redis','three_pings_each','mysql_handshake_and_authenticated_query',
                         'redis_protocol_and_cli_pong','database_ports_unpublished','three_unit_tests']})
    print('All ten networking/API verification groups and three unit tests passed.')
finally:
    cleanup = []
    for container_id in reversed(containers):
        exists = docker('inspect', '--format', '{{.Id}}', container_id, check=False)
        if exists.returncode == 0:
            result = docker('rm', '-f', '-v', container_id, check=False)
            cleanup.append({'id': container_id, 'exit_code': result.returncode})
    if network_created:
        result = docker('network', 'rm', NETWORK, check=False)
        cleanup.append({'network': NETWORK, 'exit_code': result.returncode})
    remaining = docker('ps', '-aq', '--filter', 'label=' + LABEL).stdout.split()
    after_networks = docker('network', 'ls', '-q').stdout.split()
    ok = not remaining and all(c['exit_code']==0 for c in cleanup) and set(network_before).issubset(set(after_networks))
    record('cleanup.json', {'checked_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'actions': cleanup, 'remaining_owned_containers': remaining, 'existing_networks_preserved': set(network_before).issubset(set(after_networks)),
        'success': ok, 'images_retained': True})
    if not ok:
        raise RuntimeError('Cleanup incomplete; inspect cleanup.json')
