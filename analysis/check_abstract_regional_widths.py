"""Keep abstract-only regional scales distinct from mapped/seasonal widths."""
import copy
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def validate_row(row, audit=None):
    owner=row['current_id']
    year={'california':2011,'oyashio':2005}.get(owner)
    if year is None:raise ValueError('Unknown abstract regional width owner')
    path=f'research/{owner}-{year}-abstract-width-scope-audit.json'
    raw=(ROOT/path).read_bytes()
    audit=json.loads(raw) if audit is None else audit
    source=audit['measurement']
    expected_scalar,expected_span=(None,[500,800]) if owner=='california' else (100,None)
    if (source['id'],source['current_id'],source['approximate_width_km'],source['width_range_km'])!=(f'{owner}-{year}-abstract-regional-width',owner,expected_scalar,expected_span):raise ValueError('Changed abstract regional width or identity')
    if any(source.get(k) is not None for k in ['observed_period','calendar_months','section_geometry','fixed_layer_bounds_m']):raise ValueError('Invented abstract width sampling or geometry')
    if any(source.get(k) is not False for k in ['whole_current_representative','width_rank_eligible','full_width_inference_eligible','annual_extrema_eligible','seasonal_playback_eligible','is_confidence_interval']):raise ValueError('Promoted abstract regional width')
    if any(source['source_scope_context'].get(k) is not False for k in ['boundary_coordinates_supplied','dataset_period_is_width_sampling_period','full_original_inspected','velocity_context_is_boundary_cutoff']):raise ValueError('Invented abstract source support')
    expected=copy.deepcopy(source)
    for key in ['source_scope_context']+(['regional_scalar_context'] if owner=='oyashio' else []):
        expected[key].update(audit_file=path,audit_sha256=hashlib.sha256(raw).hexdigest())
    if row!=expected:raise ValueError('Abstract regional width differs from source audit')
