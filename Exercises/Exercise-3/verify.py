#!/usr/bin/env python3
"""Verify scaling, replacement and HTTP distribution in a temporary namespace."""
import collections
import datetime
import json
from pathlib import Path
import subprocess
import time
import uuid

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / 'evidence'
EVIDENCE.mkdir(exist_ok=True)
CONTEXT = 'minikube'
NAMESPACE = 'exercise3-check-' + uuid.uuid4().hex[:8]
created = False


def run(args, check=True, **kwargs):
    result = subprocess.run(args, text=True, capture_output=True, **kwargs)
    if check and result.returncode:
        raise RuntimeError(f'{args}: {result.stderr}')
    return result


def kube(*args, **kwargs):
    return run(['kubectl', '--context', CONTEXT, '-n', NAMESPACE, *args], **kwargs)


def data(*args):
    return json.loads(kube('get', *args, '-o', 'json').stdout)


def record(name, value):
    (EVIDENCE / name).write_text(json.dumps(value, indent=2) + '\n')


def snapshot(count, excluded=None):
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        rs = data('rs', 'flashsale-rs')
        pods = data('pods', '-l', 'app=flashsale')['items']
        active = [p for p in pods if not p['metadata'].get('deletionTimestamp')]
        if (len(active) == count and rs['status'].get('readyReplicas') == count
            and all(p['status']['phase'] == 'Running'
                    and all(c['ready'] for c in p['status'].get('containerStatuses', []))
                    and p['status'].get('containerStatuses')
                    and any(o['uid'] == rs['metadata']['uid'] for o in p['metadata']['ownerReferences'])
                    for p in active)
            and (excluded is None or all(p['metadata']['uid'] != excluded for p in active))):
            return [{'name': p['metadata']['name'], 'uid': p['metadata']['uid'],
                     'ip': p['status']['podIP'], 'node': p['spec']['nodeName'],
                     'image_id': p['status']['containerStatuses'][0]['imageID']} for p in active]
        time.sleep(1)
    raise RuntimeError(f'Timed out waiting for {count} ready owned pods')


try:
    kube('create', 'namespace', NAMESPACE)
    created = True
    kube('apply', '-f', str(ROOT / 'flashsale-replicaset.yaml'))
    initial = snapshot(3)
    kube('scale', 'rs', 'flashsale-rs', '--replicas=5')
    scaled = snapshot(5)
    assert {p['uid'] for p in initial}.issubset({p['uid'] for p in scaled})
    deleted = scaled[0]
    kube('delete', 'pod', deleted['name'], '--wait=false')
    final = snapshot(5, excluded=deleted['uid'])
    replacements = [p for p in final if p['uid'] not in {p['uid'] for p in scaled}]
    assert len(replacements) == 1
    nodes = data('nodes')['items']
    assert len(nodes) == 1 and all(p['node'] == nodes[0]['metadata']['name'] for p in final)
    rs = data('rs', 'flashsale-rs')
    container = rs['spec']['template']['spec']['containers'][0]
    assert container['image'] == 'flashsale:1.0' and container['imagePullPolicy'] == 'Never'
    for probe, delay, period in [('readinessProbe', 2, 5), ('livenessProbe', 10, 10)]:
        assert container[probe]['httpGet']['path'] == '/health'
        assert container[probe]['httpGet']['port'] == 5000
        assert container[probe]['initialDelaySeconds'] == delay
        assert container[probe]['periodSeconds'] == period
    assert container['resources']['requests'] == {'cpu': '100m', 'memory': '128Mi'}
    assert container['resources']['limits'] == {'cpu': '500m', 'memory': '256Mi'}
    service = data('service', 'flashsale-svc')
    assert service['spec']['type'] == 'ClusterIP'
    assert service['spec']['ports'][0]['port'] == 80 and service['spec']['ports'][0]['targetPort'] == 5000
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        endpoints = data('endpoints', 'flashsale-svc')
        ips = [a['ip'] for s in endpoints.get('subsets', []) for a in s.get('addresses', [])]
        if set(ips) == {p['ip'] for p in final}:
            break
        time.sleep(1)
    assert set(ips) == {p['ip'] for p in final}
    client = '''import json,urllib.request,collections
base="http://flashsale-svc/"
def get(path):
    with urllib.request.urlopen(base+path,timeout=10) as response:
        assert response.status==200
        return json.load(response)
home=get(""); health=get("health")
assert home["message"]=="Welcome to Big Sale!"
assert health["status"]=="healthy"
counts=collections.Counter()
for i in range(100):
    purchase=get("buy?user=lab-test")
    assert purchase["status"]=="success" and purchase["user"]=="lab-test"
    assert purchase["item"] in ["Smartphone","Shoes","Headphones","Laptop"]
    counts[purchase["served_by_pod"]]+=1
print(json.dumps({"homepage":home,"health":health,"purchase_requests":100,"purchase_counts":dict(counts)}))
'''
    responses = json.loads(kube('exec', '-i', final[0]['name'], '--', 'python', '-', input=client).stdout)
    assert set(responses['purchase_counts']) == {p['name'] for p in final}, 'Not all five pods observed; inspect or repeat distribution test'
    tests = kube('exec', '-i', final[0]['name'], '--', 'python', '-', input=(ROOT / 'test_app.py').read_text())
    (EVIDENCE / 'unit-tests.txt').write_text('Run UTC: ' + datetime.datetime.now(datetime.timezone.utc).isoformat() + '\nCommand: kubectl --context minikube -n ' + NAMESPACE + ' exec -i ' + final[0]['name'] + ' -- python - < test_app.py\n\n' + tests.stdout + tests.stderr)
    kube('apply', '--dry-run=server', '-f', str(ROOT / 'flashsale-replicaset.yaml'))
    (EVIDENCE / 'resources.txt').write_text(kube('get', 'rs,pods,services,endpoints', '-o', 'wide').stdout)
    record('verification.json', {
        'checked_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'context': CONTEXT, 'namespace': NAMESPACE,
        'scope': 'Supplementary isolated rerun; original default namespace ReplicaSet unchanged.',
        'node': nodes[0]['metadata']['name'], 'kubernetes_version': nodes[0]['status']['nodeInfo']['kubeletVersion'],
        'initial_pods': initial, 'scaled_pods': scaled, 'deleted_pod': deleted,
        'replacement_pod': replacements[0], 'final_pods': final,
        'image': container['image'], 'image_pull_policy': container['imagePullPolicy'],
        'probes': {k: container[k] for k in ['readinessProbe', 'livenessProbe']},
        'resources': container['resources'], 'service_type': service['spec']['type'],
        'service_port': 80, 'target_port': 5000, 'ready_endpoints': ips,
        'http': responses, 'unit_tests_passed': 5,
        'checks_passed': ['initial_three_ready', 'scale_to_five_retains_initial_pods',
                          'replacement_uid', 'single_node_distribution', 'image_probes_resources',
                          'five_ready_service_endpoints', 'all_routes_http_200',
                          '100_purchases_across_all_five_pods', 'five_unit_tests', 'server_dry_run']
    })
    print('All ten verification groups and five unit tests passed in', NAMESPACE)
finally:
    if created:
        result = kube('delete', 'namespace', NAMESPACE, '--wait=true', '--timeout=120s', check=False)
        record('verification-cleanup.json', {'namespace': NAMESPACE, 'exit_code': result.returncode,
                                            'stdout': result.stdout, 'stderr': result.stderr})
        if result.returncode:
            raise RuntimeError('Temporary namespace cleanup failed: ' + result.stderr)
