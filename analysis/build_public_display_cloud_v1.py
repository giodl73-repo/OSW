"""Build a frozen-data display view, using one cloud CPU and no scientific operators."""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time
import zipfile

OUT = Path('.pytest_cache/public-display-build-v1')


def main():
    assert os.environ.get('GITHUB_ACTIONS') == 'true'
    assert os.environ.get('OSW_PUBLIC_DISPLAY_BUILD_V1') == '1'
    assert len(os.sched_getaffinity(0)) == 1 and os.getpriority(os.PRIO_PROCESS, 0) >= 15
    assert not OUT.exists()
    OUT.mkdir(parents=True)
    start = time.monotonic()
    report = {'schema': 'osw.public-display-build.v1', 'status': 'FAIL',
              'source_commit': os.environ['GITHUB_SHA'], 'new_measurements': False,
              'full_query_store_replaced': False, 'publication_approved': False}
    commands = [
        ['cargo', 'test', '--locked', '--manifest-path', 'rust/osw-display/Cargo.toml', '--target-dir', str(OUT / 'target')],
        ['cargo', 'run', '--locked', '--manifest-path', 'rust/osw-display/Cargo.toml', '--target-dir', str(OUT / 'target'), '--', '.', str(OUT / 'package')],
    ]
    with (OUT / 'build.log').open('wb') as log:
        try:
            for command in commands:
                remaining = 55 - (time.monotonic() - start)
                if remaining <= 0:
                    raise TimeoutError('Shared 55-second display build budget exhausted')
                process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                try:
                    code = process.wait(timeout=remaining)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                    raise TimeoutError('Display build deadline reached') from None
                if code:
                    raise RuntimeError('Display build or shared geometry test failed')
            built = json.loads((OUT / 'package/build.json').read_bytes())
            assert built['status'] == 'PASS_DISPLAY_EXPORT_ONLY' and built['current_count'] == 111
            assert built['publication_approved'] is False and built['physics_recomputed'] is False
            archive = OUT / 'display-package.zip'
            with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as target:
                for path in sorted((OUT / 'package').rglob('*.json')):
                    target.write(path, path.relative_to(OUT / 'package').as_posix())
            assert archive.stat().st_size <= 2_200_000, 'Display packet exceeds the output ceiling'
            report.update(status='PASS_DISPLAY_CANDIDATE_ONLY', current_count=built['current_count'],
                          object_count=built['object_count'], json_bytes=built['json_bytes'],
                          numeric_values=built['numeric_values'], logical_sha256=built['logical_sha256'],
                          archive_bytes=archive.stat().st_size,
                          archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest())
        except Exception as error:
            report['error'] = str(error)
            (OUT / 'display-package.zip').unlink(missing_ok=True)
            failure = OUT / 'package/failure.json'
            if failure.exists():
                report['export_failure'] = json.loads(failure.read_bytes())
    report['active_seconds'] = time.monotonic() - start
    report['display_geometry_source_sha256'] = {
        path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
        for path in ['rust/osw-query/src/map.rs', 'rust/osw-query/src/cartography.rs']}
    (OUT / 'result.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
    assert (OUT / 'build.log').stat().st_size < 100_000
    print(json.dumps(report))
    if report['status'] != 'PASS_DISPLAY_CANDIDATE_ONLY':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
