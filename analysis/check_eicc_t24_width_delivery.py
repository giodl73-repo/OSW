"""Read-only scoped-width admission checks; local originals required, no downloads."""
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '.pytest_cache/eicc-t24-width-replay'


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    state = {'schema': 'osw.eicc-t24-width-delivery-replay.v1', 'status': 'RUNNING',
        'canonical_delivery_verified': False, 'original_acquisition_attempted': False, 'stages': []}

    def save():
        (OUTPUT / 'result.json').write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')

    save()
    try:
        commands = [
            ('source_qualified_width_contract', [sys.executable, 'analysis/eicc_t24_width_admission.py', 'check']),
            ('scoped_width_admission_checks', [sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', '--color=no', 'analysis/test_eicc_t24_width_admission.py']),
        ]
        for stage, command in commands:
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
            (OUTPUT / (stage + '.log')).write_text(result.stdout + result.stderr, encoding='utf-8')
            item = {'stage': stage, 'exit_code': result.returncode, 'status': 'PASS' if result.returncode == 0 else 'FAIL'}
            state['stages'].append(item)
            save()
            if result.returncode:
                raise RuntimeError(stage + ' failed; see retained log')
            if stage == 'scoped_width_admission_checks':
                match = re.search(r'\b(\d+) passed\b', result.stdout)
                if not match or int(match.group(1)) != 16 or re.search(r'\b(skipped|xfailed|xpassed)\b', result.stdout):
                    raise ValueError('Complete16-check scoped width pass is not established')
                item['checks_passed'] = 16
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
