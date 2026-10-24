"""Read-only audit of a completed Exercise 9 Jenkins HTTP pipeline.

Run: python3 verify.py --build NUMBER [--save]
Docker access and GitHub CLI read access are required. No build is triggered.
Build #2's historical evidence stays in its original files.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
WORKSPACE = '/var/jenkins_home/workspace/Python-MultiStage-Pipeline'

def run(*args):
    return subprocess.check_output(args)

def read_controller(path):
    return run('docker', 'exec', 'exercise7-jenkins', 'cat', path)

def xml(data):
    return ET.fromstring(data.replace(b"version='1.1'", b"version='1.0'"))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=int, required=True)
    parser.add_argument('--save', action='store_true')
    args = parser.parse_args()
    if args.build < 3:
        parser.error('Use a new HTTP pipeline build; historical build #2 is documented separately')
    base = '/var/jenkins_home/jobs/Python-MultiStage-Pipeline'
    config_bytes = read_controller(base + '/config.xml')
    config = xml(config_bytes)
    build_bytes = read_controller(base + f'/builds/{args.build}/build.xml')
    build = xml(build_bytes)
    console = re.sub(rb'\x1b\[8mha:.*?\x1b\[0m', b'', read_controller(base + f'/builds/{args.build}/log'), flags=re.S).decode()
    revisions = set(n.text for n in build.findall('.//sha1') if n.text and re.fullmatch('[0-9a-f]{40}', n.text))
    if len(revisions) != 1:
        raise RuntimeError('Ambiguous built revision')
    revision = revisions.pop()
    archive = base + f'/builds/{args.build}/archive/python-app-deploy/'
    http_bytes = read_controller(archive + 'http-response.json')
    cleanup_bytes = read_controller(archive + 'server-cleanup.json')
    log_bytes = read_controller(archive + 'app.log')
    http = json.loads(http_bytes)
    cleanup = json.loads(cleanup_bytes)
    files = {}
    for name in ['app.py', 'requirements.txt', 'test_app.py', 'Jenkinsfile', 'pipeline_runtime.py']:
        local = (ROOT / 'python-flask-app' / name).read_bytes()
        source = run('gh', 'api', f'repos/nihal-toki/devops-sample-code/contents/python-flask-app/{name}?ref={revision}', '-H', 'Accept: application/vnd.github.raw+json')
        files[name] = {'sha256': hashlib.sha256(local).hexdigest(), 'matches_built_revision': local == source}
    stages = ['Build', 'Test', 'Deploy', 'Run Application', 'Test Application']
    definition = config.find('definition')
    checks = {
        'pipeline_from_scm': config.tag == 'flow-definition' and definition.get('class') == 'org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition',
        'expected_repository_branch_script': definition.findtext('.//url') == 'https://github.com/nihal-toki/devops-sample-code.git' and definition.findtext('.//hudson.plugins.git.BranchSpec/name') == '*/main' and definition.findtext('scriptPath') == 'python-flask-app/Jenkinsfile',
        'build_completed_success': build.findtext('result') == 'SUCCESS' and console.rstrip().endswith('Finished: SUCCESS'),
        'all_five_stages_executed': all('[Pipeline] { (' + s + ')' in console for s in stages) and 'skipped due to' not in console.lower(),
        'dependencies_consistent': 'No broken requirements found.' in console,
        'unit_test_passed': bool(re.search(r'Ran 1 test in .*?\n\nOK', console)),
        'real_server_started_in_pipeline': 'Started deployed server PID' in console and 'pipeline_runtime.py start --deployed ' in console,
        'http_verified_in_pipeline': 'pipeline_runtime.py verify --deployed ' in console and http.get('build_number') == str(args.build),
        'http_200_exact_response': http.get('status') == 200 and http.get('body') == 'Hello, Jenkins Multi-Stage Pipeline!',
        'http_process_and_module_checks': http.get('all_passed') is True and all(http['checks'].values()) and http.get('module') == WORKSPACE + '/python-app-deploy/app.py',
        'deployed_hash_matches_committed_app': http.get('source_sha256') == http.get('deployed_sha256') == files['app.py']['sha256'],
        'same_process_stopped': cleanup.get('server_started') is True and cleanup.get('process_stopped') is True and cleanup.get('pid') == http.get('pid') and cleanup.get('identity_checked_before_signal') is True,
        'all_five_files_match_built_commit': all(v['matches_built_revision'] for v in files.values()),
        'http_request_in_actual_server_log': 'GET / HTTP/1.1" 200' in log_bytes.decode(),
    }
    report = {'verified_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'job': 'Python-MultiStage-Pipeline', 'build_number': args.build, 'result': build.findtext('result'), 'checked_out_revision': revision, 'files': files, 'checks': checks, 'all_passed': all(checks.values()), 'stages_observed_in_successful_console': stages, 'http': http, 'cleanup': cleanup, 'note': 'Read-only saved build and archived reports; encoded ConsoleNote metadata removed from the visible console export. Stage execution is observed in the successful console.'}
    if args.save:
        if not report['all_passed']:
            raise RuntimeError(json.dumps(report, indent=2))
        ev = ROOT / 'evidence'
        (ev / f'jenkins-build-{args.build}.xml').write_bytes(build_bytes)
        (ev / f'jenkins-console-build-{args.build}.txt').write_text(console)
        (ev / f'jenkins-http-build-{args.build}.json').write_bytes(http_bytes)
        (ev / f'jenkins-cleanup-build-{args.build}.json').write_bytes(cleanup_bytes)
        (ev / f'jenkins-app-build-{args.build}.log').write_bytes(log_bytes)
        (ev / 'pipeline-verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return 0 if report['all_passed'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
