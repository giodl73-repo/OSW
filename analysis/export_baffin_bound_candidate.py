"""Cloud-only Baffin candidate export from the installed Davidson working cohort.

No original science producer is replayed. No native/browser process is started,
and nothing is published or merged. Full-packet and index work is cloud gated.
"""
import argparse
import datetime
import json
import os
from pathlib import Path
import shutil

import baffin_bound_admission as admission
import baffin_bound_owner_projection as owner
import baffin_bound_candidate_metadata as metadata
import check_current_gap_parent_rehearsal as resources
from export_davidson_width_candidate import require_cloud

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '.pytest_cache/baffin-bound-candidate'
OPERATORS = [
    admission.ADAPTER, 'analysis/test_baffin_bound_admission.py',
    owner.OPERATOR, 'analysis/test_baffin_bound_owner_projection.py',
    'analysis/baffin_bound_candidate_metadata.py', 'analysis/test_baffin_bound_candidate_metadata.py',
    'analysis/export_baffin_bound_candidate.py', 'analysis/test_baffin_bound_candidate_export.py',
    'analysis/build_rust_query_engine.py',
    'rust/osw-query/src/baffin_latitude_bound.rs', 'rust/osw-query/src/lib.rs',
    'rust/osw-query/src/length_assessment_overlays.rs', 'rust/osw-query/src/object_view.rs',
    'rust/osw-query/src/current_gap_admissions.rs', 'rust/osw-query/src/seasons_data.rs',
    'almanac/current-source-evidence-ui.js', 'almanac/object.html', metadata.PARENT_PROOF,
    'analysis/run_rust_query_browser_checks.py', 'analysis/test_baffin_bound_browser.py',
    'analysis/test_baffin_bound_browser_policy.py', 'analysis/test_labrador_gate_bound_browser.py',
    'analysis/browser_current_catalogue_fixture.py', 'analysis/test_browser_current_catalogue_fixture.py',
    'analysis/test_nwasc_reference_route_browser.py',
    'analysis/prepare_baffin_bound_delivery.py', 'analysis/test_baffin_bound_delivery.py',
    '.github/workflows/baffin-bound-candidate.yml', 'research/current-gap-delivery-phase.json',
]


def load_parent():
    from query_packet import assemble
    packet_raw = (ROOT / 'almanac/query-data.json').read_bytes()
    packet = json.loads(packet_raw)
    installed = json.loads((ROOT / metadata.PARENT_PROOF).read_bytes())
    metadata.validate_parent(packet, installed)
    pins = installed.get('generated_sha256', {})
    if metadata.digest(packet_raw) != pins.get('almanac/query-data.json'):
        raise ValueError('Changed installed parent packet descriptor')
    for path in ['almanac/index-catalog.json','almanac/index-sources.json','almanac/index-data.json.gz',metadata.DASHBOARD]:
        if admission.pin(path) != pins.get(path):
            raise ValueError('Changed installed parent index/dashboard: ' + path)
    folder = (ROOT / 'almanac').resolve()
    def read_part(relative):
        path = (folder / relative).resolve()
        if not path.is_relative_to(folder):
            raise ValueError('Parent transport part leaves atlas directory')
        return path.read_bytes()
    parent = json.loads(assemble(packet_raw, read_part))
    rows = parent['collections']
    candidate = installed['candidate']
    if (len(rows['objects']) != candidate['objects']
            or sum(len(r) for r in rows.values()) != candidate['rows']
            or len(rows['widths']) != 172
            or sum(row['type'] == 'named_current' for row in rows['objects']) != 106):
        raise ValueError('Assembled parent differs from installed inventory')
    return packet, installed, parent


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
    OUTPUT.mkdir(parents=True, exist_ok=True)
    result = {'schema':'osw.baffin-bound-candidate.v1', 'status':'RUNNING', 'published':False,
              'native_validation_attempted':False,
              'resource_preflight':{'free_disk_bytes':disk,'available_memory_bytes':memory}}
    def save():
        (OUTPUT / 'result.json').write_bytes(metadata.encoded(result))
    save()
    try:
        from export_current_gap_cloud_candidate import extend_index
        from query_packet import write_packet
        packet, installed, parent = load_parent()
        document = admission.build_contract()
        if admission.read(admission.FILE) != admission.encoded(document):
            raise ValueError('Changed prepared Baffin contract')
        manifest, staged, dashboard_raw, receipt = metadata.prepare(
            parent['manifest'], parent['collections'],
            parent['manifest']['dashboard_receipt']['source_json'].encode('utf8'), document,
            prepared_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00','Z'))
        result['parent_logical_sha256'] = packet['logical_sha256']
        result['parent_installed_run_id'] = installed['run_id']
        result['admission'] = receipt
        expected_rows = installed['candidate']['rows'] + 14
        del parent
        contracts = {path:admission.read(path) for path in
                     [admission.FILE, owner.FILE, owner.PARENT,
                      'research/baffin-latitude-gate-bound-execution-proof-v1.json',
                      'research/baffin-latitude-gate-bound-source-visual-review-v1.json']}
        result['index_extension'] = extend_index(dashboard_raw, contracts)
        catalog_path = ROOT / 'almanac/index-catalog.json'
        catalog = json.loads(catalog_path.read_bytes())
        for path in OPERATORS:
            catalog['input_sha256'][path] = admission.pin(path)
        catalog_path.write_bytes(metadata.encoded(catalog))
        index_paths = ['almanac/index-catalog.json','almanac/index-sources.json','almanac/index-data.json.gz']
        for path in [*OPERATORS, *index_paths]:
            manifest['input_sha256'][path] = admission.pin(path)
        (ROOT / metadata.DASHBOARD).write_bytes(dashboard_raw)
        raw = (json.dumps({'schema':'osw.query-bundle.v1','manifest':manifest,'collections':staged},
                          ensure_ascii=False,separators=(',',':'))+'\n').encode('utf8')
        packet = write_packet(ROOT / 'almanac/query-data.json', raw)
        result['candidate'] = {'logical_sha256':metadata.digest(raw),'logical_bytes':len(raw),
                               'objects':len(staged['objects']),'rows':sum(len(rows) for rows in staged.values()),
                               'named_currents':sum(row['type']=='named_current' for row in staged['objects']),
                               'widths':len(staged['widths']),'editorial_bound_scenarios':len(staged['current_length_bound_scenarios'])}
        candidate = result['candidate']
        if (candidate['rows'] != expected_rows or candidate['objects'] != 246
                or candidate['named_currents'] != 106 or candidate['widths'] != 172
                or candidate['editorial_bound_scenarios'] != 9):
            raise ValueError('Unexpected Baffin candidate inventory')
        result['admission']['complete_parent_packet_verified'] = True
        artifact = OUTPUT / 'artifact'
        paths = ['almanac/query-data.json',metadata.DASHBOARD,*index_paths,
                 *['almanac/'+row['path'] for row in packet['parts']]]
        for path in paths:
            destination = artifact / path
            destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT / path,destination)
        result.update(status='PASS',artifact_paths=paths,source_originals_redistributed=False,
                      scientific_release_published=False)
    except Exception as error:
        result.update(status='FAIL',error=type(error).__name__+': '+str(error))
        save()
        raise
    save()
    print(json.dumps({key:value for key,value in result.items() if key != 'admission'}))


if __name__ == '__main__':
    main()
