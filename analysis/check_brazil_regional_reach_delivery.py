"""Read-only source/product replay; original acquisition is an explicit option."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT/'.pytest_cache/brazil-regional-reach-replay'
TESTS = ['analysis/test_published_current_regional_reaches_v2.py',
         'analysis/test_published_current_regional_reaches_v2_admission.py',
         'analysis/test_brazil_regional_reach_query.py', 'analysis/test_object_source_links.py']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--acquire-original', action='store_true',
                        help='Explicitly hydrate the ignored, checksum-pinned textbook original first')
    args = parser.parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    state = {'schema': 'osw.brazil-regional-reach-delivery-replay.v1', 'status': 'RUNNING',
             'python': sys.version, 'platform': platform.platform(),
             'started_utc': datetime.now(timezone.utc).isoformat(),
             'source_acquisition_requested': args.acquire_original, 'stages': [],
             'canonical_admission_verified': False}

    def save():
        (OUTPUT/'result.json').write_text(json.dumps(state, indent=2)+'\n', encoding='utf8')

    save()
    try:
        if args.acquire_original:
            from acquire_local_paper_fixtures import acquire
            raw = acquire('tomczak-regional-2005', ROOT/'research/source-data/tomczak-regional-2005')
            state['stages'].append({'stage': 'explicit_original_acquisition', 'status': 'PASS',
                                    'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
            del raw
            save()
        commands = [
            ('frozen_source_report_and_figure', [sys.executable, 'analysis/published_current_regional_reaches_v2.py', 'check']),
            ('prepared_query_contract', [sys.executable, 'analysis/brazil_regional_reach_query.py', 'check']),
            ('focused_source_and_projection_checks', [sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', '--color=no', *TESTS])]
        for stage, command in commands:
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding='utf8')
            (OUTPUT/(stage+'.log')).write_text(result.stdout+result.stderr, encoding='utf8')
            record = {'stage': stage, 'exit_code': result.returncode, 'status': 'PASS' if result.returncode == 0 else 'FAIL'}
            if stage == 'focused_source_and_projection_checks' and result.returncode == 0:
                match = re.search(r'\b(\d+) passed\b', result.stdout)
                if not match or int(match.group(1)) < 63 or re.search(r'\b(skipped|xfailed|xpassed)\b', result.stdout):
                    raise ValueError('Complete focused suite pass is not established')
                record['checks_passed'] = int(match.group(1))
            state['stages'].append(record)
            save()
            if result.returncode:
                raise RuntimeError(stage+' failed; see retained stage log')
        state['status'] = 'PASS'
    except Exception as error:
        state.update(status='FAIL', error=type(error).__name__+': '+str(error))
        save()
        print(json.dumps(state))
        return 1
    save()
    print(json.dumps(state))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
