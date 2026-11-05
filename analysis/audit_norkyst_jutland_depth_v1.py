"""Reproduce every retained response and expose dated regional depth anchors."""
import copy
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path
import collect_norkyst_jutland_depth_v1 as source

ROOT = Path(__file__).resolve().parents[1]
OPERATOR = 'research/norkyst-jutland-depth-summary-operator-v1.json'
FOLDER = 'research/source-data/norkyst-jutland-depth-v1'


def audit_case(case, raw, plan, original_op):
    expected = source.derive(raw, plan, original_op)
    if case != expected:
        raise ValueError('Every original source coordinate, field, score, selection and descriptor must reproduce')
    d = case['diagnosis']; selected = d['selected_column_index']
    p = case['columns'][selected] if selected is not None else None
    primary = next((x for x in d['selected_column_threshold_layers'] if x['threshold_m_s'] == .1), None)
    horizontal = d['horizontal_selection_status'] == source.INTERIOR
    finite_lower = primary is not None and primary['lower_depth_m'] is not None
    return {'case_index': plan['case_index'], 'entity_id': case['entity_id'],
            'date': case['date'], 'time_utc': case['time_utc'], 'section_id': case['section_id'],
            'selected_column_index': selected,
            'selected_position_lon_lat': p['position_lon_lat'] if p else None,
            'selected_source_grid_indices': [p['source_x_index'],p['source_y_index']] if p else None,
            'horizontal_selection_status': d['horizontal_selection_status'],
            'horizontal_axis_proxy_interior': horizontal,
            'primary_component_layer': copy.deepcopy(primary),
            'sensitivity_layers': copy.deepcopy(d['selected_column_threshold_layers']),
            'core_depth_m': primary.get('core_depth_m') if primary else None,
            'primary_lower_component_contour_depth_m': primary['lower_depth_m'] if primary else None,
            'primary_connected_depth_lower_bound_m': primary.get('lower_last_connected_depth_m') if primary else None,
            'conditional_component_span_m': primary['layer_thickness_m'] if primary else None,
            'conditional_component_span_is_physical_thickness': False,
            'regional_axis_proxy_lower_contour_anchor_eligible': horizontal and finite_lower,
            'source_profile_instances': len(case['columns']),
            'source_wet_profile_instances': sum(c['source_sea_mask'] == 1 for c in case['columns']),
            'source_vertical_sampling': case['source_vertical_sampling'],
            'component_bearing_degrees_true': 45,
            'selection_interval_m': [0,25], 'primary_threshold_m_s': .1,
            'salinity_gate_applied': False, 'physical_current_identity_independently_verified': False,
            'whole_current_representative': False, 'physical_current_bottom_established': False,
            'physical_thickness_m': None, 'volume_m3': None, 'annual_range_m': None,
            'width_join_eligible': False, 'volume_eligible': False}


def build(root=ROOT):
    reader = lambda p: (root / p).read_bytes()
    read = lambda p: json.loads(reader(p))
    op = read(OPERATOR)
    for path, pin in op['input_sha256'].items():
        if hashlib.sha256(reader(path)).hexdigest() != pin:
            raise ValueError('Pinned source changed: ' + path)
    original_op = read(source.OPERATOR)
    pf = source.preflight(original_op)
    if read(FOLDER + '/preflight.json') != pf:
        raise ValueError('Original joint preflight must reproduce')
    manifest = read(FOLDER + '/manifest.json')
    review = read('research/current-depth-norkyst-jutland-sections-source-review-v1.json')
    if manifest['counts'] != {'planned_cases':12,'processed_cases':12,'failed_cases':0,'source_requests_attempted':12} or review['source_run'] != 41962447339 or review['tests_passed'] != 12:
        raise ValueError('Exact completed source collection and prior validation required')
    rows = []; cases = []
    for plan, part, receipt in zip(pf['plans'], manifest['case_files'], manifest['transport_receipts'], strict=True):
        file = FOLDER + '/' + part['file']; rawfile = FOLDER + '/' + part['raw_file']
        raw = reader(rawfile); content = reader(file)
        if (hashlib.sha256(raw).hexdigest() != part['raw_sha256'] or hashlib.sha256(content).hexdigest() != part['sha256']
                or len(content) != part['bytes'] or receipt['url'] != plan['http_url']
                or receipt['attempts'] != 1 or receipt['status'] != 'received_and_derived'):
            raise ValueError('Original exact response/report/transport binding required')
        case = json.loads(content); row = audit_case(case, raw, plan, original_op)
        row.update(source_case_file=file, source_case_sha256=part['sha256'],
                   source_raw_file=rawfile, source_raw_sha256=part['raw_sha256'])
        rows.append(row); cases.append(case)
    if len(rows) != 12 or len({(r['date'],r['section_id']) for r in rows}) != 12:
        raise ValueError('Every unique original section/date must remain present')
    counts = {'source_cases':12, 'source_profile_instances':sum(r['source_profile_instances'] for r in rows),
              'wet_source_profile_instances':sum(r['source_wet_profile_instances'] for r in rows),
              'selected_axis_proxy_profiles':sum(r['selected_column_index'] is not None for r in rows),
              'interior_axis_proxy_cases':sum(r['horizontal_axis_proxy_interior'] for r in rows),
              'finite_primary_lower_component_contours':sum(r['primary_lower_component_contour_depth_m'] is not None for r in rows),
              'interior_finite_primary_lower_contour_anchors':sum(r['regional_axis_proxy_lower_contour_anchor_eligible'] for r in rows),
              'primary_censored_lower_bound_cases':sum(r['primary_connected_depth_lower_bound_m'] is not None for r in rows),
              'source_dates':4, 'source_search_sections':3, 'new_direct_observations':0,
              'physical_current_thickness_estimates':0, 'whole_current_volume_estimates':0}
    profiles = [{'date':date, 'anchors':[r for r in rows if r['date'] == date],
                 'section_order_kind':'predeclared_editorial_search_cut_order_not_geographic_current_axis',
                 'between_anchor_interpolation_performed':False, 'seasonal_mean':False}
                for date in original_op['dates']]
    report = {'schema':'osw.norkyst-jutland-dated-regional-depth-anchors.v1',
              'entity_id':'current:jutland', 'counts':counts, 'rows':rows,
              'credit':manifest['credit'], 'source_documentation_url':'https://gmd.copernicus.org/articles/19/2785/2026/',
              'horizontal_status_counts':dict(sorted(Counter(r['horizontal_selection_status'] for r in rows).items())),
              'primary_lower_status_counts':dict(sorted(Counter(r['primary_component_layer']['lower_status'] if r['primary_component_layer'] else 'no_selected_column' for r in rows).items())),
              'date_profiles':profiles, 'source_collection_review_file':'research/current-depth-norkyst-jutland-sections-source-review-v1.json',
              'input_sha256':op['input_sha256'],
              'qualifications':[
                  'Four2024noon total-flow snapshots, not seasonal means, de-tided currents, annual extremes or direct observations.',
                  'New NorKyst source/window/year differs from old HYCOM2022 0-30m cases. Do not infer observed temporal change or exact source equivalence.',
                  'All original profiles, masks, salinity, candidate scores and unresolved selections are retained. No core, threshold, frame or gate was changed after values.',
                  'Depths are conditional45degree component contours or sampling bounds on provider-interpolated fixed z-levels. Brackets are sampling support, not uncertainty.',
                  'Only interior selection plus a resolved primary lower contour qualifies for the regional axis-proxy contour-anchor class. Other selected points retain explicit unresolved status.',
                  'Horizontal interior is not independently validated Jutland identity or current axis. Salinity is context without an identity gate.',
                  'A finite connected component span is not physical current thickness. Missing sample/bed/domain endpoints are not current bottoms.',
                  'No between-section/time interpolation, width join, area, volume, whole-current profile or old inventory count rewrite.'],
              'runtime_changed':False, 'full_goal_complete':False}
    features = [{'type':'Feature', 'id':'norkyst-jutland-'+r['date']+'-'+r['section_id'],
                 'geometry':{'type':'Point','coordinates':r['selected_position_lon_lat']},
                 'properties':copy.deepcopy(r)} for r in rows if r['selected_position_lon_lat'] is not None]
    geo = {'type':'FeatureCollection','schema':'osw.norkyst-jutland-depth-points.v1',
           'credit':manifest['credit'],
           'features':features, 'geometry_role':'selected_source_positions_only_not_a_current_axis',
           'vertical_coordinate_role':'provider_positive_down_depth_properties_not_GeoJSON_altitude',
           'physical_current_thickness_m':None, 'volume_m3':None, 'annual_range_m':None,
           'runtime_changed':False,'full_goal_complete':False}
    return report, geo


def csv_bytes(report):
    fields = ['case_index','date','section_id','selected_column_index','horizontal_selection_status',
              'source_vertical_sampling','component_bearing_degrees_true','primary_threshold_m_s',
              'core_depth_m','primary_lower_component_contour_depth_m','primary_connected_depth_lower_bound_m',
              'conditional_component_span_m','regional_axis_proxy_lower_contour_anchor_eligible',
              'conditional_component_span_is_physical_thickness','physical_current_bottom_established','volume_eligible',
              'source_case_file','source_case_sha256','source_raw_file','source_raw_sha256']
    stream = io.StringIO(newline=''); writer = csv.DictWriter(stream,fieldnames=fields,lineterminator='\n')
    writer.writeheader(); writer.writerows({k:r[k] for k in fields} for r in report['rows'])
    return stream.getvalue().encode()


if __name__ == '__main__':
    report, geo = build(); out = ROOT / 'norkyst-jutland-depth-summary-v1'; out.mkdir(exist_ok=True)
    outputs = {'summary.json':source.encode(report), 'points.geojson':source.encode(geo), 'depths.csv':csv_bytes(report)}
    if sum(map(len,outputs.values())) > 2400000: raise ValueError('Summary output cap exceeded')
    for name, raw in outputs.items(): (out / name).write_bytes(raw)
    print(json.dumps({'counts':report['counts'],'horizontal_status_counts':report['horizontal_status_counts'],
                      'primary_lower_status_counts':report['primary_lower_status_counts'],
                      'depth_rows':[{k:r[k] for k in ['date','section_id','core_depth_m','primary_lower_component_contour_depth_m','primary_connected_depth_lower_bound_m','horizontal_selection_status']} for r in report['rows']]}))
