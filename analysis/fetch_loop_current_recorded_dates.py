"""Explicit acquisition of four predeclared repeat dates; builds stay offline."""
import argparse
import hashlib
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import requests
from fetch_noaa_lsa_loop_snapshot import extract as noaa_extract, ROOT
from fetch_gcoos_loop_adt_snapshot import extract as adt_extract

DATES=('2025-01-15','2025-04-15','2025-07-15','2025-10-15')
MANIFEST=ROOT/'research/loop-current-recorded-date-sources.json'

def acquire(date):
    stamp=date.replace('-','')
    old=json.loads((ROOT/f'research/noaa-lsa-geostrophic-gulf-stream-{stamp}.json').read_text(encoding='utf-8'))
    select=f'[({date}T00:00:00Z)][(17.0625):1:(31.9375)][(-98.9375):1:(-79.0625)]'
    adt_url='https://gcoos5.geos.tamu.edu/erddap/griddap/SSH_GoA_2025.nc?'+','.join(n+select for n in ['adt','ugos','vgos'])
    records={}
    for method,url in [('noaa',old['source_url']),('adt',adt_url)]:
        scratch=ROOT/f'tmp/loop-{method}-{stamp}.nc'
        if scratch.exists():content=scratch.read_bytes()
        else:
            response=requests.get(url,timeout=60);response.raise_for_status();content=response.content
            scratch.write_bytes(content)
        sha=hashlib.sha256(content).hexdigest()
        if method=='noaa' and sha!=old['source_response_sha256']:raise ValueError('Changed already-pinned NOAA source: '+date)
        # Initial DUACS pin is explicit. The parser checks scientific identity,
        # units, date, grid and version before any receipt is admitted.
        receipt=(noaa_extract if method=='noaa' else adt_extract)(content,date=date,expected_sha256=sha,source_url=url)
        path=ROOT/f'research/{"noaa-lsa-geostrophic-loop" if method=="noaa" else "gcoos-duacs-loop"}-{stamp}.json'
        if path.exists():raise ValueError('Receipt exists; review before replacing: '+str(path))
        path.write_text(json.dumps(receipt,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
        records[method]={'file':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'source_response_sha256':sha,'source_url':url}
    return {'date':date,**records}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--initial-pin',action='store_true');args=parser.parse_args()
    if not args.initial_pin:raise ValueError('Explicit --initial-pin required for new regional snapshots')
    if MANIFEST.exists():raise ValueError('Manifest exists; review before replacing')
    with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(acquire,DATES))
    result={'schema':'osw.loop-current-recorded-date-sources.v1','selection':'Four predeclared quarterly-spaced 2025 dates, not selected by path length, success, named phase or extrema.',
        'created_at_utc':datetime.now(timezone.utc).isoformat(),'dates':rows,
        'annual_coverage_status':'four_days_only_not_a_seasonal_climatology','source_use_review_status':'pending_for_new_regional_snapshots'}
    MANIFEST.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    for row in rows:print(row['date'],row['noaa']['source_response_sha256'],row['adt']['source_response_sha256'])
