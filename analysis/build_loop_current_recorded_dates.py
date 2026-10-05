"""Repeat unchanged methods on declared dates, retaining unresolved outcomes."""
import hashlib
import json
from functools import partial
from pathlib import Path
from build_loop_current_dated_streamline import ROOT, build as noaa_build
from build_loop_current_adt_contours import build as adt_build
from fetch_loop_current_recorded_dates import MANIFEST, DATES
OUTPUT=ROOT/'research/loop-current-recorded-date-comparison.json'

def path_for(method,date):
    prefix='loop-current-dated-streamline' if method=='noaa' else 'loop-current-adt-contours'
    return ROOT/f'research/{prefix}-{date.replace("-", "")}.json'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def source_rows():
    manifest=json.loads(MANIFEST.read_bytes())
    if tuple(r['date'] for r in manifest['dates'])!=DATES:raise ValueError('Changed predeclared date selection')
    for row in manifest['dates']:
        for method in ['noaa','adt']:
            path=ROOT/row[method]['file']
            if digest(path)!=row[method]['sha256']:raise ValueError('Changed repeat snapshot')
            snapshot=json.loads(path.read_bytes())
            if snapshot['source_response_sha256']!=row[method]['source_response_sha256']:raise ValueError('Changed original source receipt')
    return manifest['dates']

def rebuild_noaa(row):
    src=row['noaa']
    return noaa_build(ROOT/src['file'],src['sha256'],src['source_response_sha256'],row['date'])

def rebuild_adt(row):
    src=row['adt']
    return adt_build(ROOT/src['file'],src['sha256'],row['date'],path_for('noaa',row['date']),partial(rebuild_noaa,row))

def build(*,write_diagnostics=False):
    records=[]
    for row in source_rows():
        noaa=rebuild_noaa(row);noaa_path=path_for('noaa',row['date'])
        if write_diagnostics:noaa_path.write_text(json.dumps(noaa,indent=2)+'\n',encoding='utf-8',newline='\n')
        elif json.loads(noaa_path.read_bytes())!=noaa:raise ValueError('Stale repeat NOAA diagnostic')
        adt=rebuild_adt(row);adt_path=path_for('adt',row['date'])
        if write_diagnostics:adt_path.write_text(json.dumps(adt,indent=2)+'\n',encoding='utf-8',newline='\n')
        elif json.loads(adt_path.read_bytes())!=adt:raise ValueError('Stale repeat ADT diagnostic')
        records.append({'date':row['date'],'noaa_diagnostic_file':noaa_path.relative_to(ROOT).as_posix(),
            'noaa_diagnostic_sha256':digest(noaa_path),'adt_diagnostic_file':adt_path.relative_to(ROOT).as_posix(),
            'adt_diagnostic_sha256':digest(adt_path),'noaa_connected_length_km':noaa['nominal']['open_path_length_km'],
            'noaa_stop_reason':noaa['nominal']['stop_reason'],'noaa_selected_seed_longitude':noaa['nominal']['seed_lon_lat'][0],
            'noaa_failed_scenario_count':noaa['failure_count'],'adt_selected_length_km':adt['comparison']['duacs_selected_contour_length_km'],
            'adt_eligible_count':adt['eligible_count'],'adt_selected_level_m':adt['selected']['adt_level_m'] if adt['selected'] else None,
            'signed_difference_duacs_minus_noaa_km':adt['comparison']['signed_difference_duacs_minus_noaa_km']})
    return {'schema':'osw.loop-current-recorded-date-comparison.v1','current_id':'loop',
        'source_manifest':MANIFEST.relative_to(ROOT).as_posix(),'source_manifest_sha256':digest(MANIFEST),
        'generator_sha256':digest(Path(__file__)),'dates':records,
        'rank_eligible':False,'whole_current_length_km':None,'width_km':None,'annual_length_range_km':None,'confidence_interval_km':None,
        'interpretation':'Four predeclared recorded days, not annual extrema or seasons. Methods/products may share observations. Keep every failure; no interpolation, phase labels or pooled dimension admitted.'}

if __name__=='__main__':
    result=build(write_diagnostics=True);OUTPUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    for r in result['dates']:print(r['date'],'NOAA',r['noaa_connected_length_km'],r['noaa_stop_reason'],'failed',r['noaa_failed_scenario_count'],'ADT',r['adt_selected_length_km'],'difference',r['signed_difference_duacs_minus_noaa_km'])
