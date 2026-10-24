"""Explicit cloud-sized rehearsal against the exact existing logical packet.

This validates admission and old-row preservation. It publishes no packet and
does not claim the old native engine accepts the new collections/identities.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
PARENT_SHA = '5ea582e44f8fd88d736d9ddf9c46fb52fad8e9c4cdca74f6130da10d979a2345'
OUTPUT = ROOT / '.pytest_cache/current-gap-parent-rehearsal'
OWNER_METADATA = {
    'source_ids', 'linked_source_count', 'fingerprint', 'section_fingerprints',
    'regional_reach_ids', 'evidence_links', 'regional_reach_scope_note',
    'recorded_claims', 'claim_review_counts', 'capabilities',
}


def hash_rows(rows):
    encoder = json.JSONEncoder(sort_keys=True, ensure_ascii=True, separators=(',', ':'), allow_nan=False)
    digest = hashlib.sha256()
    for row in rows:
        for chunk in encoder.iterencode(row):
            digest.update(chunk.encode('utf-8'))
        digest.update(b'\n')
    return digest.hexdigest()


def capture_prior(collections):
    return {name: {'rows': len(rows), 'canonical_rows_sha256': hash_rows(rows)}
            for name, rows in collections.items() if name != 'objects'}


def capture_objects(rows):
    return [{'id': row['id'],
             'physical_fields_sha256': hash_rows([{k: v for k, v in row.items() if k not in OWNER_METADATA}]),
             'content_sha256': hash_rows([{k: v for k, v in row.items() if k not in ('fingerprint', 'section_fingerprints')}]),
             'fingerprint': row.get('fingerprint'),
             'section_fingerprints': copy.deepcopy(row.get('section_fingerprints')),
             'capabilities': dict(row.get('capabilities', {}))} for row in rows]


def verify_preservation(prior, old_objects, candidate):
    for name, expected in prior.items():
        rows = candidate.get(name, [])
        if len(rows) < expected['rows'] or hash_rows(rows[:expected['rows']]) != expected['canonical_rows_sha256']:
            raise ValueError('Prior rows changed or erased: ' + name)
    index = {row['id']: row for row in candidate['objects']}
    unchanged_fingerprints = 0
    for old in old_objects:
        new = index.get(old['id'])
        if new is None:
            raise ValueError('Prior object erased')
        if hash_rows([{k: v for k, v in new.items() if k not in OWNER_METADATA}]) != old['physical_fields_sha256']:
            raise ValueError('Prior physical/object field changed: ' + old['id'])
        for key, value in old.get('capabilities', {}).items():
            if new.get('capabilities', {}).get(key) != value:
                raise ValueError('Prior physical capability changed: ' + old['id'] + '/' + key)
        content = {k: v for k, v in new.items() if k not in ('fingerprint', 'section_fingerprints')}
        if hash_rows([content]) == old['content_sha256']:
            if new.get('fingerprint') != old['fingerprint'] or new.get('section_fingerprints') != old['section_fingerprints']:
                raise ValueError('Unchanged object spuriously marked updated: ' + old['id'])
            unchanged_fingerprints += 1
    return {'prior_collections_verified': len(prior), 'prior_rows_verified': sum(item['rows'] for item in prior.values()),
            'prior_objects_verified': len(old_objects), 'all_prior_nonobject_rows_exact': True,
            'unchanged_object_fingerprints_verified': unchanged_fingerprints,
            'prior_physical_object_fields_and_capabilities_exact': True}


def resources(free_disk, available_memory):
    if free_disk < 2 * 1024**3:
        raise ValueError('Full parent rehearsal requires at least2GiB free disk; no packet loaded')
    if available_memory is None or available_memory < 3 * 1024**3:
        raise ValueError('Full parent rehearsal requires at least3GiB available memory; no packet loaded')


def memory_available():
    # The automated full-packet operation is run on the Linux CI source runner.
    path = Path('/proc/meminfo')
    if not path.exists():
        return None
    for line in path.read_text().splitlines():
        if line.startswith('MemAvailable:'):
            return int(line.split()[1]) * 1024
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--full-parent', action='store_true', help='Explicitly opt into the resource-gated full-packet cloud rehearsal')
    if not parser.parse_args().full_parent:
        parser.error('Explicit --full-parent is required; no packet loaded')
    OUTPUT.mkdir(parents=True, exist_ok=True)
    result = {'schema': 'osw.current-gap-parent-rehearsal.v1', 'status': 'RUNNING',
              'canonical_delivery_verified': False, 'native_validation_attempted': False,
              'published_files_modified': False}
    def save():
        (OUTPUT / 'result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    save()
    try:
        disk, memory = shutil.disk_usage(ROOT).free, memory_available()
        result['resource_preflight'] = {'free_disk_bytes': disk, 'available_memory_bytes': memory}
        resources(disk, memory)
        if hasattr(os, 'sched_getaffinity'):
            os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
            os.nice(5)
        packet_path = ROOT / 'almanac/query-data.json'
        packet = json.loads(packet_path.read_bytes())
        if packet.get('logical_sha256') != PARENT_SHA:
            raise ValueError('Unexpected parent packet; source review required')
        from query_packet import load_bundle
        from current_gap_width_admission_batch import documents, prepare
        parent = load_bundle(packet_path)
        collections = parent['collections']
        result['parent'] = {'logical_sha256': PARENT_SHA, 'logical_bytes': packet['logical_byte_length'],
            'collections': len(collections), 'rows': sum(map(len, collections.values())), 'objects': len(collections['objects'])}
        prior = capture_prior(collections)
        prior_objects = capture_objects(collections['objects'])
        stage, receipt = prepare(collections, *documents())
        result['preservation'] = verify_preservation(prior, prior_objects, stage)
        result['batch_receipt'] = receipt
        result['candidate'] = {'collections': len(stage), 'rows': sum(map(len, stage.values())),
            'objects': len(stage['objects']), 'named_currents': sum(row['type'] == 'named_current' for row in stage['objects']),
            'scoped_width_records': len(stage['widths']),
            'source_count_reference_mismatches': sum(row['linked_source_count'] != len(row['source_ids']) for row in stage['objects'])}
        if sum(receipt['added_rows'].values()) != 79 or result['candidate']['source_count_reference_mismatches']:
            raise ValueError('Unexpected admission size or unresolved owner source counts')
        result['prior_collection_hashes'] = prior
        result['required_native_changes'] = [
            'Compile exact guards for the new identities, source contexts and T24 width; preserve old guards.',
            'Extend effective current catalogue, seasonal widths/decisions and per-current measurement ownership.',
            'Read the four route-gap decisions from their separately pinned planning worklist.',
            'Refresh dashboard/taxonomy/source/index receipts and remove the dashboard source-list alias.',
            'Verify native/WASM queries and accessible cards/maps before publishing any candidate packet.',
        ]
        import resource
        result['peak_process_rss_kib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        result['status'] = 'PASS'
    except Exception as error:
        result.update(status='FAIL', error=type(error).__name__ + ': ' + str(error))
        save()
        print(json.dumps({key: value for key, value in result.items() if key != 'batch_receipt'}))
        return 1
    save()
    print(json.dumps({key: value for key, value in result.items() if key not in ('batch_receipt', 'prior_collection_hashes')}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
