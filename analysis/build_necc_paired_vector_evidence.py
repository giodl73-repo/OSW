"""Reconstruct paired monthly evidence; source spans do not become current widths."""
import collections,datetime as dt,hashlib,json,math
from pathlib import Path
from necc_paired_vectors import ROOT,BASE,parse,digest
from build_pacific_necc_oscar_section_diagnostic import measure
FROZEN_INPUTS = {'research/source-data/oscar-necc-vectors-2013/preflight.json': 'b65a57a268075c1e3efc6ebc6c1c319c3b6e7462c23ad7dedbbb2731e3427294', 'research/source-data/oscar-necc-vectors-2013/metadata.json': '8c1f41c4e7a0f91492482345e7038c47e461c46c56852dbe57f217e40b9ec2ba', 'research/source-data/oscar-necc-vectors-2013/metadata-acquisition.json': 'f9261037ca1d2bfc92ed91894736f8d29a05bb3e3c0ab6d49414a97fac110203', 'research/source-data/oscar-necc-vectors-2013/longitude.csv': 'ae0a5ee5e5aaf200456e04274d4eb677c26f97c44ad08933db0661613fc8d811', 'research/source-data/oscar-necc-vectors-2013/vectors.csv': '13244f4c65816ad1d436420a188889675b10d6f62858663150186844b8e6c00d', 'research/source-data/oscar-necc-vectors-2013/acquisition.json': 'e0f5c86892b9c7a73e3efef41a456cd46672238e08dc72c6927e12e9c25b0a05', 'analysis/necc_paired_vectors.py': 'c43b59cc343fd364f1f26cafeeb710dcdee9f0a3bdf02c5ffa83a47ff1d1f53c', 'analysis/acquire_necc_paired_vectors.py': '11de1e64ee499bcffa9aef9b00c5afa554b945644f1502d5922322d2eb928df1', 'plans/pacific-necc-paired-vector-native-column-protocol-v1.md': 'ce51294ab11274e488f503792d1824a7d9a05931ce19fc814de3fcd4068f018b', 'analysis/build_pacific_necc_oscar_section_diagnostic.py': 'fa2960b73de47588dde934ddb30bf0a29d6c8149067715a42c4f9fee098ce0f8', 'research/pacific-necc-oscar-2013-section-diagnostic.json': '7b05a062f2303202946f67dfcdd73f754560eb5fe8dbe15b87f8f70f9863aa74', 'research/source-data/oscar-necc-2013-140w/section.csv': 'fb31640c8e809d405fdea3b479cbf843d97736c76225ff4d09a14a2035550741', 'research/source-data/oscar-necc-2013-140w/metadata.json': '8c1f41c4e7a0f91492482345e7038c47e461c46c56852dbe57f217e40b9ec2ba'}
INVENTORY='research/pacific-necc-paired-vector-source-inventory.json'
REPORT='research/pacific-necc-paired-vector-direction-evidence.json'
def encoded(data):return (json.dumps(data,indent=2,ensure_ascii=False)+'\n').encode()

def verify_sources():
    for name,pin in FROZEN_INPUTS.items():
        if digest(ROOT/name)!=pin:raise ValueError('Changed retained paired-vector source '+name)
    r=json.loads((BASE/'acquisition.json').read_bytes())
    if r['status']!='COMPLETE_VALIDATED' or r['preflight_sha256']!=digest(BASE/'preflight.json'):raise ValueError('Incomplete vector source acquisition')
    for name,record in r['files'].items():
        if digest(BASE/name)!=record['sha256']:raise ValueError('Changed vector original')
    for name,pin in r['collector_and_validator_sha256'].items():
        if digest(ROOT/name)!=pin:raise ValueError('Historical vector acquisition code changed')
    if (BASE/'metadata.json').read_bytes()!=(ROOT/'research/source-data/oscar-necc-2013-140w/metadata.json').read_bytes():raise ValueError('OSCAR metadata edition changed')
    return parse(BASE/'vectors.csv',BASE/'longitude.csv')

def monthly(data):
    rows=[]
    for lon in data['longitudes']:
        for month in range(1,13):
            times=[t for t in data['times'] if int(t[5:7])==month]
            if len(times)<5:raise ValueError('Insufficient paired monthly time support')
            profile=[]
            for lat in data['latitudes']:
                pairs=[data['vectors'][t,lat,lon] for t in times]
                valid=[(u,v) for u,v in pairs if u is not None and v is not None]
                complete=len(valid)==len(pairs)
                profile.append({'latitude':lat,'eastward_m_s':sum(u for u,v in valid)/len(valid) if complete else None,'northward_m_s':sum(v for u,v in valid)/len(valid) if complete else None,'expected_samples':len(times),'valid_pair_count':len(valid),'missing_pair_count':len(pairs)-len(valid)})
            measures=[measure(profile,threshold) for threshold in [0,.05,.1]]
            primary=measures[0];peak=None
            if primary.get('peak_latitude') is not None and primary['peak_eastward_m_s']>=.1:
                cell=next(p for p in profile if p['latitude']==primary['peak_latitude'])
                angle=math.degrees(math.atan2(cell['northward_m_s'],cell['eastward_m_s']))
                peak={'latitude':cell['latitude'],'native_latitude_index':data['latitudes'].index(cell['latitude']),'eastward_m_s':cell['eastward_m_s'],'northward_m_s':cell['northward_m_s'],'speed_m_s':math.hypot(cell['eastward_m_s'],cell['northward_m_s']),'direction_degrees_from_east':angle,'direction_attention_above_15_degrees':abs(angle)>15,'peak_at_search_gate_edge':cell['latitude'] in [2,10]}
            rows.append({'id':f'oscar-necc-paired-2013-{data["longitudes"].index(lon)}-{month:02d}','source_longitude_degrees_east':lon,'month':month,'source_sample_times':times,'expected_samples_per_cell':len(times),'profile':profile,'zero_crossing_component_span':primary,'threshold_sensitivity':measures[1:],'selected_peak_vector':peak,'physical_current_width_km':None,'flow_normal_width_km':None,'width_uncertainty_km':None})
    return rows

def build():
    data=verify_sources();rows=monthly(data);code=digest(Path(__file__))
    samples=[{'time':t,'depth_coordinate_m':15,'latitude':lat,'longitude':lon,'eastward_m_s':u,'northward_m_s':v,'paired_valid':u is not None and v is not None} for (t,lat,lon),(u,v) in sorted(data['vectors'].items())]
    inventory={'schema':'osw.necc-paired-source-vectors.v1','status':'archived_near_surface_product_region_not_named_current_membership','context_current_id':'pacific-north-equatorial-countercurrent','samples_are_named_current_members':False,'product_version':'2017.0','year':2013,'vector_positions':data['vector_positions'],'paired_finite_positions':data['paired_finite_positions'],'nominal_depth_coordinate_m':15,'units':{'time':'UTC','latitude':'degrees_north','longitude':'degrees_east_0_to_360','eastward_m_s':'m/s','northward_m_s':'m/s'},'source_times':data['times'],'native_latitudes':data['latitudes'],'native_longitudes':data['longitudes'],'samples':samples,'input_sha256':FROZEN_INPUTS,'generator_sha256':code,'scope':'Satellite-derived near-surface regional samples. Negative and positive flow cells are not assigned to the named NECC; no instrument depth slice, current boundary or axis is inferred.'}
    previous=json.loads((ROOT/'research/pacific-necc-oscar-2013-section-diagnostic.json').read_bytes())
    reproduction=[]
    for row in rows:
        if row['source_longitude_degrees_east']!=220:continue
        old=next(r for r in previous['months'] if r['month']==row['month'])
        equal=all(a['latitude']==b['latitude'] and a['eastward_m_s']==b['eastward_m_s'] for a,b in zip(row['profile'],old['profile']))
        before=old['zero_crossing']['span_km'];after=row['zero_crossing_component_span']['span_km']
        reproduction.append({'month':row['month'],'paired_monthly_eastward_means_equal_old_u_only':equal,'old_component_span_km':before,'paired_component_span_km':after,'span_absolute_difference_km':abs(after-before) if before is not None and after is not None else None})
    coherence=[]
    for month in range(1,13):
        peaks=[r['selected_peak_vector'] for r in rows if r['month']==month]
        supported=[p for p in peaks if p is not None]
        spread=max(p['native_latitude_index'] for p in supported)-min(p['native_latitude_index'] for p in supported) if len(supported)==3 else None
        coherence.append({'month':month,'supported_columns':len(supported),'peak_native_latitude_index_spread':spread,'peak_separation_above_two_native_cells':spread>2 if spread is not None else None,'is_independent_validation':False,'is_width_uncertainty':False})
    gaps=collections.Counter((dt.datetime.fromisoformat(b.replace('Z','+00:00'))-dt.datetime.fromisoformat(a.replace('Z','+00:00'))).total_seconds()/86400 for a,b in zip(data['times'],data['times'][1:]))
    angles=[abs(r['selected_peak_vector']['direction_degrees_from_east']) for r in rows if r['selected_peak_vector']]
    report={'schema':'osw.necc-paired-vector-direction-evidence.v1','status':'source_component_direction_and_column_context_not_physical_width_admission','context_current_id':'pacific-north-equatorial-countercurrent','year':2013,'source_inventory_file':INVENTORY,'source_inventory_sha256':hashlib.sha256(encoded(inventory)).hexdigest(),'native_longitudes_degrees_east':data['longitudes'],'native_latitudes_degrees_north':data['latitudes'],'actual_first_sample_utc':data['times'][0],'actual_last_sample_utc':data['times'][-1],'actual_timestamp_gap_days':{str(k):v for k,v in sorted(gaps.items())},'source_timestamp_count':72,'source_vector_positions':7992,'source_scalar_velocity_slots':15984,'finite_scalar_velocity_values':sum(value is not None for pair in data['vectors'].values() for value in pair),'paired_finite_positions':data['paired_finite_positions'],'target_u_values_and_masks_exact':data['old_target_values_exact'],'rows':rows,'target_monthly_reproduction':reproduction,'native_column_context':coherence,'summary':{'row_count':len(rows),'peak_vectors_supported':len(angles),'maximum_absolute_peak_direction_degrees':max(angles) if angles else None,'rows_above_15_degree_attention_flag':sum(r['selected_peak_vector']['direction_attention_above_15_degrees'] for r in rows if r['selected_peak_vector']),'months_above_two_cell_peak_separation_flag':sum(r['peak_separation_above_two_native_cells'] is True for r in coherence),'target_monthly_means_equal_old':sum(r['paired_monthly_eastward_means_equal_old_u_only'] for r in reproduction)},'nominal_depth_coordinate_m':15,'units':{'velocity':'m/s','direction':'degrees_from_east_positive_toward_north','component_span':'km','latitude':'degrees_north','longitude':'degrees_east_0_to_360'},'layer':'Satellite-derived near-surface OSCAR field; nominal 15 m product coordinate, not a direct instrument slice or a depth-resolved measurement.','averaging':'Equal-sample paired monthly means of all available source timestamps, with complete pairs required at each cell; not exact daily/time-weighted means or a climatology.','direction_definition':'Direction of the paired monthly-mean vector at its selected eastward peak; not an average of per-frame headings.','speed_definition':'Magnitude of that paired monthly-mean vector; not mean per-frame speed.','component_span_definition':'First connected positive eastward component of the paired monthly-mean profile; not mean per-frame spans.','nominal_native_grid_spacing_degrees':1/3,'native_grid_spacing_is_effective_resolution':False,'attention_flags_are_admission_thresholds':False,'same_product_columns_are_independent_validation':False,'component_spans_are_flow_normal_widths':False,'new_width_record_admitted':False,'whole_current_width_km':None,'annual_width_range_km':None,'whole_current_length_km':None,'annual_length_range_km':None,'rank_eligible':False,'seasonal_geometry_admitted':False,'current_association_verified':False,'physical_geometry_admitted':False,'input_sha256':dict(FROZEN_INPUTS,**{INVENTORY:hashlib.sha256(encoded(inventory)).hexdigest()}),'generator_sha256':code,'credit':'ESR OSCAR version 2017.0, NOAA PIFSC ERDDAP mirror. Source license and citation retained verbatim in metadata.json. OSW derives monthly paired means and direction/column diagnostics.'}
    return inventory,report

if __name__=='__main__':
    inventory,report=build();(ROOT/INVENTORY).write_bytes(encoded(inventory));(ROOT/REPORT).write_bytes(encoded(report));print('BUILT',len(inventory['samples']),'source vectors;',report['summary'])
