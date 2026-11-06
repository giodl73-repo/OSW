"""Reconstruct daily source vectors and scoped monthly half-peak component spans."""
import calendar,hashlib,json,math,re
from datetime import datetime,timedelta
from pathlib import Path
from acquire_south_australian_hycom_section import ROOT,CONFIG,CACHE,source_urls,sha
from build_basin_surface_section_spans import measure

INVENTORY=ROOT/'research/south-australian-hycom-section-inventory.json'
OUTPUT=ROOT/'research/south-australian-132e-100m-2012-monthly-component-spans.json'
PROTOCOL=ROOT/'plans/south-australian-hycom-section-width-protocol-v1.md'

def digest(path):return sha(Path(path).read_bytes())

def source_inventory():
    config=json.loads(CONFIG.read_bytes());receipt=json.loads((CACHE/'acquisition.json').read_bytes())
    expected={'nominal_grid_spacing_degrees':.08,'monthly_minimum_complete_pair_fraction':.8,'peak_search_latitude':[-35.5,-33.5],'minimum_positive_peak_m_s':.02,'boundary_threshold_fractions':[.4,.5,.6],'report_rounding_km':10,'resolution_flag_minimum_native_spacings':4,'source_missing_int16':-30000,'source_scale_factor':.001,'source_add_offset':0}
    if any(config[k]!=v for k,v in expected.items()) or any(config[k] is not False for k in ['mask_or_missing_boundary_may_be_closed','one_sided_span_may_be_doubled','annual_extrema_eligible','current_association_verified','whole_current_representative']):raise ValueError('Changed predeclared HYCOM operator or admission')
    if receipt['config_sha256']!=digest(CONFIG):raise ValueError('Changed HYCOM config')
    raw={}
    for name,url in source_urls().items():
        data=(CACHE/name).read_bytes();r=receipt['files'][name]
        if r['url']!=url or r['bytes']!=len(data) or r['sha256']!=sha(data):raise ValueError('Changed HYCOM provider bytes')
        raw[name]=data.decode('utf-8')
    das=raw['metadata.das']
    for var in ['water_u','water_v']:
        block=re.search(r'\b'+var+r' \{(.*?)\n    \}',das,re.S).group(1)
        for token in ['Int16 _FillValue -30000;','Float32 scale_factor 0.001;','Float32 add_offset 0.0;','String units "m/s";']:
            if token not in block:raise ValueError('Changed HYCOM units, fill or scaling')
    text=raw['section.ascii'];headers=list(re.finditer(r'(?m)^(water_[uv])\.(water_[uv]|time|depth|lat|lon)((?:\[\d+\])+)[\r ]*$',text));parts={}
    if len(headers)!=10:raise ValueError('Incomplete HYCOM grid/maps response')
    for i,h in enumerate(headers):
        key=(h[1],h[2]);body=text[h.end():headers[i+1].start() if i+1<len(headers) else len(text)].strip()
        if key in parts:raise ValueError('Duplicated HYCOM section')
        if h[2] in ['water_u','water_v']:
            if h[1]!=h[2] or h[3]!='[366][1][76][1]':raise ValueError('Changed HYCOM array dimensions')
            values={}
            for line in body.splitlines():
                m=re.fullmatch(r'\[(\d+)\]\[0\]\[(\d+)\],\s*(-?\d+)',line.strip())
                if m is None:raise ValueError('Malformed HYCOM integer cell')
                t,y,v=map(int,m.groups())
                if not 0<=t<366 or not 0<=y<76 or not -32768<=v<=32767 or (t,y) in values:raise ValueError('Invalid HYCOM integer coordinate/value')
                values[t,y]=v
            if len(values)!=366*76:raise ValueError('Missing HYCOM source cells')
            parts[key]=values
        else:
            values=[float(x) for x in body.split(',')]
            if h[3]!=f'[{len(values)}]' or any(not math.isfinite(x) for x in values):raise ValueError('Invalid HYCOM coordinate map')
            parts[key]=values
    axes={name:parts['water_u',name] for name in ['time','depth','lat','lon']}
    if any(parts['water_v',name]!=axis for name,axis in axes.items()) or axes['depth']!=[100] or axes['lon']!=[132] or len(axes['lat'])!=76 or abs(axes['lat'][0]+38)>1e-5 or abs(axes['lat'][-1]+32)>1e-5 or any(abs(b-a-.08)>1e-5 for a,b in zip(axes['lat'],axes['lat'][1:])):raise ValueError('Changed HYCOM coordinate/layer alignment')
    dates=[datetime(2000,1,1)+timedelta(hours=t) for t in axes['time']]
    if dates!=[datetime(2012,1,1)+timedelta(days=i) for i in range(366)]:raise ValueError('Changed complete leap-year sampling')
    frames=[]
    for t,instant in enumerate(dates):
        samples=[]
        for y,lat in enumerate(axes['lat']):
            u,v=parts['water_u','water_u'][t,y],parts['water_v','water_v'][t,y]
            samples.append({'coordinate':lat,'latitude':lat,'longitude':132,'source_u_int16':u,'source_v_int16':v,'eastward_m_s':None if u==-30000 else u*.001,'northward_m_s':None if v==-30000 else v*.001})
        frames.append({'time':instant.isoformat()+'Z','samples':samples})
    return {'schema':'osw.hycom-daily-section-inventory.v1','status':'acquired_model_vectors_not_measurement_admission','current_id':'south-australian','config_file':CONFIG.relative_to(ROOT).as_posix(),'config_sha256':digest(CONFIG),'acquisition_file':(CACHE/'acquisition.json').relative_to(ROOT).as_posix(),'acquisition_sha256':digest(CACHE/'acquisition.json'),'source_files':receipt['files'],'source_layer_m':100,'nominal_grid_spacing_degrees':.08,'source_scaling':{'int16_missing':-30000,'scale_factor_m_s':.001,'add_offset':0},'counts':{'times':366,'cells_per_time':76,'vector_positions':366*76,'missing_vector_pairs':sum(s['eastward_m_s'] is None or s['northward_m_s'] is None for f in frames for s in f['samples'])},'frames':frames}

def build():
    source=source_inventory()
    if json.loads(INVENTORY.read_bytes())!=source:raise ValueError('Stale HYCOM source inventory')
    section={'fixed_axis':'longitude','fixed_coordinate':132,'varying_axis':'latitude','domain':[-38,-32],'peak_search':[-35.5,-33.5],'component':'eastward'}
    months=[]
    for month in range(1,13):
        frames=[f for f in source['frames'] if int(f['time'][5:7])==month];required=math.ceil(.8*calendar.monthrange(2012,month)[1]);profile=[]
        for i,grid in enumerate(frames[0]['samples']):
            complete=[f['samples'][i] for f in frames if f['samples'][i]['eastward_m_s'] is not None and f['samples'][i]['northward_m_s'] is not None]
            u=sum(s['eastward_m_s'] for s in complete)/len(complete) if len(complete)>=required else None
            v=sum(s['northward_m_s'] for s in complete)/len(complete) if len(complete)>=required else None
            profile.append({k:grid[k] for k in ['coordinate','latitude','longitude']}|{'eastward_m_s':u,'northward_m_s':v,'component_m_s':u,'paired_source_samples':len(complete),'minimum_required_pairs':required})
        scenarios=[]
        for fraction in [.4,.5,.6]:
            result=measure(profile,section,fraction)
            if result['status']=='paired_boundaries':
                lo,hi=[result['boundaries'][k]['coordinate'] for k in ['low_coordinate','high_coordinate']]
                result['native_cell_spacings']=(hi-lo)/.08;result['resolution_review_required']=result['native_cell_spacings']<4
            scenarios.append(result)
        nominal=scenarios[1];vals=[s['span_km'] for s in scenarios if s['span_km'] is not None]
        months.append({'month':month,'label':calendar.month_abbr[month],'source_times':[f['time'] for f in frames],'minimum_required_pairs':required,'profile':profile,'nominal':nominal,'threshold_scenarios':scenarios,'approximate_section_span_km':math.floor(nominal['span_km']/10+.5)*10 if nominal['span_km'] is not None else None,'threshold_sensitivity_span_km':[math.floor(min(vals)/10)*10,math.ceil(max(vals)/10)*10] if len(vals)==3 else None,'all_thresholds_resolved':len(vals)==3})
    values=[m['approximate_section_span_km'] for m in months if m['approximate_section_span_km'] is not None]
    return {'schema':'osw.hycom-monthly-component-span.v1','status':'local_component_section_diagnostic_requires_scientific_review','current_id':'south-australian','section_id':'south-australian-132e-100m','year':2012,'width_metric':'fixed_orientation_half_peak_eastward_component_span','section_latitude':None,'section_longitude_degrees_east':132,'section':section,'source_url':source['source_files']['section.ascii']['url'],'scope_note':'132 E east Great Australian Bight, modeled 100 m velocity. Local monthly-mean eastward-component spans; association and obliquity unresolved. No CARS/MOM01 reproduction, flow-normal width, whole-current dimensions or seasonal footprint.','layer':'HYCOM+NCODA reanalysis velocity interpolated to 100 m; not a direct 100 m observation or uniform-depth envelope.','time_convention':'All 366 daily 00Z 2012 analyses; monthly complete-pair means with at least 80% of calendar-day support. One leap year, not climatology or annual physical extrema.','monthly_width_is_mean_of_instantaneous_widths':False,'is_climatology':False,'current_association_verified':False,'whole_current_representative':False,'width_rank_eligible':False,'annual_extrema_eligible':False,'seasonal_playback_eligible':False,'chart_playback_eligible':True,'whole_current_length_km':None,'whole_current_width_km':None,'annual_length_range_km':None,'annual_width_range_km':None,'measurement_uncertainty_interval_km':None,'is_confidence_interval':False,'source_inventory_file':INVENTORY.relative_to(ROOT).as_posix(),'source_inventory_sha256':digest(INVENTORY),'config_file':CONFIG.relative_to(ROOT).as_posix(),'config_sha256':digest(CONFIG),'scope_audit_file':'research/south-australian-reference-path-input.json','scope_audit_sha256':digest(ROOT/'research/south-australian-reference-path-input.json'),'protocol_file':PROTOCOL.relative_to(ROOT).as_posix(),'protocol_sha256':digest(PROTOCOL),'general_protocol_sha256':digest(ROOT/'plans/ocean-current-width-measurement-protocol-v1.md'),'generator_sha256':digest(Path(__file__)),'operator_sha256':digest(ROOT/'analysis/build_basin_surface_section_spans.py'),'acquirer_sha256':digest(ROOT/'analysis/acquire_south_australian_hycom_section.py'),'range_kind':'finite_boundary_threshold_sensitivity_not_confidence_or_annual_range','months':months,'summary':{'resolved_nominal_months':len(values),'sample_monthly_mean_span_range_km':[min(values),max(values)] if values else None,'range_kind':'span_of_local_monthly_mean_component_values_not_annual_physical_range'}}

def main():
    INVENTORY.write_bytes((json.dumps(source_inventory(),indent=2)+'\n').encode())
    report=build();OUTPUT.write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print(report['summary']);print([(m['month'],m['approximate_section_span_km'],m['nominal']['status']) for m in report['months']])

if __name__=='__main__':main()
