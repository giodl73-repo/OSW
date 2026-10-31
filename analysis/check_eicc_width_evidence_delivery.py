"""Read-only width source replay, with explicitly requested original hydration."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '.pytest_cache/eicc-width-source-replay'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--acquire-original', action='store_true')
    args = parser.parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    state = {
        'schema': 'osw.eicc-width-evidence-delivery-replay.v1',
        'status': 'RUNNING', 'started_utc': datetime.now(timezone.utc).isoformat(),
        'source_acquisition_requested': args.acquire_original,
        'canonical_admission_verified': False, 'stages': [],
    }

    def save():
        (OUTPUT / 'result.json').write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')

    save()
    try:
        if args.acquire_original:
            from acquire_local_paper_fixtures import acquire
            data = acquire('wijesekera-eicc-2015', ROOT / 'research/source-data/wijesekera-eicc-2015')
            state['stages'].append({
                'stage': 'explicit_original_acquisition', 'status': 'PASS',
                'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
            })
            del data
            save()
        commands = [
            ('frozen_source_report_and_figure', [sys.executable, 'analysis/reported_current_width_evidence_v1.py', 'check']),
            ('focused_source_and_product_checks', [sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', '--color=no',
                'analysis/test_reported_current_width_evidence_v1.py', 'analysis/test_eicc_width_evidence_admission.py']),
        ]
        for stage, command in commands:
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
            (OUTPUT / (stage + '.log')).write_text(result.stdout + result.stderr, encoding='utf-8')
            record = {'stage': stage, 'exit_code': result.returncode, 'status': 'PASS' if result.returncode == 0 else 'FAIL'}
            state['stages'].append(record)
            save()
            if result.returncode:
                raise RuntimeError(stage + ' failed; see stage log')
            if stage == 'focused_source_and_product_checks':
                match = re.search(r'\b(\d+) passed\b', result.stdout)
                if not match or int(match.group(1)) != 31 or re.search(r'\b(skipped|xfailed|xpassed)\b', result.stdout):
                    raise ValueError('Complete31-check source replay is not established')
                record['checks_passed'] = 31
        state['status'] = 'PASS'
    except Exception as error:
        state.update(status='FAIL', error=type(error).__name__ + ': ' + str(error))
        save()
        print(json.dumps(state))
        return 1
    save()
    print(json.dumps(state))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
