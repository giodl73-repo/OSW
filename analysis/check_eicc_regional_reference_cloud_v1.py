"""One cloud CPU: two source conventions, eighteen retained reference probes."""
import argparse
import hashlib
import io
import itertools
import json
import math
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REQUEST = 'research/eicc-regional-reference-request-v1.json'
PREFLIGHT = 'research/eicc-regional-reference-preflight-v1.json'
PROTOCOL = 'research/eicc-spring-regional-reference-protocol-v1.json'
OUTPUT = ROOT / '.pytest_cache/eicc-regional-reference-v1'
LAND_RECEIPT = 'research/source-data/natural-earth-land-10m-5.1.1/acquisition.json'
LAND_ZIP = 'research/source-data/natural-earth-land-10m-5.1.1/ne_10m_land.zip'
PAGE = 'almanac/loop-published-metrics.html'
ARCHIVED_PAGE = 'almanac/loop-published-metrics-source-v1.html'
INSTALLED = 'research/loop-published-metrics-installed-v1.json'


def read(path):
    return json.loads((ROOT / path).read_bytes())


def digest(path):
    with (ROOT / path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def controls():
    if (os.environ.get('GITHUB_ACTIONS') != 'true' or os.environ.get('RUNNER_OS') != 'Linux'
            or os.environ.get('GITHUB_REPOSITORY') != 'giodl73-repo/OSW'
            or os.environ.get('GITHUB_REF') != 'refs/heads/codex/current-measurement-gaps'
            or os.environ.get('GITHUB_EVENT_NAME') != 'push'):
        raise ValueError('Cloud working branch required; local geographic calculation refused')
    assert len(os.sched_getaffinity(0)) == 1 and os.getpriority(os.PRIO_PROCESS, 0) >= 15
    for name in ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS']:
        assert os.environ.get(name) == '1', name
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    assert head == os.environ['GITHUB_SHA']
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT).strip()
    remote = json.loads(subprocess.check_output(['gh', 'api',
        'repos/giodl73-repo/OSW/git/ref/heads/codex/current-measurement-gaps']))
    assert remote['object']['sha'] == head
    request = read(REQUEST)
    assert request['schema'] == 'osw.eicc-regional-reference-request.v1'
    assert request['execution_permitted'] is True and request['regional_geodesic_calculation_permitted'] is True
    assert request['max_cloud_jobs'] == 1 and request['max_heavy_local_jobs'] == 0
    for key in ['original_velocity_processing_permitted', 'native_build_permitted', 'wasm_build_permitted',
                'browser_automation_permitted', 'packet_load_permitted', 'index_load_permitted',
                'working_branch_installation_permitted', 'local_bulk_sync_permitted', 'main_merge_permitted']:
        assert request[key] is False, key
    assert digest(PREFLIGHT) == request['preflight_sha256']
    preflight = read(PREFLIGHT)
    for path, sha in preflight['input_sha256'].items():
        assert digest(path) == sha, path
    relocations = []
    for name in preflight['preserve_inventories']:
        for path, sha in read(name)['input_sha256'].items():
            if path == PAGE:
                proof = read(INSTALLED)
                assert proof['presentation_overlay']['original_page_archive_path'] == ARCHIVED_PAGE
                assert proof['presentation_overlay']['original_page_sha256'] == sha
                assert digest(ARCHIVED_PAGE) == sha
                assert digest(PAGE) == proof['files'][PAGE]['sha256']
                relocations.append({'inventory': name, 'historical_path': path, 'archive_path': ARCHIVED_PAGE,
                                    'historical_sha256': sha, 'installed_sha256': digest(PAGE)})
            else:
                assert digest(path) == sha, path
    for path in preflight['disabled_requests']:
        assert read(path)['execution_permitted'] is False, path
    assert read('research/current-gap-delivery-phase.json')['heavy_work_permitted'] is False
    protocol = read(PROTOCOL)
    assert digest(protocol['source_file']) == protocol['source_sha256']
    assert [v['coordinates_lon_lat'] for v in protocol['source_coordinate_variants']] == [
        [[84, 14], [83, 16], [85.5, 18]], [[84, 14], [83, 16], [85.5, 18.5]]]
    assert protocol['bend_probes_km'] == [-10, 0, 10]
    assert protocol['public_rounding_km'] == 10 and protocol['land_check_spacing_km'] == 1
    assert protocol['distance_serialization_decimals'] == 6
    assert protocol['land_region_lon_lat'] == [80, 12, 88, 20]
    for key in ['full_current_rank_eligible', 'annual_range_eligible', 'seasonal_playback_eligible',
                'physical_state_join_eligible', 'source_velocity_or_profile_processing']:
        assert protocol[key] is False
    return head, protocol, relocations


def calculate(head, protocol, relocations):
    # No geographic libraries, coast arrays or calculations are opened before the cloud guard.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import pyproj
    import shapefile
    import shapely
    from shapely.geometry import LineString, box, shape
    from shapely.ops import unary_union
    from build_motion_state_join import PROVINCES, polygon_parts

    assert pyproj.__version__ == '3.7.2' and shapely.__version__ == '2.1.2'
    assert shapefile.__version__ == '2.3.1' and matplotlib.__version__ == '3.10.8'
    geod = pyproj.Geod(ellps='WGS84')
    assert abs(geod.inv(0, 0, 1, 0)[2] / 1000 - 111.31949079327356) < 1e-9
    region = box(*protocol['land_region_lon_lat'])
    receipt = read(LAND_RECEIPT)
    assert receipt['sha256'] == 'e547d749445eaa0964aba76738090ec88f5e63c4585122170f98c67a7ea922dc'
    assert receipt['package_version'] == '5.1.1'
    assert (ROOT / LAND_ZIP).stat().st_size == receipt['bytes'] and digest(LAND_ZIP) == receipt['sha256']
    with zipfile.ZipFile(ROOT / LAND_ZIP) as saved:
        assert {n for n in saved.namelist() if not n.endswith('/')} == set(receipt['members'])
        for name, expected in receipt['members'].items():
            raw = saved.read(name)
            assert len(raw) == expected['bytes'] and hashlib.sha256(raw).hexdigest() == expected['sha256']
        assert saved.read('ne_10m_land.VERSION.txt').decode().strip() == '5.1.1'
        assert 'GCS_WGS_1984' in saved.read('ne_10m_land.prj').decode()
        pieces = []
        with shapefile.Reader(**{key: io.BytesIO(saved.read('ne_10m_land.' + key)) for key in ['shp', 'shx', 'dbf']}) as reader:
            for item in reader.iterShapes(bbox=region.bounds):
                polygon = shape(item.__geo_interface__)
                assert polygon.is_valid, 'Do not repair the finer source coastline'
                clipped = polygon.intersection(region)
                if not clipped.is_empty:
                    pieces.append(clipped)
    fine = unary_union(pieces)
    assert fine.is_valid and not fine.is_empty
    root = ET.parse(PROVINCES).getroot()
    land_path = next(n.get('d') for n in root.iter() if n.get('class') == 'land-context')
    coarse = unary_union(polygon_parts(land_path))
    assert not coarse.is_empty and coarse.is_valid

    def project(lon, lat):
        return 60 + (lon + 180) / 360 * 1480, 90 + (90 - lat) / 180 * 740

    def length(points):
        return sum(geod.inv(*a, *b)[2] for a, b in zip(points, points[1:])) / 1000

    def dense(points):
        result = [list(points[0])]
        for a, b in zip(points, points[1:]):
            n = max(1, math.ceil(geod.inv(*a, *b)[2] / 1000))
            if n > 1:
                result.extend([list(p) for p in geod.npts(*a, *b, n - 1)])
            result.append(list(b))
        assert max(geod.inv(*a, *b)[2] for a, b in zip(result, result[1:])) <= 1000.000001
        return result

    def contacts(samples):
        assert region.covers(LineString(samples)), 'Probe leaves the predefined land-check region'
        return {'fine_land_contact': LineString(samples).intersects(fine),
                'coarse_land_contact': LineString([project(*p) for p in samples]).intersects(coarse)}

    def bend(a, b, offset):
        azimuth, _, metres = geod.inv(*a, *b)
        lon, lat, _ = geod.fwd(*a, azimuth, metres / 2)
        forward = geod.inv(lon, lat, *b)[0]
        lon, lat, _ = geod.fwd(lon, lat, forward + 90, offset * 1000)
        return [lon, lat]

    cases, variants, nominal_lines = [], [], []
    for variant in protocol['source_coordinate_variants']:
        anchors = variant['coordinates_lon_lat']
        actual_lengths, owned = [], []
        for first, second in itertools.product(protocol['bend_probes_km'], repeat=2):
            points = [anchors[0], bend(anchors[0], anchors[1], first), anchors[1],
                      bend(anchors[1], anchors[2], second), anchors[2]]
            raw_samples = dense(points)
            exported = [list(p) if i in [0, 2, 4] else [round(p[0], 8), round(p[1], 8)] for i, p in enumerate(points)]
            exported_samples = dense(exported)
            display = [[round(lon, 8), round(lat, 8)] for lon, lat in exported_samples]
            checks = {'raw': contacts(raw_samples), 'serialized_vertices': contacts(exported_samples),
                      'serialized_display': contacts(display)}
            passed = not any(value for check in checks.values() for value in check.values())
            km = length(points)
            actual_lengths.append(km)
            row = {'id': variant['id'] + f':bends:{first}:{second}', 'variant_id': variant['id'],
                   'bend_offsets_km': [first, second], 'coordinates_lon_lat': exported,
                   'display_coordinates_lon_lat': display, 'length_km': round(km, 6),
                   'land_checks': checks, 'cartographic_gate_passed': passed,
                   'rank_eligible': False, 'physical_axis_admitted': False}
            assert [row['coordinates_lon_lat'][i] for i in [0, 2, 4]] == anchors
            cases.append(row)
            owned.append(row)
        nominal_samples = dense(anchors)
        nominal_checks = contacts(nominal_samples)
        nominal_km = length(anchors)
        assert abs(next(r['length_km'] for r in owned if r['bend_offsets_km'] == [0, 0]) - nominal_km) < 1e-6
        variants.append({'id': variant['id'], 'source_anchors_lon_lat': anchors,
                         'nominal_reference_length_km': round(nominal_km, 6),
                         'public_approximate_reference_length_km': round(nominal_km / 10) * 10,
                         'scenario_length_range_km': [round(min(actual_lengths), 6), round(max(actual_lengths), 6)],
                         'public_scenario_span_km': [math.floor(min(actual_lengths) / 10) * 10, math.ceil(max(actual_lengths) / 10) * 10],
                         'nominal_land_checks': nominal_checks,
                         'all_nine_probes_clear_both_masks': all(r['cartographic_gate_passed'] for r in owned),
                         'failed_case_ids': [r['id'] for r in owned if not r['cartographic_gate_passed']]})
        nominal_lines.append(nominal_samples)
    assert len(cases) == 18 and len({r['id'] for r in cases}) == 18
    result = {'schema': 'osw.eicc-regional-reference-calculation.v1',
              'status': 'CALCULATED_CARTOGRAPHIC_GATES_PASSED' if all(v['all_nine_probes_clear_both_masks'] for v in variants) else 'CALCULATED_REFERENCE_ADMISSION_HELD',
              'source_commit': head, 'run_id': os.environ['GITHUB_RUN_ID'], 'run_attempt': os.environ['GITHUB_RUN_ATTEMPT'],
              'protocol_sha256': digest(PROTOCOL), 'variants': variants, 'cases': cases,
              'historical_source_relocations_verified': relocations,
              'runtime': {'python': os.sys.version, 'pyproj': pyproj.__version__, 'proj': pyproj.proj_version_str,
                          'shapely': shapely.__version__, 'pyshp': shapefile.__version__, 'matplotlib': matplotlib.__version__},
              'land_sources': {'fine_sha256': receipt['sha256'], 'coarse_sha256': digest(str(PROVINCES.relative_to(ROOT))),
                              'coarse_parser_note': 'Existing OSW polygon_parts buffer(0) convention retained; finer original polygons not repaired.'},
              'scope': 'Regional editorial connections through three approximate source core locations; no observed full axis or whole-current length. Both source-coordinate conventions retained without averaging.',
              'sensitivity_scope': 'Bend probes are editorial geometry sensitivity, not physical uncertainty or annual variability.',
              'source_depth_m': 50, 'source_survey_context': ['1987-03-22', '1987-04-28'],
              'exact_axis_occupation_dates': None, 'whole_current_length_km': None, 'annual_length_range_km': None,
              'new_physical_dimensions_admitted': 0, 'working_dataset_admitted': False,
              'source_figures_digitized': False, 'scientific_release_approved': False, 'visual_review_complete': False}
    (OUTPUT / 'result.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    matplotlib.rcParams.update({'svg.hashsalt': 'osw-eicc-regional-reference-v1', 'font.family': 'DejaVu Sans'})
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.subplots_adjust(left=.09, right=.96, top=.83, bottom=.25)
    ax.set_facecolor('#f3f9fc')
    polygons = list(fine.geoms) if fine.geom_type == 'MultiPolygon' else [fine]
    for polygon in polygons:
        if polygon.geom_type != 'Polygon':
            continue
        ax.fill(*polygon.exterior.xy, color='#d9e1da', edgecolor='#7b8a80', linewidth=.6)
        for interior in polygon.interiors:
            ax.fill(*interior.xy, color='#f3f9fc', edgecolor='#7b8a80', linewidth=.4)
    colors = ['#097b98', '#b55518']
    for i, variant in enumerate(variants):
        owned = [r for r in cases if r['variant_id'] == variant['id']]
        for row in owned:
            coords = row['display_coordinates_lon_lat']
            ax.plot(*zip(*coords), color=colors[i], alpha=.14, linewidth=.8)
        ax.plot(*zip(*nominal_lines[i]), color=colors[i], linestyle='-' if i == 0 else '--', linewidth=2,
                label=variant['id'] + f": about {variant['public_approximate_reference_length_km']} km")
        end = variant['source_anchors_lon_lat'][-1]
        ax.scatter(*end, marker='o' if i == 0 else 'D', color=colors[i], zorder=6)
        ax.annotate('18°N prose' if i == 0 else '18.5°N caption', end,
                    xytext=(8, -15 if i == 0 else 9), textcoords='offset points', color=colors[i], fontsize=9)
    for label, point in [('84°E, 14°N', [84, 14]), ('83°E, 16°N', [83, 16])]:
        ax.scatter(*point, color='#163745', zorder=7)
        ax.annotate(label, point, xytext=(8, -14), textcoords='offset points', fontsize=9)
    ax.set(xlim=(80, 88), ylim=(12, 20), xlabel='Longitude (°E, WGS84 convention)', ylabel='Latitude (°N, WGS84 convention)')
    ax.set_aspect(1 / math.cos(math.radians(16)))
    ax.grid(alpha=.2)
    ax.legend(loc='upper left', fontsize=9, framealpha=.96)
    fig.suptitle('Springtime Bay of Bengal WBC | regional source-reference connections', fontsize=13, weight='bold', x=.05, ha='left')
    fig.text(.05, .91, 'Gangopadhyay et al. (2013) · 50 m analysis · survey context March–April 1987', fontsize=10)
    fig.text(.05, .18, 'Thin lines: all 18 predefined bend probes. Two eastern-core coordinate conventions kept separate.', fontsize=9)
    fig.text(.05, .145, 'These are geodesic reference connections, not reconstructed meanders, whole-current lengths or annual ranges.', fontsize=9)
    fig.text(.05, .11, 'Source uses “springtime WBC” for the northward phase; OSW broad EICC association remains source-qualified.', fontsize=9)
    fig.text(.05, .075, 'Natural Earth 1:10M land 5.1.1 (public domain). Both finer and OSW coarse land contacts retained in JSON.', fontsize=9)
    fig.text(.05, .04, 'Source: doi:10.1002/grl.50412, paragraph 8 and Figure 2 caption. No physical state joins or seasonal playback.', fontsize=9)
    for suffix in ['svg', 'png']:
        fig.savefig(OUTPUT / ('eicc-regional-reference-v1.' + suffix), dpi=140,
                    metadata={'Date': None, 'Creator': 'OSW'} if suffix == 'svg' else {'Software': 'OSW'})
    plt.close(fig)
    files = ['result.json', 'eicc-regional-reference-v1.svg', 'eicc-regional-reference-v1.png']
    summary = {'status': result['status'], 'source_commit': head, 'run_id': os.environ['GITHUB_RUN_ID'],
               'run_attempt': os.environ['GITHUB_RUN_ATTEMPT'], 'case_count': 18,
               'failed_case_count': sum(not r['cartographic_gate_passed'] for r in cases),
               'variants': variants, 'files': {p: {'sha256': hashlib.sha256((OUTPUT / p).read_bytes()).hexdigest(),
                                                 'bytes': (OUTPUT / p).stat().st_size} for p in files},
               'working_dataset_admitted': False, 'visual_review_complete': False}
    (OUTPUT / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({'status': summary['status'], 'cases': 18, 'failed_cases': summary['failed_case_count']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cloud-calculate', action='store_true', required=True)
    parser.add_argument('--preflight-only', action='store_true')
    args = parser.parse_args()
    head, protocol, relocations = controls()
    if args.preflight_only:
        print('Exact EICC source and historical relocation preflight passed')
    else:
        OUTPUT.mkdir(parents=True, exist_ok=False)
        try:
            calculate(head, protocol, relocations)
        except Exception as error:
            (OUTPUT / 'failure.json').write_text(json.dumps({'status': 'FAIL', 'source_commit': head,
                'error': (type(error).__name__ + ': ' + str(error))[:1500]}, indent=2) + '\n')
            raise
