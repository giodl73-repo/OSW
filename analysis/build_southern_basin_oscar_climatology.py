"""Extend three declared southern-basin sections without changing their operators."""
import argparse
import calendar
import csv
import hashlib
import io
import json
import math
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
import urllib.request
from build_basin_surface_section_spans import measure

ROOT = Path(__file__).resolve().parents[1]
CONFIG = 'research/southern-basin-oscar-climatology-input.json'
CONFIG_SHA = 'a5ee7051a76858177769082644bfcf36405d68bbdb4cb50bc63456bff653d95d'
PROTOCOL = 'plans/southern-basin-oscar-climatology-protocol-v1.md'
CACHE = ROOT/'research/source-data/oscar-southern-basin-1995-2016'
OUTPUT = 'research/southern-basin-oscar-1995-2016-monthly-sections.json'
AUDIT = 'research/southern-basin-oscar-climatology-scope-audit.json'
BASE = 'https://oceanwatch.pifsc.noaa.gov/erddap'


def digest(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def config():
    if digest(CONFIG) != CONFIG_SHA:
        raise ValueError('Changed frozen southern-basin preflight')
    c=json.loads((ROOT/CONFIG).read_bytes())
    prior=json.loads((ROOT/c['source_preflight']).read_bytes())
    expected=[r for r in prior['sections'] if r['current_id'] in ['south-atlantic','south-pacific','south-indian']]
    if digest(c['source_preflight'])!=c['source_preflight_sha256'] or c['sections']!=expected:
        raise ValueError('Changed prior section identities, geography or contextual scope')
    for key,value in {'dataset_id':'yearly_336c_0b32_9cd3','product_version':'2017.0','analysis_years':[1995,2016], 'fractions':[.4,.5,.6],'minimum_eligible_component_m_s':.02,'monthly_cell_minimum_pairs':5,'minimum_climatology_years_per_cell':18,'nominal_depth_m':15}.items():
        if c[key]!=value:raise ValueError('Changed climatological operator or support')
    for key in ['current_association_verified','whole_current_representative','annual_extrema_eligible','seasonal_playback_eligible','width_rank_eligible','missing_edges_may_be_closed','weak_or_westward_flow_is_zero_width','interannual_span_is_measurement_uncertainty']:
        if c[key] is not False:raise ValueError('Promoted local component diagnostic')
    return c


def urls(c):
    result = {'metadata.json':f"{BASE}/info/{c['dataset_id']}/index.json"}
    for s in c['sections']:
        low,high=s['domain']
        query = ','.join(f"{v}[(1995-01-01T00:00:00Z):1:(2016-12-31T00:00:00Z)][(15)][({high}):1:({low})][({s['fixed_coordinate']%360})]" for v in ['u','v'])
        result[s['section_id']+'.csv'] = f"{BASE}/griddap/{c['dataset_id']}.csv?"+quote(query,safe='')
    return result


def parse(metadata, raw, section):
    attrs = {(r[1],r[2]):r[4] for r in json.loads(metadata)['table']['rows'] if r[0]=='attribute'}
    for key,value in {('u','units'):'m s-1',('v','units'):'m s-1',('NC_GLOBAL','version'):'2017.0',('depth','actual_range'):'15.0, 15.0'}.items():
        if attrs.get(key)!=value: raise ValueError('Changed OSCAR units, product or nominal depth')
    lines = csv.reader(io.StringIO(raw.decode('utf8')))
    if next(lines)!=['time','depth','latitude','longitude','u','v'] or next(lines)!=['UTC','m','degrees_north','degrees_east','m s-1','m s-1']:
        raise ValueError('Changed vector CSV columns or units')
    frames = {}
    low,high=section['domain']
    for line in lines:
        if len(line)!=6: raise ValueError('Malformed vector row')
        stamp = datetime.fromisoformat(line[0].replace('Z','+00:00'))
        depth,lat,lon,u,v = map(float,line[1:])
        if lon>=180:lon-=360
        if stamp.utcoffset().total_seconds()!=0 or not datetime(1994,12,29,tzinfo=timezone.utc)<=stamp<=datetime(2017,1,3,tzinfo=timezone.utc) or not all(math.isfinite(x) for x in [depth,lat,lon]) or depth!=15 or abs(lon-section['fixed_coordinate'])>1e-8 or not low-1e-8<=lat<=high+1e-8 or any(math.isinf(x) for x in [u,v]):
            raise ValueError('Changed section grid, layer, time or velocity')
        cells = frames.setdefault(line[0],{})
        if lat in cells: raise ValueError('Duplicate vector timestamp/cell')
        cells[lat] = {'coordinate':lat,'longitude':lon,'latitude':lat,'eastward_m_s':u if math.isfinite(u) else None,'northward_m_s':v if math.isfinite(v) else None}
    expected = [low+i/3 for i in range(round((high-low)*3)+1)]
    result = []
    for stamp,cells in sorted(frames.items()):
        grid = sorted(cells)
        if len(grid)!=len(expected) or any(abs(a-b)>1e-8 for a,b in zip(grid,expected)):
            raise ValueError('Missing or altered native grid cell')
        result.append({'time':stamp,'samples':[cells[x] for x in grid]})
    if not result: raise ValueError('Empty source section')
    return attrs,result


def acquire():
    if CACHE.exists(): raise ValueError('Source directory exists; refusing overwrite')
    c = config(); source_urls = urls(c)
    def get(item):
        name,url = item
        request = urllib.request.Request(url,headers={'User-Agent':'OSW public ocean-data acquisition'})
        with urllib.request.urlopen(request,timeout=120) as response: data=response.read(25_000_001)
        if len(data)>25_000_000: raise ValueError('Oversized source response')
        return name,data
    responses = dict(ThreadPoolExecutor(3).map(get,source_urls.items()))
    for s in c['sections']: parse(responses['metadata.json'],responses[s['section_id']+'.csv'],s)
    CACHE.mkdir(parents=True)
    for name,data in responses.items(): (CACHE/name).write_bytes(data)
    receipt = {'schema':'osw.source-acquisition.v1','acquired_at':datetime.now(timezone.utc).isoformat(),'config_sha256':digest(CONFIG),'files':{name:{'url':source_urls[name],'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()} for name,data in responses.items()}}
    (CACHE/'acquisition.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode())


def span(profile,section,label,month):
    cases = [measure(profile,section,f) for f in [.4,.5,.6]]
    nominal = cases[1]
    values = [r['span_km'] for r in cases if r['span_km'] is not None]
    edges = nominal['boundaries'].values()
    return {'month':month,'label':label,'profile':profile,'nominal':nominal,'threshold_scenarios':cases,
            'approximate_section_span_km':math.floor(nominal['span_km']/10+.5)*10 if nominal['span_km'] is not None else None,
            'threshold_sensitivity_span_km':[math.floor(min(values)/10)*10,math.ceil(max(values)/10)*10] if len(values)==3 else None,
            'all_thresholds_resolved':len(values)==3,
            'crossing_outside_context_window':any(b.get('coordinate') is not None and not section['peak_search'][0]<=b['coordinate']<=section['peak_search'][1] for b in edges)}


def year_months(frames,section,year):
    result=[]
    for month in range(1,13):
        selected=[f for f in frames if int(f['time'][:4])==year and int(f['time'][5:7])==month]
        profile=[]
        for i,grid in enumerate(frames[0]['samples']):
            paired=[f['samples'][i] for f in selected if all(f['samples'][i][k] is not None for k in ['eastward_m_s','northward_m_s'])]
            u=sum(p['eastward_m_s'] for p in paired)/len(paired) if len(paired)>=5 else None
            v=sum(p['northward_m_s'] for p in paired)/len(paired) if len(paired)>=5 else None
            profile.append({k:grid[k] for k in ['coordinate','longitude','latitude']}|{'eastward_m_s':u,'northward_m_s':v,'component_m_s':u,'paired_source_samples':len(paired)})
        result.append(span(profile,section,calendar.month_abbr[month],month)|{'source_times':[f['time'] for f in selected]})
    return result


def climatology(yearly,section):
    result=[]
    for month in range(1,13):
        profile=[]
        for i,grid in enumerate(yearly['1995']['months'][month-1]['profile']):
            valid=[(int(y),row['months'][month-1]['profile'][i]) for y,row in yearly.items() if all(row['months'][month-1]['profile'][i][k] is not None for k in ['eastward_m_s','northward_m_s'])]
            u=sum(p['eastward_m_s'] for _,p in valid)/len(valid) if len(valid)>=18 else None
            v=sum(p['northward_m_s'] for _,p in valid)/len(valid) if len(valid)>=18 else None
            profile.append({k:grid[k] for k in ['coordinate','longitude','latitude']}|{'eastward_m_s':u,'northward_m_s':v,'component_m_s':u,'valid_years':[y for y,_ in valid],'paired_source_samples':sum(p['paired_source_samples'] for _,p in valid)})
        readings=[{'year':int(y),'value_km':row['months'][month-1]['approximate_section_span_km'],'status':row['months'][month-1]['nominal']['status']} for y,row in yearly.items()]
        values=[r['value_km'] for r in readings if r['value_km'] is not None]
        result.append(span(profile,section,calendar.month_abbr[month],month)|{'yearly_half_peak_results':readings,'yearly_resolved_count':len(values),'yearly_monthly_mean_span_range_km':[min(values),max(values)] if values else None,'interannual_range_is_measurement_uncertainty':False,'width_of_climatological_mean_is_mean_yearly_width':False})
    return result


def build():
    c=config(); receipt=json.loads((CACHE/'acquisition.json').read_bytes())
    if receipt['config_sha256']!=digest(CONFIG): raise ValueError('Changed preflight acquisition rules')
    for name,url in urls(c).items():
        raw=(CACHE/name).read_bytes(); r=receipt['files'][name]
        if r['url']!=url or r['bytes']!=len(raw) or r['sha256']!=hashlib.sha256(raw).hexdigest(): raise ValueError('Changed original provider bytes/request')
    legacy_file='research/basin-surface-section-inventory.json'
    legacy={s['section_id']:s for s in json.loads((ROOT/legacy_file).read_bytes())['sections']}
    inputs=[CONFIG,PROTOCOL,AUDIT,legacy_file,c['source_preflight'],*(s['scope_audit'] for s in c['sections']),'analysis/build_southern_basin_oscar_climatology.py','analysis/build_basin_surface_section_spans.py',*(p.relative_to(ROOT).as_posix() for p in [CACHE/'acquisition.json',*(CACHE/n for n in urls(c))])]
    result={'schema':'osw.southern-basin-yearly-climatological-sections.v1','current_ids':[s['current_id'] for s in c['sections']],'status':'derived_local_component_sections_not_current_width_admission','analysis_years':c['analysis_years'],'year':None,'input_sha256':{p:digest(p) for p in inputs},'whole_current_representative':False,'width_rank_eligible':False,'whole_current_width_km':None,'annual_width_range_km':None,'sections':[]}
    for s in c['sections']:
        attrs,all_frames=parse((CACHE/'metadata.json').read_bytes(),(CACHE/(s['section_id']+'.csv')).read_bytes(),s)
        frames=[f for f in all_frames if 1995<=int(f['time'][:4])<=2016]
        if [f for f in frames if f['time'].startswith('2013-')]!=legacy[s['section_id']]['frames']:
            raise ValueError('Multi-year archive disagrees with original 2013 vector section')
        section={k:s[k] for k in ['fixed_axis','fixed_coordinate','varying_axis','domain','peak_search','component']}
        yearly={str(y):{'months':year_months(frames,section,y)} for y in range(1995,2017)}
        gaps=[]
        for a,b in zip(frames,frames[1:]):
            days=(datetime.fromisoformat(b['time'].replace('Z','+00:00'))-datetime.fromisoformat(a['time'].replace('Z','+00:00'))).total_seconds()/86400
            if days not in [5,6]: gaps.append({'after':a['time'],'before':b['time'],'days':days})
        result['sections'].append({**s,'section':section,'source_url':receipt['files'][s['section_id']+'.csv']['url'],'source_license':attrs[('NC_GLOBAL','license')],'counts':{'source_times':len(frames),'cells_per_time':len(frames[0]['samples']),'missing_vector_pairs':sum(p['eastward_m_s'] is None or p['northward_m_s'] is None for f in frames for p in f['samples'])},'excluded_boundary_times':[f['time'] for f in all_frames if not 1995<=int(f['time'][:4])<=2016],'unexpected_time_gaps':gaps,'yearly':yearly,'months':climatology(yearly,section)})
    return result


def diagnostics(data):
    c=config();result=[]
    for index,s in enumerate(data['sections']):
        values=[m['approximate_section_span_km'] for m in s['months'] if m['approximate_section_span_km'] is not None]
        result.append({'schema':'osw.basin-monthly-component-span.v1',
            'status':'local_component_section_diagnostic_requires_scientific_review',
            'current_id':s['current_id'],'section_id':s['section_id'],'year':None,
            'diagnostic_id':'diagnostic:basin-'+s['section_id']+'-climatology',
            'context_window_label':'declared geographic peak-search window',
            'is_climatology':True,'climatology_period_years':[1995,2016],
            'climatology_operator':c['climatology_operator'],
            'period_label':f"1995–2016 calendar-month climatology at {abs(s['fixed_coordinate']):.0f} {'W' if s['fixed_coordinate']<0 else 'E'}",
            'width_metric':'fixed_orientation_half_peak_eastward_component_span',
            'section_latitude':None,'section_longitude_degrees_east':s['fixed_coordinate'],
            'source_url':s['source_url'],'source_license':s['source_license'],
            'section':s['section'],'scope_note':s['source_scope'],
            'layer':'OSCAR2017.0 diagnostic near-surface velocity, nominal coordinate15 m; not direct 15 m instruments or a depth-resolved current.',
            'time_convention':'1995–2016 equal-year calendar-month vector climatology. Each year-month cell needs five paired records; each climatology cell needs18 valid years. Width of this mean is not mean yearly width.',
            'monthly_width_is_mean_of_instantaneous_widths':False,
            'climatological_width_is_mean_yearly_width':False,
            'current_association_verified':False,'whole_current_representative':False,
            'width_rank_eligible':False,'annual_extrema_eligible':False,'seasonal_playback_eligible':False,
            'chart_playback_eligible':True,'whole_current_length_km':None,'whole_current_width_km':None,
            'annual_length_range_km':None,'annual_width_range_km':None,
            'measurement_uncertainty_interval_km':None,'is_confidence_interval':False,
            'range_kind':'finite_boundary_threshold_sensitivity_not_confidence_or_annual_range',
            'source_inventory_file':OUTPUT,'source_inventory_sha256':digest(OUTPUT),
            'source_yearly_profiles_file':OUTPUT,'source_yearly_profiles_pointer':f'/sections/{index}/yearly',
            'profile_figure':f"figures/{s['section_id']}-1995-2016-monthly-component-profiles.svg",
            'interannual_figure':'figures/southern-basin-1995-2016-yearly-monthly-spans.svg',
            'scope_audit_file':AUDIT,'scope_audit_sha256':digest(AUDIT),
            'config_file':CONFIG,'config_sha256':digest(CONFIG),
            'protocol_file':PROTOCOL,'protocol_sha256':digest(PROTOCOL),
            'input_sha256':{**data['input_sha256'],OUTPUT:digest(OUTPUT)},
            'counts':{**s['counts'],'yearly_monthly_profiles':264,'climatological_profiles':12,
                      'resolved_yearly_monthly_spans':sum(m['yearly_resolved_count'] for m in s['months'])},
            'summary':{'resolved_nominal_months':len(values),'sample_monthly_mean_span_range_km':[min(values),max(values)] if values else None,
                       'range_kind':'span_of_resolved_calendar_month_climatological_component_values_not_annual_physical_range'},
            'months':s['months']})
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--acquire',action='store_true');args=parser.parse_args()
    if args.acquire:acquire()
    result=build();(ROOT/OUTPUT).write_bytes((json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n').encode())
    for doc in diagnostics(result):
        path=ROOT/'research'/(doc['section_id']+'-1995-2016-climatological-component-spans.json')
        path.write_bytes((json.dumps(doc,ensure_ascii=False,indent=2)+'\n').encode())
    print({s['section_id']:s['counts'] for s in result['sections']})


if __name__=='__main__':main()
