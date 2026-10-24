#!/usr/bin/env python3
"""Execute real Jenkins builds and verify their monitoring stack on a disposable CI runner."""
import base64
import datetime
import http.cookiejar
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / 'evidence'
EVIDENCE.mkdir(exist_ok=True)
PREFIX = 'exercise6-check-' + uuid.uuid4().hex[:8]
LABEL = 'devops.lab.run=' + PREFIX
EXPECTED = {
    'Total Deliveries': 'total_deliveries',
    'Pending Deliveries': 'pending_deliveries',
    'Completed Deliveries': 'total_deliveries - pending_deliveries - on_the_way_deliveries',
    'On-the-Way Deliveries': 'on_the_way_deliveries',
    'Average Delivery Time': 'average_delivery_time_sum / average_delivery_time_count',
}


def docker(*args, check=True):
    result = subprocess.run(['docker', *args], text=True, capture_output=True)
    if check and result.returncode:
        raise RuntimeError('Docker command failed: ' + result.stderr)
    return result


def save(name, value):
    (EVIDENCE / name).write_text(json.dumps(value, indent=2) + '\n')


def request(url, auth=None, data=None, headers=None):
    h = dict(headers or {})
    if auth:
        h['Authorization'] = 'Basic ' + base64.b64encode(auth.encode()).decode()
    req = urllib.request.Request(url, data=data, headers=h)
    return urllib.request.urlopen(req, timeout=20)


def get_json(url, auth=None):
    with request(url, auth=auth) as response:
        return json.load(response)


def await_result(fn, timeout=180):
    deadline = time.monotonic() + timeout
    last = None
    while time.monotonic() < deadline:
        try:
            value = fn()
            if value:
                return value
        except (OSError, ValueError, KeyError, AssertionError) as error:
            last = error
        time.sleep(2)
    raise RuntimeError('Timed out waiting for service/check: ' + repr(last))


def address(name, port):
    info = json.loads(docker('inspect', name).stdout)[0]
    binding = info['NetworkSettings']['Ports'][str(port) + '/tcp'][0]
    return 'http://127.0.0.1:' + binding['HostPort']


def metrics(url):
    with request(url + '/metrics') as response:
        text = response.read().decode()
    values = {}
    for line in text.splitlines():
        if line and not line.startswith('#'):
            key, value = line.split()[:2]
            if '{' not in key:
                values[key] = float(value)
    return values, text


def query(prom, expression, auth=None):
    body = get_json(prom + '/api/v1/query?' + urllib.parse.urlencode({'query': expression}), auth)
    assert body['status'] == 'success'
    return body['data']['result']


def verify_scenario(mode, build_number, grafana_password):
    app = address(PREFIX + '-metrics', 8000)
    prom = address(PREFIX + '-prometheus', 9090)
    grafana = address(PREFIX + '-grafana', 3000)
    auth = 'admin:' + grafana_password
    await_result(lambda: get_json(grafana + '/api/health')['database'] == 'ok')
    targets = await_result(lambda: (lambda d: d if len(d['data']['activeTargets']) == 2 and all(t['health'] == 'up' for t in d['data']['activeTargets']) else None)(get_json(prom + '/api/v1/targets')))
    first, _ = metrics(app)
    time.sleep(2)
    values, text = metrics(app)
    assert values['average_delivery_time_count'] > first['average_delivery_time_count']
    low, high = (10, 20) if mode == 'normal' else (50, 100)
    assert low <= values['pending_deliveries'] <= high
    assert 5 <= values['on_the_way_deliveries'] <= 20
    delivered = values['total_deliveries'] - values['pending_deliveries'] - values['on_the_way_deliveries']
    assert 30 <= delivered <= 70
    mean = values['average_delivery_time_sum'] / values['average_delivery_time_count']
    assert (35 if mode == 'high_pending_slow' else 15) <= mean <= 45
    (EVIDENCE / ('metrics-' + mode + '.txt')).write_text(text)
    health = get_json(grafana + '/api/datasources/uid/delivery-prometheus/health', auth)
    assert health['status'] == 'OK'
    dashboard = get_json(grafana + '/api/dashboards/uid/delivery-monitoring', auth)['dashboard']
    assert dashboard['refresh'] == '5s'
    expressions = {p['title']: p['targets'][0]['expr'] for p in dashboard['panels']}
    for title, expression in EXPECTED.items():
        assert expressions[title] == expression
    proxy = grafana + '/api/datasources/proxy/uid/delivery-prometheus'
    proxy_results = {title: await_result(lambda expression=expr: query(proxy, expression, auth)) for title, expr in EXPECTED.items()}
    rules = get_json(prom + '/api/v1/rules')
    loaded = {rule['name']: rule for group in rules['data']['groups'] for rule in group['rules']}
    assert set(loaded) == {'HighPendingDeliveries', 'HighAverageDeliveryTime'}
    assert loaded['HighPendingDeliveries']['query'] == 'pending_deliveries > 10'
    assert loaded['HighPendingDeliveries']['duration'] == 15
    assert loaded['HighPendingDeliveries']['labels']['severity'] == 'warning'
    assert loaded['HighAverageDeliveryTime']['duration'] == 0
    assert loaded['HighAverageDeliveryTime']['labels']['severity'] == 'critical'
    required = set() if mode == 'normal' else {'HighPendingDeliveries'}
    if mode == 'high_pending_slow':
        required.add('HighAverageDeliveryTime')
    def alerts_ready():
        response = get_json(prom + '/api/v1/alerts')
        firing = {a['labels']['alertname'] for a in response['data']['alerts'] if a['state'] == 'firing'}
        return response if required.issubset(firing) else None
    alerts = await_result(alerts_ready, timeout=180)
    alert_query = query(proxy, 'ALERTS{alertstate="firing"}', auth)
    assert required.issubset({x['metric']['alertname'] for x in alert_query})
    save('verification-' + mode + '.json', {
        'checked_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scenario': mode, 'jenkins_build': build_number,
        'metrics_snapshot': {k:v for k,v in values.items() if k.startswith(('total_deliveries','pending_deliveries','on_the_way_deliveries','average_delivery_time'))},
        'completed_deliveries': delivered, 'observed_mean_seconds': mean,
        'targets': [{'job':t['labels']['job'],'health':t['health'],'scrape_url':t['scrapeUrl']} for t in targets['data']['activeTargets']],
        'grafana_datasource_health': health, 'dashboard_refresh': dashboard['refresh'],
        'dashboard_queries': expressions, 'grafana_proxy_results': proxy_results,
        'rules': rules['data']['groups'], 'alerts': alerts['data']['alerts'],
        'dashboard_alert_query': alert_query,
        'service_urls': {'metrics':app,'prometheus':prom,'grafana':grafana},
        'checks_passed': ['metric_ranges_and_total','summary_count_increases','two_scrape_targets_up',
                          'grafana_datasource_healthy','five_panel_queries_return_data','five_second_refresh',
                          'alert_rules_match_source','scenario_alerts_firing','alerts_visible_through_grafana'],
        'unit_tests_passed_in_jenkins': 4, 'notifications_configured': False,
    })
    print(mode, 'Jenkins build', build_number, 'and nine monitoring check groups passed.', flush=True)


def main():
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise SystemExit('Run this privileged Docker/Jenkins verification only in the disposable GitHub Actions runner.')
    existing_networks = set(docker('network','ls','-q').stdout.split())
    network_created = False
    try:
        image = docker('build','-f',str(ROOT/'jenkins/Dockerfile'),'-t',PREFIX+'-jenkins:latest',str(ROOT))
        (EVIDENCE/'jenkins-image-build.txt').write_text(image.stdout + image.stderr)
        docker('network','create','--label',LABEL,PREFIX+'-net')
        network_created = True
        with tempfile.TemporaryDirectory() as private:
            private_path = Path(private)
            admin_password = secrets.token_urlsafe(24)
            grafana_password = secrets.token_urlsafe(24)
            env_file = private_path/'jenkins.env'
            env_file.write_text('LAB_ADMIN_PASSWORD='+admin_password+'\nLAB_PREFIX='+PREFIX+'\nJAVA_OPTS=-Djenkins.install.runSetupWizard=false\nDOCKER_BUILDKIT=0\n')
            env_file.chmod(0o600)
            (private_path/'grafana.env').write_text('GF_SECURITY_ADMIN_PASSWORD='+grafana_password+'\n')
            (private_path/'grafana.env').chmod(0o600)
            docker('run','-d','--name',PREFIX+'-jenkins','--label',LABEL,'--user','0',
                   '--network',PREFIX+'-net','--env-file',str(env_file),'-p','127.0.0.1::8080',
                   '-v','/var/run/docker.sock:/var/run/docker.sock',
                   '-v',str(ROOT)+':/lab-src:ro','-v',private+':/lab-private:ro',PREFIX+'-jenkins:latest')
            base = address(PREFIX+'-jenkins',8080)
            auth = 'labadmin:'+admin_password
            await_result(lambda: get_json(base+'/api/json',auth), timeout=240)
            # Use a cookie-backed session for the CSRF crumb; credentials are never logged.
            jar=http.cookiejar.CookieJar()
            opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
            def jenkins(path, data=None, content_type=None):
                headers={'Authorization':'Basic '+base64.b64encode(auth.encode()).decode()}
                if data is not None:
                    with opener.open(urllib.request.Request(base+'/crumbIssuer/api/json',headers=headers),timeout=20) as response:
                        crumb=json.load(response)
                    headers[crumb['crumbRequestField']]=crumb['crumb']
                    if content_type:headers['Content-Type']=content_type
                return opener.open(urllib.request.Request(base+path,data=data,headers=headers),timeout=30)
            root=ET.Element('flow-definition',{'plugin':'workflow-job'})
            ET.SubElement(root,'description').text='Exercise 6 genuine monitoring pipeline verification'
            definition=ET.SubElement(root,'definition',{'class':'org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition','plugin':'workflow-cps'})
            ET.SubElement(definition,'script').text=(ROOT/'Jenkinsfile').read_text()
            ET.SubElement(definition,'sandbox').text='true'
            properties=ET.SubElement(root,'properties');parameter_property=ET.SubElement(properties,'hudson.model.ParametersDefinitionProperty')
            definitions=ET.SubElement(parameter_property,'parameterDefinitions');parameter=ET.SubElement(definitions,'hudson.model.StringParameterDefinition')
            ET.SubElement(parameter,'name').text='SCENARIO';ET.SubElement(parameter,'defaultValue').text='normal'
            with jenkins('/createItem?name=DeliveryMonitoring',ET.tostring(root), 'application/xml') as response:
                assert response.status==200
            for mode in ['normal','high_pending','high_pending_slow']:
                with jenkins('/job/DeliveryMonitoring/buildWithParameters',urllib.parse.urlencode({'SCENARIO':mode}).encode(),'application/x-www-form-urlencoded') as response:
                    queue=urllib.parse.urlsplit(response.headers['Location']).path
                def build_number():
                    with jenkins(queue+'api/json') as response:state=json.load(response)
                    return state.get('executable',{}).get('number')
                number=await_result(build_number,timeout=180)
                def complete():
                    with jenkins('/job/DeliveryMonitoring/'+str(number)+'/api/json') as response:state=json.load(response)
                    return state if not state['building'] else None
                build=await_result(complete,timeout=900)
                with jenkins('/job/DeliveryMonitoring/'+str(number)+'/consoleText') as response:console=response.read().decode()
                (EVIDENCE/('jenkins-'+mode+'.txt')).write_text(console)
                save('jenkins-'+mode+'.json',{k:build.get(k) for k in ['number','result','duration','timestamp','url']})
                assert build['result']=='SUCCESS', 'Jenkins failed in '+mode+'; inspect its genuine console log'
                assert 'Ran 4 tests' in console and re.search(r'\bOK\s*$', console, re.MULTILINE)
                verify_scenario(mode,number,grafana_password)
            save('pipeline-environment.json',{'jenkins':get_json(base+'/api/json',auth).get('mode'),
                'scope':'Disposable Ubuntu GitHub runner; Jenkins uses its runner Docker socket, never the laptop daemon.',
                'container_images':json.loads(docker('inspect',PREFIX+'-metrics',PREFIX+'-prometheus',PREFIX+'-grafana').stdout) and [
                    {'name':name,'image_id':json.loads(docker('inspect',name).stdout)[0]['Image']} for name in [PREFIX+'-metrics',PREFIX+'-prometheus',PREFIX+'-grafana']],
                'run_prefix':PREFIX})
    finally:
        containers=docker('ps','-aq','--filter','label='+LABEL).stdout.split()
        removed=[]
        for container in containers:
            result=docker('rm','-f','-v',container,check=False)
            removed.append({'id':container,'exit_code':result.returncode})
        network_removed=True
        if network_created:
            network_removed=docker('network','rm',PREFIX+'-net',check=False).returncode==0
        remaining=docker('ps','-aq','--filter','label='+LABEL).stdout.split()
        preserved=existing_networks.issubset(set(docker('network','ls','-q').stdout.split()))
        save('cleanup.json',{'removed_containers':removed,'remaining_owned_containers':remaining,
            'network_removed':network_removed,'existing_networks_preserved':preserved,
            'success':not remaining and network_removed and preserved and all(r['exit_code']==0 for r in removed)})
        if remaining or not network_removed or not preserved:
            raise RuntimeError('Disposable runner cleanup incomplete')

if __name__ == '__main__':
    main()
