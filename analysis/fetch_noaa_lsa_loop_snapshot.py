"""Explicit acquisition of a pinned regional velocity field; never run in builds."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import urllib.request
import netCDF4
import numpy as np
from fetch_noaa_lsa_geostrophic_snapshot import URL, EXPECTED_SHA256, PRODUCT_PAGE, ROOT

OUTPUT = ROOT / 'research/noaa-lsa-geostrophic-loop-20260925.json'

def extract(content):
    digest = hashlib.sha256(content).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError('Changed pinned NOAA source')
    dataset = netCDF4.Dataset('inmemory', memory=content)
    try:
        lon = np.asarray(dataset['longitude'][:], dtype=float)
        lat = np.asarray(dataset['latitude'][:], dtype=float)
        if (len(lat), len(lon)) != (720, 1440):
            raise ValueError('Unexpected global grid')
        ix = np.where((lon >= -98) & (lon <= -79))[0]
        iy = np.where((lat >= 19) & (lat <= 31))[0]
        if (len(iy), len(ix)) != (48, 76):
            raise ValueError('Unexpected regional grid')
        time = dataset['time']
        bounds = netCDF4.num2date(dataset['time_bnds'][0], time.units, calendar=time.calendar)
        if [str(b)[:10] for b in bounds] != ['2026-09-25', '2026-09-26']:
            raise ValueError('Unexpected source date')
        fields = {}
        for name in ['ugos', 'vgos']:
            variable = dataset[name]
            variable.set_auto_maskandscale(False)
            if variable.units != 'm/s' or variable.scale_factor != .0001 or variable._FillValue != -2147483648:
                raise ValueError('Unexpected velocity encoding')
            fields[name] = variable[0, iy[0]:iy[-1]+1, ix[0]:ix[-1]+1].tolist()
        return {'schema':'osw.almanac.noaa-lsa-geostrophic-subset.v1',
            'source_provider':'NOAA/NESDIS Laboratory for Satellite Altimetry via NOAA CoastWatch',
            'source_url':URL, 'product_page':PRODUCT_PAGE, 'source_response_sha256':digest,
            'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),
            'source_product_status':dataset.getncattr('cw:product_status'),
            'source_algorithm':dataset.getncattr('cw:processing_algorithm'),
            'source_time_start':'2026-09-25T00:00:00Z', 'source_time_end_exclusive':'2026-09-26T00:00:00Z',
            'source_file_role':'Absolute surface geostrophic velocity; SLA is not used as absolute dynamic topography',
            'source_grid_shape':[720,1440], 'subset_bounds':{'south':19,'north':31,'west':-98,'east':-79},
            'subset_shape':[48,76], 'grid_origin_lon_lat':[float(lon[ix[0]]),float(lat[iy[0]])],
            'grid_step_degrees':[.25,.25], 'velocity_scale_m_s_per_raw_unit':.0001,
            'raw_fill_value':-2147483648, 'velocity_fields_raw_int32':fields,
            'model_limit':'Frozen-time surface streamline experiment; no whole-current axis, particle trajectory or depth structure',
            'source_use_review_status':'pending_for_this_regional_subset',
            'attribution':'Altimetry data provided by NOAA Laboratory for Satellite Altimetry; acknowledge NOAA CoastWatch.'}
    finally:
        dataset.close()

if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument('--source-file',type=Path)
    args=parser.parse_args()
    content=args.source_file.read_bytes() if args.source_file else urllib.request.urlopen(URL,timeout=90).read()
    receipt=extract(content)
    if OUTPUT.exists(): raise ValueError('Receipt already exists; review before replacing')
    OUTPUT.write_text(json.dumps(receipt,separators=(',',':'))+'\n',encoding='utf-8')
    print('Pinned Loop region',receipt['subset_shape'],receipt['source_response_sha256'])
