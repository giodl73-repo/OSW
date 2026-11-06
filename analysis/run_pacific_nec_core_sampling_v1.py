"""Cloud-only latitude-window and native-supported path-sampling experiment."""
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess

import pacific_nec_core_sampling_v1 as sampling
import pacific_nec_connected_core_v1 as native
import pacific_nec_monthly_dimensions_v1 as source
import run_pacific_nec_connected_core_v1 as custody

ROOT=Path(__file__).resolve().parents[1]
REQUEST='research/pacific-nec-core-sampling-request-v1.json'
PREFLIGHT='research/pacific-nec-core-sampling-preflight-v1.json'
PROTOCOL='plans/pacific-nec-core-window-sampling-protocol-v1.md'
OUT=ROOT/'.pytest_cache/pacific-nec-core-sampling-v1'
WORK=ROOT/'.pytest_cache/pacific-nec-core-sampling-work-v1'
WITNESSES=ROOT/'.pytest_cache/pacific-nec-core-sampling-witnesses-v1'
require=source.require
sha=source.sha
write=source.write
read=source.read


def guard():
    require(os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true'
        and os.environ.get('RUNNER_OS')=='Linux'
        and os.environ.get('OSW_PACIFIC_NEC_CORE_SAMPLING_V1')=='1','Cloud-only source sampling')
    require(os.environ.get('GITHUB_REF')=='refs/heads/codex/current-measurement-gaps'
        and os.environ.get('GITHUB_REPOSITORY')=='giodl73-repo/OSW'
        and os.environ.get('GITHUB_EVENT_NAME')=='push','Wrong repository/event/ref')
    require(len(os.sched_getaffinity(0))==1 and os.getpriority(os.PRIO_PROCESS,0)>=15,'One low-priority CPU required')
    for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):require(os.environ.get(key)=='1','Worker limit differs')
    request=read(REQUEST)
    require(request['schema']=='osw.pacific-nec-core-sampling-request.v1' and request['execute'] is True
        and request['cloud_saved_source_processing_permitted'] is True,'Scoped sampling disabled')
    for key in ('provider_download_permitted','local_source_processing_permitted','native_build_permitted',
                'wasm_build_permitted','browser_automation_permitted','installation_permitted','main_update_permitted'):
        require(request[key] is False,'Forbidden permission: '+key)
    require(request['max_cloud_jobs']==1 and request['max_local_heavy_jobs']==0,'Job bounds differ')
    require(custody.file_sha(ROOT/PREFLIGHT)==request['preflight_sha256'],'Preflight differs')
    pref=read(PREFLIGHT)
    for path,pin in pref['input_sha256'].items():require(custody.file_sha(ROOT/path)==pin,'Source differs: '+path)
    require(read('research/current-gap-delivery-phase.json')['heavy_work_permitted'] is False,'Broad phase enabled')
    for path in pref['disabled_requests']:
        value=read(path);require(value.get('execute',value.get('execution_permitted')) is False,'Other request enabled')
    def git(*args):return subprocess.check_output(['git','-c','core.fsmonitor=false',*args],text=True,timeout=55).strip()
    require(git('rev-parse','HEAD')==os.environ['GITHUB_SHA'] and not git('status','--porcelain'),'Checkout differs')
    require(git('ls-remote','origin','refs/heads/codex/current-measurement-gaps').split()[0]==os.environ['GITHUB_SHA'],'Working branch moved')
    require(git('ls-remote','origin','refs/heads/main').split()[0]==source.MAIN,'Main moved')
    for path,row in pref['installed_files'].items():
        require(git('rev-parse','HEAD:'+path)==row['git_blob_oid'] and int(git('cat-file','-s',row['git_blob_oid']))==row['bytes'],'Installed artifact differs')


def diagnose(means,preceding):
    from pyproj import Geod
    geod=Geod(ellps='WGS84');longitude=[130+i/3 for i in range(331)]
    def distance(x,a,y,b):return geod.inv(x,a,y,b)[2]/1000
    cases=[];native_paths=[];thinning=[];replayed=[]
    WITNESSES.mkdir(parents=True,exist_ok=False)
    with (WITNESSES/'paths.jsonl').open('xb') as stream:
        for month in range(1,13):
            for low,high in ((8,18),(7,19),(9,17)):
                latitude=[low+i/3 for i in range((high-low)*3+1)];start=(low-4)*3;stop=(high-4)*3+1
                east=means[month-1,start:stop,:,0].tolist();north=means[month-1,start:stop,:,1].tolist()
                labels,groups=native.components(native.eligible(east,north,.025))
                cache={};baseline=None
                for stride in (1,2,4):
                    for x_phase in range(stride):
                        x_indices=sampling.indices(len(longitude),stride,x_phase)
                        for y_phase in range(stride):
                            y_indices=sampling.indices(len(latitude),stride,y_phase)
                            candidate=sampling.anchored_path(latitude,longitude,east,north,x_indices,y_indices,cache)
                            path=candidate.pop('path');anchors=candidate.pop('anchors')
                            points=None;witness_length=None;anchor_length=None;contact=None;component=None
                            if path is not None:
                                identity={labels[y][x] for x,y in enumerate(path)}
                                require(len(identity)==1 and -1 not in identity,'Coarse path lost native connectivity')
                                component=next(iter(identity));group=groups[component]
                                require(group['touches_west_gate'] and group['touches_east_gate'],'Coarse path misses native gates')
                                points=[[x,latitude[y],east[y][xi],north[y][xi]] for xi,(x,y) in enumerate(zip(longitude,path))][::-1]
                                contact=sum(y in (0,len(latitude)-1) for y in path)
                                if candidate['reason'] is None:
                                    witness_length=sampling.length(longitude,latitude,path,distance)
                                    anchor_length=sampling.length(longitude,latitude,path,distance,x_indices)
                            ident=f'2013-{month:02d}:{low}-{high}:s{stride}:x{x_phase}:y{y_phase}'
                            witness=(json.dumps({'id':ident,'points':points,'anchor_columns':x_indices,'anchor_rows':anchors},separators=(',',':'),allow_nan=False)+'\n').encode()
                            stream.write(witness)
                            row=dict(candidate,id=ident,month=month,window_deg_north=[low,high],stride=stride,x_phase=x_phase,y_phase=y_phase,
                                native_witness_length_km=witness_length,anchor_polyline_length_km=anchor_length,
                                boundary_contact_native_cells=contact,component_id=component,witness_sha256=sha(witness),
                                anchor_chord_is_physical_route=False)
                            cases.append(row)
                            if stride==1:
                                native_paths.append(dict(row,points=points))
                                baseline=(path,witness_length)
                                if low==8:
                                    old=next(r for r in preceding['months'] if r['month']==month)
                                    require(points==old['points'] and witness_length==old['length_km'] and candidate['reason']==old['reason'],
                                            'Native baseline differs from original monthly path')
                                    replayed.append(month)
                require(baseline is not None,'Native baseline missing')
                path,full_length=baseline
                for stride in (1,2,4):
                    for phase in range(stride):
                        selected=sampling.indices(len(longitude),stride,phase)
                        value=sampling.length(longitude,latitude,path,distance,selected) if full_length is not None else None
                        thinning.append({'month':month,'window_deg_north':[low,high],'stride':stride,'phase':phase,
                            'native_length_km':full_length,'thinned_representation_length_km':value,
                            'difference_from_native_km':value-full_length if value is not None else None,
                            'retained_vertices':len(selected),'new_route_selected':False,'chord_is_physical_route':False})
    require(len(cases)==756 and len(native_paths)==36 and len(thinning)==252 and replayed==list(range(1,13)),'Incomplete declared experiment')
    summaries=[]
    for window in ([8,18],[7,19],[9,17]):
        for month in range(1,13):
            rows=[r for r in cases if r['month']==month and r['window_deg_north']==window]
            valid=[r for r in rows if r['native_witness_length_km'] is not None]
            baseline=next(r for r in native_paths if r['month']==month and r['window_deg_north']==window)
            summaries.append({'month':month,'window_deg_north':window,'cases':21,'qualified_cases':len(valid),
                'native_baseline_length_km':baseline['native_witness_length_km'],
                'native_baseline_boundary_cells':baseline['boundary_contact_native_cells'],
                'candidate_method_minimum_km':min(r['native_witness_length_km'] for r in valid) if valid else None,
                'candidate_method_maximum_km':max(r['native_witness_length_km'] for r in valid) if valid else None,
                'physical_uncertainty':False,'whole_current_annual_range':False})
    return {'cases':cases,'native_window_paths':native_paths,'vertex_thinning_cases':thinning,
            'window_month_summaries':summaries,'preceding_native_months_exactly_replayed':replayed}


def figures(report):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    windows=([8,18],[7,19],[9,17]);colors=('tab:blue','tab:orange','tab:green')
    fig,(atlas,series)=plt.subplots(1,2,figsize=(14,6.5),layout='constrained')
    for window,color in zip(windows,colors):
        row=next(r for r in report['native_window_paths'] if r['month']==5 and r['window_deg_north']==window)
        if row['points'] is not None:atlas.plot([p[0] for p in row['points']],[p[1] for p in row['points']],color=color,label=f'{window[0]}–{window[1]}N')
        rows=[r for r in report['native_window_paths'] if r['window_deg_north']==window]
        series.plot([r['month'] for r in rows],[r['native_witness_length_km'] if r['native_witness_length_km'] is not None else np.nan for r in rows],marker='o',color=color,label=f'{window[0]}–{window[1]}N')
        for r in rows:
            if r['native_witness_length_km'] is None:series.plot(r['month'],.04,'x',color=color,transform=series.get_xaxis_transform())
    atlas.set(xlim=(130,240),ylim=(6.5,19.5),title='May2013 | native paths in three fixed windows',ylabel='Latitude north')
    atlas.set_xticks([130,180,240],['130E','180','120W']);atlas.grid(alpha=.2);atlas.legend(fontsize=9)
    series.set(title='Native-grid regional operator lengths',xlabel='2013 month',ylabel='WGS84 km',xticks=range(1,13));series.grid(alpha=.2);series.legend(fontsize=9)
    fig.suptitle('Pacific NEC | OSCAR2017.0 | nominal15m near-surface product\nLatitude-window sensitivity; numerical candidates, not whole-current lengths',fontsize=13)
    fig.supxlabel('Fixed gates130E–120W. Windows are OSW choices, not physical boundaries or confidence limits. Crosses mean withheld.',fontsize=10)
    fig.savefig(OUT/'window-sensitivity.png',dpi=150);fig.savefig(OUT/'window-sensitivity.svg');plt.close(fig)
    fig,(search,vertices)=plt.subplots(1,2,figsize=(14,6.5),layout='constrained')
    for stride,color in zip((1,2,4),colors):
        lower=[];upper=[];failures=0
        for month in range(1,13):
            rows=[r for r in report['cases'] if r['month']==month and r['window_deg_north']==[8,18] and r['stride']==stride]
            values=[r['native_witness_length_km'] for r in rows if r['native_witness_length_km'] is not None]
            failures+=len(rows)-len(values);lower.append(min(values) if values else np.nan);upper.append(max(values) if values else np.nan)
        search.plot(range(1,13),lower,color=color,label=f'stride{stride}: {failures} withheld')
        search.fill_between(range(1,13),lower,upper,color=color,alpha=.16)
        rows=[r for r in report['vertex_thinning_cases'] if r['window_deg_north']==[8,18] and r['stride']==stride]
        lo=[];hi=[]
        for month in range(1,13):
            values=[r['difference_from_native_km'] for r in rows if r['month']==month and r['difference_from_native_km'] is not None]
            lo.append(min(values) if values else np.nan);hi.append(max(values) if values else np.nan)
        vertices.plot(range(1,13),lo,color=color,label=f'vertex stride{stride}');vertices.fill_between(range(1,13),lo,hi,color=color,alpha=.16)
    search.set(title='Anchor-grid search | native-supported witnesses',xlabel='2013 month',ylabel='Native-witness WGS84 km',xticks=range(1,13));search.grid(alpha=.2);search.legend(fontsize=9)
    vertices.set(title='Vertex thinning | same original native path',xlabel='2013 month',ylabel='Difference from full vertex sum (km)',xticks=range(1,13));vertices.grid(alpha=.2);vertices.legend(fontsize=9)
    fig.suptitle('Pacific NEC | preceding8–18N window |2013\nSearch discretization and representation effects are separate quantities',fontsize=13)
    fig.supxlabel('Bands span declared phases, not physical uncertainty. Same native data at every stride. Chord lengths do not establish flow along shortcuts.',fontsize=10)
    fig.savefig(OUT/'sampling-sensitivity.png',dpi=150);fig.savefig(OUT/'sampling-sensitivity.svg');plt.close(fig)


def main():
    guard();OUT.mkdir(parents=True,exist_ok=False)
    custody.WORK=WORK;target=custody.saved_source()
    means,counts,times,month_counts,attrs=source.parse_cube(json.loads((target/'metadata.json').read_bytes()),target/'vectors.csv')
    acquisition=read('research/pacific-nec-monthly-dimensions-run-v1/acquisition.json')
    require(times==acquisition['times'] and month_counts==acquisition['month_sample_counts'],'Monthly source support differs')
    report=diagnose(means,read('research/pacific-nec-connected-core-run-v1/diagnostic.json'))
    report.update(schema='osw.pacific-nec-core-window-sampling.v1',status='NUMERICAL_SENSITIVITY_CANDIDATES_REVIEW_REQUIRED',
        entity_id='current:pacific-north-equatorial',year=2013,nominal_depth_coordinate_m=15,
        source_commit=os.environ['GITHUB_SHA'],run_id=os.environ['GITHUB_RUN_ID'],run_attempt=os.environ['GITHUB_RUN_ATTEMPT'],
        source_artifact=custody.ARTIFACT,protocol_sha256=custody.file_sha(ROOT/PROTOCOL),
        operator_sha256=custody.file_sha(ROOT/'analysis/pacific_nec_core_sampling_v1.py'),
        source_product_resolution_changed=False,physical_uncertainty=None,whole_current_length_km=None,
        whole_current_annual_ranges=None,independent_observations_added=0,installed=False,main_updated=False,full_goal_complete=False)
    write(OUT/'diagnostic.json',report);figures(report)
    result={'schema':'osw.pacific-nec-core-sampling-result.v1','status':'PASS_DECLARED_CASES_AND_TWELVE_NATIVE_REPLAYS_REVIEW_PENDING',
        'source_commit':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],
        'source_artifact':custody.ARTIFACT,'anchor_cases':756,'vertex_thinning_cases':252,'native_window_paths':36,
        'original_nominal_paths_exactly_replayed':12,'qualified_anchor_cases':sum(r['native_witness_length_km'] is not None for r in report['cases']),
        'qualified_native_window_paths':sum(r['native_witness_length_km'] is not None for r in report['native_window_paths']),
        'witnesses':{'sha256':custody.file_sha(WITNESSES/'paths.jsonl'),'bytes':(WITNESSES/'paths.jsonl').stat().st_size},
        'files':{p.name:{'sha256':custody.file_sha(p),'bytes':p.stat().st_size} for p in OUT.iterdir()},
        'installed':False,'main_updated':False,'full_goal_complete':False}
    write(OUT/'result.json',result);print(json.dumps({k:result[k] for k in ['status','qualified_anchor_cases','qualified_native_window_paths']}))


if __name__=='__main__':
    try:main()
    except Exception as error:
        if os.environ.get('GITHUB_ACTIONS')=='true':
            OUT.mkdir(parents=True,exist_ok=True);write(OUT/'failure.json',{'status':'FAIL','error_type':type(error).__name__,'message':str(error)[:2000],'installed':False,'main_updated':False})
        raise
