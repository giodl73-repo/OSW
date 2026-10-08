"""Package audited JSON imports for the shared native/WASM Rust record store."""
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'almanac/query-data.json'
CANONICAL=['entities', 'sources', 'claims', 'relations', 'measurements', 'geometries', 'names', 'length_assessments', 'classification_vocabularies', 'named_eddy_footprint_candidates', 'footprint_movie_context', 'media', 'tiles', 'tile_state_relations', 'named_eddy_state_assessments', 'named_eddy_source_observations', 'named_current_source_observations', 'operational_eddy_state_observations', 'diagnosed_current_path_observations', 'observation_sets']

def build():
    inputs={}
    def read(path):
        raw=(ROOT/path).read_bytes();inputs[path]=hashlib.sha256(raw).hexdigest()
        return json.loads(raw)
    base='almanac/release/v0.1.0/'
    collections={name:read(base+name+'.json') for name in CANONICAL}
    read(base+'manifest.json')
    preview='almanac/release/v0.1.0-rights-screened-preview/'
    preview_manifest=read(preview+'manifest.json')
    if preview_manifest['source_manifest_sha256']!=inputs[base+'manifest.json']:raise ValueError('Stale screened preview parent')
    movies_receipts={}
    for name in ['manifest','tiles','tile_state_relations','media','entities']:
        path=preview+name+'.json';document=read(path)
        if name!='manifest':
            digest=next(r['sha256'] for r in preview_manifest['files'] if r['path']==name+'.json')
            if digest!=inputs[path]:raise ValueError('Changed screened movie input: '+path)
        movies_receipts[name]={'source_file':path,'source_sha256':inputs[path],'source_json':(ROOT/path).read_bytes().decode('utf-8')}
    dashboard=read('research/ocean-motion-dashboard.json')
    widths=read('research/ocean-current-width-inventory.json')
    from check_current_width_inventory import validate
    validate(widths,read('research/ocean-current-almanac.json'))
    routes=read('research/ocean-current-reference-path-candidates.json')
    for record in widths['measurements']:
        if record.get('extraction_file'):
            extraction = read(record['extraction_file'])
            read(extraction['acquisition_file'])
            for dependency in [extraction['protocol_file'], extraction['generator_file'], *[s['file'] for s in json.loads((ROOT / extraction['acquisition_file']).read_bytes())['files']]]:
                inputs[dependency]=hashlib.sha256((ROOT/dependency).read_bytes()).hexdigest()
            extra = extraction.get('additional_source_receipts')
            if extra:
                read(extra['acquisition_file'])
                for key in ['source_file', 'parser_file']:
                    inputs[extra[key]]=hashlib.sha256((ROOT/extra[key]).read_bytes()).hexdigest()
        context=record.get('eulerian_section_context') or record.get('width_statistics_context') or record.get('regional_range_context') or record.get('regional_scalar_context') or record.get('mean_offshore_context') or record.get('adcp_threshold_context')
        if context:
            audit=read(context['audit_file'])
            if audit.get('source_document_file'):
                path=audit['source_document_file']
                inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    collections['widths']=widths['measurements']
    collections['reference_routes']=routes['candidates']
    objects=copy.deepcopy(dashboard['entries'])
    for row in objects:row['dashboard_search']=row['label']+' '+row['basin']
    entity_index={e['id']:e for e in collections['entities']}
    sources={s['id'] for s in collections['sources']}
    from build_query_taxonomy import build as build_taxonomy
    collections['taxonomy_links'],taxonomy=build_taxonomy(objects,collections['entities'],read)
    inputs['analysis/build_query_taxonomy.py']=hashlib.sha256((ROOT/'analysis/build_query_taxonomy.py').read_bytes()).hexdigest()
    state_links=[]
    for row in objects:
        current=row['id'].removeprefix('current:')
        row['width_ids']=[w['id'] for w in collections['widths'] if w['current_id']==current]
        measures=[m for m in collections['measurements'] if m['entity_id']==row['id']]
        row['measurement_ids']=[m['id'] for m in measures]
        row['route_ids']=[r['id'] for r in collections['reference_routes'] if r['current_id']==current]
        source_ids={entity_index[row['id']].get('source_id')}
        source_ids.update(m.get('source_id') for m in measures)
        source_ids.update(c.get('source_id') for c in collections['claims'] if row['id'] in [c.get('subject_id'),c.get('object_id')])
        row['source_ids']=sorted(s for s in source_ids if s in sources)
        row['state_codes']=sorted({r['state_code'] for r in row['state_evidence']})
        lengths=[m['value'] for m in measures if m.get('rank_eligible') is True and m['quantity']=='reported_length']
        if len(lengths)>1:raise ValueError('Multiple ranked source lengths require explicit variant selection')
        row['published_length_km']=lengths[0] if lengths else None
        for i,relation in enumerate(row['state_evidence']):
            state_links.append({'id':f"query-state:{row['id']}:{i}",'entity_id':row['id'],'entity_label':row['label'],**relation})
    collections['objects']=objects
    recurrence_path='research/black-sea-eddy-recurrence.json'
    recurrence=read(recurrence_path)
    from build_black_sea_eddy_recurrence import validate as validate_recurrence
    validate_recurrence(recurrence)
    collections['eddy_recurrence']=recurrence['entries']
    for key in ['source_document_file','protocol_file','generator_file']:
        path=recurrence[key];inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    collections['state_links']=state_links
    collections['states']=[{**e,'code':e['id'].removeprefix('state:')} for e in collections['entities'] if e['type']=='osw_state']
    # Import the same coarse, land-masked OSW polygons as the existing state joins.
    from build_cartographic_current_state_join import load_states
    from shapely.geometry import mapping
    from shapely.ops import transform
    import shapely
    for path in ['figures/osw-province-atlas-interactive.svg', 'analysis/build_cartographic_current_state_join.py', 'analysis/build_motion_state_join.py', 'analysis/build_current_reference_path_candidate.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    state_shapes=load_states()
    for state in collections['states']:
        shape=state_shapes[state['code']]
        if not shape.is_valid or shape.is_empty:raise ValueError('Invalid masked state geometry')
        geographic=transform(lambda x,y,z=None:((x-60)*360/1480-180,90-(y-90)*180/740),shape)
        state['display_geometry']=json.loads(json.dumps(mapping(geographic)))
        state['geometry_scope']='Approximate OSW display-state polygons with coarse atlas land removed; not a physical ocean boundary.'
    # Source semantic exclusions remain attached to each route geometry.
    route_shapes={}
    from build_current_reference_path_candidate import display_coordinates
    for route in collections['reference_routes']:
        candidate=read(route['candidate_file'])
        if inputs[route['candidate_file']]!=route['candidate_sha256']:raise ValueError('Stale route candidate')
        route_shapes[route['id']]=candidate
    for row in objects:
        for feature in row['map_features']:
            matches=[g for g in collections['geometries'] if g['entity_id']==row['id'] and g['role']==feature['role'] and g['geometry']==feature['geometry']]
            if len(matches)==1:
                geometry=matches[0]
                feature['geometry_id']=geometry['id']
                for key in ['observation_date','coordinate_reference_system','coordinate_reference_status','positional_uncertainty','source_id','source_snapshot_id']:
                    if key in geometry:feature[key]=geometry[key]
            if feature.get('role')=='editorial_reference_route':
                matches=[route for route in collections['reference_routes'] if route['id'] in row['route_ids'] and route_shapes[route['id']]['coordinates_lon_lat']==feature['geometry']['coordinates']]
                if len(matches)!=1:raise ValueError('Ambiguous route geometry identity')
                route=matches[0];candidate=route_shapes[route['id']]
                feature['candidate_id']=route['id']
                feature['state_semantic_exclusions']=candidate.get('state_semantic_exclusions',[])
                points=display_coordinates(candidate['coordinates_lon_lat'],allow_seam=candidate.get('longitude_seam_policy')=='shortest_geodesic_periodic_display')
                feature['spatial_geometry']={'type':'LineString','coordinates':[[((x-60)*360/1480)%360-180,90-(y-90)*180/740] for x,y in points]}
                feature['spatial_geometry_method']='WGS84 geodesic legs densified at <=10 km as in the existing reference-route state join; planar relation to coarse masked OSW display polygons.'
    collections['series']=[{'id':f"query-series:{row['id']}:{i}",'entity_id':row['id'],**series} for row in objects for i,series in enumerate(row['series'])]
    # Seasonal source conventions are distinct from exact observation dates.
    seasonal_path='research/ocean-current-seasonal-route-frames.json'
    seasonal=read(seasonal_path)
    if inputs[seasonal['width_inventory_file']]!=seasonal['width_inventory_sha256']:raise ValueError('Stale seasonal width inventory')
    reports={}
    for phase in seasonal['frames']:
        reports[phase['route_candidate_file']]=read(phase['route_candidate_file'])
        if inputs[phase['route_candidate_file']]!=phase['route_candidate_sha256']:raise ValueError('Stale seasonal route')
    from check_current_seasonal_route_frames import validate as validate_seasonal
    validate_seasonal(seasonal,reports,widths)
    inputs['analysis/check_current_seasonal_route_frames.py']=hashlib.sha256((ROOT/'analysis/check_current_seasonal_route_frames.py').read_bytes()).hexdigest()
    collections['seasonal_routes']=[]
    for phase in seasonal['frames']:
        candidate=reports[phase['route_candidate_file']]
        entity_id='current:'+phase['current_id'];row=next(r for r in objects if r['id']==entity_id)
        comparison=next(c for c in seasonal['comparability'] if c['current_id']==phase['current_id'])
        record={**copy.deepcopy(phase),'entity_id':entity_id,'label':row['label']+' — '+phase['phase_label'],
                'status':seasonal['status'],'seasonal_inventory_file':seasonal_path,'seasonal_inventory_sha256':inputs[seasonal_path],
                'coordinates_lon_lat':copy.deepcopy(candidate['coordinates_lon_lat']),'comparability':copy.deepcopy(comparison)}
        collections['seasonal_routes'].append(record);row.setdefault('seasonal_route_ids',[]).append(record['id'])
        points=display_coordinates(candidate['coordinates_lon_lat'],allow_seam=candidate.get('longitude_seam_policy')=='shortest_geodesic_periodic_display')
        row['map_features'].append({'geometry':{'type':'LineString','coordinates':copy.deepcopy(candidate['coordinates_lon_lat'])},
            'role':phase['geometry_role'],'phase_id':phase['id'],
            **{key:copy.deepcopy(record[key]) for key in ['phase_label','calendar_months','flow_direction','source_url','source_locator','time_convention','layer','route_candidate_sha256','seasonal_inventory_sha256','comparability']},
            'spatial_geometry':{'type':'LineString','coordinates':[[((x-60)*360/1480)%360-180,90-(y-90)*180/740] for x,y in points]},
            'state_semantic_exclusions':candidate.get('state_semantic_exclusions',[]),
            'spatial_geometry_method':'WGS84 geodesic legs densified at <=10 km; planar relation to coarse land-masked OSW display polygons. Source-defined seasonal regional editorial route, not an occupied footprint.',
            'note':phase['time_convention']+' '+comparison['reason']})
    # Import existing checked diagnostic frames without admitting them as current axes.
    from check_current_dated_timeline import validate as validate_timeline
    collections['geometry_frames']=[]
    for path in ['research/ocean-current-dated-timeline-2025.json','research/ocean-current-dated-timeline.json']:
        timeline=read(path)
        validate_timeline(timeline)
        for dependency in [timeline['audit_file'],'analysis/build_current_dated_timeline.py','analysis/check_current_dated_timeline.py','analysis/build_gulf_stream_geostrophic_path.py','analysis/build_loop_current_recorded_dates.py']:
            inputs[dependency]=hashlib.sha256((ROOT/dependency).read_bytes()).hexdigest()
        entity_id='current:'+timeline['current_id']
        row=next(r for r in objects if r['id']==entity_id)
        series=next(s for s in collections['series'] if s['entity_id']==entity_id and s['url']=='dated-current.html')
        for frame in timeline['frames']:
            frame_id=f"query-frame:{entity_id}:{frame['date']}:fixed-seed-geostrophic"
            for dependency in [frame['source_subset'],frame['figure']]:
                inputs[dependency]=hashlib.sha256((ROOT/dependency).read_bytes()).hexdigest()
            record={'id':frame_id,'entity_id':entity_id,'series_id':series['id'],
                'label':f"{timeline['name']} — {frame['date']} frozen-field diagnostic",'status':timeline['status'],
                'timeline_file':path,'timeline_sha256':inputs[path],
                **{key:copy.deepcopy(timeline[key]) for key in ['layer','method','geometry_role','sampling_note','limitations','attribution','product_page','annual_extrema_eligible','annual_length_range_km','annual_width_range_km']},
                **copy.deepcopy(frame)}
            collections['geometry_frames'].append(record)
            row.setdefault('frame_ids',[]).append(frame_id)
            series.setdefault('frame_ids',[]).append(frame_id)
            row['map_features'].append({'geometry':{'type':'LineString','coordinates':copy.deepcopy(frame['coordinates_lon_lat'])},
                'role':timeline['geometry_role'],'observation_date':frame['date'],'frame_id':frame_id,'series_id':series['id'],
                'source_url':frame['source_url'],'source_subset_sha256':frame['source_subset_sha256'],
                'source_response_sha256':frame['source_response_sha256'],'timeline_sha256':inputs[path],
                'source_algorithm':frame['source_algorithm'],'source_product_status':frame['source_product_status'],
                'coordinate_reference_system':'longitude_latitude_source_grid_with_WGS84_trace_integration',
                'coordinate_reference_status':'Trace integration uses WGS84; source grid datum is not independently resolved here.',
                'positional_uncertainty':None,
                'note':f"{timeline['sampling_note']} {timeline['limitations']} Stop: {frame['stop_reason']}. {timeline['attribution']}"})
    for series in collections['series']:
        if series.get('frame_ids') and len(series['frame_ids'])!=series['frames']:raise ValueError('Incomplete geometry frame series')
    collections['diagnostics']=[{'id':id,'document':read(path)} for id,path in [
        ('diagnostic:florida-monthly-width','research/florida-monthly-width-plot-extraction.json'),
        ('diagnostic:leeuwin-monthly-width','research/leeuwin-a101-monthly-plot-extraction.json'),
        ('diagnostic:kuroshio-seasonal-width','research/kuroshio-ecs-seasonal-width-profile-extraction.json'),
        ('diagnostic:necc-monthly-section','research/pacific-necc-oscar-2013-section-diagnostic.json'),
        ('diagnostic:antilles-observed-sections','research/antilles-ab0505-400m-section-diagnostic.json'),
        ('diagnostic:gulf-stream-widths','research/gulf-stream-section-width-series.json')]]
    florida_diagnostic=next(d for d in collections['diagnostics'] if d['id']=='diagnostic:florida-monthly-width')
    florida_path='research/florida-monthly-width-plot-extraction.json'
    florida_diagnostic.update(source_file=florida_path,source_file_sha256=inputs[florida_path],source_json=(ROOT/florida_path).read_bytes().decode('utf-8'))
    # Two same-day Loop experiments remain separate methods and unranked.
    from build_loop_current_dated_streamline import build as rebuild_loop_noaa
    from build_loop_current_adt_contours import build as rebuild_loop_adt
    loop_owner=next(r for r in objects if r['id']=='current:loop')
    loop_owner['diagnostic_ids']=[]
    loop_specs=[
        ('diagnostic:loop-noaa-20260925','research/loop-current-dated-streamline-20260925.json','Loop Current — NOAA velocity integration, 25 September 2026',rebuild_loop_noaa,'nominal','source_subset'),
        ('diagnostic:loop-adt-20260925','research/loop-current-adt-contours-20260925.json','Loop Current — DUACS ADT contour search, 25 September 2026',rebuild_loop_adt,'selected','source_file')]
    from build_loop_current_recorded_dates import build as rebuild_loop_series, source_rows, rebuild_noaa, rebuild_adt, path_for, OUTPUT as LOOP_SERIES
    from functools import partial
    series=read(LOOP_SERIES.relative_to(ROOT).as_posix())
    if series!=rebuild_loop_series():raise ValueError('Stale Loop repeat series')
    read(series['source_manifest'])
    for row in source_rows():
        for method,fn,key,source_key in [('noaa',rebuild_noaa,'nominal','source_subset'),('adt',rebuild_adt,'selected','source_file')]:
            stamp=row['date'].replace('-','')
            loop_specs.append((f'diagnostic:loop-{method}-{stamp}',path_for(method,row['date']).relative_to(ROOT).as_posix(),
                'Loop Current — '+('NOAA velocity integration' if method=='noaa' else 'DUACS ADT contour search')+', '+row['date'],partial(fn,row),key,source_key))
    for ident,path,label,rebuild,coordinates_key,source_key in loop_specs:
        document=read(path)
        if document!=rebuild():raise ValueError('Stale Loop diagnostic: '+ident)
        for key in [source_key,'protocol_file']:
            dependency=document[key];raw_hash=hashlib.sha256((ROOT/dependency).read_bytes()).hexdigest()
            expected=document['source_subset_sha256' if key=='source_subset' else 'source_sha256' if key=='source_file' else 'protocol_sha256']
            if raw_hash!=expected:raise ValueError('Stale Loop dependency: '+dependency)
            inputs[dependency]=raw_hash
        snapshot=read(document[source_key])
        record={'id':ident,'label':label,'entity_id':'current:loop','current_id':'loop',
            'observation_date':document['observation_date'],'status':document['status'],
            'rank_eligible':False,'source_file':path,'source_file_sha256':inputs[path],
            'diagnostic_page':'almanac/loop-current-experiment.html' if document['observation_date']=='2026-09-25' else 'almanac/loop-current-recorded-dates.html','source_url':document['source_url'],
            'scope':'Dated surface diagnostic between editorial gates. No whole-current length, width, annual range or independent observational confirmation.',
            'document':document,'source_json':(ROOT/path).read_bytes().decode('utf-8')}
        collections['diagnostics'].append(record);loop_owner['diagnostic_ids'].append(ident)
        selected=document[coordinates_key]
        if selected is not None and (coordinates_key=='selected' or selected['gate_connected']):
            frame_id='geometry-frame:'+ident.removeprefix('diagnostic:')
            role='frozen_field_diagnostic_streamline_not_current_axis_or_parcel_track' if coordinates_key=='nominal' else 'finite_ADT_contour_diagnostic_not_admitted_current_axis'
            frame={'id':frame_id,'entity_id':'current:loop','label':label,'date':document['observation_date'],
                'observation_date':document['observation_date'],'geometry_role':role,'diagnostic_id':ident,
                'coordinates_lon_lat':copy.deepcopy(selected['coordinates_lon_lat']),
                'rank_eligible':False,'source_url':document['source_url'],'status':document['status'],
                'scope':record['scope'],'diagnostic_page':record['diagnostic_page']}
            collections['geometry_frames'].append(frame);loop_owner.setdefault('frame_ids',[]).append(frame_id)
            loop_owner['map_features'].append({'geometry':{'type':'LineString','coordinates':copy.deepcopy(frame['coordinates_lon_lat'])},
                'role':role,'observation_date':frame['date'],'frame_id':frame_id,'diagnostic_id':ident,
                'source_url':document['source_url'],'source_subset_sha256':inputs[document[source_key]],
                'source_response_sha256':snapshot['source_response_sha256'],
                'source_algorithm':snapshot.get('source_algorithm',snapshot.get('source_metadata',{}).get('subset_datasetId')),
                'layer':document['layer'],'note':record['scope']+' '+document['interpretation']})
    for path in ['analysis/build_loop_current_dated_streamline.py','analysis/build_loop_current_adt_contours.py','analysis/build_gulf_stream_geostrophic_path.py','analysis/build_loop_current_recorded_dates.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    from check_current_section_width_series import validate as validate_dated_widths
    dated_widths=next(d['document'] for d in collections['diagnostics'] if d['id']=='diagnostic:gulf-stream-widths')
    validate_dated_widths(dated_widths)
    for path in ['analysis/build_current_section_width_series.py','analysis/check_current_section_width_series.py','plans/gulf-stream-section-width-protocol-v1.md','plans/ocean-current-width-measurement-protocol-v1.md']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    for frame in dated_widths['frames']:
        path=frame['source_subset'];inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
        if inputs[path]!=frame['source_subset_sha256']:raise ValueError('Changed dated width source')
    from build_loop_current_section_spans import build as rebuild_loop_sections, output as loop_section_output
    for method in ['noaa','adt']:
        path=loop_section_output(method).relative_to(ROOT).as_posix();document=read(path)
        if document!=rebuild_loop_sections(method):raise ValueError('Stale Loop section span diagnostic')
        collections['diagnostics'].append({'id':f'diagnostic:yucatan-{method}-sections','label':f'Loop inflow — {method.upper()} fixed-section spans',
            'entity_id':'current:loop','current_id':'loop','status':document['status'],'rank_eligible':False,
            'source_file':path,'source_file_sha256':inputs[path],'source_json':(ROOT/path).read_bytes().decode('utf-8'),'document':document})
        for dependency in ['analysis/build_loop_current_section_spans.py',document['protocol_file']]:
            inputs[dependency]=hashlib.sha256((ROOT/dependency).read_bytes()).hexdigest()
    from build_query_width_samples import build as build_width_samples
    from build_leeuwin_monthly_plot import build as rebuild_leeuwin
    from build_kuroshio_seasonal_width_profiles import build as rebuild_kuroshio
    from build_pacific_necc_oscar_section_diagnostic import build as rebuild_necc, diagnostic_matches
    from build_florida_monthly_plot import build as rebuild_florida
    rebuilds={'diagnostic:florida-monthly-width':rebuild_florida,'diagnostic:leeuwin-monthly-width':rebuild_leeuwin,'diagnostic:kuroshio-seasonal-width':rebuild_kuroshio,'diagnostic:necc-monthly-section':rebuild_necc}
    for diagnostic in collections['diagnostics']:
        if diagnostic['id'] not in rebuilds:continue
        original=diagnostic['document'];calculated=rebuilds[diagnostic['id']]()
        matches=diagnostic_matches(original,calculated) if diagnostic['id']=='diagnostic:necc-monthly-section' else original==calculated
        if not matches:raise ValueError('Width diagnostic differs from pinned source reconstruction: '+diagnostic['id'])
        for key,path in original.items():
            if key.endswith('_file') and key.removesuffix('_file')+'_sha256' in original:
                actual=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
                if actual!=original[key.removesuffix('_file')+'_sha256']:raise ValueError('Stale width diagnostic dependency: '+path)
                inputs[path]=actual
    for path in ['analysis/build_florida_monthly_plot.py','analysis/build_leeuwin_monthly_plot.py','analysis/build_kuroshio_seasonal_width_profiles.py','analysis/build_pacific_necc_oscar_section_diagnostic.py','analysis/acquire_pacific_necc_oscar_section.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    inputs['analysis/build_query_width_samples.py']=hashlib.sha256((ROOT/'analysis/build_query_width_samples.py').read_bytes()).hexdigest()
    collections['width_samples']=build_width_samples(collections['diagnostics'])
    for row in objects:
        row['width_sample_ids']=[sample['id'] for sample in collections['width_samples'] if sample['entity_id']==row['id']]
        row['capabilities']['width_samples']=len(row['width_sample_ids'])
    # Keep the complete remaining-length worklist queryable without assigning
    # dimensions to unresolved names, families or continuity hypotheses.
    collections['route_decisions']=[]
    for original in routes['remaining_current_decisions']:
        entity_id='current:'+original['current_id']
        owner=next(row for row in objects if row['id']==entity_id)
        if sorted(original['candidate_ids'])!=sorted(owner['route_ids']):
            raise ValueError('Planning candidate IDs disagree with imported routes')
        reviews=[]
        for note in owner['scope_notes']:
            document=read(note['audit_file'])
            if document['current_id']!=original['current_id']:raise ValueError('Scope review owner mismatch')
            reviews.append({'note':copy.deepcopy(note),'document':document,'source_sha256':inputs[note['audit_file']]})
        record={'id':'route-decision:'+original['current_id'],'entity_id':entity_id,
                'label':original['name'],'current_id':original['current_id'],
                'strategy_id':original['route_strategy_id'],'strategy_label':original['route_strategy_label'],
                'construction_status':original['reference_path_decision'],
                'candidate_count':len(original['candidate_ids']),'route_ids':copy.deepcopy(original['candidate_ids']),
                'next_action':original['next_action'],'scope':original['existing_scope'],
                'status':original['planning_status'],'rank_eligible':False,
                'source_url':original['name_source_url'],'source_decision':copy.deepcopy(original),
                'source_catalog_file':'research/ocean-current-reference-path-candidates.json',
                'source_catalog_sha256':inputs['research/ocean-current-reference-path-candidates.json'],
                'scope_reviews':reviews}
        collections['route_decisions'].append(record)
        owner['route_decision_ids']=[record['id']]
    from build_flow_network import build as build_network, INPUT as NETWORK_INPUT
    read(NETWORK_INPUT.relative_to(ROOT).as_posix())
    network_collections=build_network();collections.update(network_collections)
    inputs['analysis/build_flow_network.py']=hashlib.sha256((ROOT/'analysis/build_flow_network.py').read_bytes()).hexdigest()
    network_owner=next(row for row in objects if row['id']=='current:indonesian-throughflow')
    network_owner['flow_network_ids']=[r['id'] for r in collections['flow_networks']]
    network_owner['passage_sample_ids']=[r['id'] for r in collections['passage_samples']]
    model_timeline=read('research/norkyst-ingoy-2024-section-timeline.json')
    model_maps=read('research/norkyst-ingoy-2024-map-frames.json')
    from check_norkyst_ingoy_timeline import validate as validate_model_timeline
    from check_norkyst_ingoy_maps import validate as validate_model_maps
    validate_model_timeline(model_timeline);validate_model_maps(model_maps,model_timeline)
    for document in [model_timeline,model_maps]:
        for kind in ['acquisition','generator','protocol','projection_helper']:
            if kind+'_file' not in document:continue
            path=document[kind+'_file'];inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
            if inputs[path]!=document[kind+'_sha256']:raise ValueError('Stale model source provenance: '+path)
        for frame in document['frames']:
            for file_key,hash_key in [('receipt_file','receipt_sha256'),('figure','figure_sha256')]:
                if file_key not in frame:continue
                path=frame[file_key];inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
                if inputs[path]!=frame[hash_key]:raise ValueError('Stale model frame support: '+path)
    from build_query_model_sections import build as build_model_sections, UNITS as MODEL_UNITS
    for frame in model_timeline['frames']:
        receipt=read(frame['receipt_file'])
        if {key:receipt['packing'][key]['units'] for key in MODEL_UNITS}!=MODEL_UNITS:
            raise ValueError('Changed model field units: '+frame['receipt_file'])
    collections.update(build_model_sections(model_timeline,model_maps,inputs))
    inputs['analysis/build_query_model_sections.py']=hashlib.sha256((ROOT/'analysis/build_query_model_sections.py').read_bytes()).hexdigest()
    model_owner=next(row for row in objects if row['id']=='current:norwegian-coastal')
    model_owner['model_frame_ids']=[row['id'] for row in collections['model_frames']]
    model_owner['capabilities']['model_frames']=len(collections['model_frames'])
    model_owner['capabilities']['model_samples']=len(collections['model_samples'])
    for name,rows in collections.items():
        if len({r['id'] for r in rows})!=len(rows):raise ValueError('Duplicate ID in '+name)
    from check_norwegian_atlantic_branch_widths import validate as validate_proposed_widths, AUDIT, ACQUISITION, SOURCE
    validate_proposed_widths(read('research/ocean-current-inventory-expansion-candidates.json'))
    read(AUDIT);read(ACQUISITION)
    inputs[SOURCE]=hashlib.sha256((ROOT/SOURCE).read_bytes()).hexdigest()
    inputs['analysis/check_norwegian_atlantic_branch_widths.py']=hashlib.sha256((ROOT/'analysis/check_norwegian_atlantic_branch_widths.py').read_bytes()).hexdigest()
    atlas_paths=['research/ocean-current-inventory-expansion-candidates.json',
                 'research/ocean-current-reference-route-state-join.json',
                 'research/ocean-current-dated-timeline-2025.json',
                 'research/ocean-current-dated-timeline.json',
                 'research/antilles-ab0505-400m-section-diagnostic.json',
                 'research/leeuwin-a101-monthly-plot-extraction.json',
                 'research/kuroshio-ecs-seasonal-width-profile-extraction.json',
                 'research/pacific-necc-oscar-2013-section-diagnostic.json',
                 'research/gulf-stream-section-width-series.json',
                 'research/norkyst-ingoy-2024-section-timeline.json',
                 'research/norkyst-ingoy-2024-map-frames.json',
                 *[r['candidate_file'] for r in routes['candidates']]]
    atlas_receipts={}
    for path in atlas_paths:
        document=read(path)
        atlas_receipts[path]={'source_sha256':inputs[path],'source_json':(ROOT/path).read_bytes().decode('utf-8')}
        if path.endswith('reference-route-state-join.json'):
            for dependency,digest in document['input_sha256'].items():
                read(dependency)
                if inputs[dependency]!=digest:raise ValueError('Stale atlas state join: '+dependency)
        if path.endswith('antilles-ab0505-400m-section-diagnostic.json'):
            read(document['inventory_file'])
            if inputs[document['inventory_file']]!=document['inventory_sha256']:raise ValueError('Stale observed-section inventory')
    return {'schema':'osw.query-bundle.v1','manifest':{'status':'local_editorial_and_canonical_snapshot_not_new_scientific_admission',
            'canonical_release':'v0.1.0','canonical_collections':CANONICAL,
            'eddy_recurrence_receipt':{'source_file':recurrence_path,'source_sha256':inputs[recurrence_path],'source_json':(ROOT/recurrence_path).read_bytes().decode('utf-8')},
            'atlas_receipts':atlas_receipts,
            'movies_receipts':movies_receipts,
            'loop_recorded_receipts':{path:{'source_file':path,'source_sha256':inputs[path],'source_json':(ROOT/path).read_bytes().decode('utf-8')} for path in ['research/loop-current-recorded-date-comparison.json','research/loop-current-recorded-date-sources.json']},
            'taxonomy':taxonomy,'editorial_collections':['eddy_recurrence','taxonomy_links','objects','widths','reference_routes','state_links','states','series','geometry_frames','seasonal_routes','diagnostics','width_samples','route_decisions','flow_networks','flow_network_nodes','flow_network_edges','passage_samples','model_frames','model_samples'],
            'seasons_receipts':{key:{'source_file':path,'source_sha256':inputs[path],'source_json':(ROOT/path).read_bytes().decode('utf-8')} for key,path in [('widths','research/ocean-current-width-inventory.json'),('routes','research/ocean-current-reference-path-candidates.json'),('frames','research/ocean-current-seasonal-route-frames.json'),('directions','research/new-guinea-coastal-current-seasonal-direction-scope-audit.json')]},
            'dashboard_receipt':{'source_file':'research/ocean-motion-dashboard.json','source_sha256':inputs['research/ocean-motion-dashboard.json'],'source_json':(ROOT/'research/ocean-motion-dashboard.json').read_bytes().decode('utf-8')},
            'input_sha256':inputs,'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'state_geometry_runtime':{'shapely':shapely.__version__,'pyproj':__import__('pyproj').__version__},
            'scope':'State joins retain relation kinds; gateways are not containment. Widths retain scope. Published lengths and editorial route lengths are separate collections.'},
            'collections':collections}

def main():
    data=build();OUTPUT.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    print('Built Rust query bundle:',{name:len(rows) for name,rows in data['collections'].items()})

if __name__=='__main__':main()
