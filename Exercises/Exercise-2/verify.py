#!/usr/bin/env python3
"""Repeat Exercise 2 before/after checks in a temporary Minikube namespace."""
import datetime
import json
from pathlib import Path
import re
import subprocess
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / 'evidence'
EVIDENCE.mkdir(exist_ok=True)
NAMESPACE = 'exercise2-check-' + uuid.uuid4().hex[:8]
CONTEXT = 'minikube'
tunnel = None
created = False


def run(args, check=True, **kwargs):
    result = subprocess.run(args, capture_output=True, text=True, **kwargs)
    if check and result.returncode:
        raise RuntimeError(f'{args}: {result.stderr}')
    return result


def kube(*args, **kwargs):
    return run(['kubectl', '--context', CONTEXT, '-n', NAMESPACE, *args], **kwargs)


def record(name, data):
    (EVIDENCE / name).write_text(json.dumps(data, indent=2) + '\n')


try:
    kube('create', 'namespace', NAMESPACE)
    created = True
    kube('apply', '-f', str(ROOT / 'flask-deployment.yaml'))
    kube('rollout', 'status', 'deployment/flask-deployment', '--timeout=180s')
    before_services = json.loads(kube('get', 'services', '-o', 'json').stdout)['items']
    before = run(['curl', '--noproxy', '*', '--max-time', '5', 'http://127.0.0.1:15000/'], check=False)
    record('before-service.json', {
        'checked_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'namespace': NAMESPACE, 'service_count': len(before_services),
        'url': 'http://127.0.0.1:15000/', 'curl_exit_code': before.returncode,
        'stdout': before.stdout, 'stderr': before.stderr,
        'scope': 'Fresh isolated namespace; existing default namespace Service remains running.'
    })
    assert not before_services, 'Unexpected Service in verification namespace'
    assert before.returncode == 7, 'Expected connection refusal; check for a host process on port 15000'
    # Keep the repository manifest intact; allocate a free NodePort for this temporary copy.
    manifest = run(['kubectl', 'create', '--dry-run=client', '-f', str(ROOT / 'flask-service.yaml'), '-o', 'json']).stdout
    service = json.loads(manifest)
    service['metadata']['namespace'] = NAMESPACE
    for port in service['spec']['ports']:
        port.pop('nodePort', None)
    kube('apply', '-f', '-', input=json.dumps(service))
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        endpoints = json.loads(kube('get', 'endpoints', 'flask-service', '-o', 'json').stdout)
        addresses = [a['ip'] for subset in endpoints.get('subsets', []) for a in subset.get('addresses', [])]
        if len(addresses) == 2:
            break
        time.sleep(1)
    assert len(addresses) == 2, 'Expected two ready endpoints'
    with tempfile.TemporaryFile(mode='w+') as tunnel_log:
        tunnel = subprocess.Popen(['minikube', '-p', CONTEXT, 'service', 'flask-service', '-n', NAMESPACE, '--url'], stdout=tunnel_log, stderr=subprocess.STDOUT, text=True)
        url = None
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline:
            tunnel_log.seek(0)
            transcript = tunnel_log.read()
            match = re.search(r'http://127\.0\.0\.1:\d+', transcript)
            if match:
                url = match.group(0) + '/'
                break
            if tunnel.poll() is not None:
                raise RuntimeError(transcript)
            time.sleep(0.5)
        assert url, 'No tunnel URL obtained'
        response = run(['curl', '--noproxy', '*', '--fail', '--show-error', '--max-time', '10', '-i', url])
        (EVIDENCE / 'service-http-response.txt').write_text('Command: curl --noproxy "*" --fail --show-error --max-time 10 -i ' + url + '\n\n' + response.stdout)
        assert response.stdout.splitlines()[0].split()[1] == '200'
        assert response.stdout.split('\n\n', 1)[1] == 'Hello from Flask on Kubernetes!'
        deployment = json.loads(kube('get', 'deployment', 'flask-deployment', '-o', 'json').stdout)
        pods = json.loads(kube('get', 'pods', '-l', 'app=flask', '-o', 'json').stdout)['items']
        service = json.loads(kube('get', 'service', 'flask-service', '-o', 'json').stdout)
        container = deployment['spec']['template']['spec']['containers'][0]
        assert deployment['status']['availableReplicas'] == 2
        assert container['image'] == 'flask-k8s-app:v1' and container['imagePullPolicy'] == 'Never'
        assert container['ports'][0]['containerPort'] == 15000
        assert len(pods) == 2 and all(p['status']['phase'] == 'Running' and all(c['ready'] for c in p['status']['containerStatuses']) for p in pods)
        assert service['spec']['type'] == 'NodePort'
        assert service['spec']['ports'][0]['port'] == service['spec']['ports'][0]['targetPort'] == 15000
        (EVIDENCE / 'deployment.txt').write_text(kube('get', 'deployments,pods', '-o', 'wide').stdout)
        (EVIDENCE / 'service.txt').write_text(kube('get', 'services,endpoints', '-o', 'wide').stdout)
        kube('apply', '--dry-run=server', '-f', str(ROOT / 'flask-deployment.yaml'))
        kube('apply', '--dry-run=server', '-f', '-', input=json.dumps(service))
        record('verification.json', {
            'checked_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'context': CONTEXT, 'namespace': NAMESPACE,
            'deployment': deployment['metadata']['name'], 'replicas': 2,
            'image': container['image'], 'image_pull_policy': container['imagePullPolicy'],
            'pods': [{'name': p['metadata']['name'], 'ip': p['status']['podIP'], 'phase': p['status']['phase']} for p in pods],
            'service': service['metadata']['name'], 'service_type': 'NodePort',
            'service_port': 15000, 'target_port': 15000,
            'node_port': service['spec']['ports'][0]['nodePort'], 'ready_endpoints': addresses,
            'request_url': url, 'http_status': 200, 'body': 'Hello from Flask on Kubernetes!',
            'before_service_curl_exit_code': before.returncode,
            'checks_passed': ['before_service_absent', 'host_connection_refused', 'deployment_image_and_replicas', 'two_ready_pods', 'service_ports_and_endpoints', 'http_status_and_body', 'server_dry_run'],
            'scope': 'Supplementary isolated rerun; original deployment and Service unchanged. Temporary NodePort allocated automatically.'
        })
    print('All seven Kubernetes/HTTP verification groups passed in', NAMESPACE)
finally:
    if tunnel is not None:
        tunnel.terminate()
        try:
            tunnel.wait(timeout=10)
        except subprocess.TimeoutExpired:
            tunnel.kill()
            tunnel.wait()
    if created:
        cleanup = kube('delete', 'namespace', NAMESPACE, '--wait=true', '--timeout=90s', check=False)
        record('verification-cleanup.json', {'namespace': NAMESPACE, 'exit_code': cleanup.returncode, 'stdout': cleanup.stdout, 'stderr': cleanup.stderr})
        if cleanup.returncode:
            raise RuntimeError('Temporary namespace cleanup failed: ' + cleanup.stderr)
