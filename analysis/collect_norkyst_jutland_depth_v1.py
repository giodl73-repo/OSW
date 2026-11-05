"""Bounded new Jutland-region NorKyst profiles; never replay Ingoy fields."""
import hashlib
import itertools
import json
import math
import re
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from interval_depth_diagnostic_v1 import diagnose, INTERIOR

ROOT = Path(__file__).resolve().parents[1]
OPERATOR = 'research/norkyst-jutland-depth-operator-v1.json'
PROJ = '+proj=stere +lat_0=90 +lat_ts=60 +lon_0=70 +x_0=3369600 +y_0=1844800 +a=6378137 +b=6356752.3142 +units=m +no_defs'
DEPTH = [0,1,2,3,5,7,10,15,25,50,65,75,100,200,300,400,500,750,1000,1250,1500,1750,2000,2250,2500]
FIELDS = ['u_eastward', 'v_northward', 'salinity', 'lon', 'lat', 'h', 'sea_mask']


def encode(value):
    return (json.dumps(value, separators=(',', ':'), allow_nan=False) + '\n').encode()


def preflight(op):
    from pyproj import CRS, Transformer
    transform = Transformer.from_crs(4326, CRS.from_proj4(PROJ), always_xy=True)
    if op['dates'] != ['2024-03-15','2024-06-15','2024-09-15','2024-12-15'] or op['component_bearing_degrees_true'] != 45:
        raise ValueError('Four predeclared dates and independently declared northeast component required')
    plans = []
    for date in op['dates']:
        for section in op['sections']:
            xx, yy = transform.transform(*section['editorial_center_lon_lat'])
            x = round(xx / 800); center_y = round(yy / 800)
            y0, y1 = center_y - 38, center_y + 38
            if not 0 <= x < 2747 or not 0 <= y0 < y1 < 1148:
                raise ValueError('Predeclared section falls outside retained source dimensions')
            # Prior Ingoy capture used X2420:4:2616/Y576:4:764 at10m.
            if 2420 <= x <= 2616 and not (y1 < 576 or y0 > 764):
                raise ValueError('Do not replay or overlap prior Ingoy field support')
            slice2 = f'[{y0}:2:{y1}][{x}]'
            query = ','.join(name + ('[12][0:1:24]' if name in FIELDS[:3] else '') + slice2 for name in FIELDS)
            url = 'https://thredds.met.no/thredds/dodsC/romshindcast/norkyst_v3/zdepth/2024/' + date[5:7] + '/norkyst800-' + date.replace('-','') + '.nc.ascii?' + urllib.parse.quote(query, safe=',:')
            plans.append({'case_index': len(plans), 'date': date, 'section_id': section['id'],
                          'editorial_center_lon_lat': section['editorial_center_lon_lat'],
                          'x_index': x, 'y_indices': list(range(y0, y1 + 1, 2)),
                          'http_url': url, 'metadata_file': 'research/norkyst-ingoy-source-metadata-' + date.replace('-','') + '.das',
                          'source_cell_pairs': 39 * 25, 'decoded_scalar_values': 39 * 25 * 3 + 39 * 4 + 3 * (1 + 25 + 39 + 1)})
    total = sum(p['decoded_scalar_values'] for p in plans)
    if len(plans) != 12 or len({p['http_url'] for p in plans}) != 12 or total > 250000 or total * 8 > 7000000:
        raise ValueError('All twelve distinct requests must jointly fit frozen source budgets')
    return {'schema': 'osw.norkyst-jutland-depth-preflight.v1', 'plans': plans,
            'maximum_http_requests': 12, 'maximum_attempts_per_target': 1,
            'total_reserved_decoded_scalar_values': total, 'total_reserved_decoded_bytes': total * 8,
            'provider_fixed_z_levels': 25, 'profiles_per_patch': 39,
            'maximum_cell_pairs_per_patch': 975, 'source_grid_spacing_m': 800,
            'retained_spacing_m': 1600, 'vertical_values_are_provider_interpolated': True,
            'new_requests_overlap_prior_ingoy_support': False}


def parse_array(text, name, expected_shape):
    matches = list(re.finditer(r'(?m)^' + re.escape(name + '.' + name) + r'((?:\[\d+\])+)\r?\n', text))
    if len(matches) != 1:
        raise ValueError('Exactly one original Grid array required: ' + name)
    match = matches[0]; shape = [int(n) for n in re.findall(r'\d+', match[1])]
    if shape != expected_shape:
        raise ValueError('Bounded field shape changed: ' + name)
    rows = []
    for line in text[match.end():].splitlines():
        if not line.strip(): break
        index, values = line.split(',', 1)
        rows.append(([int(n) for n in re.findall(r'\d+', index)], [float(v) for v in values.split(',')]))
    expected_indices = list(itertools.product(*(range(n) for n in shape[:-1])))
    if len(rows) != len(expected_indices) or any(tuple(idx) != wanted or len(values) != shape[-1] for (idx, values), wanted in zip(rows, expected_indices)):
        raise ValueError('Complete original ordered rows required: ' + name)
    return [value for _, values in rows for value in values]


def vector(text, field, axis, size):
    matches = list(re.finditer(r'(?m)^' + re.escape(field + '.' + axis) + r'\[' + str(size) + r'\]\r?\n([^\r\n]+)', text))
    if len(matches) != 1:
        raise ValueError('One original coordinate map required: ' + field + '.' + axis)
    values = [float(v) for v in matches[0][1].split(',')]
    if len(values) != size or not all(math.isfinite(v) for v in values):
        raise ValueError('Finite complete coordinate map required')
    return values


def validate_metadata(raw, date):
    text = raw.decode()
    for term in ['project "Norkyst_v3"', 'CC-BY-4.0', 'time_coverage_start "' + date + 'T00:00:00"', 'straight_vertical_longitude_from_pole 70.0', 'false_easting 3369600.0', 'false_northing 1844800.0']:
        if term not in text: raise ValueError('Frozen daily source metadata changed: ' + term)
    for field, offset, standard in [('u_eastward',0,'eastward_sea_water_velocity'), ('v_northward',0,'northward_sea_water_velocity'), ('salinity',30,'sea_water_salinity')]:
        block = re.search(r'(?m)^    ' + field + r' \{(.*?)^    \}', text, re.S)
        if block is None or any(t not in block[1] for t in ['scale_factor 0.001', 'add_offset ' + str(offset) + '.0', '_FillValue -32767', 'standard_name "' + standard + '"']):
            raise ValueError('Frozen field packing or component meaning changed')


def decode(packed, offset=0):
    if not math.isfinite(packed) or packed != int(packed) or not -32768 <= packed <= 32767:
        raise ValueError('Original packed Int16 required')
    return None if packed == -32767 else packed * .001 + offset


def derive(raw, plan, op):
    from pyproj import CRS, Transformer
    text = raw.decode(); n = len(plan['y_indices'])
    arrays = {name: parse_array(text, name, [1,25,n,1] if name in FIELDS[:3] else [n,1]) for name in FIELDS}
    wanted = {'time': [datetime.fromisoformat(plan['date'] + 'T12:00:00+00:00').timestamp()],
              'depth': DEPTH, 'Y': [i * 800 for i in plan['y_indices']], 'X': [plan['x_index'] * 800]}
    for field in FIELDS[:3]:
        for axis, values in wanted.items():
            if vector(text, field, axis, len(values)) != values:
                raise ValueError('Returned source time/depth/grid indices changed')
    transform = Transformer.from_crs(4326, CRS.from_proj4(PROJ), always_xy=True)
    columns = []
    for i, yindex in enumerate(plan['y_indices']):
        lon, lat = arrays['lon'][i], arrays['lat'][i]
        if not all(math.isfinite(v) for v in [lon,lat]) or not -180 <= lon <= 180 or not -90 <= lat <= 90:
            raise ValueError('Original finite source positions required')
        x, y = transform.transform(lon, lat)
        if math.hypot(x - plan['x_index'] * 800, y - yindex * 800) > 1:
            raise ValueError('Source grid/projection closure must remain within1m')
        wet = arrays['sea_mask'][i]
        if wet not in [0,1]: raise ValueError('Original binary source mask required')
        component = []; salinity = []
        for k in range(25):
            index = k*n+i
            u, v, s = decode(arrays['u_eastward'][index]), decode(arrays['v_northward'][index]), decode(arrays['salinity'][index], 30)
            component.append((u+v)/math.sqrt(2) if wet == 1 and u is not None and v is not None else None)
            salinity.append(s if wet == 1 else None)
        h = arrays['h'][i]
        columns.append({'source_x_index': plan['x_index'], 'source_y_index': yindex,
                        'position_lon_lat': [lon,lat], 'source_sea_mask': int(wet),
                        'static_model_bathymetry_m': h if math.isfinite(h) else None,
                        'northeast_component_m_s': component, 'salinity_source_units_1': salinity})
    diagnosis = diagnose(DEPTH, [c['northeast_component_m_s'] for c in columns], op['diagnostic'])
    return {'schema': 'osw.norkyst-jutland-provider-z-depth-section.v1',
            'entity_id': 'current:jutland', 'date': plan['date'], 'section_id': plan['section_id'],
            'time_utc': plan['date'] + 'T12:00:00Z', 'source_http_url': plan['http_url'],
            'source_response_sha256': hashlib.sha256(raw).hexdigest(),
            'source_depth_levels_m': DEPTH, 'source_vertical_sampling': 'provider_interpolated_fixed_z_not_native_ROMS_s_layers',
            'source_grid_spacing_m': 800, 'retained_cross_section_spacing_m': 1600,
            'component_bearing_degrees_true': 45, 'salinity_gate_applied': False,
            'editorial_center_lon_lat': plan['editorial_center_lon_lat'],
            'section_geometry': 'constant_source_projected_X_with_predeclared_Y_window_not_flow_normal_or_independently_validated_axis',
            'columns': columns, 'diagnosis': diagnosis,
            'physical_current_identity_independently_verified': False,
            'tidal_correction_applied': False, 'physical_current_bottom_established': False,
            'physical_current_thickness_m': None, 'volume_m3': None,
            'annual_range_m': None, 'whole_route_profile': False}


def read_target(plan, receipt, opener):
    receipt.update(case_index=plan['case_index'], url=plan['http_url'], attempts=1, bytes_received=0, status='reserved')
    request = urllib.request.Request(plan['http_url'], headers={'Accept-Encoding':'identity', 'User-Agent':'OSW-new-Jutland-depth-sections-v1'})
    try:
        with opener(request, timeout=25) as response:
            if response.status != 200 or response.url != plan['http_url'] or response.headers.get('Content-Encoding') not in [None,'identity']:
                raise ValueError('Exact uncompressed source200 response required')
            length = response.headers.get('Content-Length')
            if length is not None and (not length.isdigit() or int(length) > 120000):
                raise ValueError('Source patch response exceeds predeclared120kB cap')
            raw = response.read(120001); receipt['bytes_received'] = len(raw)
            if len(raw) > 120000: raise ValueError('Source patch body cap exceeded')
        receipt.update(status='received', sha256=hashlib.sha256(raw).hexdigest())
        return raw
    except Exception as error:
        receipt.update(status='failed_no_retry', error_type=type(error).__name__, error_summary=str(error)[:200])
        raise


def main():
    op = json.loads((ROOT / OPERATOR).read_bytes())
    for path, pin in op['input_sha256'].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != pin:
            raise ValueError('Pinned input changed: ' + path)
    out = ROOT / 'norkyst-jutland-depth-v1'; out.mkdir(exist_ok=True)
    pf = preflight(op); (out / 'preflight.json').write_bytes(encode(pf))
    for plan in pf['plans']:
        validate_metadata((ROOT / plan['metadata_file']).read_bytes(), plan['date'])
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs): return None
    opener = urllib.request.build_opener(NoRedirect()).open
    manifest = {'schema': 'osw.norkyst-jutland-depth-manifest.v1', 'operator_file': OPERATOR,
                'operator_sha256': hashlib.sha256((ROOT / OPERATOR).read_bytes()).hexdigest(),
                'input_sha256': op['input_sha256'], 'transport_receipts': [], 'case_files': [],
                'new_source_product': 'NorKyst_v3_2024_provider_interpolated_z_depth',
                'credit': 'Modified MET Norway/Institute of Marine Research NorKyst_v3 data,CC BY4.0;Christensen et al.(2026),doi10.5194/gmd-19-2785-2026.',
                'previous_ingoy_sources_retrieved_again': False, 'runtime_changed': False, 'full_goal_complete': False}
    for plan in pf['plans']:
        receipt = {}; manifest['transport_receipts'].append(receipt)
        try:
            raw = read_target(plan, receipt, opener)
            rawname = 'case-' + str(plan['case_index']).zfill(2) + '.ascii'; (out / rawname).write_bytes(raw)
            receipt['raw_file'] = rawname
            report = derive(raw, plan, op)
            name = 'case-' + str(plan['case_index']).zfill(2) + '.json'; content = encode(report)
            if len(content) > 70000: raise ValueError('Reserved per-case report budget exceeded')
            (out / name).write_bytes(content)
            manifest['case_files'].append({'file':name, 'bytes':len(content), 'sha256':hashlib.sha256(content).hexdigest(),
                                           'raw_file':rawname, 'raw_sha256':receipt['sha256']})
            receipt['status'] = 'received_and_derived'
        except Exception as error:
            if receipt.get('status') == 'received':
                receipt.update(status='received_but_derivation_failed_no_replay', error_type=type(error).__name__, error_summary=str(error)[:200])
        manifest['counts'] = {'planned_cases':12, 'processed_cases':len(manifest['case_files']),
                              'failed_cases':sum(r['status'] != 'received_and_derived' for r in manifest['transport_receipts']),
                              'source_requests_attempted':len(manifest['transport_receipts'])}
        (out / 'manifest.json').write_bytes(encode(manifest))
        if sum(p.stat().st_size for p in out.iterdir()) > 2400000:
            raise ValueError('Combined scientific output budget exceeded; stop new requests')
        print(json.dumps({'case_index':plan['case_index'], 'status':receipt['status']}), flush=True)
    if manifest['counts']['failed_cases']:
        raise SystemExit(1)


if __name__ == '__main__': main()
