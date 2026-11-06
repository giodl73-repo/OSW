"""Preserve source-selected vector-speed and harmonic summaries without synthesizing time series."""
import copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FACTS='research/richardson-walsh-1986-characteristic-velocity-source-facts-v1.json'
PREPARED='research/richardson-walsh-1986-characteristic-velocities-prepared-v1.json'
FIGURE='figures/richardson-walsh-1986-characteristic-velocities-v1.svg'

def encode(v):return (json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def prepare(facts):
    rows=facts['table_rows'];operators=facts['operators']
    if (facts['source']['doi']!='10.1029/JC091iC09p10537' or len(rows)!=10
        or len({r['entity_id'] for r in rows})!=8
        or operators['harmonic_formula_as_printed']!='0.5*sqrt(A_x^2+A_y^2)'
        or operators['harmonic_formula_reinterpreted_as_RMS'] is not False
        or operators['monthly_series_reconstructable_from_table'] is not False
        or operators['seasonal_variation_is_minmax_range'] is not False):
        raise ValueError('Exact characteristic-map and printed-operator scope required')
    expected=[(35,5,4,3),(40,10,10,3),(75,16,14,6),(10,5,5,1),(40,15,12,6),(14,4,3,2),(None,20,15,5),(14,5,2,2),(30,15,10,10),(30,10,6,5)]
    owners=['caribbean','guiana','north-brazil','brazil','guinea','atlantic-north-equatorial','atlantic-north-equatorial-countercurrent','atlantic-south-equatorial','atlantic-south-equatorial','atlantic-south-equatorial']
    out=[]
    for i,(r,values) in enumerate(zip(rows,expected),1):
        if r['entity_id']!='current:'+owners[i-1] or r['source_row']!=i or tuple(r[k] for k in ['mean_speed_cm_s','seasonal_variation_cm_s','annual_harmonic_cm_s','semiannual_harmonic_cm_s'])!=values:
            raise ValueError('Exact source table row required')
        interval=r['mean_speed_interval_cm_s']
        if interval!=([5,10] if i==7 else None):raise ValueError('Characteristic interval changed')
        out.append({'id':f'richardson-walsh1986-table1-characteristic-velocity-{i:02}',
            'entity_id':r['entity_id'],'current_id':r['entity_id'].removeprefix('current:'),
            'measurement_type':'published_author_selected_characteristic_velocity_summary',
            'source_current_label':r['source_current_label'],'source_row':i,
            'characteristic_mean_vector_speed_m_s':None if values[0] is None else values[0]/100,
            'characteristic_mean_vector_speed_interval_m_s':None if interval is None else [x/100 for x in interval],
            'seasonal_velocity_variation_m_s':values[1]/100,
            'annual_harmonic_source_amplitude_m_s':values[2]/100,
            'semiannual_harmonic_source_amplitude_m_s':values[3]/100,
            'source_values_cm_s':copy.deepcopy(r),'quantity_definition':operators['mean_speed_column'],
            'characteristic_value_selection':'author_selected_from_spatially_varying_maps',
            'seasonal_variation_definition':operators['seasonal_variation_formula'],
            'harmonic_amplitude_definition_as_printed':operators['harmonic_formula_as_printed'],
            'harmonic_phase':None,'monthly_velocity_series':None,'annual_speed_extrema':None,
            'confidence_interval':None,'numerical_uncertainty_m_s':None,
            'source_sampling_years':[1875,1976],'dominant_sampling_years':[1920,1940],
            'fixed_depth_m':None,'sampling_geometry':None,'whole_current_representative':False,
            'seasonal_geometry_playback_eligible':False,'monthly_speed_playback_eligible':False,
            'global_speed_rank_eligible':False,'independent_new_observation':False,
            'source_file':FACTS,'source_pointer':f'/table_rows/{i-1}',
            'source_doi':facts['source']['doi'],'source_locator':facts['source']['table_locator'],
            'source_url':facts['source']['url'],'status':'PREPARED_PENDING_EXACT_INSTALLED_DUPLICATE_AUDIT'})
    return {'schema':'osw.richardson-walsh-1986-characteristic-velocities-prepared.v1',
        'status':'ORIGINAL_TABLE_EXTRACTED_AND_OPERATOR_CLASSIFIED_PENDING_INSTALLED_AUDIT',
        'proposed_collection':'current_characteristic_velocities','records':out,'prepared_records':10,
        'prepared_owners':8,'existing_speed_statistics_reclassified':False,'new_independent_observations':0,
        'new_lengths':0,'new_widths':0,'new_annual_dimension_ranges':0,'installed':False,'full_goal_complete':False}

def figure(facts):
    from html import escape
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="770" viewBox="0 0 1120 770" role="img" aria-labelledby="title desc"><title id="title">Characteristic tropical Atlantic velocities</title><desc id="desc">Ten source-table rows in original order. Mean-vector speed and three variation metrics retain separate definitions. No annual extrema, uncertainty or monthly series inferred.</desc><rect width="1120" height="770" fill="#071d2c"/><g font-family="Arial,sans-serif" fill="#e8f3f8"><text x="32" y="42" font-size="25" font-weight="bold">Tropical Atlantic: characteristic velocities</text><text x="32" y="73" font-size="17">Richardson and Walsh (1986), Table 1 · source-selected map values · PREPARED</text>']
    for x,label in [(32,'Source current'),(426,'Mean-vector speed'),(606,'Seasonal variation'),(800,'Annual harmonic'),(975,'Semiannual')]:
        parts.append(f'<text x="{x}" y="121" font-size="16" font-weight="bold">{label}</text>')
    for x in [426,606,800,975]:parts.append(f'<text x="{x}" y="146" font-size="15">cm/s</text>')
    for n,r in enumerate(facts['table_rows']):
        y=184+n*42;parts.append(f'<path d="M32 {y+15}H1088" stroke="#274353"/><text x="32" y="{y}" font-size="17">{escape(r["source_current_label"])}</text>')
        values=[r['mean_speed_cm_s'] if r['mean_speed_cm_s'] is not None else '5–10',r['seasonal_variation_cm_s'],r['annual_harmonic_cm_s'],r['semiannual_harmonic_cm_s']]
        for x,value in zip([426,606,800,975],values):parts.append(f'<text x="{x}" y="{y}" font-size="18">{value}</text>')
    for y,text in [(650,'The authors chose these characteristic values from maps with large geographic variation.'),(680,'Seasonal variation and harmonic amplitudes are separate metrics; they are not annual min/max bounds.'),(710,'Historical ship drifts: 1875–1976, strongly weighted toward 1920–1940. No fixed sampling depth.'),(740,'No pooled-speed equivalence, monthly reconstruction, whole-current dimensions or global speed ranking.')]:
        parts.append(f'<text x="32" y="{y}" font-size="16">{text}</text>')
    parts.append('</g></svg>');return ''.join(parts)

if __name__=='__main__':
    facts=json.loads((ROOT/FACTS).read_bytes());prepared=prepare(facts)
    prepared['input_sha256']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [FACTS,'analysis/richardson_walsh_1986_characteristic_velocities_v1.py']}
    for name,raw in [(PREPARED,encode(prepared)),(FIGURE,figure(facts).encode())]:
        target=ROOT/name
        if target.exists():raise ValueError('New version required')
        target.write_bytes(raw)
    print('Prepared ten source-scoped characteristic velocity summaries; none installed.')
