"""Run the independent UI byte audit on one idle cloud CPU with a hard deadline."""
import json
import os
from pathlib import Path
import signal
import subprocess
import time

OUT = Path('.pytest_cache/public-atlas-transport-v1')


def main():
    assert os.environ.get('GITHUB_ACTIONS') == 'true'
    assert os.environ.get('OSW_PUBLIC_ATLAS_TRANSPORT_V1') == '1'
    assert len(os.sched_getaffinity(0)) == 1 and os.getpriority(os.PRIO_PROCESS, 0) >= 15
    assert not OUT.exists(), 'Fresh diagnostic output required'
    OUT.mkdir(parents=True)
    start = time.monotonic()
    with (OUT / 'phases.jsonl').open('wb') as log:
        process = subprocess.Popen(['node', 'analysis/audit_public_atlas_transport_v1.mjs'], stdout=log,
                                   stderr=subprocess.STDOUT, start_new_session=True)
        try:
            code = process.wait(timeout=55)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            code = 124
    report = OUT / 'result.json'
    if code or not report.exists():
        report.write_text(json.dumps({'schema': 'osw.public-atlas-transport-audit.v1', 'status': 'FAIL',
                                     'source_commit': os.environ['GITHUB_SHA'], 'exit_code': code,
                                     'active_seconds': time.monotonic() - start,
                                     'scientific_field_processing': False, 'publication_approved': False}, indent=2) + '\n', encoding='utf8')
    assert sum(p.stat().st_size for p in OUT.iterdir()) < 200_000, 'Metadata only'
    print(report.read_text(encoding='utf8')[:600])
    raise SystemExit(0 if code == 0 else 1)


if __name__ == '__main__':
    main()
