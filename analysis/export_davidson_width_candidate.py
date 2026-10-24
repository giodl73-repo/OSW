"""Export one scoped Davidson append from the verified 106-current parent.

Cloud only, one CPU. Original science products and historical transport parts
are preserved. This command does not compile, run a browser, publish or merge.
"""
import argparse
import datetime
import json
import os
from pathlib import Path
import shutil

import check_current_gap_parent_rehearsal as resources
import davidson_wallace_width_admission as admission
import davidson_width_candidate_metadata as metadata

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '.pytest_cache/davidson-width-candidate'
OPERATORS = [
    'analysis/davidson_width_candidate_metadata.py',
    'analysis/test_davidson_width_candidate_metadata.py',
    'analysis/export_davidson_width_candidate.py',
    'analysis/test_davidson_width_candidate_export.py',
    metadata.PARENT_PACKET,
]


def require_cloud(explicit, *, environment, free_disk, available_memory):
    """Fail before loading any packet/index or creating candidate output."""
    if not explicit or environment.get('GITHUB_ACTIONS') != 'true':
        raise ValueError('Explicit isolated cloud export required; no full data loaded')
    if free_disk < 3 * 1024**3 or available_memory is None or available_memory < 6 * 1024**3:
        raise ValueError('Cloud export requires 3 GiB disk and 6 GiB available memory')


def load_parent():
    from query_packet import assemble
    current = json.loads((ROOT / 'almanac/query-data.json').read_bytes())
    installed = json.loads((ROOT / resources.INSTALLED_PROOF).read_bytes())
    metadata.validate_parent(current, installed)
    raw = (ROOT / metadata.PARENT_PACKET).read_bytes()
    if metadata.digest(raw) != metadata.PARENT_PACKET_SHA:
        raise ValueError('Pinned 106-current parent transport changed')
    packet = json.loads(raw)
    metadata.validate_parent(packet, installed)
    folder = (ROOT / 'almanac').resolve()

    def read_part(relative):
        path = (folder / relative).resolve()
        if not path.is_relative_to(folder):
            raise ValueError('Parent transport part leaves atlas directory')
        return path.read_bytes()

    parent = json.loads(assemble(raw, read_part))
    rows = parent['collections']
    if (len(rows['objects']) != metadata.PARENT_OBJECTS
            or sum(len(v) for v in rows.values()) != metadata.PARENT_ROWS
            or sum(row['type'] == 'named_current' for row in rows['objects']) != 106):
        raise ValueError('Assembled parent inventory differs from tested receipt')
    return parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cloud-candidate', action='store_true')
    args = parser.parse_args()
    # Even the memory inspection follows explicit cloud opt-in.
    if not args.cloud_candidate or os.environ.get('GITHUB_ACTIONS') != 'true':
        parser.error('Explicit --cloud-candidate in GitHub Actions required; no full data loaded')
    disk, memory = shutil.disk_usage(ROOT).free, resources.memory_available()
    require_cloud(args.cloud_candidate, environment=os.environ,
                  free_disk=disk, available_memory=memory)
    if hasattr(os, 'sched_getaffinity'):
        os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
        os.nice(5)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    result = {'schema':'osw.davidson-width-candidate.v1', 'status':'RUNNING',
              'published':False, 'parent_logical_sha256':metadata.PARENT_SHA,
              'native_validation_attempted':False,
              'resource_preflight':{'free_disk_bytes':disk, 'available_memory_bytes':memory}}

    def save():
        (OUTPUT / 'result.json').write_bytes(metadata.encoded(result))

    save()
    try:
        from export_current_gap_cloud_candidate import extend_index
        from query_packet import write_packet
        parent = load_parent()
        document = admission.build_contract()
        if (ROOT / admission.FILE).read_bytes() != admission.encoded(document):
            raise ValueError('Changed prepared admission contract')
        manifest, staged, dashboard_raw, receipt = metadata.prepare(
            parent['manifest'], parent['collections'],
            (ROOT / metadata.DASHBOARD).read_bytes(), document,
            prepared_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00','Z'))
        result['admission'] = receipt
        del parent
        # Existing index verifier preserves all old source strings except the
        # explicit dashboard projection. No scientific producer is replayed.
        result['index_extension'] = extend_index(
            dashboard_raw, {admission.FILE:(ROOT / admission.FILE).read_bytes()})
        catalog_path = ROOT / 'almanac/index-catalog.json'
        catalog = json.loads(catalog_path.read_bytes())
        for path in OPERATORS:
            catalog['input_sha256'][path] = metadata.digest((ROOT / path).read_bytes())
        catalog_path.write_bytes(metadata.encoded(catalog))
        index_paths = ['almanac/index-catalog.json', 'almanac/index-sources.json',
                       'almanac/index-data.json.gz']
        for path in [*OPERATORS, *index_paths]:
            manifest['input_sha256'][path] = metadata.digest((ROOT / path).read_bytes())
        (ROOT / metadata.DASHBOARD).write_bytes(dashboard_raw)
        packet_path = ROOT / 'almanac/query-data.json'
        candidate = {'schema':'osw.query-bundle.v1','manifest':manifest,'collections':staged}
        raw = (json.dumps(candidate, ensure_ascii=False, separators=(',',':')) + '\n').encode('utf-8')
        packet = write_packet(packet_path, raw)
        added = sum(receipt['added_rows'].values())
        result['candidate'] = {
            'logical_sha256':metadata.digest(raw),'logical_bytes':len(raw),
            'objects':len(staged['objects']),'rows':sum(len(v) for v in staged.values()),
            'named_currents':sum(row['type'] == 'named_current' for row in staged['objects']),
            'widths':len(staged['widths'])}
        if (added not in (5,6) or result['candidate']['rows'] != metadata.PARENT_ROWS + added
                or result['candidate']['objects'] != metadata.PARENT_OBJECTS
                or result['candidate']['named_currents'] != 106
                or result['candidate']['widths'] != 172):
            raise ValueError('Unexpected Davidson candidate inventory')
        artifact = OUTPUT / 'artifact'
        paths = ['almanac/query-data.json', metadata.DASHBOARD, *index_paths,
                 *['almanac/' + row['path'] for row in packet['parts']]]
        for path in paths:
            target = artifact / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, target)
        result.update(status='PASS', artifact_paths=paths,
                      source_originals_redistributed=False, scientific_release_published=False)
    except Exception as error:
        result.update(status='FAIL', error=type(error).__name__ + ': ' + str(error))
        save()
        raise
    save()
    print(json.dumps({k:v for k,v in result.items() if k != 'admission'}))
    return 0


if __name__ == '__main__':raise SystemExit(main())
