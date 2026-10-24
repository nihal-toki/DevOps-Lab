"""Audit saved Jenkins build #2 and optionally test its deployed app over HTTP.
Run from Exercise 9: python3 verify.py [--http] [--save]
Docker access and GitHub CLI read access are required. No Jenkins job is changed.
"""
import argparse, datetime, hashlib, json, re, subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parent
WORKSPACE = '/var/jenkins_home/workspace/Python-MultiStage-Pipeline'

def run(*args):
    return subprocess.check_output(args)

def read_controller(path):
    return run('docker','exec','exercise7-jenkins','cat',path)

def xml(data):
    return ET.fromstring(data.replace(b"version='1.1'",b"version='1.0'"))

HTTP_CHECK = r'''
import subprocess,sys,json,hashlib,os,signal,time,urllib.request,tempfile,datetime
from pathlib import Path
base=Path('/var/jenkins_home/workspace/Python-MultiStage-Pipeline')
source=base/'python-flask-app/app.py'
deployed=base/'python-app-deploy/app.py'
expected='Hello, Jenkins Multi-Stage Pipeline!'
# The child creates the HTTP server from the deployed module and lets the OS
# choose a free loopback port. It disables debug/reloader without editing app.py.
child="""import json,os,sys
from werkzeug.serving import make_server
import app
server=make_server('127.0.0.1',0,app.app)
with open(sys.argv[1],'w') as f:
 json.dump({'port':server.server_port,'module':app.__file__,'pid':os.getpid()},f)
server.serve_forever()
"""
with tempfile.TemporaryDirectory(prefix='exercise9-http-') as tmp:
 ready=Path(tmp)/'ready.json'
 log=Path(tmp)/'server.log'
 with log.open('w') as stream:
  p=subprocess.Popen([sys.executable,'-c',child,str(ready)],cwd=deployed.parent,stdout=stream,stderr=stream,start_new_session=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
  report={'verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'Supplementary live HTTP check outside Jenkins build #2; deployed module served by a temporary Werkzeug server inside the controller.'}
  try:
   for _ in range(100):
    if ready.exists():break
    if p.poll() is not None:raise RuntimeError(log.read_text())
    time.sleep(.1)
   details=json.loads(ready.read_text())
   url='http://127.0.0.1:'+str(details['port'])+'/'
   with urllib.request.urlopen(url,timeout=5) as response:
    report.update(url=url,status=response.status,body=response.read().decode())
   report.update(details)
   report['deployed_sha256']=hashlib.sha256(deployed.read_bytes()).hexdigest()
   report['source_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
   report['checks']={'http_200':report['status']==200,'exact_response':report['body']==expected,'deployed_module_identity':Path(details['module']).resolve()==deployed.resolve(),'deployment_matches_source':report['deployed_sha256']==report['source_sha256'],'child_pid_matches':details['pid']==p.pid}
  finally:
   if p.poll() is None:os.killpg(p.pid,signal.SIGTERM)
   try:p.wait(timeout=5)
   except subprocess.TimeoutExpired:
    os.killpg(p.pid,signal.SIGKILL);p.wait(timeout=5)
   report['process_stopped']=p.poll() is not None
  report['checks']['process_cleanup']=report['process_stopped']
  report['all_passed']=all(report['checks'].values())
  print(json.dumps(report))
  assert report['all_passed'],report
'''

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--http',action='store_true',help='Start and stop a temporary loopback HTTP server from deployed file')
    parser.add_argument('--save',action='store_true',help='Save measured verification reports')
    args=parser.parse_args()
    base='/var/jenkins_home/jobs/Python-MultiStage-Pipeline'
    config_bytes=read_controller(base+'/config.xml');config=xml(config_bytes)
    build_bytes=read_controller(base+'/builds/2/build.xml');build=xml(build_bytes)
    console=re.sub(rb'\x1b\[8mha:.*?\x1b\[0m',b'',read_controller(base+'/builds/2/log'),flags=re.S).decode()
    revisions=set(n.text for n in build.findall('.//sha1') if n.text and re.fullmatch('[0-9a-f]{40}',n.text))
    if len(revisions)!=1:raise RuntimeError('Ambiguous source revision')
    revision=revisions.pop()
    hashes={}
    for name in ['app.py','requirements.txt','test_app.py','Jenkinsfile']:
        local=(ROOT/'python-flask-app'/name).read_bytes()
        github=run('gh','api',f'repos/nihal-toki/devops-sample-code/contents/python-flask-app/{name}?ref={revision}','-H','Accept: application/vnd.github.raw+json')
        hashes[name]={'sha256':hashlib.sha256(local).hexdigest(),'matches_built_github_source':local==github}
    stages=['Build','Test','Deploy','Run Application','Test Application']
    definition=config.find('definition')
    checks={
        'pipeline_scm_configuration':config.tag=='flow-definition' and definition.get('class')=='org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition' and definition.findtext('.//url')=='https://github.com/nihal-toki/devops-sample-code.git' and definition.findtext('.//hudson.plugins.git.BranchSpec/name')=='*/main' and definition.findtext('scriptPath')=='python-flask-app/Jenkinsfile',
        'completed_success':build.findtext('result')=='SUCCESS' and console.rstrip().endswith('Finished: SUCCESS'),
        'all_five_stages_executed':all('[Pipeline] { ('+s+')' in console for s in stages) and 'skipped due to' not in console.lower(),
        'dependencies_installed':'Successfully installed' in console and 'Flask-2.1.2' in console and 'Werkzeug-2.1.2' in console,
        'one_unit_test_passed':bool(re.search(r'Ran 1 test in .*?\n\nOK',console)),
        'copy_deployment_recorded':'+ cp app.py '+WORKSPACE+'/python-app-deploy/' in console,
        'deployed_in_process_validation':"app.test_client().get('/')" in console and "assert r.status_code == 200" in console and 'Hello, Jenkins Multi-Stage Pipeline!' in console.splitlines(),
        'all_local_files_match_built_revision':all(v['matches_built_github_source'] for v in hashes.values()),
    }
    report={'verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'job':'Python-MultiStage-Pipeline','build_number':2,'result':build.findtext('result'),'checked_out_revision':revision,'stages_observed_in_successful_console':stages,'files':hashes,'checks':checks,'all_passed':all(checks.values()),'limitations':['Build #2 imports and tests the deployed app in-process; it does not start an HTTP server','Build #1 is no longer retained; its reported failure cannot be independently verified','Per-stage execution is observed in the successful console, not queried via the stage REST API'],'console_note':'Encoded Jenkins ConsoleNote metadata removed; visible text preserved'}
    if args.http:
        measured=json.loads(run('docker','exec','-i','-u','jenkins','exercise7-jenkins',WORKSPACE+'/.jenkins-venv/bin/python','-B','-c',HTTP_CHECK))
        report['supplementary_http_all_passed']=measured['all_passed']
        if args.save:(ROOT/'evidence/http-response.json').write_text(json.dumps(measured,indent=2)+'\n')
    if args.save:
        if not report['all_passed']:raise RuntimeError('Verification failed')
        (ROOT/'job.xml').write_bytes(config_bytes)
        (ROOT/'evidence/build.xml').write_bytes(build_bytes)
        (ROOT/'evidence/console.txt').write_text(console)
        (ROOT/'evidence/verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return 0 if report['all_passed'] else 1

if __name__=='__main__':raise SystemExit(main())
