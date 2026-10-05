"""Explicitly freeze one public DUACS ADT response served by GCOOS."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from build_gulf_stream_geostrophic_path import ROOT

DATASET='SSH_GoA_2026'
PAGE=f'https://gcoos5.geos.tamu.edu/erddap/griddap/{DATASET}.html'
SELECT='[(2026-09-25T00:00:00Z)][(17.0625):1:(31.9375)][(-98.9375):1:(-79.0625)]'
URL=f'https://gcoos5.geos.tamu.edu/erddap/griddap/{DATASET}.nc?'+','.join(n+SELECT for n in ['adt','ugos','vgos'])
RESPONSE_SHA256='70e3ca76813cc39bf449baa72074e4fff066f7f7e1ad0b7ba46a1cc0a6257d57'
OUTPUT=ROOT/'research/gcoos-duacs-loop-20260925.json'

def extract(content, *, date="2026-09-25", expected_sha256=RESPONSE_SHA256, source_url=URL):
    dataset_id="SSH_GoA_"+date[:4]
    page=f"https://gcoos5.geos.tamu.edu/erddap/griddap/{dataset_id}.html"
    import netCDF4
    import numpy as np
    checksum=hashlib.sha256(content).hexdigest()
    if checksum!=expected_sha256:
        raise ValueError('Different response bytes; ERDDAP history timestamps may change. Review numerical payload and metadata before accepting another snapshot.')
    dataset=netCDF4.Dataset('inmemory',memory=content)
    try:
        lon=np.asarray(dataset['longitude'][:]);lat=np.asarray(dataset['latitude'][:])
        if lon.shape!=(160,) or lat.shape!=(120,) or not np.allclose(np.diff(lon),.125) or not np.allclose(np.diff(lat),.125):
            raise ValueError('Unexpected DUACS grid')
        if [float(lon[0]),float(lon[-1]),float(lat[0]),float(lat[-1])]!=[-98.9375,-79.0625,17.0625,31.9375]:
            raise ValueError('Unexpected region')
        time=dataset['time'];dates=netCDF4.num2date(time[:],time.units)
        if len(dates)!=1 or str(dates[0])[:19]!=date+' 00:00:00':
            raise ValueError('Unexpected observation date')
        fields={}
        for name,units,standard in [('adt','m','sea_surface_height_above_geoid'),('ugos','m/s','surface_geostrophic_eastward_sea_water_velocity'),('vgos','m/s','surface_geostrophic_northward_sea_water_velocity')]:
            var=dataset[name]
            if var.units!=units or var.standard_name!=standard or var.shape!=(1,120,160):
                raise ValueError('Unexpected field identity/units/dimensions: '+name)
            values=np.ma.filled(var[0],np.nan)
            fields[name]=[[float(v) if np.isfinite(v) else None for v in row] for row in values]
        metadata={k:dataset.getncattr(k) for k in ['subset_datasetId','subset_productId','acknowledgment','license','history','institution','publisher_name','source','Conventions']}
        if metadata['subset_datasetId']!='cmems_obs-sl_glo_phy-ssh_nrt_allsat-l4-duacs-0.125deg_P1D_202411':
            raise ValueError('Unexpected source version')
        return {'schema':'osw.gcoos-duacs-adt-subset.v1','dataset_id':dataset_id,'source_url':source_url,'dataset_page':page,
            'source_response_sha256':checksum,'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),
            'observation_date':date,'source_time_label':date+'T00:00:00Z',
            'time_scope':'Provider labels a daily average; source has no time_bnds. Exact averaging support is not invented.',
            'source_metadata':metadata,'grid_origin_lon_lat':[-98.9375,17.0625],
            'grid_step_degrees':[.125,.125],'grid_shape':[120,160],
            'field_units':{'adt':'m','ugos':'m/s','vgos':'m/s'},'fields':fields,
            'source_use_review_status':'pending_for_regional_snapshot',
            'independence_note':'Different DUACS product and geometry method from NOAA RADS; both use satellite altimetry and may share missions. Not independent in-situ confirmation.'}
    finally:dataset.close()

if __name__=='__main__':
    import argparse,requests
    parser=argparse.ArgumentParser();parser.add_argument('--source-file',type=Path);args=parser.parse_args()
    if OUTPUT.exists():raise ValueError('Snapshot exists; review before replacing')
    if args.source_file:content=args.source_file.read_bytes()
    else:
        response=requests.get(URL,timeout=60);response.raise_for_status();content=response.content
    receipt=extract(content);OUTPUT.write_text(json.dumps(receipt,separators=(',',':'))+'\n',encoding='utf-8')
    print('Pinned ADT and velocity fields',receipt['grid_shape'],receipt['source_response_sha256'])
