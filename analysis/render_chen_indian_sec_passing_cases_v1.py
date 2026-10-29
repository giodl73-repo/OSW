"""Reproduce and render the three source cases containing previously passing traces."""
import json
import os
from pathlib import Path
import tempfile
import urllib.request
import chen_indian_sec_axis_feasibility_v1 as frozen
import inspect_chen_indian_sec_headers_v1 as custody
import inspect_chen_indian_sec_coordinates_v1 as coordinates

REQUEST='research/chen-indian-sec-passing-map-request-v1.json'
OUTPUT=Path('.pytest_cache/chen-indian-sec-passing-maps-v1')
YEARS=[1995,2010,2011]


def main():
    if os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps' or len(os.sched_getaffinity(0))!=1:
        raise RuntimeError('One cloud CPU on declared branch required')
    raw=Path(REQUEST).read_bytes();r=json.loads(raw)
    if r['schema']!='osw.chen-indian-sec-passing-map-request.v1' or r['execute'] is not True or r['years']!=YEARS or r['length_calculation_permitted'] is not False:
        raise ValueError('Frozen render-only request mismatch')
    for path,expected in r['input_sha256'].items():
        if custody.digest(Path(path).read_bytes())!=expected:raise ValueError('Frozen render input changed: '+path)
    report={'schema':'osw.chen-indian-sec-passing-map-report.v1','source_commit':os.environ['GITHUB_SHA'],
            'request_sha256':custody.digest(raw),'status':'FAILED','new_measurements':0,'lengths_calculated':False,
            'reproduced_routes':0,'years':YEARS}
    OUTPUT.mkdir(parents=True,exist_ok=False)
    try:
        from scipy.io import loadmat
        reference=json.loads(Path('research/chen-indian-sec-axis-feasibility-run-v2/report.json').read_bytes())
        with tempfile.TemporaryDirectory(prefix='osw-chen-passing-maps-') as directory:
            original=Path(directory)/'original.mat'
            with urllib.request.urlopen(custody.URL,timeout=40) as response:report['custody']=custody.acquire(response,original)
            if report['custody']['sha256']!=coordinates.SOURCE_SHA256 or report['custody']['bytes']!=coordinates.SOURCE_BYTES:
                raise ValueError('Original custody changed')
            data=loadmat(original,variable_names=frozen.VARIABLES,squeeze_me=False)
            if {p for p in data if not p.startswith('__')}!=set(frozen.VARIABLES):raise ValueError('Unexpected variables')
            lat=data['lat'][0];lon=data['lon'][0]
            if data['uyear'].shape!=(76,212,24) or data['vyear'].shape!=(76,212,24):raise ValueError('Unexpected field shape')
            for year in YEARS:
                case=next(c for c in reference['cases'] if c['id']=='provider-year-'+str(year))
                index=case['source_slice_index'];u=data['uyear'][:,:,index];v=data['vyear'][:,:,index]
                reproduced=[frozen.trace(lat,lon,u,v,kernel) for kernel in frozen.KERNELS]
                if reproduced!=case['routes']:raise ValueError('Source-field traces differ from retained frozen results')
                frozen.draw(case,lat,lon,u,v,OUTPUT)
                report['reproduced_routes']+=len(reproduced)
        report['status']='THREE_ACTUAL_SOURCE_MAPS_RENDERED_NINE_REPRODUCED_ROUTES_IDENTICAL'
    except Exception as error:
        report['error_type']=type(error).__name__;report['error']=str(error)[:500];raise
    finally:
        (OUTPUT/'report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
        print(json.dumps(report),flush=True)


if __name__=='__main__':main()
