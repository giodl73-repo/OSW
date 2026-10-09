"""Source-reviewed qualitative calendar; no synthetic monthly measurements."""
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PATH='research/zeehan-ridgway-2007-seasonal-scope-audit.json'
PROTOCOL='plans/qualitative-current-calendar-protocol-v1.md'
URL='https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2006JC003898'

def expected():
    claims=[
        {'id':'summer-indication','months':[10,11,12,1,2,3],'kind':'indirect_property_indication','label':'Weak southward flow indicated','summary':'Seasonal property fields suggest weak southward flow; the inshore edge is unresolved.','locator':'Section 6, paragraph 29','reference_state':'seasonal property fields'},
        {'id':'april-transition','months':[4],'kind':'regional_transition','label':'Coastal transition','summary':'Rising western coastal sea level favors southward alongshore flow.','locator':'Section 6, paragraph 30','reference_state':'seasonal coastal steric height'},
        {'id':'may-development','months':[5],'kind':'development','label':'Warm-water flow develops','summary':'Continuous shelf-edge warm-water flow develops in May.','locator':'Section 9, paragraph 45','reference_state':'seasonal warm-water flow'},
        {'id':'winter-peak','months':[6,7],'kind':'qualitative_peak','label':'Reported peak','summary':'Flow intensifies and peaks in June–July; numerical strength is unspecified.','locator':'Section 6, paragraph 30; Section 9, paragraph 45','reference_state':'seasonal boundary flow'},
        {'id':'winter-persistence','months':[5,6,7,8,9],'kind':'qualified_persistence','label':'Persists through at least September','summary':'May development and persistence through at least September do not establish an October disappearance.','locator':'Section 6, paragraph 30; Section 9, paragraph 45','reference_state':'seasonal Zeehan boundary flow','endpoint_qualifier':'at_least','month_assignment':'Continuous May–September interval inferred from development and persistence statements.'},
        {'id':'summer-anomaly','months':[10,11,12,1,2,3,4],'kind':'anomaly_direction','label':'Equatorward shelf-edge anomaly','summary':'The summer anomaly opposes mean southward slope flow; it does not establish reversal of the whole current.','locator':'Section 9, paragraph 47','reference_state':'anomaly relative to mean flow'},
    ]
    return {'schema':'osw.current-qualitative-seasonal-scope-audit.v1','current_id':'zeehan',
        'status':'editorial_primary_html_extraction_pending_independent_review',
        'source':{'author':'K. R. Ridgway','year':2007,'title':'Seasonal circulation around Tasmania: An interface between eastern and western boundary dynamics','doi':'10.1029/2006JC003898','url':URL,'access':'Complete publisher HTML read; original response bytes not pinned. Direct download returned HTTP 403.','reviewed_on':'2026-10-08','original_response_sha256':None,'redistribution_license':None},
        'protocol_file':PROTOCOL,'protocol_sha256':hashlib.sha256((ROOT/PROTOCOL).read_bytes()).hexdigest(),
        'seasonal_calendar':{'time_convention':'Gregorian months; recurring qualitative climatological interpretation, no representative year','claims':claims,
            'months':[{'month':m,'claim_ids':[c['id'] for c in claims if m in c['months']]} for m in range(1,13)],
            'observation_dates':None,'speed_values':None,'width_values':None,'length_values':None,'occupied_geometry':None,
            'annual_dimension_extrema_eligible':False,'dimension_rank_eligible':False,'seasonal_geometry_playback_eligible':False,
            'map_context':{'route_id':'zeehan-reference-path-candidate','source_doi':'10.1029/2003JC001921','role':'existing_static_editorial_reference_path','month_changes_geometry':False}},
        'field_context':{'altimetry_period':'1992-10 through 2006-12','seasonal_operator':'Annual and semiannual least-squares harmonic reconstruction of SLA and SST; Figure 7 combines CMDT mean with reconstructed monthly SLA.','cmdt_mean_period':'1993–1999','sst_mean_figure_2_period':'1993–2004','cars':'Historical in situ profiles; 0.5 degree grid; poor western/southern winter sampling. No common occupation period assigned.','layer':'Surface seasonal fields and shelf/slope interpretation; exact current depth bounds unresolved.','numeric_current_edges':None},
        'excluded_dimension_proxies':['120 km filter cutoff','200 km loess radius','200–220 km interpolation correlation scales','more than 300 km WTL offshore extent','400 km temperature wavefront propagation','200 km offshore net transport location'],
        'unresolved':['Numerical seasonal length and width ranges','Monthly speed amplitudes','Occupied seasonal current geometry','Exact onset and disappearance dates','Subsurface seasonal structure']}

def validate(document):
    if document!=expected():raise ValueError('Zeehan calendar differs from reviewed qualitative scope')
    return document

if __name__=='__main__':
    validate(json.loads((ROOT/PATH).read_bytes()))
    print('PASS: Zeehan qualitative seasonal calendar')
