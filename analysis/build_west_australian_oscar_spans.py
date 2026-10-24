"""Acquire and reproduce one declared offshore northward component diagnostic."""
import argparse, calendar, hashlib, json, math, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from acquire_basin_surface_sections import parse
from build_basin_surface_section_spans import measure

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'research/west-australian-oscar-section-input.json'
PROTOCOL=ROOT/'plans/west-australian-oscar-section-protocol-v1.md'
CACHE=ROOT/'research/source-data/oscar-west-australian-2013'
OUTPUT=ROOT/'research/west-australian-32s-2013-monthly-component-spans.json'
BASE='https://oceanwatch.pifsc.noaa.gov/erddap'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def source_urls(cfg):
    expected={'current_id':'west-australian','section_id':'west-australian-32s','dataset_id':'yearly_336c_0b32_9cd3','product_version':'2017.0','year':2013,'nominal_depth_m':15,'fixed_axis':'latitude','fixed_coordinate':-32,'varying_axis':'longitude','domain':[60,116],'peak_search':[80,105],'component':'northward','fractions':[.4,.5,.6],'minimum_eligible_component_m_s':.02,'monthly_cell_minimum_pairs':5,'rounding_km':10,'current_association_verified':False,'whole_current_representative':False,'annual_extrema_eligible':False,'mask_or_missing_boundary_may_be_closed':False,'one_sided_span_may_be_doubled':False}
    if any(cfg.get(k)!=v for k,v in expected.items()):raise ValueError('Changed predeclared offshore diagnostic')
    dataset=cfg['dataset_id']
    query=','.join(c+'[(2013-01-01T00:00:00Z):1:(2013-12-28T00:00:00Z)][(15)][(-32)][(60):1:(116)]' for c in ['u','v'])
    return {'metadata.json':BASE+'/info/'+dataset+'/index.json','section.csv':BASE+'/griddap/'+dataset+'.csv?'+quote(query,safe='')}

def acquire():
    if CACHE.exists():raise ValueError('Source cache exists; refusing overwrite')
    cfg=json.loads(CONFIG.read_bytes());urls=source_urls(cfg);responses={}
    for name,url in urls.items():
        with urllib.request.urlopen(url,timeout=60) as response:responses[name]=response.read(5_000_001)
        if len(responses[name])>5_000_000:raise ValueError('Oversized section response')
    parse(responses['metadata.json'],responses['section.csv'],cfg)
    CACHE.mkdir(parents=True)
    for name,data in responses.items():(CACHE/name).write_bytes(data)
    receipt={'schema':'osw.source-acquisition.v1','acquired_at':datetime.now(timezone.utc).isoformat(),'config_sha256':digest(CONFIG),'files':{name:{'url':urls[name],'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()} for name,data in responses.items()}}
    (CACHE/'acquisition.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode())

def profiles(frames,section):
    months=[]
    for month in range(1,13):
        selected=[f for f in frames if int(f['time'][5:7])==month]
        if len(selected)<5:raise ValueError('Insufficient monthly archive sampling')
        rows=[]
        for i,grid in enumerate(selected[0]['samples']):
            cells=[f['samples'][i] for f in selected]
            if any([r[k] for k in ['coordinate','longitude','latitude']]!=[grid[k] for k in ['coordinate','longitude','latitude']] for r in cells):raise ValueError('Changed vector grid')
            paired=[r for r in cells if r['eastward_m_s'] is not None and r['northward_m_s'] is not None]
            u=sum(r['eastward_m_s'] for r in paired)/len(paired) if len(paired)>=5 else None
            v=sum(r['northward_m_s'] for r in paired)/len(paired) if len(paired)>=5 else None
            rows.append({k:grid[k] for k in ['coordinate','longitude','latitude']}|{'eastward_m_s':u,'northward_m_s':v,'component_m_s':v,'paired_source_samples':len(paired)})
        scenarios=[measure(rows,section,f) for f in [.4,.5,.6]];nominal=scenarios[1]
        values=[s['span_km'] for s in scenarios if s['span_km'] is not None]
        months.append({'month':month,'label':calendar.month_abbr[month],'source_times':[f['time'] for f in selected],'profile':rows,'nominal':nominal,'threshold_scenarios':scenarios,'approximate_section_span_km':math.floor(nominal['span_km']/10+.5)*10 if nominal['span_km'] is not None else None,'threshold_sensitivity_span_km':[math.floor(min(values)/10)*10,math.ceil(max(values)/10)*10] if len(values)==3 else None,'all_thresholds_resolved':len(values)==3})
    return months

def build():
    cfg=json.loads(CONFIG.read_bytes());receipt=json.loads((CACHE/'acquisition.json').read_bytes())
    if receipt['config_sha256']!=digest(CONFIG):raise ValueError('Changed acquisition rules')
    for name,url in source_urls(cfg).items():
        raw=(CACHE/name).read_bytes();r=receipt['files'][name]
        if r['url']!=url or r['bytes']!=len(raw) or r['sha256']!=hashlib.sha256(raw).hexdigest():raise ValueError('Changed provider bytes or query')
    attrs,frames=parse((CACHE/'metadata.json').read_bytes(),(CACHE/'section.csv').read_bytes(),cfg)
    months=profiles(frames,cfg);values=[m['approximate_section_span_km'] for m in months if m['approximate_section_span_km'] is not None]
    inputs=[CONFIG,PROTOCOL,ROOT/cfg['scope_audit'],Path(__file__),ROOT/'analysis/acquire_basin_surface_sections.py',ROOT/'analysis/build_basin_surface_section_spans.py',CACHE/'acquisition.json',CACHE/'metadata.json',CACHE/'section.csv']
    return {'schema':'osw.basin-monthly-component-span.v1','status':'local_component_section_diagnostic_requires_scientific_review','current_id':cfg['current_id'],'section_id':cfg['section_id'],'year':2013,'section_latitude':-32,'section_longitude_degrees_east':None,'width_metric':'fixed_orientation_half_peak_northward_component_span','section':{k:cfg[k] for k in ['fixed_axis','fixed_coordinate','varying_axis','domain','peak_search','component']},'scope_note':cfg['scope_note'],'source_url':receipt['files']['section.csv']['url'],'provider':'Earth & Space Research / NOAA PIFSC ERDDAP mirror','product_version':'2017.0','source_license':attrs[('NC_GLOBAL','license')],'layer':'Satellite-derived near-surface product with nominal 15 m coordinate, not direct depth-resolved observations.','time_convention':'72 nominal five-day archive samples with four six-day gaps, 2013-01-01 through 2013-12-26; not climatology.','monthly_width_is_mean_of_instantaneous_widths':False,'current_association_verified':False,'whole_current_representative':False,'width_rank_eligible':False,'annual_extrema_eligible':False,'seasonal_playback_eligible':False,'whole_current_length_km':None,'whole_current_width_km':None,'is_confidence_interval':False,'measurement_uncertainty_interval_km':None,'is_climatology':False,'chart_playback_eligible':True,'annual_length_range_km':None,'annual_width_range_km':None,'input_sha256':{p.relative_to(ROOT).as_posix():digest(p) for p in inputs},'counts':{'source_times':len(frames),'cells_per_time':len(frames[0]['samples']),'missing_vector_pairs':sum(r['eastward_m_s'] is None or r['northward_m_s'] is None for f in frames for r in f['samples'])},'range_kind':'finite_boundary_threshold_sensitivity_not_confidence_or_annual_range','months':months,'summary':{'resolved_nominal_months':len(values),'sample_monthly_mean_span_range_km':[min(values),max(values)] if values else None,'range_kind':'span_of_local_monthly_mean_component_values_not_annual_physical_range'}}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--acquire',action='store_true');args=parser.parse_args()
    if args.acquire:acquire()
    doc=build();OUTPUT.write_bytes((json.dumps(doc,indent=2)+'\n').encode())
    print(doc['counts']);print(doc['summary'])
    print([(m['label'],m['approximate_section_span_km'],m['nominal']['status']) for m in doc['months']])

if __name__=='__main__':main()
