"""An attributed historical width never inherits later ship-section supports."""
import copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/zeehan-cresswell-2000-width-section-scope-audit.json'
SHA='159b1c3e9b57fc9ef726cc7ce8744574b14ccfb61174dcfbb8ffc60fcfef4175'
def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()

def validate_row(row,audit=None):
    audit=json.loads((ROOT/AUDIT).read_bytes()) if audit is None else audit
    if audit['source_document_sha256']!=SHA or audit['source_document_bytes']!=565364 or digest(audit['source_document_file'])!=SHA:
        raise ValueError('Changed Zeehan Cresswell original')
    for key in ['acquisition','protocol']:
        if digest(audit[key+'_file'])!=audit[key+'_sha256']:raise ValueError('Changed Zeehan provenance')
    source=audit['measurement']
    if (source['current_id'],source['approximate_width_km'],source['width_range_km'],source['phase_kind'])!=('zeehan',40,None,'regional_summary'):
        raise ValueError('Changed Zeehan attributed historical width')
    if any(source[k] is not None for k in ['observed_period','calendar_months','section_geometry','fixed_layer_bounds_m','uncertainty_km']):
        raise ValueError('Historical Zeehan width inherited later section support')
    if any(source[k] is not False for k in ['whole_current_representative','width_rank_eligible','full_width_inference_eligible','annual_extrema_eligible','seasonal_playback_eligible','is_confidence_interval']):
        raise ValueError('Promoted Zeehan historical width')
    c=source['original_regional_context']
    exclusions=['underlying_width_methods_reviewed','historical_width_is_1997_section_width','two_occupations_are_annual_extrema','survey_months_are_width_calendar','adcp_depth_coverage_is_fixed_width_layer','mooring_isobaths_are_width_layer','drifter_drogue_is_width_layer','velocity_sign_contours_are_admitted_paired_edges','boundary_coordinates_extracted']
    if any(c[k] is not False for k in exclusions):raise ValueError('Conflated Zeehan historical and survey evidence')
    original=c['original_width_source_access']
    if original['doi']!='10.1071/MF9830155' or original['source_response_sha256'] is not None or original['is_independent_width_record'] is not False:
        raise ValueError('Invented original Zeehan source receipt or duplicate observation')
    if c['method_context']!={'ship_adcp_frequency_khz':150,'ship_depth_coverage_m':300,'lowest_water_column_fraction_excluded':0.15,'mooring_isobaths_m':[100,200],'drifter_drogue_depth_m':15,'is_historical_width_layer':False,'december_flow_extends_beyond_adcp_depth_coverage':True}:
        raise ValueError('Changed Zeehan method coverage')
    comparison=c['section_comparison']
    if comparison['comparison_kind']!='author_qualitative_between_two_occupations' or comparison['width_relation']!='December narrower than March' or comparison['strength_relation']!='December slightly stronger than March' or comparison['numerical_width_ratio'] is not None or any(comparison[k] is not False for k in ['annual_range_eligible','monthly_climatology_eligible','occupied_geometry_eligible']):
        raise ValueError('Promoted Zeehan relative section comparison')
    records=comparison['records']
    if len(records)!=2:raise ValueError('Invented Zeehan section samples')
    for r,month,station,start,end in zip(records,['1997-03','1997-12'],['19:27','41–49'],['1997-03-19','1997-12-01'],['1997-03-27','1997-12-09']):
        if r['observed_month']!=month or r['station_label']!=station or r['width_km'] is not None or r['width_range_km'] is not None or r['whole_voyage_context']!={'start':start,'end':end,'is_exact_section_support':False}:
            raise ValueError('Changed Zeehan section precision or invented width')
    if audit['annual_width_range_km'] is not None or audit['width_geometry'] is not None:raise ValueError('Invented Zeehan annual width or occupied geometry')
    expected=copy.deepcopy(source);expected['original_regional_context'].update(audit_file=AUDIT,audit_sha256=digest(AUDIT))
    if row!=expected:raise ValueError('Zeehan width differs from pinned attributed source')
    return row
