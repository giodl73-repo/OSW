"""One cloud-only sequential native source check; no packet, WASM or browser."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REQUEST = 'research/south-java-runtime-cloud-request-v2.json'
PREFLIGHT = 'research/south-java-runtime-cloud-preflight-v2.json'
WORKFLOW = '.github/workflows/south-java-runtime-cloud-v2.yml'
OUTPUT = ROOT / '.pytest_cache/south-java-runtime-cloud-v2'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(name, value):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / name).write_bytes((json.dumps(value, indent=2, allow_nan=False) + '\n').encode())


def controls():
    if (os.name != 'posix' or os.environ.get('GITHUB_ACTIONS') != 'true'
            or os.environ.get('GITHUB_REPOSITORY') != 'giodl73-repo/OSW'
            or os.environ.get('GITHUB_REF') != 'refs/heads/codex/current-measurement-gaps'
            or os.environ.get('GITHUB_EVENT_NAME') != 'push'):
        raise ValueError('Cloud working-branch source-check push required')
    if len(os.sched_getaffinity(0)) != 1 or os.getpriority(os.PRIO_PROCESS, 0) < 15:
        raise ValueError('One CPU and nice15 required')
    for key in ['CARGO_BUILD_JOBS', 'RUST_TEST_THREADS', 'OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
                'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS']:
        if os.environ.get(key) != '1':
            raise ValueError('Single worker required: ' + key)
    request = json.loads((ROOT / REQUEST).read_bytes())
    if (request.get('schema') != 'osw.south-java-runtime-cloud-request.v2'
            or request.get('workflow') != WORKFLOW or request.get('execute') is not True
            or request.get('max_cloud_jobs') != 1 or request.get('max_heavy_local_jobs') != 0
            or request.get('native_source_test_build_permitted') is not True):
        raise ValueError('Exact native source-check request is disabled or invalid')
    for key in ['wasm_build_permitted', 'packet_or_index_load_permitted', 'browser_permitted',
                'ocean_field_processing_permitted', 'working_branch_installation_permitted',
                'local_bulk_sync_permitted', 'main_merge_permitted']:
        if request.get(key) is not False:
            raise ValueError('Forbidden source-check permission: ' + key)
    phase = json.loads((ROOT / 'research/current-gap-delivery-phase.json').read_bytes())
    if phase.get('phase') != 'source-review-only-v1' or phase.get('heavy_work_permitted') is not False:
        raise ValueError('Global phase must remain source-review-only and disabled')
    if sha(ROOT / PREFLIGHT) != request.get('preflight_sha256'):
        raise ValueError('Changed frozen source-check preflight')
    preflight = json.loads((ROOT / PREFLIGHT).read_bytes())
    for path, expected in preflight['input_sha256'].items():
        if sha(ROOT / path) != expected:
            raise ValueError('Changed source-check input: ' + path)
    head = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    remote = json.loads(subprocess.check_output(['gh', 'api',
        'repos/giodl73-repo/OSW/git/ref/heads/codex/current-measurement-gaps']))['object']['sha']
    if head != os.environ.get('GITHUB_SHA') or remote != head:
        raise ValueError('Exact current working-branch checkout required')
    if subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'status', '--porcelain'], cwd=ROOT).strip():
        raise ValueError('Clean checkout required before source check')
    import south_java_reference_runtime_v1 as runtime
    import south_java_reference_runtime_scope_v1 as scope
    if (ROOT / runtime.FILE).read_bytes() != runtime.query.encoded(runtime.build_contract()):
        raise ValueError('Saved runtime contract differs')
    if (ROOT / scope.FILE).read_bytes() != runtime.query.encoded(scope.build()):
        raise ValueError('Saved source scope differs')
    write('preflight.json', {'status': 'PASS', 'source_commit': head,
          'run_id': os.environ.get('GITHUB_RUN_ID'), 'run_attempt': os.environ.get('GITHUB_RUN_ATTEMPT'),
          'preflight_sha256': sha(ROOT / PREFLIGHT), 'input_count': len(preflight['input_sha256']),
          'cpu_count': 1, 'nice': os.getpriority(os.PRIO_PROCESS, 0), 'packet_loaded': False})
    return head


def command(args, name, input_bytes=None):
    result = subprocess.run(args, cwd=ROOT, input=input_bytes, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    raw = result.stdout
    (OUTPUT / name).write_bytes(raw)
    print(raw.decode('utf-8', errors='replace'), flush=True)
    if result.returncode:
        raise ValueError('Source check failed: ' + name)
    return raw.decode('utf-8', errors='replace')


def tests():
    head = controls()
    command(['python', '-m', 'unittest', 'test_south_java_reference_runtime_v1.RuntimeProjection',
             'test_south_java_reference_query_v1.ReferenceAdmission', '-v'], 'python-tests.txt')
    command(['node', '--input-type=module', '--check'], 'atlas-js-syntax.txt',
        input_bytes=(ROOT / 'almanac/reference-routes.js').read_bytes())
    compiler = subprocess.check_output(['rustc', '+1.95.0', '--version']).decode().strip()
    if not compiler.startswith('rustc 1.95.0 '):
        raise ValueError('Exact pinned compiler required')
    checks = {}
    for namespace, name, expected in [('south_java_reference::tests', 'south-java', 5),
        ('pacific_secc_reference::tests', 'pacific', 5), ('planning::tests', 'planning', 6),
        ('nwasc_reference_route::tests', 'nwasc', 4), ('madagascar_coastal_curve::tests', 'coastal', 4)]:
        text = command(['cargo', '+1.95.0', 'test', '--locked', '--manifest-path',
            'rust/osw-query/Cargo.toml', '--lib', namespace, '--', '--test-threads=1'], name + '-tests.txt')
        matched = re.search(r'test result: ok\. (\d+) passed; 0 failed;', text)
        if not matched or int(matched.group(1)) != expected:
            raise ValueError('No verified passing test inventory: ' + namespace)
        checks[namespace] = int(matched.group(1))
    write('result.json', {'schema': 'osw.south-java-runtime-cloud-result.v2', 'status': 'PASS',
        'source_commit': head, 'run_id': os.environ['GITHUB_RUN_ID'], 'run_attempt': os.environ['GITHUB_RUN_ATTEMPT'],
        'compiler': compiler, 'rust_test_counts': checks, 'python_tests_passed': 12,
        'packet_or_index_loaded': False, 'wasm_built': False, 'browser_run': False,
        'scientific_data_changed': False, 'working_branch_installed': False,
        'outputs': {p.name: sha(p) for p in OUTPUT.iterdir() if p.is_file() and p.name != 'result.json'}})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['preflight', 'tests'])
    args = parser.parse_args()
    try:
        if args.action == 'preflight':
            controls()
        else:
            tests()
    except Exception as error:
        # Never create outputs on a local refusal.
        if os.environ.get('GITHUB_ACTIONS') == 'true' and os.name == 'posix':
            write('failure.json', {'status': 'FAIL', 'error': str(error),
                  'source_commit': os.environ.get('GITHUB_SHA'), 'installed': False})
        raise
