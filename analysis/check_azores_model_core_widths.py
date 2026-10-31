"""Bind the seasonal model-core rows to the reviewed primary-source extraction."""
import copy,hashlib,json
from pathlib import Path
from build_azores_climatological_core_width_figure import load,RECORD,RECORD_SHA,ROOT

AUDIT='research/azores-carracedo-2014-model-core-width-scope-audit.json'
PROTOCOL='plans/azores-model-core-width-protocol-v1.md'

def rows():
    doc=load();result=[]
    for i,r in enumerate(doc['measurements']):
        context={'description_kind':'azores_seasonal_model_core','audit_pointer':f'/measurements/{i}',
            'display_aria_label':r['phase_label']+': about '+str(r['approximate_width_km'])+' km regional model core span; width error unknown.',
            'display_caption':r['phase_label']+' · about '+str(r['approximate_width_km'])+' km in the regional inverse-model core at 19.5 W. Model-climatological seasonal extremes are about 240–400 km; whole-current annual physical range and width uncertainty remain unknown.',
            'display_method_note':'Source criterion: velocities greater than 2 cm/s. WOA09 input grid is 1 degree; finer integration is not improved observational resolution. Historical climatologies have mixed support. Depth varies; no fixed-layer width, monthly interpolation or mapped band inferred.',
            'model_support':doc['model_support'],'season_convention':doc['season_convention'],
            'reported_model_core_seasonal_extrema':doc['reported_regional_model_core_seasonal_extrema'],
            'source_record_file':RECORD.relative_to(ROOT).as_posix(),'source_record_sha256':RECORD_SHA,
            'comparison_figure':'figures/azores-carracedo-2014-climatological-core-widths.svg'}
        result.append({**copy.deepcopy(r),'current_id':'azores','name':'Azores Current','status':'editorial_source_extraction_not_canonical',
            'measurement_type':'published_regional_seasonal_summary','width_metric':doc['metric'],'phase_kind':'seasonal_summary',
            'range_interpretation':'Approximate source-reported seasonal core value; no width uncertainty interval supplied.',
            'geographic_scope':doc['geographic_scope'],'section_geometry':None,'section_orientation':'Meridional western WOA-Box section; no exact flow-normal correction inferred.',
            'layer':doc['layer'],'time_convention':'WOA09 mixed historical climatologies in a regional inverse model; source quarter '+r['phase_label']+'. Not an individual occupation or dated current footprint.',
            'boundary_rule':doc['boundary_rule'],'source_url':doc['source_url'],'source_citation':doc['source_citation'],'source_locator':doc['source_locator'],
            'source_retrieved_date':doc['source_retrieved_date'],'source_evidence_kind':'published_inverse_model_climatological_core_summary',
            'extraction_method':'Author-reported values transcribed from original prose; no contour digitization or model reproduction.',
            'whole_current_representative':False,'width_rank_eligible':False,'full_width_inference_eligible':False,'annual_extrema_eligible':False,'seasonal_playback_eligible':False,
            'observed_period':None,'fixed_layer_bounds_m':None,'uncertainty_km':None,
            'remaining_gates':['Recover original model fields and paired boundaries before geometry or scientific reproduction.','Width error and whole-current dimensions remain unknown.','Independent scientific and canonical admission.'],
            'calendar_source_locator':doc['season_convention']['source_locator'],
            'calendar_source_url':doc['season_convention']['source_url'],
            'original_regional_context':context})
    return result

def document():
    return {'schema':'osw.original-seasonal-model-core-scope-audit.v1','current_id':'azores','status':'editorial_source_extraction_not_canonical',
        'source_record_file':RECORD.relative_to(ROOT).as_posix(),'source_record_sha256':RECORD_SHA,'source_record_status_is_review_stage_snapshot':True,
        'protocol_file':PROTOCOL,'protocol_sha256':hashlib.sha256((ROOT/PROTOCOL).read_bytes()).hexdigest(),'measurements':rows()}

def validate_row(row,audit=None):
    raw=(ROOT/AUDIT).read_bytes();saved=json.loads(raw)
    if saved!=document() or audit is not None and audit!=saved:raise ValueError('Changed Azores model-core audit or source binding')
    expected=next((copy.deepcopy(r) for r in saved['measurements'] if r['id']==row['id']),None)
    if expected is None:raise ValueError('Unknown Azores model-core row')
    expected['original_regional_context'].update(audit_file=AUDIT,audit_sha256=hashlib.sha256(raw).hexdigest())
    if row!=expected:raise ValueError('Azores model-core width differs from reviewed source and season convention')

def validate_inventory(inventory):
    identifiers={r['id'] for r in rows()}
    actual=[r for r in inventory['measurements'] if r['id'] in identifiers]
    if len(actual)!=2 or {r['id'] for r in actual}!=identifiers:raise ValueError('Missing or duplicate Azores model-core inventory')
    for row in actual:validate_row(row)

if __name__=='__main__':
    (ROOT/AUDIT).write_bytes((json.dumps(document(),indent=2)+'\n').encode());print(AUDIT)
