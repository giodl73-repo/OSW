"""Reproduce conditional fresh/component boundaries before reference admission."""
import copy,csv,hashlib,io,json
from collections import Counter
import load_current_depth_reference_inventory_v1 as base_loader
import load_current_depth_reference_inventory_v8 as defaults
import load_current_depth_reference_inventory_v9 as prior
from ncc_core_salinity_diagnostic_v1 import diagnose

checked_piece=prior.checked_piece
reference_csv_bytes=prior.reference_csv_bytes
SCHEMA='osw.current-depth-conditional-fresh-component-addendum.v1'
METRIC='derived_conditional_fresh_component_lower_boundary_depth'
CONTEXT='ncc-original-core-hycom2022-practical-salinity35-component10cms'
DIRECTORY='research/source-data/ncc-original-core-salinity-v1/'


def source_context():
    return {'entity_id':'current:norwegian-coastal','source_product':'HYCOM_GOFS3.1_GLBy0.08_expt93.0_ts3z_2022_with_frozen_uv3z_columns','velocity_threshold_m_s':.1,'practical_salinity_exclusive_upper_threshold':35,'support_start':'original_velocity_core_no_reselection','time_operator':'original_quarterly_instantaneous_snapshots_not_annual_envelope','independently_validated_axis':False,'physical_current_bottom_established':False}


def reference(record,index,profile_piece,report_piece):
    original=record['original_audit_record'];classification=record['classification'];lower=classification['lower'];row={k:None for k in defaults.NULL_FIELDS};row.update({k:False for k in defaults.FALSE_FIELDS})
    row.update(id='ncc-fresh-component-'+original['snapshot_time_utc'][:10]+'-'+original['section_id'],entity_id=original['entity_id'],metric=METRIC,approximate_value_m=lower['boundary_depth_m'],lower_bound_m=None,lower_bound_operator=None,unit='m',vertical_datum='local_sea_surface_positive_down',phase_label=original['snapshot_time_utc'],geographic_scope=original['branch_scope'],temporal_scope='Single original 2022 instantaneous model snapshot at retained regional section;not seasonal mean or annual envelope.',source_definition='First native-bracket lower exit from contiguous practical salinity<35PSU AND original northward component>0.1m/s,connected to original velocity core. Conditional water-mass/component descriptor,not physical NCCbottom.',evidence_kind='reproduced_collocated_native_model_conditional_fresh_component_crossing',source_url='https://www.hycom.org/dataserver/gofs-3pt1/analysis',source_citation='GOFS3.1expt93.0ts3z2022native practicalsalinity with exact original uv3z2022profile;Enge2025motivates conditional fresh-water classifier,not HYCOMaxis validation.',source_locator=profile_piece['file']+'#/classification/lower',qualification='Interpolated descriptor retained with exact native bracket. Numerical decimals do not imply physical precision. Practical salinity class and geographic velocity maximum do not uniquely validate NCCidentity. No whole-current depth,physical boundary,paired thickness,annual extrema or volume.',source_context_id=CONTEXT,source_file=profile_piece['file'],source_sha256=profile_piece['sha256'],source_pointer='/classification/lower',source_report_file=report_piece['file'],source_report_sha256=report_piece['sha256'],source_report_pointer='/records/'+str(index),source_native_bracket_m=copy.deepcopy(lower['bracket_m']),source_native_bracket_is_confidence_interval=False,source_native_bracket_is_annual_range=False,source_original_audit_record=copy.deepcopy(original),source_classification=copy.deepcopy(classification),source_contiguous_support_start='original_velocity_core',source_sampled_lon_lat=copy.deepcopy(original['sampled_lon_lat']),source_surface_sample_support=classification['upper']['status']=='surface_sample_supported')
    return row


def read_bundle(addendum,reader):
    report=json.loads(checked_piece(addendum['derived_source_report'],reader));original=json.loads(checked_piece(addendum['original_velocity_audit_report'],reader));profiles=[];sections={}
    if len(report['profiles'])!=5 or [p['file'] for p in report['profiles']]!=['target-'+str(i)+'.json' for i in range(1,6)]:raise ValueError('Exact five source profile files required')
    for piece in report['profiles']:
        profiles.append(json.loads(checked_piece({**piece,'file':DIRECTORY+piece['file']},reader)))
    for record in report['records']:
        r=record['original_audit_record'];raw=reader(r['source_section_file'])
        if hashlib.sha256(raw).hexdigest()!=r['source_section_sha256']:raise ValueError('Original velocity source section changed')
        sections[r['source_section_file']]=json.loads(raw)
    return {'report':report,'original_audit':original,'profiles':profiles,'sections':sections}


def reproduce(bundle):
    report=bundle['report'];original=bundle['original_audit'];profiles=bundle['profiles']
    if report['schema']!='osw.ncc-original-core-salinity-source-report.v1' or report['status']!='ALL_FIVE_TARGETS_RETRIEVED' or report['all_five_targets_preflighted_before_field_reads'] is not True or report['reference_inventory_updated'] is not False or report['new_reference_inventory_rows_admitted']!=0 or report['physical_current_bottom_established'] is not False or report['runtime_changed'] is not False or report['full_goal_complete'] is not False:raise ValueError('Original source audit stage and exact collocation required')
    if report['source_global_attributes'].get('field_type')!='instantaneous' or report['source_variable_attributes'].get('units') not in ['psu','PSU'] or report['source_variable_attributes'].get('standard_name')!='sea_water_salinity':raise ValueError('Original instantaneous practical-salinity metadata required')
    expected=[('/studies/'+str(si)+'/records/'+str(ri),r) for si,s in enumerate(original['studies']) for ri,r in enumerate(s['records']) if r['entity_id']=='current:norwegian-coastal' and r['reach_eligible']]
    if len(expected)!=5 or len(report['records'])!=5 or len(profiles)!=5 or [r['source_audit_pointer'] for r in report['records']]!=[p for p,r in expected]:raise ValueError('All and only five original directly owned NCCcores required')
    for i,(record,profile,(pointer,r)) in enumerate(zip(report['records'],profiles,expected)):
        s=bundle['sections'][r['source_section_file']];column=s['columns'][r['selected_column_index']];ix=column['global_longitude_index'];iy=column['global_latitude_index'];core=r['core_native_index'];z=s['depth_levels_m']
        if record['original_audit_record']!=r or profile['original_audit_record']!=r or profile['source_audit_pointer']!=pointer or record['status']!='SALINITY_PROFILE_RETRIEVED_AND_CONDITIONAL_CORE_CLASSIFIED' or record['profile']!=report['profiles'][i] or profile['schema']!='osw.ncc-original-core-native-salinity-profile.v1':raise ValueError('Exact source audit record/profile linkage required')
        if profile['depth_levels_m']!=z or len(z)!=40 or profile['selected_original_component_m_s']!=column['signed_reference_component_m_s'] or profile['selected_patch_column_index']!=1 or profile['native_latitude_index']!=iy or profile['native_longitude_indices_inclusive']!=[ix-1,ix+1] or profile['native_latitude_degrees_north']!=column['native_source_latitude_degrees_north'] or profile['native_longitudes_degrees_east']!=[s['columns'][r['selected_column_index']+j]['native_source_longitude_degrees_east'] for j in [-1,0,1]]:raise ValueError('Original native depths,component,column and neighbor stencil required')
        if profile['opendap_dataset']!='https://tds.hycom.org/thredds/dodsC/GLBy0.08/expt_93.0/ts3z/2022' or profile['source_time_index']!=s['source_time_index'] or profile['source_returned_timestamp_utc']!=r['snapshot_time_utc'] or s['snapshot_time_utc']!=r['snapshot_time_utc'] or len(profile['practical_salinity_columns'])!=3 or any(len(c)!=40 for c in profile['practical_salinity_columns']):raise ValueError('Exact original source,date and native patch required')
        result=diagnose(z,column['signed_reference_component_m_s'],profile['practical_salinity_columns'][1],core)
        if result!=profile['classification'] or result!=record['classification'] or result['status']!='conditional_fresh_component_core_supported' or result['lower']['status']!='adjacent_native_joint_predicate_crossing' or result['lower']['boundary_depth_m'] is None:raise ValueError('Exact frozen native-field reproduction and resolved crossing required')
    return report['records']


def assemble(*parts):
    result=prior.assemble(*parts[:-1]);known={r['entity_id'] for r in result['records']};seen={r['id'] for r in result['evidence']}
    for a,bundle in parts[-1]:
        records=reproduce(bundle);expected=[reference(r,i,{**bundle['report']['profiles'][i],'file':DIRECTORY+bundle['report']['profiles'][i]['file']},a['derived_source_report']) for i,r in enumerate(records)]
        if a['source_contexts']!={CONTEXT:source_context()} or CONTEXT in result['source_contexts'] or a['evidence']!=expected:raise ValueError('Exact source-owned context and all five reproduced references required')
        for r in expected:
            if r['id'] in seen or r['entity_id'] not in known:raise ValueError('Unique known direct owner required')
            seen.add(r['id'])
        result['source_contexts'][CONTEXT]=source_context();result['evidence'].extend(copy.deepcopy(expected))
    for r in result['records']:r['depth_reference_ids']=[e['id'] for e in result['evidence'] if e['entity_id']==r['entity_id']]
    result['counts']=base_loader.counts_for(result['records'],result['evidence']);result['metric_counts']=dict(sorted(Counter(r['metric'] for r in result['evidence']).items()));return result


def read_parts(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v10':raise ValueError('Known reference inventory v10 required')
    old=[];fresh=[];seen=set()
    for part in manifest['addenda']:
        if part['id'] in seen:raise ValueError('Duplicate addendum identity')
        seen.add(part['id']);a=json.loads(checked_piece(part['json'],reader))
        if a['schema']!=SCHEMA:
            if fresh:raise ValueError('Prior source classes must precede fresh/component descriptors')
            old.append(part);continue
        if a['id']!=part['id'] or a['base_snapshot_sha256']!=manifest['base']['json']['sha256'] or a['runtime_changed'] or a['full_goal_complete']:raise ValueError('Original base/admission identity required')
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));rows=list(incoming);fields=list(incoming.fieldnames)
        if len(rows)!=len(a['evidence']) or set(fields)!={k for r in a['evidence'] for k in r} or any(row!={k:base_loader.cell(raw.get(k)) for k in fields} for raw,row in zip(a['evidence'],rows)):raise ValueError('Every typed source JSON/CSVcell required')
        fresh.append((a,read_bundle(a,reader)))
    return (*prior.read_parts({'schema':'osw.current-depth-reference-inventory.v9','base':manifest['base'],'addenda':old},reader),fresh)


def load_inventory(manifest,reader):
    result=assemble(*read_parts(manifest,reader))
    if result['counts']!=manifest['counts'] or result['metric_counts']!=manifest['metric_counts']:raise ValueError('Reference inventory counts do not reproduce')
    allowed={'schema','status','generator_file','generator_sha256','interpretation','runtime_changed','query_ui_integration_performed','full_goal_complete'}
    if not set(manifest['view_metadata'])<=allowed or any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):raise ValueError('No runtime or completion promotion')
    result.update(copy.deepcopy(manifest['view_metadata']));result['inventory_base_file']=manifest['base']['json']['file'];result['inventory_addendum_files']=[p['json']['file'] for p in manifest['addenda']];result['member_depth_index_scope']='base_only_not_updated_for_addenda';return result


def combined_csv_bytes(manifest,reader):
    load_inventory(manifest,reader);first=csv.DictReader(io.StringIO(checked_piece(manifest['base']['csv'],reader).decode()));columns=list(first.fieldnames);rows=list(first)
    for part in manifest['addenda']:
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));columns.extend(k for k in incoming.fieldnames if k not in columns);rows.extend(list(incoming))
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');writer.writeheader();writer.writerows(rows);return out.getvalue().encode()
