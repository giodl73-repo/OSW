"""Bind proposed branch widths to original-source scope, without name admission."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/norwegian-atlantic-branch-width-scope-audit.json'
ACQUISITION='research/source-data/mork-norwegian-2010/acquisition.json'
SOURCE='research/source-data/mork-norwegian-2010/journal-article.pdf'
SOURCE_HASH='cc0c4a94ba785c8bcd0e7b6bbc8e46f86583615909a265e3e5a3d4566e9f2fc3'
PROTOCOL='plans/ocean-current-width-measurement-protocol-v1.md'

def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()

def validate(proposals, audit=None):
    audit=json.loads((ROOT/AUDIT).read_bytes()) if audit is None else audit
    if audit.get('schema')!='osw.proposed-current-width-scope-audit.v1' or audit.get('source_document_file')!=SOURCE or audit.get('source_document_sha256')!=SOURCE_HASH or audit.get('source_document_bytes')!=2577439:
        raise ValueError('Norwegian branch original source identity mismatch')
    source=(ROOT/SOURCE).read_bytes()
    if len(source)!=2577439 or not source.startswith(b'%PDF-') or digest(SOURCE)!=SOURCE_HASH:
        raise ValueError('Changed Norwegian branch original PDF')
    acquisition=json.loads((ROOT/ACQUISITION).read_bytes())
    if (audit.get('acquisition_file'),audit.get('acquisition_sha256'),acquisition.get('source_file'),acquisition.get('sha256'),acquisition.get('license'))!=(ACQUISITION,digest(ACQUISITION),SOURCE,SOURCE_HASH,'CC BY 3.0'):
        raise ValueError('Changed Norwegian branch acquisition or rights receipt')
    if (audit.get('measurement_protocol_file'),audit.get('measurement_protocol_sha256'))!=(PROTOCOL,digest(PROTOCOL)):
        raise ValueError('Stale Norwegian branch width protocol')
    if audit.get('mean_front_width_km') is not None or audit.get('mean_front_width_range_km') is not None:
        raise ValueError('Invented temporal mean frontal width')
    rows=audit['measurements']
    expected={
        'norwegian-atlantic-slope-orvik-2001-regional-width':('norwegian-atlantic-slope',None,[30,50]),
        'norwegian-atlantic-front-orvik-2001-regional-width':('norwegian-atlantic-front',None,[30,50]),
        'norwegian-atlantic-slope-mork-2010-surface-scale':('norwegian-atlantic-slope',50,None)}
    if len(rows)!=3 or {r['id'] for r in rows}!=set(expected):raise ValueError('Incomplete or duplicate Norwegian branch widths')
    for row in rows:
        owner,value,span=expected[row['id']]
        if (row.get('proposed_current_id'),row.get('approximate_width_km'),row.get('width_range_km'))!=(owner,value,span) or 'current_id' in row:
            raise ValueError('Norwegian branch numeric or identity scope mismatch')
        if row.get('status')!='editorial_width_evidence_for_proposed_identity_not_canonical':raise ValueError('Promoted Norwegian branch identity')
        if any(row.get(k) is not None for k in ['observed_period','calendar_months','fixed_layer_bounds_m','section_geometry']):raise ValueError('Invented Norwegian branch dates, layer or geometry')
        if any(row.get(k) is not False for k in ['whole_current_representative','full_width_inference_eligible','rank_eligible','annual_extrema_eligible','seasonal_playback_eligible','is_confidence_interval']):raise ValueError('Promoted Norwegian branch width or seasonal range')
        for k in ['source_url','source_citation','source_locator','source_access','geographic_scope','layer','boundary_rule','temporal_interpretation']:
            if not isinstance(row.get(k),str) or not row[k].strip():raise ValueError('Missing Norwegian branch definition '+k)
        if row.get('unit')!='km' or row.get('source_publication_year')!=(2001 if value is None else 2010):raise ValueError('Changed branch units or publication year')
        context=row['sampling_context']
        if value is None:
            if row.get('measurement_type')!='published_regional_branch_width_summary' or row.get('width_metric')!='author_reported_branch_width' or row.get('range_kind')!='reported_regional_branch_width_span' or row['source_url']!='https://www.sciencedirect.com/science/article/pii/S0967063700000388':raise ValueError('Changed original branch range convention')
            if context!={'mooring_context_months':{'start':'1995-04','end':'1999-02'},'mooring_context_is_width_sampling_interval':False,'mooring_bathymetry_m':[490,990],'bathymetry_is_width_layer':False,'reported_jet_depth_m':400 if owner.endswith('front') else None,'jet_depth_is_width_layer':False}:raise ValueError('Conflated 2001 width sampling or depth')
        else:
            if row.get('measurement_type')!='published_ADT_surface_branch_scale' or row.get('width_metric')!='author_reported_surface_branch_scale' or row.get('range_kind') is not None or row['source_url']!='https://os.copernicus.org/articles/6/901/2010/':raise ValueError('Changed ADT surface scale convention')
            if context!={'ADT_context_months':{'start':'1992-10','end':'2009-07'},'ADT_context_is_exact_width_observation_interval':False,'surface_grid_resolution_km_at_section_approx':17,'figure_2_moving_average_months':3,'width_is_temporal_mean_or_mean_of_widths':False,'core_bathymetry_m_approx':500,'bathymetry_is_width_layer':False,'validation_instrument_depth_m':100,'validation_depth_is_width_layer':False}:raise ValueError('Conflated ADT width averaging or layer')
    entries={r['proposed_id']:r for r in proposals['entries']}
    for owner in ['norwegian-atlantic','norwegian-atlantic-slope','norwegian-atlantic-front']:
        proposal=entries[owner]
        if proposal.get('width_evidence')!=[r for r in rows if r['proposed_current_id']==owner] or proposal.get('width_scope_audit')!={'file':AUDIT,'sha256':digest(AUDIT)}:raise ValueError('Proposed branch width differs from audited extraction')
        if proposal.get('whole_current_width_km') is not None or proposal.get('annual_width_range_km') is not None or proposal.get('rank_eligible') is not False:raise ValueError('Proposed widths promoted to system or annual dimensions')
        if owner=='norwegian-atlantic':
            if proposal.get('component_proposed_ids')!=['norwegian-atlantic-slope','norwegian-atlantic-front']:raise ValueError('Changed proposed system components')
        elif proposal.get('parent_proposed_id')!='norwegian-atlantic':raise ValueError('Changed proposed branch parent')
    return {'records':3,'proposed_branch_owners':2}

if __name__=='__main__':
    print('OK:',validate(json.loads((ROOT/'research/ocean-current-inventory-expansion-candidates.json').read_bytes())))
