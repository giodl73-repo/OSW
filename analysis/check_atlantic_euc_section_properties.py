"""Check core-property extraction without promoting it to current width."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PATH='research/atlantic-euc-layer-island-scope-audit.json'
SHA='a1c4b1dfc46247cb9c7da90ea03aa1a240bc987bd26b21c9cdf49f027d457e0b'
ROWS=[('7701','26','Jan 77','January 1977',98,65,False),('7706','7','Jul 77','July 1977',30,50,False),('7802','7','Août 78','August–September 1978',68,65,False),('7902','48','Jan 79','January–February 1979',110,65,False),('7906','8','Avr 79','April 1979',96,55,False),('7910','4','Juin 79','June 1980',64,60,True),('7912','82','Nov 74','October–November 1979',103,70,True),('8001','2','Jan 80','January 1980',110,65,False)]
def validate(audit,require_original=False):
    s=audit['section_properties']
    if audit['current_id']!='atlantic-equatorial-undercurrent' or s['current_id']!=audit['current_id']:raise ValueError('Atlantic section owner mismatch')
    if s['source_document_sha256']!=SHA or s['source_document_bytes']!=1887693:raise ValueError('Changed Atlantic original receipt')
    for key in ['acquisition','protocol']:
        if hashlib.sha256((ROOT/s[key+'_file']).read_bytes()).hexdigest()!=s[key+'_sha256']:raise ValueError('Stale Atlantic section provenance')
    if s['section_longitude_deg_e']!=-4 or s['velocity_reference_depth_m']!=500 or s['transport_context']!={'eastward_speed_threshold_cm_s':20,'depth_bounds_m':[0,200],'is_horizontal_width_definition':False}:raise ValueError('Changed Atlantic section method')
    if any(s[k] is not None for k in ['station_latitude_deg','uncertainty_cm_s','core_depth_uncertainty_m','whole_current_width_km']):raise ValueError('Invented Atlantic section support')
    if any(s[k] is not False for k in ['seasonal_playback_eligible','annual_extrema_eligible','width_inference_eligible','occupied_geometry_eligible']):raise ValueError('Promoted Atlantic section properties')
    expected=[{'id':'atlantic-euc-cap-'+c,'campaign':c,'station_label':station,'table_ii_date_text':d,'table_i_campaign_period':period,'date_conflict':conflict,'resolved_observation_date':None,'maximum_eastward_speed_cm_s':speed,'maximum_speed_depth_m':depth} for c,station,d,period,speed,depth,conflict in ROWS]
    if s['records']!=expected or s['date_conflict_count']!=2:raise ValueError('Changed Atlantic table extraction or resolved a date conflict')
    original=ROOT/s['source_document_file']
    if require_original or original.exists():
        data=original.read_bytes()
        if len(data)!=1887693 or hashlib.sha256(data).hexdigest()!=SHA:raise ValueError('Changed Atlantic local original')
if __name__=='__main__':
    import sys
    validate(json.loads((ROOT/PATH).read_bytes()),'--require-original' in sys.argv)
    print('OK: eight Atlantic core-property records; two unresolved dates; no width/seasonal geometry admission')
