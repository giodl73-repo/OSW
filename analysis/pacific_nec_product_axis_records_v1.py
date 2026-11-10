"""Pure record construction from retained numerical diagnostics; no field processing."""
import copy
import hashlib
import json
import math

OWNER='current:pacific-north-equatorial'
FAMILY='current:north-equatorial'
KEY='pacific_nec_surface_product_axes_v1'
COLLECTIONS=('current_axis_series','current_axis_readings','current_axis_scenarios','current_axis_section_spans')
PREFIXES=('product_axis_series:pacific-nec:','product_axis_reading:pacific-nec:',
          'product_axis_scenario:pacific-nec:','product_axis_span:pacific-nec:')


def encoded(value):return (json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)+'\n').encode()


def fingerprint(value):return hashlib.sha256(encoded(value)).hexdigest()


def series_id(window):return f'product_axis_series:pacific-nec:oscar2017:2013:w{window[0]}-{window[1]}:v1'


def reading_id(window,month):return f'product_axis_reading:pacific-nec:oscar2017:2013-{month:02d}:w{window[0]}-{window[1]}:v1'


def split_native_geometry(points):
    """Use only the existing180E vertex; never interpolate an invented seam point."""
    if len(points)<2:raise ValueError('At least two native coordinates required')
    if not all(len(p)>=2 and all(type(v) in (int,float) and math.isfinite(v) for v in p[:2]) for p in points):raise ValueError('Nonfinite native geometry')
    if not all(0<a[0]-b[0]<180 for a,b in zip(points,points[1:])):raise ValueError('Westward ordered unwrapped geometry required')
    segments=[];current=[]
    for lon,lat,*_ in points:
        if not -90<=lat<=90 or not 0<=lon<360:raise ValueError('Coordinates outside declared source convention')
        if lon==180:
            current.append([-180,lat]);segments.append(current);current=[[180,lat]]
        else:current.append([lon-360 if lon>180 else lon,lat])
    if current:segments.append(current)
    if any(len(part)<2 for part in segments):raise ValueError('Degenerate dateline display segment')
    if any(abs(a[0]-b[0])>=180 for part in segments for a,b in zip(part,part[1:])):raise ValueError('Dateline crossing lacks an existing180E vertex')
    return {'type':'MultiLineString','coordinates':segments} if len(segments)>1 else {'type':'LineString','coordinates':segments[0]}


def common(window,month,source_ids):
    return {'entity_id':OWNER,'current_id':'pacific-north-equatorial','series_id':series_id(window),
        'year':2013,'month':month,'window_deg_north':list(window),'source_ids':list(source_ids),
        'quality_tier':'experimental_reproducible_product_operator','unit':'km',
        'is_independent_observation':False,'is_physical_uncertainty':False,'is_annual_physical_range':False,
        'physical_current_axis_qualified':False,'whole_current_representative':False,
        'rank_eligible':False,'physical_state_join_eligible':False,'seasonal_playback_eligible':False}


def records(core_report,sampling_report,acquisition,source_ids,report_pins):
    core_file='research/pacific-nec-connected-core-run-v1/diagnostic.json'
    sampling_file='research/pacific-nec-core-sampling-run-v1/diagnostic.json'
    for path in (core_file,sampling_file):
        pin=report_pins.get(path,'')
        if len(pin)!=64 or any(c not in '0123456789abcdef' for c in pin):raise ValueError('Exact source-report hashes required')
    if not source_ids or any(not isinstance(i,str) or not i for i in source_ids) or len(source_ids)!=len(set(source_ids)):
        raise ValueError('Explicit unique source bindings required')
    if (len(core_report['months'])!=12 or len(core_report['cases'])!=324 or len(core_report['section_spans'])!=36
        or len(sampling_report['native_window_paths'])!=36 or len(sampling_report['cases'])!=756
        or len(sampling_report['vertex_thinning_cases'])!=252):raise ValueError('Incomplete scientific source reports')
    if acquisition['month_sample_counts']!=[sum(int(t[5:7])==month for t in acquisition['times']) for month in range(1,13)]:
        raise ValueError('Archive timestamp counts differ')
    if len(acquisition['times'])!=72 or len(set(acquisition['times']))!=72 or any(not t.startswith('2013-') or not t.endswith('Z') for t in acquisition['times']):
        raise ValueError('Exact dated source year required')
    series=[];readings=[];scenarios=[];spans=[]
    windows=([8,18],[7,19],[9,17])
    for window in windows:
        originals=[r for r in sampling_report['native_window_paths'] if r['window_deg_north']==window]
        if sorted(r['month'] for r in originals)!=list(range(1,13)):raise ValueError('Missing/duplicate monthly window cases')
        for original in originals:
            month=original['month'];points=original['points'];length=original['native_witness_length_km']
            if original['reason'] is not None or length is None or not math.isfinite(length) or length<=0:
                raise ValueError('Reviewed native window path is no longer qualified')
            if len(points)!=331 or points[0][0]!=240 or points[-1][0]!=130:raise ValueError('Native path gates/vertices changed')
            if window==[8,18]:
                previous=next(r for r in core_report['months'] if r['month']==month)
                if points!=previous['points'] or length!=previous['length_km']:raise ValueError('Nominal path differs between retained reports')
            times=[t for t in acquisition['times'] if int(t[5:7])==month]
            geometry=split_native_geometry(points)
            readings.append({**common(window,month,source_ids),'id':reading_id(window,month),
                'record_type':'surface_product_axis_reading','label':f'Pacific NEC ·2013-{month:02d} ·{window[0]}–{window[1]}N diagnostic',
                'status':'numerically_qualified_physical_scope_unresolved','quantity':'window_constrained_native_product_core_path_length',
                'length_km':length,'approximate_length_km':100*math.floor(length/100+.5),
                'threshold_m_s':.025,'penalty_m_s':.02,'maximum_angle_deg':60,
                'nominal_depth_coordinate_m':15,'product_version':'OSCAR2017.0',
                'layer_scope':'Satellite-derived near-surface product; nominal15m coordinate is not a direct instrument section.',
                'sample_times_utc':times,'sample_count':len(times),'time_statistic':'equal_sample_mean_grouped_by_UTC_archive_timestamp_month',
                'is_climatology':False,'fixed_gates_degrees_east_unwrapped':[240,130],
                'gate_role':'Editorial regional comparison gates, not physical current endpoints.',
                'native_vector_points':copy.deepcopy(points),'native_point_columns':['longitude_east_unwrapped','latitude_north','eastward_m_s','northward_m_s'],
                'native_point_order':'westward_240E_to_130E','native_point_count':331,
                'geometry':geometry,'geometry_role':'experimental_regional_surface_product_reference',
                'geometry_vertex_kind':'native_grid_points_with_existing_dateline_vertex_duplicated_for_display',
                'display_geometry_is_new_observation':False,'product_month_playback_eligible':True,
                'boundary_contact_native_cells':original['boundary_contact_native_cells'],
                'shared_measurement_claim_id':reading_id(window,month),
                'scientific_report_file':sampling_file,'scientific_report_sha256':report_pins[sampling_file],
                'scientific_report_case_id':original['id'],'native_path_fingerprint':fingerprint(points)})
        rows=[r for r in readings if r['window_deg_north']==window]
        series.append({**common(window,None,source_ids),'id':series_id(window),'record_type':'surface_product_axis_series',
            'label':f'Pacific NEC2013 ·{window[0]}–{window[1]}N product-core diagnostics',
            'quantity':'window_constrained_native_product_core_path_length','sample_collection':COLLECTIONS[1],
            'scenario_collection':COLLECTIONS[2],'section_span_collection':COLLECTIONS[3],
            'reading_count':12,'qualified_numerical_readings':12,'physical_axis_qualified_readings':0,
            'scenario_count':660 if window==[8,18] else 336,'section_span_count':36 if window==[8,18] else 0,
            'scientific_report_file':sampling_file,'scientific_report_sha256':report_pins[sampling_file],
            'nominal_depth_coordinate_m':15,'product_version':'OSCAR2017.0','is_climatology':False,
            'fixed_gates_degrees_east_unwrapped':[240,130],'boundary_contact_months':[r['month'] for r in rows if r['boundary_contact_native_cells']],
            'native_monthly_operator_minimum_km':min(r['length_km'] for r in rows),
            'native_monthly_operator_maximum_km':max(r['length_km'] for r in rows),
            'range_meaning':'Dated monthly product-operator values in one fixed window; no annual physical-current envelope or confidence interval.',
            'whole_current_length_km':None,'physical_uncertainty_km':None,'whole_current_annual_length_range_km':None,
            'physical_width_range_km':None,'source_product_resolution_changed':False})
    groups=[('core_method',core_report['cases']),('anchor_grid',sampling_report['cases']),('vertex_thinning',sampling_report['vertex_thinning_cases'])]
    for kind,originals in groups:
        for index,original in enumerate(originals):
            window=original.get('window_deg_north',[8,18]);month=original['month']
            if kind=='core_method':suffix=original['id'];value=original['length_km'];quantity='native_product_core_path_length';reason=original['reason']
            elif kind=='anchor_grid':suffix=original['id'];value=original['native_witness_length_km'];quantity='native_supported_anchor_search_path_length';reason=original['reason']
            else:suffix=f'2013-{month:02d}:{window[0]}-{window[1]}:s{original["stride"]}:p{original["phase"]}';value=original['thinned_representation_length_km'];quantity='fixed_path_thinned_geodesic_representation_length';reason=None if value is not None else 'native_path_withheld'
            if value is not None and (type(value) not in (int,float) or not math.isfinite(value) or value<=0):
                raise ValueError('Scenario length must be positive finite or null')
            report_file=core_file if kind=='core_method' else sampling_file
            pointer='/vertex_thinning_cases/' if kind=='vertex_thinning' else '/cases/'
            scenarios.append({**copy.deepcopy(original),**common(window,month,source_ids),
                'id':'product_axis_scenario:pacific-nec:'+kind+':'+suffix+':v1',
                'record_type':'surface_product_axis_method_scenario','scenario_kind':kind,'reading_id':reading_id(window,month),
                'quantity':quantity,'length_km':value,'reason':reason,
                'status':'withheld' if value is None else 'computed_operator_sensitivity',
                'shared_measurement_claim_id':reading_id(window,month),
                'parameter_choices_are_independent_measurements':False,'source_product_resolution_changed':False,
                'scientific_report_file':report_file,'scientific_report_sha256':report_pins[report_file],
                'scientific_report_pointer':pointer+str(index),
                'anchor_chord_is_physical_route':False,'chord_is_physical_route':False})
    for index,original in enumerate(core_report['section_spans']):
        month=original['month'];lon=original['longitude_east']
        spans.append({**copy.deepcopy(original),**common([8,18],month,source_ids),
            'id':f'product_axis_span:pacific-nec:oscar2017:2013-{month:02d}:lon{lon}:v1',
            'record_type':'surface_product_axis_section_span','reading_id':reading_id([8,18],month),
            'quantity':'fixed_meridian_connected_negative_zonal_component_span',
            'status':'withheld' if original['width_km'] is None else 'numerical_section_span_physical_scope_unresolved',
            'flow_normal_width_qualified':False,'physical_width_qualified':False,
            'full_year_tracking_passed':False,'annual_physical_width_range_km':None,
            'scientific_report_file':core_file,'scientific_report_sha256':report_pins[core_file],
            'scientific_report_pointer':'/section_spans/'+str(index),
            'previous_fastest_span_is_independent_observation':False})
    result=dict(zip(COLLECTIONS,(series,readings,scenarios,spans)))
    expected=(3,36,1332,36)
    for name,count in zip(COLLECTIONS,expected):
        ids=[r['id'] for r in result[name]]
        if len(ids)!=count or len(set(ids))!=count:raise ValueError('Incomplete or colliding record set: '+name)
    return result
