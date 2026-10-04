"""Build comparable fixed-section model profiles, without current-width inference."""
import hashlib
import json
import math
from pathlib import Path
from pyproj import CRS, Geod, Transformer

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'research/norkyst-ingoy-2024-section-timeline.json'
PROJ = '+proj=stere +lat_0=90 +lat_ts=60 +lon_0=70 +x_0=3369600 +y_0=1844800 +a=6378137 +b=6356752.3142 +units=m +no_defs'
TRANSFORM = Transformer.from_crs(4326, CRS.from_proj4(PROJ), always_xy=True)
GEOD = Geod(ellps='WGS84')


def profile(receipt):
    arrays = receipt['packed_field_arrays']
    ys, xs = (receipt['grid_index_slices'][key] for key in ['Y', 'X'])
    # Verify source lon/lat correspond to the projected-grid coordinates.
    for iy, ix in [(0, 0), (0, 49), (47, 0), (47, 49), (24, 25)]:
        x, y = TRANSFORM.transform(arrays['lon'][iy][ix], arrays['lat'][iy][ix])
        if math.hypot(x - (xs[0] + ix * xs[1]) * 800, y - (ys[0] + iy * ys[1]) * 800) > 1:
            raise ValueError('Projected grid coordinate mismatch')
    result = []
    for i in range(191):
        lat = round(71.1 + i * 0.01, 2)
        x, y = TRANSFORM.transform(24, lat)
        fx, fy = (x / 800 - xs[0]) / xs[1], (y / 800 - ys[0]) / ys[1]
        ix, iy = math.floor(fx), math.floor(fy)
        if not (0 <= ix < 49 and 0 <= iy < 47):
            raise ValueError('Section outside pinned subset')
        dx, dy = fx - ix, fy - iy
        corners = [(iy, ix, (1-dx)*(1-dy)), (iy, ix+1, dx*(1-dy)), (iy+1, ix, (1-dx)*dy), (iy+1, ix+1, dx*dy)]
        values = {}
        for name in ['salinity', 'u_eastward', 'v_northward']:
            packing = receipt['packing'][name]
            wet = all(arrays['sea_mask'][r][c] == 1 and arrays[name][r][c] != packing['fill'] for r, c, _ in corners)
            values[name] = round(sum((arrays[name][r][c]*packing['scale'] + packing['offset'])*weight for r, c, weight in corners), 6) if wet else None
        result.append({'coordinates_lon_lat': [24, lat], 'distance_from_section_start_km': round(GEOD.inv(24, 71.1, 24, lat)[2]/1000, 3), **values})
    return result


def main():
    acquisition_path = ROOT / 'research/norkyst-ingoy-2024-monthly-sample-receipts.json'
    acquisition = json.loads(acquisition_path.read_text(encoding='utf-8'))
    if len(acquisition['observations']) != 12:
        raise ValueError('Incomplete annual sample acquisition')
    frames = []
    for observation in acquisition['observations']:
        path = ROOT / observation['file']
        if hashlib.sha256(path.read_bytes()).hexdigest() != observation['receipt_sha256']:
            raise ValueError('Stale sample pin')
        receipt = json.loads(path.read_text(encoding='utf-8'))
        for kind in ['response', 'metadata']:
            if hashlib.sha256((ROOT/receipt[f'source_{kind}_file']).read_bytes()).hexdigest() != receipt[f'source_{kind}_sha256']:
                raise ValueError('Stale raw source pin')
        frames.append({'date': observation['date'], 'sample_time_utc': receipt['sample_time_utc'], 'receipt_file': observation['file'], 'receipt_sha256': observation['receipt_sha256'], 'source_url': receipt['source_url'], 'profile': profile(receipt), 'current_length_km': None, 'current_width_km': None})
    result = {'schema': 'osw.norkyst-section-timeline.v1', 'status': 'model_section_diagnostic_not_canonical_current_measurement', 'current_context_id': 'norwegian-coastal', 'year': 2024, 'sampling_rule': acquisition['sampling_rule'], 'section': {'longitude_degrees_east': 24, 'start_latitude': 71.1, 'end_latitude': 73, 'depth_m': 10, 'sample_spacing_degrees': 0.01, 'orientation': 'fixed meridional section, not a fitted flow-normal section', 'location_role': 'Ingoy region coastal-to-offshore diagnostic; selected limits are not current boundaries'}, 'interpolation': 'Bilinear in projected grid coordinates, four wet non-fill corners required; 3.2 km decimated source spacing, approximately 1.1 km display spacing adds no resolution.', 'source_project': 'Norkyst_v3', 'source_license': 'CC-BY-4.0', 'credit': 'Contains modified Norkyst v3 hindcast data from MET Norway and the Institute of Marine Research; Albretsen, Sperrevik and Simonsen (2026), archive; model description Christensen et al. (2026), doi:10.5194/gmd-19-2785-2026. OSW selects and interpolates section samples.', 'source_catalog_url': 'https://thredds.met.no/thredds/catalog/romshindcast/norkyst_v3/catalog.html', 'acquisition_file': acquisition_path.relative_to(ROOT).as_posix(), 'acquisition_sha256': hashlib.sha256(acquisition_path.read_bytes()).hexdigest(), 'generator_file': Path(__file__).relative_to(ROOT).as_posix(), 'generator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'annual_extrema_eligible': False, 'limitations': 'Hourly hindcast snapshots include tides and weather-driven variability. They are not monthly means, observations, a climatology or a current footprint. Low salinity and flow components alone do not identify current boundaries. Width, whole-current length and annual extrema remain unknown. Missing four-corner support remains a gap.', 'frames': frames}
    protocol = ROOT / 'plans/norkyst-ingoy-section-sampling-protocol-v1.md'
    result['protocol_file'] = protocol.relative_to(ROOT).as_posix()
    result['protocol_sha256'] = hashlib.sha256(protocol.read_bytes()).hexdigest()
    OUTPUT.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print('Built 12 fixed-section snapshots, 191 samples each; no current-width inference')


if __name__ == '__main__':
    main()
