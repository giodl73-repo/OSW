"""Presentation-only rendering of the exact saved connected-core report."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
REPORT='research/pacific-nec-connected-core-run-v1/diagnostic.json'
RESULT='research/pacific-nec-connected-core-run-v1/result.json'
REQUEST='research/pacific-nec-connected-core-render-request-v2.json'
PREFLIGHT='research/pacific-nec-connected-core-render-preflight-v2.json'
OUT=ROOT/'.pytest_cache/pacific-nec-connected-core-render-v2'
REPORT_SHA='b87c053bd510418e42bea3e026e64d78ef37eb95c9a93f0f075ede4b0109ef67'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def require(value,message):
    if not value:raise ValueError(message)


def read(path):return json.loads((ROOT/path).read_bytes())


def saved_report(raw,result):
    require(sha(raw)==REPORT_SHA and result['generated_files']['diagnostic.json']=={'sha256':REPORT_SHA,'bytes':len(raw)},'Saved report bytes differ')
    require(result['source_commit']=='d4c7fe8d7d390a06367a7af2a04294112b3c6710'
        and str(result['run_id'])=='40890546061' and str(result['run_attempt'])=='2'
        and result['exact_previous_diagnostic_replay'] is True,'Report custody differs')
    report=json.loads(raw)
    require(len(report['cases'])==324 and len(report['months'])==12
        and sum(r['length_km'] is not None for r in report['cases'])==312
        and all(r['length_km'] is not None for r in report['months'])
        and not report['installed'],'Incomplete saved candidates')
    return report


def guard():
    require(os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true' and os.environ.get('RUNNER_OS')=='Linux'
            and os.environ.get('OSW_PACIFIC_NEC_CORE_RENDER_V2')=='1','Cloud-only saved-report rendering')
    require(len(os.sched_getaffinity(0))==1 and os.getpriority(os.PRIO_PROCESS,0)>=15,'One low-priority CPU required')
    require(os.environ.get('GITHUB_REF')=='refs/heads/codex/current-measurement-gaps'
            and os.environ.get('GITHUB_REPOSITORY')=='giodl73-repo/OSW'
            and os.environ.get('GITHUB_EVENT_NAME')=='push','Wrong event or ref')
    for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):require(os.environ.get(key)=='1','Worker limit differs')
    request=read(REQUEST)
    require(request['execute'] is True and request['cloud_saved_report_render_permitted'] is True,'Render request disabled')
    require(request['max_cloud_jobs']==1 and request['max_local_heavy_jobs']==0,'Job bounds differ')
    for key in ('source_field_processing_permitted','provider_download_permitted','native_build_permitted',
                'wasm_build_permitted','browser_automation_permitted','installation_permitted','main_update_permitted'):
        require(request[key] is False,'Forbidden permission: '+key)
    require(sha((ROOT/PREFLIGHT).read_bytes())==request['preflight_sha256'],'Preflight differs')
    pref=read(PREFLIGHT)
    for path,pin in pref['input_sha256'].items():require(sha((ROOT/path).read_bytes())==pin,'Source differs: '+path)
    require(read('research/current-gap-delivery-phase.json')['heavy_work_permitted'] is False,'Broad phase enabled')
    for path in pref['disabled_requests']:
        value=read(path);require(value.get('execute',value.get('execution_permitted')) is False,'Other request enabled')
    source=os.environ['GITHUB_SHA']
    def git(*args):return subprocess.check_output(['git','-c','core.fsmonitor=false',*args],text=True,timeout=55).strip()
    require(git('rev-parse','HEAD')==source and not git('status','--porcelain'),'Checkout differs')
    require(git('ls-remote','origin','refs/heads/codex/current-measurement-gaps').split()[0]==source,'Working branch moved')
    require(git('ls-remote','origin','refs/heads/main').split()[0]=='19148702de6433253dbf412a0a28c0cb4f8e409e','Main moved')


def render(report,stem):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    fig=plt.figure(figsize=(13,10),layout='constrained')
    grid=fig.add_gridspec(3,2,height_ratios=[1.25,.17,1])
    atlas=fig.add_subplot(grid[0,:]);legend_ax=fig.add_subplot(grid[1,:]);legend_ax.set_axis_off()
    lengths=fig.add_subplot(grid[2,0]);widths=fig.add_subplot(grid[2,1])
    for row,color in zip(report['months'],plt.cm.tab20(np.linspace(0,1,12))):
        if row['points'] is not None:
            atlas.plot([p[0] for p in row['points']],[p[1] for p in row['points']],color=color,lw=1.3,
                linestyle='--' if row['reason'] else '-',label=f"2013-{row['month']:02d}"+(' (ambiguous)' if row['reason'] else ''))
    atlas.set(xlim=(130,240),ylim=(7.5,18.5),ylabel='Latitude north',
        title='Window-constrained product-core candidates | 130E to 120W regional gates\nThreshold0.025m/s; direction60deg; penalty0.02m/s; eight-to-eighteen-degree window')
    atlas.set_xticks([130,150,180,210,240],['130E','150E','180','150W','120W']);atlas.grid(alpha=.2)
    handles,labels=atlas.get_legend_handles_labels();legend=None
    if handles:legend=legend_ax.legend(handles,labels,ncol=6,fontsize=9,loc='center')
    else:atlas.text(.5,.5,'All twelve regional paths withheld',ha='center',transform=atlas.transAxes)
    valid=[r for r in report['months'] if r['length_km'] is not None]
    if valid:
        lengths.plot([r['month'] for r in report['months']],
            [r['length_km'] if r['length_km'] is not None else np.nan for r in report['months']],marker='o')
        lengths.set(title='Regional operator length candidates',ylabel='WGS84 km',xlabel='2013 month',xticks=range(1,13));lengths.grid(alpha=.2)
        for row in report['months']:
            if row['length_km'] is None:lengths.plot(row['month'],.04,'x',color='gray',transform=lengths.get_xaxis_transform())
    else:lengths.set_axis_off();lengths.text(.5,.6,'REGIONAL LENGTHS WITHHELD\nNo nominal path passes every gate',ha='center',va='center',transform=lengths.transAxes,fontsize=13)
    if any(r['width_km'] is not None for r in report['section_spans']):
        for lon,color in zip((137,180,220),('tab:blue','tab:orange','tab:green')):
            rows=[r for r in report['section_spans'] if r['longitude_east']==lon]
            widths.plot([r['month'] for r in rows],[r['width_km'] if r['width_km'] is not None else np.nan for r in rows],marker='o',color=color,label={137:'137E',180:'180',220:'140W'}[lon])
            for row in rows:
                if row['width_km'] is None:widths.plot(row['month'],.03+(lon==180)*.03+(lon==220)*.06,'x',color=color,transform=widths.get_xaxis_transform())
        widths.set(title='Selected branch section-span candidates',ylabel='Meridional WGS84 km',xlabel='2013 month',xticks=range(1,13));widths.grid(alpha=.2);widths.legend(fontsize=9)
    else:widths.set_axis_off();widths.text(.5,.6,'SECTION SPANS WITHHELD\nNo paired span anchored to a qualified core',ha='center',va='center',transform=widths.transAxes,fontsize=13)
    fixture=stem=='withheld-fixture'
    fig.suptitle(('SYNTHETIC WITHHELD QA FIXTURE\n' if fixture else '')+'Pacific NEC | OSCAR2017.0 | nominal15m near-surface product | 2013\nRegional numerical candidates; not whole-current dimensions or seasonal climatology',fontsize=13)
    footer=('Fixture validates missing-data presentation; no scientific values are shown.' if fixture else
        'March–July paths contact the8N window edge and need window-sensitivity review. No tracked full-year width range passes.\nCrosses mark withheld spans, not zero. Component overlap does not establish physical current identity.')
    fig.supxlabel(footer,fontsize=10)
    fig.canvas.draw();renderer=fig.canvas.get_renderer()
    if legend:
        box=legend.get_window_extent(renderer);slot=legend_ax.get_window_extent(renderer)
        require(box.x0>=slot.x0-1 and box.x1<=slot.x1+1 and box.y0>=slot.y0-1 and box.y1<=slot.y1+1,'Legend leaves its dedicated row')
    fig.savefig(OUT/(stem+'.png'),dpi=150);fig.savefig(OUT/(stem+'.svg'))
    metrics={'legend_in_dedicated_row':True,'length_axis_visible':lengths.axison,'width_axis_visible':widths.axison}
    plt.close(fig);return metrics


def main():
    import copy
    guard();OUT.mkdir(parents=True,exist_ok=False)
    raw=(ROOT/REPORT).read_bytes();report=saved_report(raw,read(RESULT))
    metrics={'actual':render(report,'connected-core')}
    empty=copy.deepcopy(report)
    for row in empty['months']:row.update(points=None,length_km=None,reason='WITHHELD_TEST_FIXTURE')
    for row in empty['section_spans']:row.update(width_km=None,reason='WITHHELD_TEST_FIXTURE')
    metrics['withheld_fixture']=render(empty,'withheld-fixture')
    require(not metrics['withheld_fixture']['length_axis_visible'] and not metrics['withheld_fixture']['width_axis_visible'],'Empty numeric axes remain')
    require(sha((ROOT/REPORT).read_bytes())==REPORT_SHA,'Rendering changed saved report')
    result={'schema':'osw.pacific-nec-core-render-result.v2','status':'PASS_SAVED_REPORT_RENDER_GEOMETRY_VISUAL_REVIEW_PENDING',
        'source_commit':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],
        'report_sha256':REPORT_SHA,'report_unchanged':True,'source_fields_processed':False,'metrics':metrics,
        'files':{p.name:{'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in OUT.iterdir()},
        'installed':False,'main_updated':False,'full_goal_complete':False}
    (OUT/'result.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print(result['status'])


if __name__=='__main__':main()
