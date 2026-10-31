"""Frozen EAC source selection, calendar support and unresolved method scope."""
from collections import Counter
from datetime import datetime,timedelta,timezone
from pathlib import Path
import hashlib,json
import numpy as np
from pyproj import Geod
from acquire_eac_100m_source import ROOT,DIRECTORY,FIELDS,verify,sha

ACQUISITION_SHA='08d720f2ab6fdbe2b8c28e6871e297885b43c75e806b3b907b32026cc89612c2'
REPORT='research/eac-csiro-v23-100m-source-quality.json'
READBACK='plans/eac-fixed-array-distance-readback-v1.md'
READBACK_SHA='7caf13242b17167a21d7da3553f28308f481decb2af9748c6e33ba63b1d2e3aa'


def load(directory=DIRECTORY):
    directory=Path(directory)
    if sha(directory/'acquisition.json')!=ACQUISITION_SHA:
        raise ValueError('Changed frozen EAC subset acquisition')
    receipt,arrays=verify(directory)
    header=json.loads((directory/'source-header.json').read_bytes())
    if arrays['TIME'].shape!=(3770,) or arrays['DEPTH'].shape!=(271,) or any(arrays[k].shape!=(124,) for k in ['LONGITUDE','LATITUDE','BOTTOM_DEPTH']):
        raise ValueError('Changed EAC coordinate support')
    if arrays['DEPTH'][receipt['source_depth_index']]!=100:
        raise ValueError('Changed EAC100m depth index')
    for name in FIELDS:
        expected_unit='m s-1' if name.startswith(('UCUR','VCUR')) else 'degC' if name.startswith('TEMP') else '1'
        if header['datasets'][name]['attributes']['units']!=expected_unit or arrays[name].shape!=(3770,124):
            raise ValueError('Changed EAC field units or shape')
    if header['datasets']['TIME']['attributes']['units']!='days since 1950-01-01 00:00:00 UTC':
        raise ValueError('Changed EAC time convention')
    if header['datasets']['TIME']['attributes']['calendar']!='gregorian':raise ValueError('Changed EAC calendar')
    if any(np.any(~np.isfinite(arrays[k])) for k in ['TIME','DEPTH','LONGITUDE','LATITUDE','BOTTOM_DEPTH']):
        raise ValueError('Nonfinite EAC coordinate')
    if np.any(np.diff(arrays['TIME'])<=0) or np.any(np.diff(arrays['LONGITUDE'])<=0):
        raise ValueError('EAC source ordering changed')
    return receipt,header,arrays


def times(array):
    epoch=datetime(1950,1,1,tzinfo=timezone.utc)
    return [epoch+timedelta(days=float(value)) for value in array]


def iso(date):return date.isoformat().replace('+00:00','Z')


def absent_runs(mask,dates):
    result=[];start=None
    for i,missing in enumerate([*mask,False]):
        if missing and start is None:start=i
        if not missing and start is not None:
            result.append({'first_source_index':start,'last_source_index':i-1,
                           'first_source_time':iso(dates[start]),'last_source_time':iso(dates[i-1]),
                           'source_records':i-start,'reason':'no_finite_retained_paired_velocity_values_not_independent_cause_identification'})
            start=None
    return result


def build(directory=DIRECTORY):
    if sha(ROOT/READBACK)!=READBACK_SHA:raise ValueError('Changed EAC array distance readback protocol')
    receipt,header,arrays=load(directory);dates=times(arrays['TIME'])
    fields={}
    for name in FIELDS:
        data=arrays[name];valid=np.isfinite(data);values=data[valid]
        fields[name]={'units':header['datasets'][name]['attributes']['units'],
            'finite_values':int(valid.sum()),'nan_values':int(np.isnan(data).sum()),
            'positive_infinity_values':int(np.isposinf(data).sum()),'negative_infinity_values':int(np.isneginf(data).sum()),
            'minimum_finite':float(values.min()) if len(values) else None,'maximum_finite':float(values.max()) if len(values) else None,
            'negative_finite_values':int((values<0).sum()),'zero_values':int((values==0).sum()),
            'profiles_without_finite_cells':int((~valid.any(axis=1)).sum()),
            'finite_cells_per_profile':valid.sum(axis=1).tolist(),'finite_times_per_cell':valid.sum(axis=0).tolist(),
            'source_float_bytes_sha256':receipt['source_array_sha256'][name]['sha256']}
    paired=np.isfinite(arrays['UCUR'])&np.isfinite(arrays['VCUR'])
    paired_error=paired&np.isfinite(arrays['UCUR_uncertainty'])&np.isfinite(arrays['VCUR_uncertainty'])
    bottom_positions=np.flatnonzero(arrays['BOTTOM_DEPTH']<=100)
    bottom_support=[{'source_position_index':int(i),'longitude':float(arrays['LONGITUDE'][i]),'latitude':float(arrays['LATITUDE'][i]),
        'bottom_depth_m':float(arrays['BOTTOM_DEPTH'][i]),
        'finite_paired_velocity_records':int(paired[:,i].sum()),
        'zero_paired_velocity_records':int(((arrays['UCUR'][:,i]==0)&(arrays['VCUR'][:,i]==0)).sum()),
        'zero_paired_velocity_uncertainty_records':int(((arrays['UCUR_uncertainty'][:,i]==0)&(arrays['VCUR_uncertainty'][:,i]==0)).sum())} for i in bottom_positions]
    intervals=np.diff(arrays['TIME'])*86400
    months=[]
    for year,month in sorted({(d.year,d.month) for d in dates}):
        indices=[i for i,d in enumerate(dates) if (d.year,d.month)==(year,month)]
        first=datetime(year,month,1,tzinfo=timezone.utc);end=datetime(year+(month==12),month%12+1,1,tzinfo=timezone.utc)
        complete=(dates[indices[0]]-first).total_seconds()<=86400 and (end-dates[indices[-1]]).total_seconds()<=86400
        months.append({'year':year,'month':month,'source_time_indices':indices,'source_records':len(indices),
            'first_source_time':iso(dates[indices[0]]),'last_source_time':iso(dates[indices[-1]]),
            'complete_nominal_calendar_schedule':complete,'complete_schedule_is_complete_data_coverage':False,
            'finite_field_cells':{name:int(np.isfinite(arrays[name][indices]).sum()) for name in FIELDS},
            'paired_velocity_cells':int(paired[indices].sum()),'paired_velocity_and_uncertainty_cells':int(paired_error[indices].sum())})
    points=[list(point) for point in zip(arrays['LONGITUDE'].tolist(),arrays['LATITUDE'].tolist())]
    geod=Geod(ellps='WGS84')
    segment_lengths=[geod.inv(a[0],a[1],b[0],b[1])[2] for a,b in zip(points,points[1:])]
    distances=[0.0,*np.cumsum(segment_lengths).tolist()]
    return {'schema':'osw.eac-fixed-depth-source-quality.v1','status':'processed_source_quality_not_current_dimensions',
        'current_id':'east-australian','entity_id':'current:east-australian','depth_m':100,
        'source_profiles':3770,'source_positions':124,'source_field_values':3770*124*8,
        'source_doi':receipt['dataset_doi'],'source_url':'https://doi.org/10.25919/sfw7-hc46',
        'source_citation':receipt['attribution'],'data_descriptor':receipt['data_descriptor'],
        'source_acquisition_file':'research/source-data/eac-csiro-v23-100m/acquisition.json','source_acquisition_sha256':ACQUISITION_SHA,
        'operator_file':'analysis/check_eac_100m_source.py','operator_sha256':sha(ROOT/'analysis/check_eac_100m_source.py'),
        'calculation_readback_protocol':READBACK,
        'input_sha256':{READBACK:READBACK_SHA,receipt['protocol_file']:receipt['protocol_sha256'],receipt['operator_file']:receipt['operator_sha256'],
            'research/source-data/eac-csiro-v23-100m/acquisition.json':ACQUISITION_SHA,
            'research/source-data/eac-csiro-v23-100m/selected-source.npz':receipt['subset_sha256'],
            'research/source-data/eac-csiro-v23-100m/source-header.json':receipt['source_header_sha256']},
        'fields':fields,'first_source_time':iso(dates[0]),'last_source_time':iso(dates[-1]),
        'source_step_seconds':sorted(set(intervals.tolist())),'source_timestamps_modified':False,
        'complete_source_checksum_verified':True,'second_source_read_all_selected_bits_equal':True,
        'paired_velocity_cells':int(paired.sum()),'paired_velocity_and_uncertainty_cells':int(paired_error.sum()),
        'all_eight_field_finite_masks_identical':all(np.array_equal(np.isfinite(arrays[name]),paired) for name in FIELDS),
        'source_bottom_support':bottom_support,
        'finite_paired_velocity_cells_at_or_below_source_bottom':int(paired[:,bottom_positions].sum()),
        'profiles_without_paired_velocity':int((~paired.any(axis=1)).sum()),
        'missing_paired_velocity_runs':absent_runs(~paired.any(axis=1),dates),
        'monthly_support':months,'calendar_bins':len(months),
        'complete_nominal_calendar_bins':sum(m['complete_nominal_calendar_schedule'] for m in months),
        'fixed_source_geometry':{'role':'fixed_processed_mooring_array_not_current_axis_or_edges','crs':'WGS84',
            'longitude_latitude_points':points,'bottom_depth_m':arrays['BOTTOM_DEPTH'].tolist(),
            'distance_from_first_grid_point_m':[round(v,3) for v in distances],
            'grid_segment_distance_m_range':[round(min(segment_lengths),3),round(max(segment_lengths),3)],
            'source_array_polyline_length_km':round(sum(segment_lengths)/1000,6),'array_length_is_current_length':False,
            'positions_shallower_than_or_at_selected_depth':np.flatnonzero(arrays['BOTTOM_DEPTH']<=100).tolist()},
        'method_scope':{'nominal_output_interval_days':1,'source_low_pass_filter_days':5,
            'daily_records_are_independent_observations':False,'source_is_SOM_filled_and_spatially_mapped':True,
            'per_cell_observed_versus_filled_flags_available_in_selected_product':False,
            'spatial_output_spacing_is_instrument_resolution':False,'original_field_frame':'geographic eastward/northward',
            'OSW_rotation_applied':False,'OSW_missing_value_filling_applied':False,
            'source_zero_velocity_at_bottom_is_independent_observed_current_absence':False,
            'source_zero_uncertainty_is_guaranteed_no_error':False,
            'provider_uncertainty_names_are_a_universal_confidence_convention':False},
        'documentary_disagreements':[
            {'topic':'quality_control_wording','file_header':'Lineage says remove good flags1/2/5.',
             'descriptor':'Methods says retain good or changed flags1/2/5.',
             'processing_code_context':'Pinned precursor clean_data.m removes flags3/4, not1/2/5; this is not an exact final spatial-product build attestation.',
             'status':'source_wording_disagrees_precursor_code_does_not_support_removing_good_flags'},
            {'topic':'final_spatial_mapping','file_header':'Nearest-neighbour interpolation.',
             'descriptor_and_collection_metadata':'Natural-neighbour interpolation.',
             'status':'exact_final_spatial_generation_code_not_bound_to_this_file'},
            {'topic':'versions','collection_metadata_version':23,'provider_data_version':19,'file_citation_version':19,
             'status':'metadata_and_data_versions_distinguished_not_silently_equated'}],
        'processing_repository':{'url':'https://github.com/csiro-oceandata-code/IMOSMooringGridding',
            'inspected_commit':'7e9702b2f66468dcfe6808e5a05e7868424ce4bb',
            'precursor_clean_data_sha256':'ec77d65805860ab3be9181c2af87143222be2aeb5b66242442092998feb698ac',
            'scope':'Individual-mooring stacking/filtering code; not independent reproduction of the final spatial/SOM product.'},
        'whole_current_width_km':None,'annual_width_range_km':None,'geographic_current_edges':None,
        'width_measurement_admitted':False,'width_rank_eligible':False,'seasonal_current_polygon_playback_eligible':False,
        'remaining_gates':['Integrate exact chronological source queries and field visualization without presenting filled cells as direct observations.',
            'Declare current association, vector-axis, boundary, depth and uncertainty interpretation before dimensions.',
            'Assess missing-period and spatial-mapping support; retain physical ranges and current boundaries unresolved until justified.']}


if __name__=='__main__':
    report=build();(ROOT/REPORT).write_bytes((json.dumps(report,separators=(',',':'),allow_nan=False)+'\n').encode())
    print(json.dumps({k:report[k] for k in ['source_profiles','source_positions','source_field_values','calendar_bins','profiles_without_paired_velocity']}))
