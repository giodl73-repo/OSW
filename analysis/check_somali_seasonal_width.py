"""Source-supported months are not monthly widths or annual extrema."""
import copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/somali-schott-2001-premonsoon-width-scope-audit.json'
HASH='6d85965c19dac54ee808603299afc9fb752193cc75d2efb76f2df06768f7f95e'
def digest(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def validate_row(row,audit=None):
    audit=json.loads((ROOT/AUDIT).read_bytes()) if audit is None else audit
    if audit['source_document_sha256']!=HASH or audit['source_document_bytes']!=7144046 or digest(audit['source_document_file'])!=HASH:raise ValueError('Changed Somali original source')
    if digest(audit['acquisition_file'])!=audit['acquisition_sha256'] or digest(audit['protocol_file'])!=audit['protocol_sha256']:raise ValueError('Changed Somali provenance or rules')
    source=audit['measurement']
    if (source['current_id'],source['phase_kind'],source['width_range_km'],source['approximate_width_km'],source['calendar_months'])!=('somali','seasonal_regional_width_range',[50,100],None,[3,4,5]):raise ValueError('Changed Somali seasonal width or calendar')
    if any(source.get(k) is not None for k in ['observed_period','section_geometry','fixed_layer_bounds_m']):raise ValueError('Invented Somali width occupations or edges')
    if any(source.get(k) is not False for k in ['whole_current_representative','width_rank_eligible','annual_extrema_eligible','seasonal_playback_eligible','full_width_inference_eligible','is_confidence_interval']):raise ValueError('Promoted Somali seasonal prose span')
    context=source['seasonal_regional_context']
    if any(context.get(k) is not False for k in ['southern_turnoff_latitude_is_width_edge','undercurrent_is_same_width_layer','Great_Whirl_scale_is_coastal_width','season_months_are_monthly_measurements','boundary_coordinates_extracted']):raise ValueError('Conflated Somali regional support')
    expected=copy.deepcopy(source);expected['seasonal_regional_context'].update(audit_file=AUDIT,audit_sha256=digest(AUDIT))
    if row!=expected:raise ValueError('Somali width differs from pinned seasonal source extraction')
