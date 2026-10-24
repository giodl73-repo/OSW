"""Cloud-only coastal context export; no original data extraction or publishing."""
import argparse
import datetime
import json
import os
from pathlib import Path
import shutil

import indian_coastal_dimension_context_v1 as context
import indian_coastal_context_candidate as metadata
import check_current_gap_parent_rehearsal as resources
from export_davidson_width_candidate import require_cloud

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '.pytest_cache/indian-coastal-context-candidate'
OPERATORS = ['analysis/indian_coastal_context_candidate.py',
             'analysis/test_indian_coastal_context_candidate.py',
             'analysis/export_indian_coastal_context_candidate.py',
             'analysis/test_indian_coastal_context_export.py',
             'analysis/current_gap_index_extension.py', 'analysis/build_rust_query_engine.py',
             'rust/osw-query/src/indian_coastal_context.rs', 'rust/osw-query/src/lib.rs',
             'almanac/current-source-evidence-ui.js', metadata.PARENT_PROOF]


def load_parent():
    from query_packet import assemble
    if context.pin(metadata.PARENT_PROOF) != metadata.PARENT_PROOF_SHA:
        raise ValueError('Installed Baffin proof changed')
    proof = json.loads((ROOT / metadata.PARENT_PROOF).read_bytes())
    raw = (ROOT / 'almanac/query-data.json').read_bytes()
    packet = json.loads(raw)
    metadata.validate_parent(packet, proof)
    for path in ['almanac/query-data.json', 'almanac/index-catalog.json', 'almanac/index-sources.json',
                 'almanac/index-data.json.gz', metadata.DASHBOARD]:
        if context.pin(path) != proof['generated_sha256'].get(path):
            raise ValueError('Installed parent descriptor/index/dashboard changed: ' + path)
    folder = (ROOT / 'almanac').resolve()
    def read_part(relative):
        path = (folder / relative).resolve()
        if not path.is_relative_to(folder):raise ValueError('Parent part leaves atlas directory')
        return path.read_bytes()
    parent = json.loads(assemble(raw, read_part))
    rows = parent['collections']
    if (len(rows['objects']) != 246 or sum(map(len, rows.values())) != 108544
            or len(rows['widths']) != 172 or sum(row['type'] == 'named_current' for row in rows['objects']) != 106):
        raise ValueError('Assembled parent inventory differs from installed proof')
    return packet, parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cloud-candidate', action='store_true')
    args = parser.parse_args()
    if not args.cloud_candidate or os.environ.get('GITHUB_ACTIONS') != 'true':
        parser.error('Explicit --cloud-candidate in GitHub Actions required; no full data loaded')
    disk, memory = shutil.disk_usage(ROOT).free, resources.memory_available()
    require_cloud(args.cloud_candidate, environment=os.environ, free_disk=disk, available_memory=memory)
    if hasattr(os, 'sched_getaffinity'):
        os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
        os.nice(5)
    contract, contract_hash = context.evidence()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    result = {'schema': 'osw.indian-coastal-context-candidate.v1', 'status': 'RUNNING',
              'published': False, 'contract_sha256': contract_hash,
              'native_validation_attempted': False,
              'resource_preflight': {'free_disk_bytes': disk, 'available_memory_bytes': memory}}
    def save():
        (OUTPUT / 'result.json').write_bytes(metadata.encoded(result))
    save()
    try:
        from export_current_gap_cloud_candidate import extend_index
        from query_packet import write_packet
        parent_packet, parent = load_parent()
        manifest, staged, dashboard_raw, receipt = metadata.prepare(
            parent['manifest'], parent['collections'],
            parent['manifest']['dashboard_receipt']['source_json'].encode('utf8'), contract,
            prepared_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z'))
        result.update(parent_logical_sha256=parent_packet['logical_sha256'], admission=receipt)
        del parent
        sources = {path: (ROOT / path).read_bytes() for path in contract['source_documents']}
        result['index_extension'] = extend_index(dashboard_raw, sources)
        catalog_path = ROOT / 'almanac/index-catalog.json'
        catalog = json.loads(catalog_path.read_bytes())
        for path in OPERATORS:catalog['input_sha256'][path] = context.pin(path)
        catalog_path.write_bytes(metadata.encoded(catalog))
        index_paths = ['almanac/index-catalog.json', 'almanac/index-sources.json', 'almanac/index-data.json.gz']
        for path in [context.FILE, *OPERATORS, *index_paths]:manifest['input_sha256'][path] = context.pin(path)
        (ROOT / metadata.DASHBOARD).write_bytes(dashboard_raw)
        raw = (json.dumps({'schema': 'osw.query-bundle.v1', 'manifest': manifest, 'collections': staged},
                          ensure_ascii=False, separators=(',', ':')) + '\n').encode('utf8')
        packet = write_packet(ROOT / 'almanac/query-data.json', raw)
        result['candidate'] = {'logical_sha256': metadata.digest(raw), 'logical_bytes': len(raw),
                               'objects': len(staged['objects']), 'rows': sum(map(len, staged.values())),
                               'named_currents': sum(row['type'] == 'named_current' for row in staged['objects']),
                               'widths': len(staged['widths'])}
        c = result['candidate']
        if c['rows'] != 108551 or c['objects'] != 246 or c['named_currents'] != 106 or c['widths'] != 172:
            raise ValueError('Unexpected coastal source-context candidate inventory')
        artifact = OUTPUT / 'artifact'
        paths = ['almanac/query-data.json', metadata.DASHBOARD, *index_paths,
                 *['almanac/' + row['path'] for row in packet['parts']]]
        for path in paths:
            destination = artifact / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, destination)
        result.update(status='PASS', artifact_paths=paths, source_originals_redistributed=False,
                      scientific_release_published=False)
    except Exception as error:
        result.update(status='FAIL', error=type(error).__name__ + ': ' + str(error))
        save()
        raise
    save()
    print(json.dumps({key: value for key, value in result.items() if key != 'admission'}))


if __name__ == '__main__':
    main()
