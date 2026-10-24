"""Expose every declared case as a typed query record, without new calculations."""
from pathlib import Path
import copy
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL='plans/current-section-measurement-records-v1.md'
PROVIDERS=[('research/redsox-winter-section3-component-spans.json','layers','RSX1',
    'plans/redsox-section3-width-protocol-v1.md','9f77b4fc986490948c4e74bc9c5c486eeec157e0d47735a0ee66758034e2e22c'),
    ('research/redsox-section3-repeat-surveys.json','summer_layers','RSX2',
    'plans/redsox-section3-repeat-survey-protocol-v1.md','2d866d6d2b98961f86a30891671d4900f6a497df92d413f868d1e458c50985c9')]
ASCA_PROVIDER=('research/agulhas-asca-100m-dated-component-spans.json',
    '59c839aa4ed6363ddfa75af01a2932d73763424c19cb04cd075ee1a9b2ea3e3a')


def build():
    rows=[];pins={}
    for path,key,campaign,protocol,pin in PROVIDERS:
        raw=(ROOT/path).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=pin:raise ValueError('Changed current section provider: '+path)
        doc=json.loads(raw);pins[path]=pin
        for li,layer in enumerate(doc[key]):
            low,high=layer['height_layer_m']
            times=[p['time_utc'] for p in layer['profiles']]
            for ci,case in enumerate(layer['cases']):
                fraction=round(case['fraction']*100)
                offset=round(case['uniform_component_offset_m_s']*1000)
                branch=case['branch']
                rows.append({'id':f'section-measurement:redsox-section3:{campaign.lower()}:{branch}:{low}-{high}:f{fraction}:dq{offset}',
                    'label':f'Red Sea Section 3 / {campaign} / {branch} / {low}-{high} m / f{fraction} / dq{offset} mm/s',
                    'current_id':'red-sea-saline-overflow','entity_id':'current:red-sea-saline-overflow',
                    'campaign':campaign,'branch':branch,'observation_start_utc':min(times),'observation_end_utc':max(times),
                    'height_low_m':low,'height_high_m':high,'metric':'local_section_normal_component_span',
                    'vertical_reference':'height_above_bottom','depth_low_m':None,'depth_high_m':None,
                    'component_frame':'local_section_right_normal','time_support':'non_synoptic_section_survey',
                    'component_span_km':case['span_km'],'boundary_fraction':case['fraction'],
                    'normal_component_velocity_offset_m_s':case['uniform_component_offset_m_s'],
                    'status':case['status'],'saline_outflow_screen':case.get('saline_outflow_screen'),
                    'peak_station':case.get('peak_station'),'is_primary_convention':low==20 and high==60 and fraction==50 and offset==0,
                    'source_file':path,'source_file_sha256':pin,'source_pointer':f'/{key}/{li}/cases/{ci}',
                    'protocol_file':protocol,'source_case':copy.deepcopy(case),
                    'new_width_record_admitted':False,'rank_eligible':False,'current_association_verified':False,
                    'whole_current_width_km':None,'annual_width_range_km':None,'tides_removed':False})
    path,pin=ASCA_PROVIDER;raw=(ROOT/path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=pin:raise ValueError('Changed current section provider: '+path)
    doc=json.loads(raw);pins[path]=pin
    for pi,profile in enumerate(doc['profiles']):
        stamp=profile['source_profile_id'].split(':',1)[1]
        for ci,case in enumerate(profile['cases']):
            fraction=round(case['fraction']*100)
            rows.append({'id':f'section-measurement:asca100m:{stamp}:f{fraction}',
                'label':f"Agulhas ASCA / {profile['observed_at']} / 100 m depth / f{fraction}",
                'current_id':'agulhas','entity_id':'current:agulhas','campaign':'ASCA-2016-2018','branch':None,
                'observation_start_utc':profile['observed_at'],'observation_end_utc':profile['observed_at'],
                'vertical_reference':'depth_below_surface','depth_low_m':100,'depth_high_m':100,
                'height_low_m':None,'height_high_m':None,'metric':'fixed_array_southwestward_v_component_span',
                'component_frame':'source_fixed_array_negative_v','time_support':'filtered_mapped_source_timestamp',
                'component_span_km':case['span_km'],'boundary_fraction':case['fraction'],
                'normal_component_velocity_offset_m_s':None,'status':case['status'],
                'saline_outflow_screen':None,'peak_station':None,'is_primary_convention':case['primary'],
                'source_profile_id':profile['source_profile_id'],'source_time_index':profile['source_time_index'],
                'year':profile['year'],'month':profile['month'],
                'source_profile_pointer':f'/profiles/{pi}',
                'peak_source_index':profile['peak_index'],'peak_distance_m':profile['peak_distance_m'],
                'peak_v_m_s':profile['peak_v_m_s'],'peak_U_m_s':profile['peak_U_m_s'],
                'peak_alignment_indicator_deg':profile['peak_alignment_indicator_deg'],
                'source_file':path,'source_file_sha256':pin,'source_pointer':f'/profiles/{pi}/cases/{ci}',
                'protocol_file':'plans/agulhas-asca-100m-component-span-protocol-v1.md','source_case':copy.deepcopy(case),
                'new_width_record_admitted':False,'rank_eligible':False,'current_association_verified':False,
                'whole_current_width_km':None,'annual_width_range_km':None,'tides_removed':None})
    for path in [PROTOCOL,'analysis/current_section_measurements.py']:
        pins[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    return rows,pins
