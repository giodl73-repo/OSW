"""Lossless finite-value JSON view of the pinned EAC source subset."""
import json,math
import numpy as np
from acquire_eac_100m_source import ROOT,FIELDS,sha
from check_eac_100m_source import REPORT,load,build as quality,times,iso

OUTPUT='research/eac-csiro-v23-100m-source-profiles.json'
CONTRACT='research/eac-csiro-v23-100m-source-query-contract.json'
OPERATOR='analysis/build_eac_source_profiles.py'


def document():
    receipt,header,arrays=load();dates=times(arrays['TIME']);rows=[]
    for index,date in enumerate(dates):
        rows.append({'id':'eac100m:'+date.strftime('%Y%m%dT%H%M%SZ'),'source_time_index':index,
            'current_id':'east-australian','depth_m':100,'source_time_utc':iso(date),
            'source_time_days_since_1950':float(arrays['TIME'][index]),'year':date.year,'month':date.month,
            'fields':{name:[None if math.isnan(v) else v for v in arrays[name][index].tolist()] for name in FIELDS}})
    return {'schema':'osw.eac-fixed-depth-source-profiles.v1','status':'processed_SOM_filled_source_not_dimensional_admission',
        'current_id':'east-australian','entity_id':'current:east-australian','dataset_doi':receipt['dataset_doi'],
        'collection_version':23,'data_version':19,'depth_m':100,'source_profiles':3770,'source_positions':124,
        'source_acquisition_file':'research/source-data/eac-csiro-v23-100m/acquisition.json',
        'source_acquisition_sha256':sha(ROOT/'research/source-data/eac-csiro-v23-100m/acquisition.json'),
        'source_subset_file':'research/source-data/eac-csiro-v23-100m/selected-source.npz','source_subset_sha256':receipt['subset_sha256'],
        'serializer_file':OPERATOR,'serializer_sha256':sha(ROOT/OPERATOR),
        'null_encoding':'Source NaNs become JSON null; finite float64 values, including signed zero, round-trip exactly. Original NaN bit payloads remain in the NPZ source.',
        'coordinates':{'longitude_degrees_east':arrays['LONGITUDE'].tolist(),'latitude_degrees_north':arrays['LATITUDE'].tolist(),
            'bottom_depth_m':arrays['BOTTOM_DEPTH'].tolist(),'crs':'WGS84','role':'fixed_source_processing_grid_not_current_edges'},
        'field_attributes':{name:header['datasets'][name]['attributes'] for name in FIELDS},
        'source_time_is_independent_observation_time':False,'source_values_rounded_by_OSW':False,
        'whole_current_width_km':None,'annual_width_range_km':None,'geographic_current_edges':None,
        'width_measurement_admitted':False,'width_rank_eligible':False,'profiles':rows}


def verify_json_against_subset(stored):
    _,_,arrays=load()
    if len(stored['profiles'])!=3770:raise ValueError('Incomplete EAC chronological source view')
    for name in FIELDS:
        decoded=np.array([row['fields'][name] for row in stored['profiles']],dtype='<f8')
        original=arrays[name];finite=np.isfinite(original)
        if not np.array_equal(np.isnan(decoded),np.isnan(original)) or not np.array_equal(decoded[finite].view('u8'),original[finite].view('u8')):
            raise ValueError('EAC JSON lost source bits/missing positions: '+name)
    for i,row in enumerate(stored['profiles']):
        if row['source_time_index']!=i or row['source_time_days_since_1950']!=arrays['TIME'][i]:
            raise ValueError('EAC JSON source ordering/time changed')


def verify():
    expected=document();stored=json.loads((ROOT/OUTPUT).read_bytes())
    if stored!=expected:raise ValueError('EAC chronological JSON differs from frozen source')
    verify_json_against_subset(stored)
    contract=json.loads((ROOT/CONTRACT).read_bytes())
    for path,pin in contract['input_sha256'].items():
        if sha(ROOT/path)!=pin:raise ValueError('Changed EAC source-query contract input: '+path)
    if contract['raw_profile_file']!=OUTPUT or contract['raw_profile_sha256']!=sha(ROOT/OUTPUT):
        raise ValueError('Changed EAC chronological source hash')
    if contract['physical_width_admitted'] is not False or contract['annual_range_admitted'] is not False:
        raise ValueError('Promoted EAC source-query contract')
    return stored,contract


if __name__=='__main__':
    report=json.loads((ROOT/REPORT).read_bytes())
    if report!=quality():raise ValueError('Stale EAC source quality')
    data=document();(ROOT/OUTPUT).write_bytes((json.dumps(data,separators=(',',':'),allow_nan=False)+'\n').encode())
    verify_json_against_subset(json.loads((ROOT/OUTPUT).read_bytes()))
    contract={'schema':'osw.eac-source-query-contract.v1','status':'frozen_processed_source_query_contract',
        'current_id':'east-australian','entity_id':'current:east-australian','raw_profile_file':OUTPUT,'raw_profile_sha256':sha(ROOT/OUTPUT),
        'source_quality_file':REPORT,'source_quality_sha256':sha(ROOT/REPORT),
        'profiles':3770,'positions':124,'depth_m':100,'calendar_bins':124,'profiles_with_paired_velocity':3141,
        'profiles_without_paired_velocity':629,'physical_width_admitted':False,'annual_range_admitted':False,
        'input_sha256':{**report['input_sha256'],REPORT:sha(ROOT/REPORT),OPERATOR:sha(ROOT/OPERATOR),
            report['operator_file']:report['operator_sha256']}}
    (ROOT/CONTRACT).write_bytes((json.dumps(contract,indent=2)+'\n').encode());verify()
    print(json.dumps({'status':'PASS','profiles':len(data['profiles']),'raw_profile_bytes':(ROOT/OUTPUT).stat().st_size,
        'finite_float64_and_null_mask_round_trip_verified':True,'raw_profile_sha256':sha(ROOT/OUTPUT)}))
