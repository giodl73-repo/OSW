"""Bounded read of existing eddy eligibility and independent-case descriptors only."""
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import signal
import time

from compiled_depth_catalog_query_guard_v3 import DescriptorQuery

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.pytest_cache/eddy-public-case-metadata-v1'



def case_metadata(value):
    if not isinstance(value, dict):
        return None
    labels = {'name', 'source_name', 'source_case_name', 'label', 'case_label', 'identity_status',
              'source_name_match', 'source_kind', 'source_access', 'source_id', 'source_url',
              'source_locator', 'source_file', 'source_pointer', 'source_year', 'source_publication_year'}
    out = {'schema_fields': sorted(value)}
    for key, item in value.items():
        if isinstance(item, bool):
            out[key] = item
        elif key in labels and isinstance(item, (str, int)):
            out[key] = item
        elif isinstance(item, dict):
            child = case_metadata(item)
            if len(child) > 1:
                out[key] = child
    return out


def main():
    assert os.environ.get('GITHUB_ACTIONS') == 'true'
    assert len(os.sched_getaffinity(0)) == 1 and os.getpriority(os.PRIO_PROCESS, 0) >= 15
    assert not OUT.exists()
    OUT.mkdir(parents=True)
    started = time.monotonic()
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError('Shared source-use review deadline')))
    signal.alarm(54)
    save = lambda value: (OUT / 'query-ledger.json').write_text(json.dumps(value, indent=2) + '\n', encoding='utf8')
    # Conservative bounds carry the preceding 5 MB display-source inventory,
    # including its numeric metadata, rather than resetting the same review.
    query = DescriptorQuery(save, prior_numeric=100_000, prior_bytes=6_000_000)
    path = 'research/eddy-measurement-register-v1.json'
    reader = query.reader(lambda p: (ROOT / p).read_bytes())
    raw = reader(path)
    with query.decoding():
        doc = json.loads(raw)
    assert doc['schema'] == 'osw.eddy-measurement-register.v1'
    evidence = doc['evidence']
    cases = []
    for row in evidence:
        independent = case_metadata(row.get('independent_named_case'))
        association = case_metadata(row.get('named_case_association'))
        cases.append({'id': row['id'], 'entity_id': row['entity_id'], 'category': row.get('category'),
                      'metric': row.get('metric'), 'evidence_role': row.get('evidence_role'),
                      'rights_screened_release_eligible': row.get('rights_screened_release_eligible'),
                      'source_url': row.get('source_url'), 'source_access': row.get('source_access'),
                      'source_locator': row.get('source_locator'),
                      'independent_named_case': independent, 'named_case_association': association})
    report = {'schema': 'osw.eddy-public-case-metadata.v1', 'status': 'ELIGIBILITY_METADATA_ONLY_NOT_A_NEW_RELEASE_DECISION',
              'source_commit': os.environ['GITHUB_SHA'], 'register_sha256': hashlib.sha256(raw).hexdigest(),
              'register_counts': doc['counts'], 'register_identity_rule': doc['identity_rule'],
              'register_release_scope': doc['release_scope'],
              'record_schema_fields': sorted({k for row in doc['records'] for k in row}),
              'evidence_schema_fields': sorted({k for row in evidence for k in row}),
              'eligible_size_owner_count': len({r['entity_id'] for r in evidence if r.get('category') == 'size' and r.get('rights_screened_release_eligible') is True}),
              'eligibility_by_role': {str(key): dict(value) for key, value in
                                      ((role, Counter(str(r.get('rights_screened_release_eligible')) for r in evidence if r.get('evidence_role') == role))
                                       for role in sorted({str(r.get('evidence_role')) for r in evidence}))},
              'cases': cases, 'physical_values_or_new_measurements_emitted': False,
              'previous_source_inventory_active_seconds': 0.3673168720000035,
              'active_seconds': time.monotonic() - started,
              'provider_requests': 0, 'publication_approved': False}
    output = (json.dumps(report, indent=2) + '\n').encode('utf8')
    assert len(output) < 2_400_000
    (OUT / 'result.json').write_bytes(output)
    signal.alarm(0)
    print(json.dumps({'status': report['status'], 'evidence_rows': len(cases), 'eligible_size_owners': report['eligible_size_owner_count'], 'active_seconds': report['active_seconds']}))


if __name__ == '__main__':
    main()
