"""Strict complete actual-source derived-report byte reproduction."""
import hashlib
import json

from build_south_indian_front_temperature import ROOT, REPORT, build
from inspect_scientific_reproduction import differences


def main():
    retained = (ROOT/REPORT).read_bytes()
    document = build()
    rebuilt = (json.dumps(document, indent=2, allow_nan=False)+'\n').encode()
    exact = retained == rebuilt
    result = {'status': 'PASS' if exact else 'FAIL',
              'actual_source_report_bytes_exact': exact,
              'retained_sha256': hashlib.sha256(retained).hexdigest(),
              'rebuilt_sha256': hashlib.sha256(rebuilt).hexdigest(),
              'months': len(document['months']), 'native_depths_m': document['depth_m'],
              'source_daily_timestamps': sum(m['sample_days'] for m in document['months']),
              'network_requests': 0,
              'physical_width_admitted': document['physical_width_admitted']}
    if not exact:
        result['differences'] = differences(json.loads(retained), document)
    print(json.dumps(result, indent=2, allow_nan=False))
    if not exact: raise SystemExit(1)
    return result


if __name__ == '__main__':
    main()
