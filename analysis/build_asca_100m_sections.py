"""Prepare source profiles and descriptive monthly sections without width inference."""
import calendar
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from check_asca_100m_source import ROOT, DIRECTORY, FIELDS, load, quality

PROTOCOL = 'plans/agulhas-asca-100m-section-aggregation-protocol-v1.md'
RAW = 'research/agulhas-asca-100m-observed-profiles.json'
MONTHLY = 'research/agulhas-asca-100m-monthly-sections.json'
CONTRACT = 'research/agulhas-asca-100m-query-contract.json'


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def iso(seconds):
    return datetime.fromtimestamp(float(seconds), timezone.utc).isoformat().replace('+00:00','Z')


def finite_list(values):
    return [float(v) if np.isfinite(v) else None for v in values]


def statistics(values, valid=None):
    data = values.astype('float64')
    valid = np.isfinite(data) if valid is None else valid
    count = valid.sum(axis=0)
    mean = np.full(data.shape[1], np.nan)
    np.divide(np.where(valid,data,0).sum(axis=0), count, out=mean, where=count>0)
    sd = np.full(data.shape[1], np.nan)
    residual = np.where(valid,data-mean,0)
    np.divide((residual*residual).sum(axis=0), count-1, out=sd, where=count>1)
    np.sqrt(sd,out=sd)
    return {'mean':finite_list(mean),'sample_sd':finite_list(sd),'valid_count':count.tolist()}


def build():
    receipt, coordinates, arrays = load()
    unit = {'temp':'degrees C','sal':'PSU','v':'m/s','U':'m/s'}
    dates = [datetime.fromtimestamp(float(t),timezone.utc) for t in coordinates['time']]
    profiles = []
    for index,(timestamp,date) in enumerate(zip(coordinates['time'],dates)):
        profiles.append({'id':'asca100m:'+date.strftime('%Y%m%dT%H%M%SZ'),
                         'source_time_index':index,'current_id':'agulhas',
                         'observed_at':iso(timestamp),'source_epoch_seconds':float(timestamp),
                         'year':date.year,'month':date.month,'depth_m':100,
                         'fields':{key:finite_list(arrays[key][index]) for key in FIELDS}})
    common = {'status':'source_observational_interpolation_not_dimensional_admission',
              'current_id':'agulhas','entity_id':'current:agulhas',
              'dataset_doi':'10.5281/zenodo.20515068','provider_product_version':2.0,
              'source_acquisition_file':DIRECTORY.relative_to(ROOT).as_posix()+'/acquisition.json',
              'source_acquisition_sha256':digest(DIRECTORY.relative_to(ROOT).as_posix()+'/acquisition.json'),
              'protocol_file':PROTOCOL,'protocol_sha256':digest(PROTOCOL),
              'builder_file':'analysis/build_asca_100m_sections.py',
              'builder_sha256':digest('analysis/build_asca_100m_sections.py'),
              'coordinates':{'distance_m':finite_list(coordinates['dist']),'depth_m':100},
              'field_units':unit,'whole_current_width_km':None,'annual_width_range_km':None,
              'width_rank_eligible':False,'geographic_edges':None,
              'source_float_sha256':{k:receipt['source_bound_arrays'][k]['source_float_bytes_sha256'] for k in FIELDS},
              'complete_file_checksum_verified':False}
    raw = {'schema':'osw.asca-fixed-depth-source-profiles.v1',**common,
           'profile_count':len(profiles),'source_timestamps_modified':False,
           'source_distance_spacing_is_independent_resolution':False,'profiles':profiles}
    clock_tolerance=float(np.max(np.abs(coordinates['time'].astype('float64')-(float(coordinates['time'][0])+np.arange(len(dates))*72000))))
    if clock_tolerance != 64:raise ValueError('Unexpected ASCA source clock precision')
    frames = []
    for year,month in sorted({(d.year,d.month) for d in dates}):
        indices=[i for i,d in enumerate(dates) if (d.year,d.month)==(year,month)]
        start=datetime(year,month,1,tzinfo=timezone.utc)
        end=datetime(year+(month==12),month%12+1,1,tzinfo=timezone.utc)
        complete=((dates[indices[0]]-start).total_seconds()<=72000+clock_tolerance
                  and (end-dates[indices[-1]]).total_seconds()<=72000+clock_tolerance)
        selected={k:arrays[k][indices] for k in FIELDS}
        paired=np.isfinite(selected['v'])&np.isfinite(selected['U'])
        frames.append({'id':f'section:agulhas:asca100m:{year:04d}-{month:02d}',
                       'label':f'Agulhas / ASCA 100 m / {calendar.month_name[month]} {year}'+(' / partial month' if not complete else ''),
                       'entity_id':'current:agulhas','current_id':'agulhas',
                       'record_type':'observational_interpolation_calendar_month_section',
                       'year':year,'month':month,'depth_m':100,'sample_count':len(indices),
                       'first_observed_at':iso(coordinates['time'][indices[0]]),
                       'last_observed_at':iso(coordinates['time'][indices[-1]]),
                       'complete_calendar_time_support':complete,
                       'calendar_time_coverage_clock_tolerance_seconds':clock_tolerance,
                       'source_timestamps_modified':False,
                       'complete_calendar_time_support_is_complete_cell_coverage':False,
                       'source_profile_ids':[profiles[i]['id'] for i in indices],
                       'source_time_indices':indices,
                       'distance_m':finite_list(coordinates['dist']),
                       'field_statistics':{k:statistics(selected[k]) for k in FIELDS},
                       'paired_vector_statistics':{k:statistics(selected[k],paired) for k in ['v','U']},
                       'sample_spread_is_measurement_error':False,
                       'climatology':False,'whole_current_width_km':None,'annual_width_range_km':None,
                       'width_rank_eligible':False,'geographic_edges':None,
                       'source_file':RAW,
                       'source_query':{'document':RAW,'pointer':'/profiles',
                                       'filters':[{'field':'record.year','op':'eq','value':year},
                                                  {'field':'record.month','op':'eq','value':month}],
                                       'sort':{'field':'record.source_time_index','direction':'asc'},'limit':100}})
    return raw,{'schema':'osw.asca-monthly-source-sections.v1',**common,
                'counts':{'source_profiles':931,'frames':len(frames),
                          'complete_calendar_time_bins':sum(f['complete_calendar_time_support'] for f in frames)},
                'scope':'Descriptive year-month sections, with variable-specific and shared vector support. No current-width, seasonal-extrema, density, geographic-edge or climatology inference.',
                'chronological_profile_playback_eligible':True,
                'interpolated_frame_playback_eligible':False,'seasonal_cycle_playback_eligible':False,
                'frames':frames}


def write(path, document):
    (ROOT/path).write_bytes((json.dumps(document,ensure_ascii=True,separators=(',',':'),allow_nan=False)+'\n').encode())


def checked_packets():
    """Verify stored packets against original bytes before a product imports them."""
    raw, monthly = build()
    monthly.update(raw_profile_file=RAW, raw_profile_sha256=digest(RAW))
    for path, expected in [(RAW, raw), (MONTHLY, monthly)]:
        if json.loads((ROOT/path).read_bytes()) != expected:
            raise ValueError('ASCA packet differs from exact source reconstruction: '+path)
    contract = json.loads((ROOT/CONTRACT).read_bytes())
    for file_key, hash_key in [('raw_profile_file','raw_profile_sha256'),
                               ('monthly_section_file','monthly_section_sha256'),
                               ('source_acquisition_file','source_acquisition_sha256'),
                               ('protocol_file','protocol_sha256'),('builder_file','builder_sha256')]:
        if digest(contract[file_key]) != contract[hash_key]:
            raise ValueError('ASCA packet contract dependency changed: '+file_key)
    if contract['counts'] != monthly['counts'] or contract['width_measurement_admitted'] is not False:
        raise ValueError('ASCA packet coverage or dimensional admission changed')
    return raw, monthly, contract


if __name__ == '__main__':
    raw,monthly=build()
    write(RAW,raw)
    monthly.update(raw_profile_file=RAW,raw_profile_sha256=digest(RAW))
    write(MONTHLY,monthly)
    write(CONTRACT,{'schema':'osw.asca-source-section-query-contract.v1',
                    'status':'frozen_source_section_query_contract',
                    'current_id':'agulhas','entity_id':'current:agulhas',
                    'dataset_doi':'10.5281/zenodo.20515068',
                    'source_acquisition_file':monthly['source_acquisition_file'],
                    'source_acquisition_sha256':monthly['source_acquisition_sha256'],
                    'protocol_file':PROTOCOL,'protocol_sha256':digest(PROTOCOL),
                    'builder_file':monthly['builder_file'],'builder_sha256':monthly['builder_sha256'],
                    'raw_profile_file':RAW,'raw_profile_sha256':digest(RAW),
                    'monthly_section_file':MONTHLY,'monthly_section_sha256':digest(MONTHLY),
                    'counts':monthly['counts'],'width_measurement_admitted':False,
                    'chronological_frame_interpolation':False})
    print('Prepared source/monthly sections:',monthly['counts'])
