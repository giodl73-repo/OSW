"""One-CPU cloud replay of saved OSCAR source; no provider download or admission."""
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import zipfile

import pacific_nec_connected_core_v1 as core
import pacific_nec_monthly_dimensions_v1 as previous
from pacific_nec_monthly_evidence_v1 import expand

ROOT=Path(__file__).resolve().parents[1]
REQUEST='research/pacific-nec-connected-core-request-v1.json'
PREFLIGHT='research/pacific-nec-connected-core-preflight-v1.json'
PROTOCOL='plans/pacific-nec-connected-core-protocol-v1.md'
OUT=ROOT/'.pytest_cache/pacific-nec-connected-core-v1'
WORK=ROOT/'.pytest_cache/pacific-nec-connected-core-work-v1'
WITNESSES=ROOT/'.pytest_cache/pacific-nec-connected-core-witnesses-v1'
REPO='repos/giodl73-repo/OSW'
SOURCE_COMMIT='f11587af695883500cce9500b72ac2840d97929f'
SOURCE_RUN=40887454328
ARTIFACT={'id':12903990715,'bytes':37597803,'sha256':'54de0d3099ca3f23ab93226a063248b34f48c176723864928ad0bbe0fb1bba7a'}
require=previous.require
sha=previous.sha
write=previous.write
read=previous.read


def file_sha(path):
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()


def api(path):return json.loads(subprocess.check_output(['gh','api',path],timeout=55))


def guard():
    require(os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true'
            and os.environ.get('RUNNER_OS')=='Linux'
            and os.environ.get('OSW_PACIFIC_NEC_CONNECTED_CORE_V1')=='1','Cloud-only source replay')
    require(os.environ.get('GITHUB_REF')=='refs/heads/codex/current-measurement-gaps'
            and os.environ.get('GITHUB_EVENT_NAME')=='push'
            and os.environ.get('GITHUB_REPOSITORY')=='giodl73-repo/OSW','Wrong repository/event/ref')
    require(len(os.sched_getaffinity(0))==1 and os.getpriority(os.PRIO_PROCESS,0)>=15,'One low-priority CPU required')
    for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
        require(os.environ.get(key)=='1','Worker limit differs')
    request=read(REQUEST)
    require(request['schema']=='osw.pacific-nec-connected-core-request.v1' and request['execute'] is True
            and request['cloud_saved_source_processing_permitted'] is True,'Scoped replay disabled')
    for key in ('provider_download_permitted','local_source_processing_permitted','native_build_permitted',
                'wasm_build_permitted','browser_automation_permitted','installation_permitted','main_update_permitted'):
        require(request[key] is False,'Forbidden permission: '+key)
    require(request['max_cloud_jobs']==1 and request['max_local_heavy_jobs']==0,'Job bounds differ')
    require(file_sha(ROOT/PREFLIGHT)==request['preflight_sha256'],'Preflight differs')
    pref=read(PREFLIGHT)
    for path,pin in pref['input_sha256'].items():require(file_sha(ROOT/path)==pin,'Source differs: '+path)
    require(read('research/current-gap-delivery-phase.json')['heavy_work_permitted'] is False,'Broad phase enabled')
    for path in pref['disabled_requests']:
        value=read(path);require(value.get('execute',value.get('execution_permitted')) is False,'Other request enabled')
    def git(*args):return subprocess.check_output(['git','-c','core.fsmonitor=false',*args],text=True,timeout=55).strip()
    require(git('rev-parse','HEAD')==os.environ['GITHUB_SHA'] and not git('status','--porcelain'),'Checkout differs')
    require(git('ls-remote','origin','refs/heads/main').split()[0]==previous.MAIN,'Main moved')
    require(git('ls-remote','origin','refs/heads/codex/current-measurement-gaps').split()[0]==os.environ['GITHUB_SHA'],'Working branch moved')
    for path,row in pref['installed_files'].items():
        require(git('rev-parse','HEAD:'+path)==row['git_blob_oid'] and int(git('cat-file','-s',row['git_blob_oid']))==row['bytes'],'Installed artifact differs')


def extract_source(archive,target,expected):
    require(not target.exists(),'Source target already exists')
    with zipfile.ZipFile(archive) as saved:
        rows=saved.infolist()
        require(len(rows)==3 and {r.filename for r in rows}==set(expected),'Original source archive differs')
        for row in rows:
            path=PurePosixPath(row.filename);mode=row.external_attr>>16
            require(not path.is_absolute() and '..' not in path.parts and '\\' not in row.filename
                    and str(path)==row.filename and not row.is_dir() and stat.S_IFMT(mode) in (0,stat.S_IFREG),'Unsafe source member')
            require(row.file_size==expected[row.filename]['bytes'] and row.file_size<=160000000,'Source member size differs')
        target.mkdir()
        for row in rows:
            with saved.open(row) as stream,(target/row.filename).open('xb') as output:
                for block in iter(lambda:stream.read(1024*1024),b''):output.write(block)
            require(file_sha(target/row.filename)==expected[row.filename]['sha256'],'Source hash differs')


def saved_source():
    run=api(REPO+f'/actions/runs/{SOURCE_RUN}/attempts/2')
    require(run['status']=='completed' and run['conclusion']=='success' and run['head_sha']==SOURCE_COMMIT,'Source run differs')
    meta=api(REPO+f"/actions/artifacts/{ARTIFACT['id']}")
    require(meta['workflow_run']['id']==SOURCE_RUN and meta['workflow_run']['head_sha']==SOURCE_COMMIT
            and not meta['expired'] and meta['size_in_bytes']==ARTIFACT['bytes']
            and meta['digest']=='sha256:'+ARTIFACT['sha256'],'Source artifact custody differs')
    WORK.mkdir(parents=True,exist_ok=False);archive=WORK/'source.zip'
    with archive.open('xb') as output:
        subprocess.run(['gh','api',REPO+f"/actions/artifacts/{ARTIFACT['id']}/zip"],stdout=output,check=True,timeout=180)
    require(archive.stat().st_size==ARTIFACT['bytes'] and file_sha(archive)==ARTIFACT['sha256'],'Source archive bytes differ')
    acquisition=ROOT/'research/pacific-nec-monthly-dimensions-run-v1/acquisition.json'
    expected=dict(read(acquisition)['files'])
    expected['acquisition.json']={'sha256':file_sha(acquisition),'bytes':acquisition.stat().st_size}
    target=WORK/'source';extract_source(archive,target,expected)
    return target


def diagnose(means,old):
    from pyproj import Geod
    geod=Geod(ellps='WGS84');longitude=[130+i/3 for i in range(331)]
    latitude=[8+i/3 for i in range(31)];halo_latitude=[4+i/3 for i in range(67)]
    def distance(x,a,y,b):return geod.inv(x,a,y,b)[2]/1000
    cases=[];months=[];month_groups=[];month_selected=[];sections=[];component_summary=[]
    WITNESSES.mkdir(parents=True,exist_ok=False)
    with (WITNESSES/'paths.jsonl').open('xb') as witnesses:
        for mi in range(12):
            east=means[mi,12:43,:,0].tolist();north=means[mi,12:43,:,1].tolist()
            for threshold in (0,.025,.05):
                labels,groups=core.components(core.eligible(east,north,threshold))
                full=[g for g in groups if g['touches_west_gate'] and g['touches_east_gate']]
                component_summary.append({'month':mi+1,'threshold_m_s':threshold,'components':len(groups),
                    'full_gate_components':[{'id':g['id'],'native_cells':len(g['cells']),
                        'touches_window_edge':g['touches_window_edge']} for g in full]})
                for penalty in (0,.02,.05):
                    for angle in (45,60,90):
                        value=core.core_path(latitude,longitude,east,north,threshold,penalty,angle)
                        path=value.pop('path');points=None;ident=None;length=None
                        if path is not None:
                            identities={labels[y][x] for x,y in enumerate(path)}
                            require(len(identities)==1 and -1 not in identities,'Path jumped between disconnected components')
                            ident=next(iter(identities));require(any(g['id']==ident for g in full),'Path misses a gate')
                            points=[[x,latitude[y],east[y][i],north[y][i]] for i,(x,y) in enumerate(zip(longitude,path))][::-1]
                            if value['reason'] is None:length=math.fsum(distance(a[0],a[1],b[0],b[1]) for a,b in zip(points,points[1:]))
                        ident_case=f"2013-{mi+1:02d}:u{threshold}:p{penalty}:a{angle}"
                        raw=(json.dumps({'id':ident_case,'path':points},separators=(',',':'),allow_nan=False)+'\n').encode()
                        witnesses.write(raw)
                        case=dict(value,id=ident_case,month=mi+1,threshold_m_s=threshold,penalty_m_s=penalty,
                            maximum_angle_deg=angle,length_km=length,length_rounded_km=100*math.floor(length/100+.5) if length is not None else None,
                            component_id=ident,witness_sha256=sha(raw))
                        cases.append(case)
                        if threshold==.025 and penalty==.02 and angle==60:
                            months.append(dict(case,points=points));month_groups.append(full);month_selected.append(ident if length is not None else None)
                            for lon in (137,180,220):
                                xi=round((lon-130)*3);profile=means[mi,:,xi,0].tolist()
                                if length is None:span={'south_latitude':None,'north_latitude':None,'reason':'regional_core_path_withheld','anchor_latitude':None,'source_cell_interval':None}
                                else:span=core.anchored_span(halo_latitude,profile,path[xi]+12)
                                width=distance(lon,span['south_latitude'],lon,span['north_latitude']) if span['reason'] is None else None
                                fastest=next(r for r in old['section_spans'] if r['month']==mi+1 and r['longitude_east']==lon and r['threshold_m_s']==0)
                                sections.append(dict(span,month=mi+1,longitude_east=lon,component_id=ident,width_km=width,
                                    width_rounded_km=10*math.floor(width/10+.5) if width is not None else None,
                                    previous_fastest_peak_latitude=fastest['peak_latitude'],previous_fastest_span_km=fastest['width_km']))
    links=[]
    for mi in range(11):
        edges=core.component_links(month_groups[mi],month_groups[mi+1])
        continues=any(e['previous']==month_selected[mi] and e['following']==month_selected[mi+1] and e['unique_one_to_one'] for e in edges)
        links.append({'previous_month':mi+1,'following_month':mi+2,'overlaps':edges,'selected_core_component_continues':continues})
    section_ranges={}
    for lon in (137,180,220):
        rows=[r for r in sections if r['longitude_east']==lon];checks=[]
        for mi in range(11):
            a,b=rows[mi],rows[mi+1]
            def bounds(row):return (row['south_latitude'],row['north_latitude']) if row['width_km'] is not None else None
            check=core.interval_continuation(bounds(a),bounds(b))
            checks.append(dict(check,previous_month=mi+1,following_month=mi+2,
                component_continues=links[mi]['selected_core_component_continues']))
        complete=all(r['width_km'] is not None for r in rows) and all(c['continues'] and c['component_continues'] for c in checks)
        section_ranges[str(lon)]={'all_twelve_paired_spans':all(r['width_km'] is not None for r in rows),
            'all_eleven_component_and_local_continuations':complete,
            'tracked_candidate_minimum_km':min(r['width_km'] for r in rows) if complete else None,
            'tracked_candidate_maximum_km':max(r['width_km'] for r in rows) if complete else None,
            'continuations':checks,'physical_width_range_admitted':False}
    return {'months':months,'cases':cases,'component_summaries':component_summary,'component_transitions':links,
        'section_spans':sections,'section_tracking':section_ranges,'regional_length_candidate_range':previous.monthly_range(months,'length_km')}


def figure(report):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    fig=plt.figure(figsize=(13,9),layout='constrained');grid=fig.add_gridspec(2,2,height_ratios=[1.2,1])
    atlas=fig.add_subplot(grid[0,:]);lengths=fig.add_subplot(grid[1,0]);widths=fig.add_subplot(grid[1,1])
    for row,color in zip(report['months'],plt.cm.tab20(np.linspace(0,1,12))):
        points=row['points']
        if points is not None:
            atlas.plot([p[0] for p in points],[p[1] for p in points],color=color,lw=1.3,
                linestyle='--' if row['reason'] else '-',label=f"2013-{row['month']:02d}"+(' (ambiguous)' if row['reason'] else ''))
    atlas.set(xlim=(130,240),ylim=(7.5,18.5),ylabel='Latitude north',title='Connected product-core candidates | 130E to 120W regional gates')
    atlas.set_xticks([130,150,180,210,240],['130E','150E','180','150W','120W']);atlas.grid(alpha=.2)
    handles,_=atlas.get_legend_handles_labels()
    if handles:atlas.legend(ncol=6,fontsize=9,loc='upper center',bbox_to_anchor=(.5,-.07))
    else:atlas.text(.5,.5,'All twelve regional paths withheld',ha='center',transform=atlas.transAxes)
    valid=[r for r in report['months'] if r['length_km'] is not None]
    if valid:
        lengths.plot([r['month'] for r in report['months']],[r['length_km'] if r['length_km'] is not None else np.nan for r in report['months']],marker='o')
        lengths.set(title='Regional core-path length candidates',ylabel='WGS84 km',xlabel='2013 month',xticks=range(1,13));lengths.grid(alpha=.2)
        for row in report['months']:
            if row['length_km'] is None:lengths.plot(row['month'],.04,'x',color='gray',transform=lengths.get_xaxis_transform())
    else:lengths.set_axis_off();lengths.text(.5,.6,'REGIONAL LENGTHS WITHHELD\nNo nominal path passes every gate',ha='center',va='center',transform=lengths.transAxes,fontsize=13)
    width_valid=any(r['width_km'] is not None for r in report['section_spans'])
    if width_valid:
        for lon,color in zip((137,180,220),('tab:blue','tab:orange','tab:green')):
            rows=[r for r in report['section_spans'] if r['longitude_east']==lon]
            widths.plot([r['month'] for r in rows],[r['width_km'] if r['width_km'] is not None else np.nan for r in rows],marker='o',color=color,label={137:'137E',180:'180',220:'140W'}[lon])
            for row in rows:
                if row['width_km'] is None:widths.plot(row['month'],.03+(lon==180)*.03+(lon==220)*.06,'x',color=color,transform=widths.get_xaxis_transform())
        widths.set(title='Anchored section spans | temporal identity pending',ylabel='Meridional WGS84 km',xlabel='2013 month',xticks=range(1,13));widths.grid(alpha=.2);widths.legend(fontsize=9)
    else:widths.set_axis_off();widths.text(.5,.6,'SECTION SPANS WITHHELD\nNo paired span anchored to a qualified core',ha='center',va='center',transform=widths.transAxes,fontsize=13)
    failures=[f"{r['month']:02d}" for r in report['months'] if r['reason']]
    atlas.set_xlabel('Withheld months: '+(', '.join(failures) if failures else 'none')+' | Threshold0.025m/s; direction60deg; penalty0.02m/s')
    fig.suptitle('Pacific NEC | OSCAR2017.0 | nominal15m near-surface product | 2013\nRegional operator candidates; not whole-current dimensions or seasonal climatology',fontsize=13)
    fig.supxlabel('Missing values stay withheld. Section spans follow the selected local branch; component overlap does not establish physical current identity.',fontsize=10)
    fig.savefig(OUT/'connected-core.png',dpi=150);fig.savefig(OUT/'connected-core.svg');plt.close(fig)


def main():
    guard();OUT.mkdir(parents=True,exist_ok=False);target=saved_source()
    means,counts,times,month_counts,attrs=previous.parse_cube(json.loads((target/'metadata.json').read_bytes()),target/'vectors.csv')
    acquisition=read('research/pacific-nec-monthly-dimensions-run-v1/acquisition.json')
    require(times==acquisition['times'] and month_counts==acquisition['month_sample_counts'],'Original monthly support differs')
    old=expand(read('research/pacific-nec-monthly-dimensions-run-v1/diagnostic-compacted.json'))
    replay=previous.diagnose(means,counts,times,month_counts)
    require(all(replay[k]==old[k] for k in replay),'Saved source does not exactly reproduce preceding diagnostics')
    report=diagnose(means,old)
    report.update(schema='osw.pacific-nec-connected-core-diagnostic.v1',status='NUMERICAL_CANDIDATES_PHYSICAL_AND_VISUAL_REVIEW_REQUIRED',
        entity_id='current:pacific-north-equatorial',year=2013,product_version='OSCAR2017.0',
        nominal_depth_coordinate_m=15,layer_interpretation='Satellite-derived near-surface product, not a direct15m instrument section.',
        stored_point_order='westward_from_240E_to_130E',
        point_columns=['longitude_east_unwrapped','latitude_north','eastward_m_s','northward_m_s'],
        source_commit=os.environ['GITHUB_SHA'],run_id=os.environ['GITHUB_RUN_ID'],run_attempt=os.environ['GITHUB_RUN_ATTEMPT'],
        source_artifact=ARTIFACT,source_acquisition_sha256=file_sha(target/'acquisition.json'),
        exact_previous_diagnostic_replay=True,protocol_sha256=file_sha(ROOT/PROTOCOL),
        core_operator_sha256=file_sha(ROOT/'analysis/pacific_nec_connected_core_v1.py'),
        whole_current_length_km=None,physical_uncertainty=None,whole_current_annual_ranges=None,
        installed=False,main_updated=False,full_goal_complete=False)
    write(OUT/'diagnostic.json',report);figure(report)
    result={'schema':'osw.pacific-nec-connected-core-result.v1','status':'PASS_SOURCE_REPLAY_AND_DECLARED_CASES_REVIEW_PENDING',
        'source_commit':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],
        'exact_previous_diagnostic_replay':True,'source_artifact':ARTIFACT,'cases':len(report['cases']),
        'qualified_sensitivity_cases':sum(r['length_km'] is not None for r in report['cases']),
        'nominal_months':12,'qualified_nominal_lengths':sum(r['length_km'] is not None for r in report['months']),
        'qualified_nominal_section_spans':sum(r['width_km'] is not None for r in report['section_spans']),
        'tracked_sections':[k for k,v in report['section_tracking'].items() if v['all_eleven_component_and_local_continuations']],
        'witnesses':{'sha256':file_sha(WITNESSES/'paths.jsonl'),'bytes':(WITNESSES/'paths.jsonl').stat().st_size},
        'generated_files':{p.name:{'sha256':file_sha(p),'bytes':p.stat().st_size} for p in OUT.iterdir()},
        'installed':False,'main_updated':False,'full_goal_complete':False}
    write(OUT/'result.json',result)
    print(json.dumps({k:result[k] for k in ('status','qualified_nominal_lengths','qualified_nominal_section_spans','tracked_sections')}))


if __name__=='__main__':
    try:main()
    except Exception as error:
        if os.environ.get('GITHUB_ACTIONS')=='true':
            OUT.mkdir(parents=True,exist_ok=True);write(OUT/'failure.json',{'status':'FAIL','type':type(error).__name__,'message':str(error)[:2000],'installed':False,'main_updated':False})
        raise
