#!/usr/bin/env bash
set -euo pipefail
export PATH="/opt/homebrew/bin:/Applications/Docker.app/Contents/Resources/bin:$PATH"
cd "$(dirname "$0")"
python3 - "$@" <<'PY'
import argparse, datetime, json, subprocess, urllib.request
from pathlib import Path
parser=argparse.ArgumentParser(description='Verify Nginx and save measured evidence')
parser.add_argument('url', help='URL printed by minikube service')
parser.add_argument('--context', default='minikube')
parser.add_argument('--namespace', default='default')
a=parser.parse_args()
def resource(*args):
    return json.loads(subprocess.check_output(['kubectl','--context',a.context,'-n',a.namespace,'get',*args,'-o','json']))
def check(ok,message):
    if not ok: raise SystemExit('FAIL: '+message)
p=resource('pod','hello-k8s'); s=resource('service','hello-k8s')
c=p['spec']['containers'][0]; port=s['spec']['ports'][0]
check(p['status']['phase']=='Running' and any(x['type']=='Ready' and x['status']=='True' for x in p['status']['conditions']), 'Pod readiness')
check(c['image'] in ('nginx','nginx:latest') and any(x['containerPort']==80 for x in c.get('ports',[])), 'Nginx image and port 80')
check(s['spec']['type']=='NodePort' and port['port']==80 and port['targetPort']==80 and 30000<=port['nodePort']<=32767 and s['spec']['selector'].get('run')=='hello-k8s','NodePort configuration')
e=resource('endpointslices','-l','kubernetes.io/service-name=hello-k8s')
addresses=[ip for item in e['items'] for ep in item.get('endpoints',[]) if ep.get('conditions',{}).get('ready') for ip in ep['addresses']]
check(p['status']['podIP'] in addresses,'Ready endpoint matching pod')
with urllib.request.urlopen(a.url,timeout=30) as response:
    html=response.read(); status=response.status; server=response.headers.get('Server','')
check(status==200 and b'<h1>Welcome to nginx!</h1>' in html,'HTTP 200 and Nginx welcome page')
report=dict(checked_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),profile=a.context,namespace=a.namespace,pod=p['metadata']['name'],phase=p['status']['phase'],ready=True,image=c['image'],image_id=p['status']['containerStatuses'][0]['imageID'],pod_ip=p['status']['podIP'],service_type=s['spec']['type'],service_port=port['port'],node_port=port['nodePort'],ready_endpoints=addresses,request_url=a.url,http_status=status,server=server,welcome_page=True,checks_passed=5)
d=Path('evidence');d.mkdir(exist_ok=True)
(d/'nginx-response.html').write_bytes(html)
(d/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
print('PASS: all five checks; evidence saved.')
PY
