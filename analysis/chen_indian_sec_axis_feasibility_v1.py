"""Frozen regional model-core tracing diagnostic. No lengths or measurement admission."""
import json
import os
from pathlib import Path
import tempfile
import urllib.request

import numpy as np
import inspect_chen_indian_sec_headers_v1 as custody
import inspect_chen_indian_sec_coordinates_v1 as coordinates

REQUEST = 'research/chen-indian-sec-axis-feasibility-request-v1.json'
OUTPUT = Path('.pytest_cache/chen-indian-sec-axis-feasibility-v1')
VARIABLES = ['lat', 'lon', 'time_year', 'uyear', 'vyear']
KERNELS = (1, 3, 5)
NOMINAL_KERNEL = 3
WEST, EAST, SOUTH, NORTH = 65.0, 105.0, -18.0, -6.0
MAX_ROW_JUMP = 3


def smooth(field, kernel):
    """Finite-neighbor arithmetic mean; never fill a missing center cell."""
    if kernel not in KERNELS:
        raise ValueError('Unfrozen smoothing kernel')
    field = np.asarray(field, dtype=float)
    finite = np.isfinite(field)
    if kernel == 1:
        return field.copy()
    pad = kernel // 2
    values = np.pad(np.where(finite, field, 0.0), pad)
    valid = np.pad(finite.astype(int), pad)
    total = np.zeros_like(field)
    count = np.zeros_like(field)
    for row in range(kernel):
        for column in range(kernel):
            total += values[row:row+field.shape[0], column:column+field.shape[1]]
            count += valid[row:row+field.shape[0], column:column+field.shape[1]]
    out = np.full_like(field, np.nan)
    use = finite & (count >= np.ceil(0.8 * kernel * kernel))
    np.divide(total, count, out=out, where=use)
    return out


def trace(lat, lon, u, v, kernel):
    lat, lon = np.asarray(lat), np.asarray(lon)
    u, v = np.asarray(u), np.asarray(v)
    if u.shape != (len(lat), len(lon)) or v.shape != u.shape:
        raise ValueError('Field/coordinate shapes disagree')
    if not np.all(np.diff(lat) > 0) or not np.all(np.diff(lon) > 0):
        raise ValueError('Increasing source coordinates required')
    rows = np.where((lat >= SOUTH) & (lat <= NORTH))[0]
    west = int(np.argmin(np.abs(lon - WEST)))
    east = int(np.argmin(np.abs(lon - EAST)))
    if len(rows) < 5 or west >= east or lon[0] > WEST or lon[-1] < EAST:
        raise ValueError('Declared regional gates not supported')
    zonal = smooth(np.where(np.isfinite(u) & np.isfinite(v), u, np.nan), kernel)
    points, failures = [], []
    previous = None
    for column in range(east, west-1, -1):
        candidate = zonal[rows, column]
        wet = np.isfinite(candidate) & (candidate < 0)
        if not wet.any():
            failures.append({'column':column,'reason':'NO_FINITE_WESTWARD_CORE'})
            points.append(None)
            previous = None
            continue
        # First minimum is the declared southmost tie-break; no inferred branch bridge.
        local = int(np.argmin(np.where(wet, candidate, np.inf)))
        row = int(rows[local])
        if local in (0, len(rows)-1):
            failures.append({'column':column,'reason':'CORE_TOUCHES_SEARCH_BAND_EDGE'})
        jump = None if previous is None else abs(row-previous)
        if jump is not None and jump > MAX_ROW_JUMP:
            failures.append({'column':column,'reason':'CORE_JUMPS_MORE_THAN_THREE_LATITUDE_CELLS','row_jump':jump})
        points.append({'longitude':float(lon[column]), 'latitude':float(lat[row]),
                       'column':column,'row':row,'row_jump_from_previous':jump})
        previous = row
    return {'kernel_cells':kernel,'intended_gate_longitudes':[EAST,WEST],
            'sampled_gate_longitudes':[float(lon[east]),float(lon[west])],
            'search_latitude_band':[SOUTH,NORTH],'points':points,'failures':failures,
            'status':'TRACE_FEASIBILITY_PASSED_REQUIRES_PHYSICAL_REVIEW' if not failures else 'TRACE_FEASIBILITY_FAILED',
            'physical_axis_admitted':False,'length_km':None,'rank_eligible':False}


def draw(case, lat, lon, u, v, folder):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    figure, axes = plt.subplots(1,3,figsize=(15,4.6),sharex=True,sharey=True)
    for ax, route in zip(axes,case['routes']):
        zonal=smooth(u,route['kernel_cells'])
        mask=(lat>=SOUTH)&(lat<=NORTH)
        cols=(lon>=WEST-1)&(lon<=EAST+1)
        selected=zonal[np.ix_(mask,cols)]
        scale=np.nanmax(np.abs(selected)) if np.isfinite(selected).any() else 1.0
        scale=max(float(scale),1e-30)
        mesh=ax.pcolormesh(lon[cols],lat[mask],-selected/scale,cmap='RdBu_r',vmin=-1,vmax=1,shading='nearest')
        xx,yy=np.meshgrid(lon,lat)
        speed=np.hypot(u,v)
        arrowmask=np.isfinite(speed)&(speed>0)&(xx>=WEST)&(xx<=EAST)&(yy>=SOUTH)&(yy<=NORTH)
        qu=np.divide(u,speed,out=np.zeros_like(u),where=arrowmask)
        qv=np.divide(v,speed,out=np.zeros_like(v),where=arrowmask)
        ax.quiver(xx[::5,::5],yy[::5,::5],qu[::5,::5],qv[::5,::5],color='#334155',scale=24,width=.003)
        for a,b in zip(route['points'],route['points'][1:]):
            if a is None or b is None or abs(a['row']-b['row'])>MAX_ROW_JUMP:
                continue
            ax.plot([a['longitude'],b['longitude']],[a['latitude'],b['latitude']],color='#fef08a',lw=2)
        boundary=[p for p in route['points'] if p is not None and (p['row']==np.where(mask)[0][0] or p['row']==np.where(mask)[0][-1])]
        if boundary:ax.scatter([p['longitude'] for p in boundary],[p['latitude'] for p in boundary],color='black',s=10,zorder=5)
        passed=not route['failures']
        ax.set_title(str(route['kernel_cells'])+' x '+str(route['kernel_cells'])+' cell mean | '+('PASS' if passed else str(len(route['failures']))+' flags'),fontsize=10)
        ax.set_xlim(WEST-1,EAST+1);ax.set_ylim(SOUTH-1,NORTH+1)
        ax.set_xlabel('Longitude (degrees east)');ax.grid(alpha=.2)
        ax.axvline(WEST,color='black',ls=':',lw=.7);ax.axvline(EAST,color='black',ls=':',lw=.7)
    axes[0].set_ylabel('Latitude (degrees north)')
    figure.suptitle('Indian SEC | '+case['id']+' | upper-100 m SON model-core diagnostic',fontsize=13)
    figure.text(.04,.02,'Relative westward component; arrows show direction only. Yellow: selected core; gaps/jumps remain disconnected. No physical axis or length admitted.',fontsize=9)
    figure.subplots_adjust(left=.06,right=.97,bottom=.16,top=.82,wspace=.12)
    for extension in ['png','svg']:
        figure.savefig(folder/(case['id']+'.'+extension),dpi=110)
    plt.close(figure)


def main():
    if os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps' or len(os.sched_getaffinity(0))!=1:
        raise RuntimeError('Declared one-CPU cloud branch required')
    raw=Path(REQUEST).read_bytes();request=json.loads(raw)
    if request['schema']!='osw.chen-indian-sec-axis-feasibility-request.v1' or request['execute'] is not True or request['bounded_source_diagnostic_permitted'] is not True or request['measurement_admission_permitted'] is not False:
        raise ValueError('Scoped diagnostic request invalid')
    for path,expected in request['input_sha256'].items():
        if custody.digest(Path(path).read_bytes())!=expected:raise ValueError('Frozen diagnostic input changed: '+path)
    phase=json.loads(Path('research/current-gap-delivery-phase.json').read_bytes())
    if phase['heavy_work_permitted'] is not False or phase['phase']!='source-review-only-v1':raise ValueError('Broad field processing must stay disabled')
    from scipy.io import loadmat
    OUTPUT.mkdir(parents=True,exist_ok=False)
    report={'schema':'osw.chen-indian-sec-axis-feasibility-report.v1','source_commit':os.environ['GITHUB_SHA'],
            'request_sha256':custody.digest(raw),'status':'FAILED','new_measurements':0,
            'physical_axis_admitted':False,'lengths_calculated':False,'field_source':'HYCOM_CR upper100m SON provider-described product',
            'units_status':'No speed measurement. Core argmin and normalized direction assume standard east/north component signs; MAT variable units are undocumented.',
            'cases':[]}
    try:
        with tempfile.TemporaryDirectory(prefix='osw-chen-sec-axis-') as directory:
            target=Path(directory)/'original.mat'
            with urllib.request.urlopen(custody.URL,timeout=40) as response:report['custody']=custody.acquire(response,target)
            if report['custody']['sha256']!=coordinates.SOURCE_SHA256 or report['custody']['bytes']!=coordinates.SOURCE_BYTES:raise ValueError('Exact source changed')
            data=loadmat(target,variable_names=VARIABLES,squeeze_me=False)
            if {p for p in data if not p.startswith('__')}!=set(VARIABLES):raise ValueError('Unexpected loaded variables')
            lat=data['lat'][0];lon=data['lon'][0]
            prior=json.loads(Path('research/chen-indian-sec-coordinate-run-v1/report.json').read_bytes())['coordinates']
            for name in ['lat','lon','time_year']:
                if data[name].tolist()[0]!=prior[name]['values']:raise ValueError('Coordinate identity changed')
            u=data['uyear'];v=data['vyear']
            if u.shape!=(76,212,24) or v.shape!=u.shape:raise ValueError('Field shapes changed')
            if any(np.any(np.abs(a[np.isfinite(a)])>1e10) for a in [u,v]):raise ValueError('Potential finite fill value; source mask unresolved')
            for index in range(-1,24):
                if index<0:
                    wet=np.isfinite(u)&np.isfinite(v)
                    count=wet.sum(axis=2)
                    uu=np.divide(np.where(wet,u,0).sum(axis=2),count,out=np.full(u.shape[:2],np.nan),where=count==24)
                    vv=np.divide(np.where(wet,v,0).sum(axis=2),count,out=np.full(v.shape[:2],np.nan),where=count==24)
                    case_id='mean-of-24-SON-fields'
                else:uu=u[:,:,index];vv=v[:,:,index];case_id='provider-year-'+str(1993+index)
                case={'id':case_id,'source_slice_index':index if index>=0 else None,
                      'year_label_basis':'Provider1993–2016 ordered support corroborated by inferred MATLAB dates; not an observation date.',
                      'routes':[trace(lat,lon,uu,vv,kernel) for kernel in KERNELS]}
                report['cases'].append(case)
                if index in [-1,1,4,22,23]:draw(case,lat,lon,uu,vv,OUTPUT)
            report['status']='REGIONAL_MODEL_CORE_FEASIBILITY_DIAGNOSTICS_COMPLETE_NOT_MEASUREMENTS'
            report['trace_count']=sum(len(c['routes']) for c in report['cases'])
            report['feasibility_pass_count']=sum(not r['failures'] for c in report['cases'] for r in c['routes'])
    except Exception as error:
        report['error_type']=type(error).__name__;report['error']=str(error)[:500];raise
    finally:
        (OUTPUT/'report.json').write_bytes((json.dumps(report,indent=2,allow_nan=False)+'\n').encode())
        print(json.dumps({k:v for k,v in report.items() if k!='cases'}),flush=True)


if __name__=='__main__':main()
