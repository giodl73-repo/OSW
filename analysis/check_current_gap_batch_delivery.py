"""Read-only replay of the compatible source contracts and atomic admission checks."""
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '.pytest_cache/current-gap-batch-replay'


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    state = {'schema': 'osw.current-gap-batch-delivery-replay.v1', 'status': 'RUNNING',
        'canonical_delivery_verified': False, 'complete_runtime_audit_verified': False,
        'original_acquisition_attempted': False, 'stages': []}

    def save():
        (OUTPUT / 'result.json').write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')

    save()
    try:
        commands = [
            ('prepared_indian_identity_and_evidence_contracts', [sys.executable, 'analysis/indian_current_evidence_query.py', 'check']),
            ('prepared_brazil_reach_contract', [sys.executable, 'analysis/brazil_regional_reach_query.py', 'check']),
            ('atomic_batch_checks', [sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', '--color=no', 'analysis/test_current_gap_admission_batch.py']),
        ]
        for stage, command in commands:
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
            (OUTPUT / (stage + '.log')).write_text(result.stdout + result.stderr, encoding='utf-8')
            item = {'stage': stage, 'exit_code': result.returncode, 'status': 'PASS' if result.returncode == 0 else 'FAIL'}
            state['stages'].append(item)
            save()
            if result.returncode:
                raise RuntimeError(stage + ' failed; see retained log')
            if stage == 'atomic_batch_checks':
                match = re.search(r'\b(\d+) passed\b', result.stdout)
                if not match or int(match.group(1)) != 19 or re.search(r'\b(skipped|xfailed|xpassed)\b', result.stdout):
                    raise ValueError('Complete19-check batch pass is not established')
                item['checks_passed'] = 19
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
