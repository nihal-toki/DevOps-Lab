#!/usr/bin/env python3
"""Record local capability, build, route tests and HTTP without claiming confinement."""
import datetime
import json
from pathlib import Path
import platform
import subprocess
import time
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / 'evidence'
EVIDENCE.mkdir(exist_ok=True)
NAME = 'exercise5-local-' + uuid.uuid4().hex[:8]
started = False


def run(*args, **kwargs):
    return subprocess.run(args, text=True, capture_output=True, check=True, **kwargs)


def save(name, data):
    (EVIDENCE / name).write_text(json.dumps(data, indent=2) + '\n')


try:
    security = json.loads(run('docker','info','--format','{{json .SecurityOptions}}').stdout)
    save('macos-host.json', {'checked_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'host_os': platform.system(), 'docker_version': run('docker','version','--format','{{.Server.Version}}').stdout.strip(),
        'security_options': security, 'apparmor_supported': any('apparmor' in s for s in security),
        'enforcement_claimed': False})
    result = run('docker','build','-t',NAME+':latest',str(ROOT))
    (EVIDENCE/'local-build.txt').write_text(result.stdout+result.stderr)
    tests=run('docker','run','--rm','-i',NAME+':latest','python','-',input=(ROOT/'test_app.py').read_text())
    (EVIDENCE/'unit-tests.txt').write_text(tests.stdout+tests.stderr)
    run('docker','run','-d','--name',NAME,'-p','127.0.0.1::5000',NAME+':latest')
    started=True
    info=json.loads(run('docker','inspect',NAME).stdout)[0]
    port=info['NetworkSettings']['Ports']['5000/tcp'][0]['HostPort'];url='http://127.0.0.1:'+port+'/'
    deadline=time.monotonic()+30
    while time.monotonic()<deadline:
        try:
            with urllib.request.urlopen(url,timeout=2) as response:
                body=response.read().decode()
                assert response.status==200 and body=='Hello, this is a secure Flask application running inside a Docker container!'
                save('local-http.json',{'url':url,'status':response.status,'body':body,'reported_apparmor_profile':info.get('AppArmorProfile'),'enforcement_claimed':False})
                break
        except OSError:
            time.sleep(.5)
    else:
        raise RuntimeError('HTTP startup timed out')
    print('Local build, both route tests and HTTP passed; AppArmor enforcement is not claimed.')
finally:
    if started:
        run('docker','rm','-f','-v',NAME)
    remaining=run('docker','ps','-aq','--filter','name=^/'+NAME+'$').stdout.strip()
    save('local-cleanup.json',{'container':NAME,'removed':not bool(remaining),'images_retained':True})
