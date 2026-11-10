"""Append Florida fitted cores, supported reach bounds and relative decay depths."""
import csv, hashlib, io, json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v46 as previous
ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v47.json'
RULES='research/current-depth-rules-v47.json'
OUTPUT='research/current-depth-register-v47.json'
CSV='research/current-depth-register-v47.csv'
MEMBER_OUTPUT='research/current-depth-member-index-v6.json'
MEMBERS='research/current-length-family-conventions-v1.json'
validate_reference=previous.validate_reference
EXPECTED_REFERENCE_SHA256 = {'florida-spray-2023-mean-core': '80a8012108c9bc66fcb195b806d46bae3f78551ee9733af139e4618d789417c2', 'florida-spray-2023-mean-reach-5cms': '012e8ad0bda44a0fdea49f716406213b664baf23ebb8abe639181950dff8c01c', 'florida-spray-2023-mean-half-core': '730e9596f29f838c2b6a1b39f417d2a8627bd491d1a2f0f6f05634e941c012ef', 'florida-spray-2023-phase-01-core': '5a93de4e0ab2d4353d30cb4dbe2526ce6065c4a86a3b8731057c482acf2e77e9', 'florida-spray-2023-phase-01-reach-5cms': 'a9bc38b45d14d0b4eef0e000caadcf7dea10f1af0b26f41238177acc9ccb45cc', 'florida-spray-2023-phase-01-half-core': '160ede22c117dc3522a25133f3edd9606341100363b957e3150b7f67d2a7c1f3', 'florida-spray-2023-phase-02-core': 'c9412015fa8bc1b1901a2b46d81071310df0741a059d703462e324b91e6e77b8', 'florida-spray-2023-phase-02-reach-5cms': '9cc0cd666ca0067f3e4a072189051f2860bef34ac3113c58ad325ed0ddce19a2', 'florida-spray-2023-phase-02-half-core': '046f7170d6ccffa7dfd976a692e963548b51cb03bf8a2c6516ed4d89bbc02c75', 'florida-spray-2023-phase-03-core': '87769a365d08c4a3534542769fd25acb21023d1a17c6bf3c4a734005de52f641', 'florida-spray-2023-phase-03-reach-5cms': 'e4f6bbd9e5224ba3af8436ec707fd5b794dec1442832995b27f36f5f96bb6322', 'florida-spray-2023-phase-03-half-core': '90e6455fd690fa83aadfff085e3aea78f500868f82dee2fa21727d455fd9d010', 'florida-spray-2023-phase-04-core': '02529e9a4bb3acc5b26c84e393737f64d7c78058acdbb8156ebd1f7e6d090b15', 'florida-spray-2023-phase-04-reach-5cms': 'bd402fb443a5c0972b75ce5163b06816e9a074e5310cf3c967d9567f6b8d7971', 'florida-spray-2023-phase-04-half-core': '60aeadcb6dce6684e5471bbe68b6e10bdaf2eedad20fe528dd0ffe9d3d755f47', 'florida-spray-2023-phase-05-core': '8526260a4e5d34eaca0cae3b60a34e423d9bf0a7dc1d65301030a5182975ccd3', 'florida-spray-2023-phase-05-reach-5cms': 'a1c4692d06520f69be7394c34e93af3d8652f610b76dd11d111412d8cc5a6506', 'florida-spray-2023-phase-05-half-core': 'c84016634dc9cd814867875d26e949de5a3967ff54c0860e2250df38ac695740', 'florida-spray-2023-phase-06-core': '8ebb54ee44815cf54dcc1a1796a1bff228209223c3fb242232b830d4027f7062', 'florida-spray-2023-phase-06-reach-5cms': 'abc1fe3dba10d26ac7e8266a505dd8f76a17c13f2a6233494426e53183c13187', 'florida-spray-2023-phase-06-half-core': '5a5e13c4a2a0e2115f74d89e00ffe178404bfb33ba75c91e63cb9ac919385372', 'florida-spray-2023-phase-07-core': '38c9e52644dfcc945ba7e36c7845890d08148f11c17ccbfda8ee65c8236a7935', 'florida-spray-2023-phase-07-reach-5cms': '60e677b59a0697451c546a225ff914e2ae86f6c33bbc938456e0ad4cb669ed6b', 'florida-spray-2023-phase-07-half-core': '31d2706aaae016e8833c0a1674322fe7ea17d37aa03a00c9ca16aee413a37cfe', 'florida-spray-2023-phase-08-core': 'f9a47341e2a54360d5359dd05b8787f038db2fa5d37d9d65c2a1d2d249c635ab', 'florida-spray-2023-phase-08-reach-5cms': '28c8a01c204ab06fde28811c6f688181d6d67e44bf3e5ff84666894a6f0109ff', 'florida-spray-2023-phase-08-half-core': '62c3bac43fcfac04e9643621f4422dce79bb1e928011852bab99ba4cf5abaad8', 'florida-spray-2023-phase-09-core': 'e2c2f9669c4f24a510733d35fbdf04fe211cf91f64fc08a5e9476beaac28ffd6', 'florida-spray-2023-phase-09-reach-5cms': '317cf7a4902d837ce76c863793dd6f9fedcbbfeb37d7f9ece27d00fd3a51e4e5', 'florida-spray-2023-phase-09-half-core': '72519cbbee8ce316da8e456fbb53ef2884f63d0a6534247496f2242d8b5c626a', 'florida-spray-2023-phase-10-core': 'f1a9f4c59068d41174665e8dab95a8617babb12295418fd2309853ce7f396939', 'florida-spray-2023-phase-10-reach-5cms': 'f8189966e681df46d608e0b51248448915b00d6b18c882f7e717ad5822444b17', 'florida-spray-2023-phase-10-half-core': 'fa4f3293eb39ea8afd4e31ae5469e959347136c5e8f14c610060c6bbc6d328a6', 'florida-spray-2023-phase-11-core': '64c146844c38f7df942aead6544c61426e8b7bb9d065eb3d8babd2d42090f645', 'florida-spray-2023-phase-11-reach-5cms': '918d528544eed497eddfa293cfbe36372c64e2393820c2c32faf9b7a8f405852', 'florida-spray-2023-phase-12-core': '40ba082ea2cec8be9137183fd590ec346f99ea7c93325bce105f50efcd47267f', 'florida-spray-2023-phase-12-reach-5cms': '3ea1abb17f590a1fdc1753b5bccd5d089984995a36a4492353b113a6d99b0fb7', 'florida-spray-2023-phase-12-half-core': 'a0878138004c2f90c931fe4d31e8b6d0fbfaed8b156fa158c96b437b8b6f7ab5'}


def validate_context(row,root=ROOT):
    clean={k:v for k,v in row.items() if k not in ['source_file','source_pointer','source_sha256']}
    if hashlib.sha256(json.dumps(clean,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()!=EXPECTED_REFERENCE_SHA256.get(row['id']):raise ValueError('Unreviewed Florida fitted phase, metric role, bound or source support')


def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    extra_inputs=['research/source-data/florida-spray-seasonal-depth-v1/candidate.json', 'research/florida-spray-seasonal-depth-source-facts-v1.json', 'research/florida-spray-seasonal-depth-operator-v1.json', 'research/florida-spray-seasonal-depth-source-review-v1.json', 'analysis/acquire_florida_spray_seasonal_depth_v1.py', 'analysis/derive_eac_connected_layer_thickness_v1.py']
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v46.py',RULES,SOURCE,MEMBERS,MEMBER_OUTPUT]+extra_inputs:
        pins[p]=hashlib.sha256((root/p).read_bytes()).hexdigest()
    source=json.loads((root/SOURCE).read_bytes());rules=json.loads((root/RULES).read_bytes())
    if source['previous_register_sha256']!=pins[previous.OUTPUT]:raise ValueError('Prior pin mismatch')
    for p,digest in source['source_input_sha256'].items():
        if pins[p]!=digest:raise ValueError('Retained source XML changed')
    evidence=list(prior['evidence']);seen={r['id'] for r in evidence};identities={r['entity_id'] for r in prior['records']}
    for i,row in enumerate(source['references']):
        validate_reference(row,identities,rules['metric_types']);validate_context(row,root)
        if row['id'] in seen:raise ValueError('Duplicate source reference')
        seen.add(row['id']);evidence.append(dict(row,source_file=SOURCE,source_pointer=f'/references/{i}',source_sha256=pins[SOURCE]))
    records=[]
    for raw in prior['records']:
        row=dict(raw);row['depth_reference_ids']=[r['id'] for r in evidence if r['entity_id']==row['entity_id']]
        row['status']='scoped_depth_reference' if row['depth_reference_ids'] else 'not_yet_assessed';records.append(row)
    owners=sum(bool(r['depth_reference_ids']) for r in records)
    return {'schema':'osw.current-depth-register.v47','status':'FLORIDA13_CORE13_REACH_AND12_HALF_CORE_DESCRIPTORS',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v47.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v47.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' Thirty-eight Florida descriptors retain thirteen sampled cores, thirteen inclusive supported reach lower bounds and twelve resolved half-core decay depths across thirteen shared fitted profiles. November relative crossing remains censored; absolute lower boundaries and whole-flow thickness are unresolved. These are fitted phases, not independent observed dates or annual extrema.',
            'metadata_correction_file':prior.get('metadata_correction_file'),'metadata_correction_count':prior.get('metadata_correction_count',0),'member_depth_index_file':MEMBER_OUTPUT,'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


NEW_CSV_FIELDS = ['source_definition', 'source_url', 'source_citation', 'source_locator', 'source_case_id', 'source_profile_file', 'source_profile_sha256', 'source_profile_pointer', 'source_product_kind', 'source_dataset_doi', 'source_documented_fit_observation_period', 'source_actual_provider_phase_timestamp_utc', 'source_nominal_phase_calendar_date', 'source_phase_timestamp_is_observation_date', 'source_original_time_coordinate_modified', 'source_nominal_phase_midnight_tolerance_seconds', 'source_is_monthly_average', 'source_annual_harmonics_fit', 'source_selected_lon_lat', 'source_nominal_section_latitude_degrees_north', 'source_longitude_gate_degrees_east', 'source_horizontal_axis_operator', 'source_horizontal_selection_status', 'source_velocity_quantity', 'source_shallowest_fitted_depth_m', 'source_native_fitted_depth_spacing_m', 'source_native_grid_is_independent_observation_spacing', 'source_product_deep_limit_m', 'source_product_limit_is_current_bottom', 'source_sampled_core_at_shallowest_valid_level', 'source_sampled_core_depth_m', 'source_computed_depth_before_display_rounding_m', 'source_velocity_threshold_m_s', 'source_relative_core_fraction', 'source_native_bracketing_depths_m', 'source_depth_interpolation', 'source_metric_role', 'source_primary5cms_lower_boundary_status', 'source_half_core_lower_boundary_status', 'source_fit_support_pointer', 'source_velocity_uncertainty_field', 'source_component_uncertainty_is_depth_error', 'source_current_identity_context', 'lower_bound_operator']

def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns += [p for p in NEW_CSV_FIELDS if p not in columns]
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n',extrasaction='ignore');writer.writeheader()
    for raw in document['evidence']:
        row=dict(raw)
        if row.get('section_sampling_window'):
            row['section_window_start']=row['section_sampling_window']['start'];row['section_window_end']=row['section_sampling_window']['end']
        for key,value in list(row.items()):
            if isinstance(value,(dict,list)):row[key]=json.dumps(value,ensure_ascii=False,separators=(',',':'))
        writer.writerow(row)
    return out.getvalue().encode('utf8')
