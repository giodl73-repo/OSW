"""Append partial-strait cores and explicitly non-geometric transport depth diagnostics."""
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v13 as previous

ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v14.json'
RULES='research/current-depth-rules-v14.json'
OUTPUT='research/current-depth-register-v14.json'
CSV='research/current-depth-register-v14.csv'
validate_reference=previous.validate_reference


def validate_context(row):
    if row.get('same_source_width_reference_id') is not None or row.get('independent_observation_count_claimed') is not False:
        raise ValueError('No width join or independent repeat established')
    case=row['source_case_id'];entity=row['entity_id']
    if case=='itf-jiang-2019-makassar-observed-mean':
        if entity!='current:indonesian-throughflow' or row['metric']!='core_depth' or row['approximate_value_m']!=100 or row['evidence_kind']!='published_observational_mean_summary':raise ValueError('Retain observed Makassar mean core')
        if row.get('source_branch')!='makassar_strait' or row.get('branch_section_scope')!='partial_named_branch' or row.get('core_definition')!={'kind':'observed_mean_meridional_velocity_maximum'}:raise ValueError('Makassar core is not all ITF passages')
        if row.get('averaging_years')!=[2004,2012] or row.get('observing_record_span_years')!=[2004,2017] or not row.get('averaging_source_locator') or row.get('reference_dataset')!='INSTANT_observed_comparison_profile':raise ValueError('Figure mean years differ from overall observing span and model products')
    elif case=='egcc-bacon-2002-aug1997':
        if entity!='current:east-greenland-coastal' or row['metric']!='reported_vertical_extent' or row['approximate_value_m']!=100 or row['evidence_kind']!='published_observed_section_summary':raise ValueError('Coastal jet depth is not160m bathymetry or offshore EGC')
        if row.get('section_sampling_month')!='1997-08' or row.get('source_access_scope')!='primary_publisher_abstract':raise ValueError('Retain regional snapshot and abstract access scope')
    elif case=='agulhas-return-lutjeharms-2007-transport':
        if entity!='current:agulhas-return' or row['metric']!='transport_selected_depth_extent' or row['approximate_value_m']!=1500 or row['evidence_kind']!='published_literature_transport_summary':raise ValueError('Integration limit is not full ARC reach')
        if row.get('depth_basis')!='source_transport_integration_limit' or row.get('source_total_vertical_extent_established') is not False or row.get('section_sampling_month') is not None:raise ValueError('Source explicitly does not establish total extent')
    elif case.startswith('agulhas-casal-2009-auce-'):
        expected={'rb':('Richards Bay',-30,1500,'offshore_cyclonic_eddy_excluded'),'ps':('Port Shepstone',-32,3100,'elongated_anticyclonic_northward_and_southward_contributions_included_to_cancel'),'el':('East London',-34,1900,'weak_deep_flows_within_error_bars_excluded'),'pe':('Port Elizabeth',-36,3500,'inshore_shear_edge_eddy_northward_and_southward_contributions_cancelled_deep_undercurrent_excluded')}
        tag=case.removeprefix('agulhas-casal-2009-auce-')
        if tag not in expected:raise ValueError('Unknown AUCE section')
        name,latitude,value,exception=expected[tag]
        if entity!='current:agulhas' or row['metric']!='net_section_transport_zero_depth' or row['approximate_value_m']!=value or row['evidence_kind']!='published_inverse_section_transport_diagnostic':raise ValueError('Section net transport zero is not pointwise flow boundary')
        if row.get('section_name')!=name or row.get('section_latitude_degrees_north')!=latitude:raise ValueError('Do not swap section depths along the route')
        definition={'kind':'zero_of_source_selected_section_integrated_transport_per_unit_depth','current_selection':'southwestward_WBC_with_source_eddy_cancellation_and_counterflow_exclusions','zero_velocity_lateral_boundary_where_no_eddy':True,'section_exception':exception}
        if row.get('diagnostic_definition')!=definition or row.get('depth_basis')!='laterally_integrated_net_transport_zero' or row.get('velocity_reconstruction')!='LADCP_referenced_geostrophy_with_inverse_constraints':raise ValueError('Retain section-specific diagnostic and eddy treatment')
        if row.get('campaign_window')!={'start_month':'2003-02','end_month':'2003-03'} or row.get('window_role')!='whole_cruise_not_exact_cross_section' or row.get('section_sampling_month') is not None:raise ValueError('Retain whole survey month support')
    else:raise ValueError('Unreviewed source case')


def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v13.py',RULES,SOURCE]:
        pins[p]=hashlib.sha256((root/p).read_bytes()).hexdigest()
    source=json.loads((root/SOURCE).read_bytes());rules=json.loads((root/RULES).read_bytes())
    if source['previous_register_sha256']!=pins[previous.OUTPUT]:raise ValueError('Prior pin mismatch')
    for p,digest in source['source_input_sha256'].items():
        if pins[p]!=digest:raise ValueError('Retained source XML changed')
    evidence=list(prior['evidence']);seen={r['id'] for r in evidence};identities={r['entity_id'] for r in prior['records']}
    for i,row in enumerate(source['references']):
        validate_reference(row,identities,rules['metric_types']);validate_context(row)
        if row['id'] in seen:raise ValueError('Duplicate source reference')
        seen.add(row['id']);evidence.append(dict(row,source_file=SOURCE,source_pointer=f'/references/{i}',source_sha256=pins[SOURCE]))
    records=[]
    for raw in prior['records']:
        row=dict(raw);row['depth_reference_ids']=[r['id'] for r in evidence if r['entity_id']==row['entity_id']]
        row['status']='scoped_depth_reference' if row['depth_reference_ids'] else 'not_yet_assessed';records.append(row)
    owners=sum(bool(r['depth_reference_ids']) for r in records)
    return {'schema':'osw.current-depth-register.v14','status':'SCOPED_STRAIT_CORES_AND_SECTION_TRANSPORT_DEPTH_DIAGNOSTICS',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v14.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v14.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' Partial strait cores retain mean-profile years separately from observing-record span. Net section transport zero depths retain section-specific lateral selection and are not pointwise flow boundaries.',
            'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns+=['averaging_years','observing_record_span_years','averaging_source_locator','source_total_vertical_extent_established','diagnostic_definition']
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n',extrasaction='ignore');writer.writeheader()
    for raw in document['evidence']:
        row=dict(raw)
        if row.get('section_sampling_window'):
            row['section_window_start']=row['section_sampling_window']['start'];row['section_window_end']=row['section_sampling_window']['end']
        for key,value in list(row.items()):
            if isinstance(value,(dict,list)):row[key]=json.dumps(value,ensure_ascii=False,separators=(',',':'))
        writer.writerow(row)
    return out.getvalue().encode('utf8')
