"""Transcribe two reported model spread scales, without inventing a full width."""
import copy,hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUTPUT='research/pacific-necc-chen-2016-axis-spread-scale-scope-audit.json'
PROTOCOL='plans/pacific-necc-model-axis-spread-protocol-v1.md'
BASE='research/source-data/chen-necc-2016/'
PAPER_SHA='89af9045ed11f2bf18903b405f6beae14fbe83a3c9ca0202d6cb25122b7d381e'
PRODUCER_SHA='825d5ae4dc299099afb0d600453027d43bb1d2163aa79e2bdbebda2863597527'
FROZEN_INPUTS={'research/source-data/chen-necc-2016/journal-article.pdf': '89af9045ed11f2bf18903b405f6beae14fbe83a3c9ca0202d6cb25122b7d381e',
 'research/source-data/chen-necc-2016/acquisition.json': 'b947dd7163ad4301c157505c3a6dd80529c44660227624f7b70510b0c107ab8a',
 'analysis/acquire_pacific_width_papers.py': '825d5ae4dc299099afb0d600453027d43bb1d2163aa79e2bdbebda2863597527',
 'research/source-data/tls/emsign-root-tls-g1-cross.pem': 'e99a766c20aa3d8c86d3e8604c4b5c75bc33b4d0353597d3a4190209bfc41e1e',
 'plans/pacific-necc-model-axis-spread-protocol-v1.md': 'a0c5d34605a561bc30f4a31a1a0d19779ba39581aaae8526f6c01656067581b6'}


def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()


def build():
    if len(FROZEN_INPUTS)!=5:raise ValueError('Missing reviewed model-scale source inputs')
    for name,pin in FROZEN_INPUTS.items():
        if digest(name)!=pin:raise ValueError('Changed reviewed model-scale input: '+name)
    acquisition=json.loads((ROOT/(BASE+'acquisition.json')).read_bytes())
    if (acquisition['sha256'],acquisition['producer_sha256'],acquisition['byte_count'])!=(PAPER_SHA,PRODUCER_SHA,8585355):raise ValueError('Changed source custody')
    operator={'weight':'q = max(integral from 0 to 150m of u dz,0)',
        'axis':'Y = integral(q*y dy) / integral(q dy)',
        'scale':'W = integral(q*abs(y-Y) dy) / integral(q dy)',
        'source_latitude_integration_degrees_north':[0,10],
        'source_zonal_averaging_degrees_east':[135,155],
        'velocity_weight_layer_m':[0,150],'running_mean_months':13,
        'weight_is_vector_speed':False,'scale_is_rms_or_standard_deviation':False,
        'scale_is_paired_edge_distance':False,'scale_is_half_peak_width':False,
        'normalization_at_zero_eastward_transport':'undefined_not_zero',
        'source_figure_8_width_axis_unit':'degrees_latitude',
        'reported_km_values_transcribed_from':'Conclusion, printed p7757 / original PDF page15',
        'osw_latitude_to_kilometre_conversion_applied':False}
    context={'model':'OFES','horizontal_grid_degrees':[0.1,0.1],'vertical_levels':54,
        'forcing':'NCEP-NCAR reanalysis','model_analysis_period_years':[1960,2014],
        'time_support':'Monthly model output; 13-month running mean for the diagnostic figure.',
        'raw_model_fields_acquired':False,'raw_width_series_extracted':False,
        'exact_state_dates_extracted':False,'author_estimator_reproduced':False,
        'source_value_class':'two_approximate_author_reported_change_states_not_series_extrema',
        'independent_observed_width_trend_verified':False,
        'same_as_2013_140w_oscar_component_span':False,
        'full_width_conversion_applied':False,'operator':operator}
    records=[]
    for state,value in [('from',100),('to',130)]:
        records.append({'id':f'pacific-necc-chen-2016-model-axis-spread-{state}',
            'current_id':'pacific-north-equatorial-countercurrent','name':'Pacific North Equatorial Countercurrent',
            'status':'editorial_source_extraction_not_canonical',
            'measurement_type':'published_model_axis_distance_scale_summary',
            'width_metric':'eastward_transport_weighted_mean_absolute_axis_distance',
            'width_metric_label':'Model mean axis-distance scale W',
            'approximate_width_km':value,'width_range_km':None,'uncertainty_km':None,
            'range_kind':'reported_approximate_change_state_not_temporal_extremum',
            'range_interpretation':'Two reported model change states, not series minimum/maximum, an annual range or confidence limits. No width error reported.',
            'geographic_scope':'Western Pacific; 0-10 N meridional integration and 135-155 E zonal averaging. No geographic current edges extracted.',
            'section_geometry':None,'section_orientation':'Meridional distance from a transport-weighted latitude axis; not diagnosed flow-normal paired edges.',
            'layer':'0-150 m velocity-weight integration. Bounds define the operator support, not physical current edges at every depth.',
            'time_convention':'1960-2014 OFES model context; 13-month running-mean diagnostic. Exact dates of the two reported change states are unextracted; not observation dates or annual extrema.',
            'boundary_rule':'No edge threshold. Equation 3 is the eastward-transport-weighted mean absolute distance from the equation 2 axis.',
            'boundary_sides':'not_an_edge_based_metric',
            'source_url':acquisition['source_url'],
            'source_citation':'Chen, X., B. Qiu, Y. Du, S. Chen and Y. Qi (2016), Interannual and interdecadal variability of the North Equatorial Countercurrent in the Western Pacific, doi:10.1002/2016JC012190.',
            'source_locator':'Section 4.2, equations 1-3 (printed pp7748-7749 / PDF 6-7); Figure 8 (PDF 9); conclusion p7757 / PDF 15; model data p7744 / PDF 2.',
            'source_retrieved_date':acquisition['acquired_at_utc'][:10],
            'source_evidence_kind':'published_model_diagnostic_summary_not_direct_current_width_observation',
            'extraction_method':'Approximate kilometre states transcribed from original conclusion; formula and degree-axis figure checked visually. No curve digitization, unit conversion, raw-model reconstruction or full-width conversion.',
            'whole_current_representative':False,'width_rank_eligible':False,'full_width_inference_eligible':False,
            'annual_extrema_eligible':False,'seasonal_playback_eligible':False,'is_confidence_interval':False,
            'phase_kind':'published_model_axis_spread_scale','phase_label':f'Reported change: {state}',
            'observed_period':None,'calendar_months':None,'fixed_layer_bounds_m':[0,150],
            'model_axis_spread_context':{**copy.deepcopy(context),'reported_change_state':state},
            'remaining_gates':['Recover numerical model fields and reproduce the exact estimator before a derived series.',
                'Independent observed widths, physical edges and compatible seasonal sampling remain separate requirements.',
                'Do not pool with the 2013 eastern Pacific OSCAR component diagnostic.']})
    return {'schema':'osw.published-model-axis-spread-scale.v1','status':'editorial_source_extraction_not_canonical',
        'current_id':'pacific-north-equatorial-countercurrent','source_document_file':BASE+'journal-article.pdf',
        'source_document_sha256':PAPER_SHA,'source_document_bytes':8585355,
        'acquisition_file':BASE+'acquisition.json','protocol_file':PROTOCOL,'protocol_sha256':digest(PROTOCOL),
        'generator_file':'analysis/build_necc_chen_spread_scale.py','generator_sha256':digest('analysis/build_necc_chen_spread_scale.py'),
        'input_sha256':FROZEN_INPUTS,'operator':operator,'model_context':context,'measurements':records,
        'reviewed_original_pdf_pages':[2,6,7,9,15],'original_figures_redistributed':False,
        'original_pdf_redistributed':False,'prior_values_viewed_before_declaration':True,
        'whole_current_width_km':None,'annual_width_range_km':None}


def record_rows():
    document=build()
    if json.loads((ROOT/OUTPUT).read_bytes())!=document:raise ValueError('Stale model spread extraction')
    rows=copy.deepcopy(document['measurements']);pin=digest(OUTPUT)
    for i,row in enumerate(rows):
        row['model_axis_spread_context'].update(audit_file=OUTPUT,audit_sha256=pin)
        row.update(source_file=OUTPUT,source_pointer=f'/measurements/{i}')
    return rows


def validate_inventory(inventory):
    expected=record_rows();ids={r['id'] for r in expected}
    actual=[r for r in inventory['measurements'] if r['id'] in ids or r.get('model_axis_spread_context') is not None]
    if actual!=expected:raise ValueError('Missing, duplicate, reassigned or altered published model axis-distance scale')


if __name__=='__main__':
    (ROOT/OUTPUT).write_text(json.dumps(build(),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Extracted two reported model axis-distance states: 100 and 130 km; no full width or annual range')
