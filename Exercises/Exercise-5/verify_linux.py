#!/usr/bin/env python3
"""Require real AppArmor enforcement and matched unconfined controls on Linux."""
import datetime
import json
from pathlib import Path
import time
import urllib.request
import uuid
import docker

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / 'evidence'
EVIDENCE.mkdir(exist_ok=True)
PROFILE = 'my-apparmor-profile'
NAME = 'exercise5-check-' + uuid.uuid4().hex[:8]
client = docker.from_env()
containers = []


def save(name, value):
    (EVIDENCE / name).write_text(json.dumps(value, indent=2) + '\n')


def exec_python(container, source):
    result = container.exec_run(['/usr/local/bin/python', '-c', source])
    return {'exit_code': result.exit_code, 'output': result.output.decode(errors='replace')}


def launch(suffix, confined):
    container = client.containers.run(NAME + ':latest', name=NAME + '-' + suffix,
        security_opt=['apparmor=' + (PROFILE if confined else 'unconfined')],
        ports={'5000/tcp': ('127.0.0.1', None)},
        labels={'devops.lab.exercise': '5', 'devops.lab.verification': NAME}, detach=True)
    containers.append(container)
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        container.reload()
        if not container.attrs['State']['Running']:
            raise RuntimeError(container.logs().decode(errors='replace'))
        port = container.attrs['NetworkSettings']['Ports']['5000/tcp'][0]['HostPort']
        url = 'http://127.0.0.1:' + port + '/'
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                body = response.read().decode()
                assert response.status == 200 and body == 'Hello, this is a secure Flask application running inside a Docker container!'
                return container, {'url': url, 'status': response.status, 'body': body}
        except OSError:
            time.sleep(0.5)
    raise RuntimeError('Flask HTTP startup timeout')


try:
    security = client.info().get('SecurityOptions', [])
    save('linux-host.json', {'checked_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                            'docker_version': client.version()['Version'], 'security_options': security})
    if not any('apparmor' in option for option in security):
        raise RuntimeError('AppArmor support is required; refusal is not an enforcement pass')
    image, _ = client.images.build(path=str(ROOT), tag=NAME + ':latest', rm=True)
    control, control_http = launch('control', False)
    confined, confined_http = launch('confined', True)
    confined.reload()
    current = exec_python(confined, "print(open('/proc/self/attr/current').read().strip())")
    assert confined.attrs.get('AppArmorProfile') == PROFILE
    assert PROFILE + ' (enforce)' in current['output'] and current['exit_code'] == 0
    tests = exec_python(confined, (ROOT / 'test_app.py').read_text())
    (EVIDENCE / 'linux-unit-tests.txt').write_text(tests['output'])
    assert tests['exit_code'] == 0
    operations = {
        'read_etc_passwd': "open('/etc/passwd').read(1); print('read allowed')",
        'write_var': "open('/var/lab-test','w').write('lab'); print('write allowed')",
        'spawn_bash': "import subprocess; subprocess.run(['/bin/bash','-c','exit 0'],check=True); print('bash allowed')",
        'spawn_cat': "import subprocess; subprocess.run(['/usr/bin/cat','/etc/passwd'],stdout=subprocess.DEVNULL,check=True); print('cat allowed')",
    }
    records = {}
    for name, source in operations.items():
        allowed = exec_python(control, source)
        denied = exec_python(confined, source)
        records[name] = {'control': allowed, 'confined': denied}
        assert allowed['exit_code'] == 0, (name, allowed)
        assert denied['exit_code'] != 0 and ('PermissionError' in denied['output'] or 'Permission denied' in denied['output']), (name, denied)
    allowed_write = exec_python(confined, "open('/app/allowed-test','w').write('lab'); print('app write allowed')")
    assert allowed_write['exit_code'] == 0
    direct = []
    for command in [['/bin/bash'], ['/bin/bash','-c','exit 0'], ['/usr/bin/cat','/etc/passwd']]:
        a = control.exec_run(command); b = confined.exec_run(command)
        item = {'command': command, 'control_exit_code': a.exit_code, 'confined_exit_code': b.exit_code,
                'confined_output': b.output.decode(errors='replace')}
        direct.append(item)
        assert a.exit_code == 0 and b.exit_code != 0, item
    with urllib.request.urlopen(confined_http['url'], timeout=5) as response:
        assert response.status == 200
    save('profile-application.json', {'checked_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'image_id': image.id, 'security_options': confined.attrs['HostConfig']['SecurityOpt'],
        'reported_profile': confined.attrs['AppArmorProfile'], 'process_profile': current['output'].strip(),
        'http': confined_http, 'unit_tests_passed': 2})
    save('restricted-actions.json', {'checked_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'control_http': control_http, 'operations': records, 'allowed_app_write': allowed_write,
        'direct_exec': direct, 'http_after_tests': 200, 'all_checks_passed': True})
    print('Linux profile is in enforce mode; all controls, denials, allowed writes and HTTP checks passed.')
finally:
    results = []
    for container in reversed(containers):
        container.remove(force=True, v=True)
        results.append(container.id)
    remaining = client.containers.list(all=True, filters={'label': 'devops.lab.verification=' + NAME})
    save('linux-cleanup.json', {'removed_container_ids': results, 'remaining_owned_containers': [c.id for c in remaining],
                               'success': not remaining, 'images_retained': True})
    client.close()
