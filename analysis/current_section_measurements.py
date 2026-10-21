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
                    'component_span_km':case['span_km'],'boundary_fraction':case['fraction'],
                    'normal_component_velocity_offset_m_s':case['uniform_component_offset_m_s'],
                    'status':case['status'],'saline_outflow_screen':case.get('saline_outflow_screen'),
                    'peak_station':case.get('peak_station'),'is_primary_convention':low==20 and high==60 and fraction==50 and offset==0,
                    'source_file':path,'source_file_sha256':pin,'source_pointer':f'/{key}/{li}/cases/{ci}',
                    'protocol_file':protocol,'source_case':copy.deepcopy(case),
                    'new_width_record_admitted':False,'rank_eligible':False,'current_association_verified':False,
                    'whole_current_width_km':None,'annual_width_range_km':None,'tides_removed':False})
    for path in [PROTOCOL,'analysis/current_section_measurements.py']:
        pins[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    return rows,pins
