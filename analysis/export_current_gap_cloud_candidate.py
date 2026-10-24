"""Export the verified complete-parent batch in an isolated cloud checkout.

Produces a candidate packet/dashboard/index for native and WASM checks. Does
not commit, publish, merge, or redistribute source PDF originals.
"""
import argparse
import datetime
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil

import check_current_gap_parent_rehearsal as rehearsal
import current_gap_candidate_metadata as metadata
import current_gap_index_extension as index_extension

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '.pytest_cache/current-gap-cloud-candidate'


def read_json(path):
    return json.loads((ROOT / path).read_bytes())


def write_json(path, value):
    (ROOT / path).write_bytes(metadata.encoded(value))


def extend_index(dashboard_raw, contracts):
    catalog_path = 'almanac/index-catalog.json'
    corpus_path = 'almanac/index-data.json.gz'
    registry_path = 'almanac/index-sources.json'
    catalog = read_json(catalog_path)
    compressed = (ROOT / corpus_path).read_bytes()
    if metadata.digest(compressed) != catalog['compressed_sha256']:
        raise ValueError('Changed compressed parent index')
    raw = gzip.decompress(compressed)
    if metadata.digest(raw) != catalog['bundle_sha256'] or len(raw) != catalog['bundle_bytes']:
        raise ValueError('Changed logical parent index')
    corpus = json.loads(raw)
    del raw, compressed
    additions = dict(contracts)
    additions[metadata.DASHBOARD] = dashboard_raw
    for contract_raw in contracts.values():
        contract = json.loads(contract_raw)
        paths = set(contract.get('source_documents', []))
        paths.update(path for path in contract.get('input_sha256', {})
                     if path.startswith('research/') and path.endswith('.json'))
        for path in paths:
            raw = (ROOT / path).read_bytes()
            expected = contract.get('input_sha256', {}).get(path)
            if expected is not None and metadata.digest(raw) != expected:
                raise ValueError('Changed candidate index source: ' + path)
            if path in additions and additions[path] != raw:
                raise ValueError('Conflicting candidate index source: ' + path)
            additions[path] = raw
    catalog, corpus, registry, audit = index_extension.extend(
        catalog, corpus, read_json(registry_path), additions)
    raw = (json.dumps(corpus, ensure_ascii=False, separators=(',', ':')) + '\n').encode('utf-8')
    compressed = gzip.compress(raw, compresslevel=9, mtime=0)
    catalog.update(bundle_sha256=metadata.digest(raw), compressed_sha256=metadata.digest(compressed),
                   bundle_bytes=len(raw), compressed_bytes=len(compressed))
    write_json(registry_path, registry)
    catalog['input_sha256'][registry_path] = metadata.digest((ROOT / registry_path).read_bytes())
    for path in ['analysis/current_gap_index_extension.py', 'analysis/export_current_gap_cloud_candidate.py']:
        catalog['input_sha256'][path] = metadata.digest((ROOT / path).read_bytes())
    (ROOT / corpus_path).write_bytes(compressed)
    write_json(catalog_path, catalog)
    return {**audit, 'candidate_source_count': catalog['source_count'],
            'candidate_index_sha256': catalog['bundle_sha256']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cloud-candidate', action='store_true')
    args = parser.parse_args()
    if not args.cloud_candidate or os.environ.get('GITHUB_ACTIONS') != 'true':
        parser.error('Explicit --cloud-candidate in an isolated GitHub Actions checkout required; no full data loaded')
    disk, memory = shutil.disk_usage(ROOT).free, rehearsal.memory_available()
    rehearsal.resources(disk, memory)
    if disk < 3 * 1024**3 or memory < 6 * 1024**3:
        raise SystemExit('Candidate packet and index require3GiB disk and6GiB available memory')
    if hasattr(os, 'sched_getaffinity'):
        os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
        os.nice(5)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    result = {'schema': 'osw.current-gap-cloud-candidate.v1', 'status': 'RUNNING',
              'published': False, 'native_validation_attempted': False,
              'resource_preflight': {'free_disk_bytes': disk, 'available_memory_bytes': memory}}
    def save():
        (OUTPUT / 'result.json').write_bytes(metadata.encoded(result))
    save()
    try:
        from query_packet import load_bundle, write_packet
        from current_gap_width_admission_batch import documents, prepare
        packet_path = ROOT / 'almanac/query-data.json'
        packet = json.loads(packet_path.read_bytes())
        if packet['logical_sha256'] != rehearsal.PARENT_SHA:
            raise ValueError('Unexpected candidate parent')
        parent = load_bundle(packet_path)
        prior = rehearsal.capture_prior(parent['collections'])
        owners = rehearsal.capture_objects(parent['collections']['objects'])
        stage, receipt = prepare(parent['collections'], *documents())
        result['preservation'] = rehearsal.verify_preservation(prior, owners, stage)
        result['batch_receipt'] = receipt
        contracts = {path: (ROOT / path).read_bytes() for path in metadata.CONTRACTS}
        manifest, dashboard_raw = metadata.prepare(parent['manifest'], stage,
            (ROOT / metadata.DASHBOARD).read_bytes(), contracts,
            prepared_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z'))
        result['index_extension'] = extend_index(dashboard_raw, contracts)
        # Keep historical input receipts intact; record the separate delivery
        # operator and the candidate's actually rebuilt presentation artifacts.
        paths = ['analysis/current_gap_candidate_metadata.py', 'analysis/current_gap_index_extension.py',
                 'analysis/export_current_gap_cloud_candidate.py', 'almanac/index-catalog.json',
                 'almanac/index-sources.json', 'almanac/index-data.json.gz']
        for path in paths:
            manifest['input_sha256'][path] = metadata.digest((ROOT / path).read_bytes())
        (ROOT / metadata.DASHBOARD).write_bytes(dashboard_raw)
        candidate = {'schema': parent['schema'], 'manifest': manifest, 'collections': stage}
        raw = (json.dumps(candidate, ensure_ascii=False, separators=(',', ':')) + '\n').encode('utf-8')
        write_packet(packet_path, raw)
        result['candidate'] = {
            'logical_sha256': hashlib.sha256(raw).hexdigest(), 'logical_bytes': len(raw),
            'objects': len(stage['objects']), 'rows': sum(map(len, stage.values())),
            'named_currents': sum(row['type'] == 'named_current' for row in stage['objects'])}
        if sum(receipt['added_rows'].values()) != 79 or result['candidate']['named_currents'] != 106:
            raise ValueError('Unexpected candidate inventory')
        result['candidate_workspace_files_modified'] = True
        result['status'] = 'PASS'
        # Transfer only the new packet's referenced parts, not retained parent
        # parts or any original PDFs. The next cloud job uses a fresh checkout.
        artifact = OUTPUT / 'artifact'
        paths = ['almanac/query-data.json', metadata.DASHBOARD,
                 'almanac/index-catalog.json', 'almanac/index-sources.json', 'almanac/index-data.json.gz']
        paths.extend('almanac/' + row['path'] for row in json.loads(packet_path.read_bytes())['parts'])
        for path in paths:
            target = artifact / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, target)
        result['artifact_paths'] = paths
    except Exception as error:
        result.update(status='FAIL', error=type(error).__name__ + ': ' + str(error))
        save()
        print(json.dumps({k: v for k, v in result.items() if k != 'batch_receipt'}))
        return 1
    save()
    print(json.dumps({k: v for k, v in result.items() if k != 'batch_receipt'}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
