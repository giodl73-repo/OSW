"""Paired local component spans from checked shipboard observations, with gaps."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from statistics import median
from pyproj import Geod

ROOT = Path(__file__).resolve().parents[1]
SUBSET = 'research/source-data/noaa-wbts-ab0505-sadcp/regional-samples.json'
INPUT = 'research/antilles-sadcp-layer-span-input.json'
OUTPUT = 'research/antilles-ab0505-sadcp-layer-span-diagnostics.json'
SOURCE_SHA = 'a74954072c841d335238f92c274b313d2e53366787f83e9edb9364b671ac6e43'
SUBSET_SHA = '0b1847f058db75809bff52cfda79e4d747d0628d656b3804334da95de2a1aec9'
INPUT_SHA = '2b53571bf402b1bef65c766084082f974dcdfe21781ebe5f09a35341058ca325'
GEOD = Geod(ellps='WGS84')


def pinned(path, pin):
    raw = (ROOT/path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != pin:
        raise ValueError('Changed predeclared shipboard source/input: '+path)
    return json.loads(raw)


def crossing(bins, peak_index, threshold, step):
    previous = bins[peak_index]
    for i in range(peak_index+step, len(bins) if step>0 else -1, step):
        outer = bins[i]
        if outer['northward_m_s'] is None:
            return {'status':'blocked_by_missing_bin', 'coordinates_lon_lat':None}
        if outer['northward_m_s'] <= threshold:
            ratio = (threshold-previous['northward_m_s'])/(outer['northward_m_s']-previous['northward_m_s'])
            point = [a+ratio*(b-a) for a,b in zip(previous['coordinates_lon_lat'],outer['coordinates_lon_lat'])]
            return {'status':'resolved', 'coordinates_lon_lat':point,
                    'bracket_bin_indices':[previous['bin_index'],outer['bin_index']],
                    'interpolation_fraction':ratio}
        previous = outer
    return {'status':'open_at_domain_edge', 'coordinates_lon_lat':None}


def measure(bins, fraction, gate):
    candidates = [(i,r) for i,r in enumerate(bins) if r['northward_m_s'] is not None
                  and gate[0] <= r['coordinates_lon_lat'][0] <= gate[1]]
    result = {'threshold_fraction':fraction,'threshold_m_s':None,'peak_bin_index':None,
              'peak_northward_m_s':None,'survey_span_km':None,'approximate_span_km':None,
              'shoreward_boundary':{'status':'not_attempted','coordinates_lon_lat':None},
              'offshore_boundary':{'status':'not_attempted','coordinates_lon_lat':None}}
    if not candidates:
        return {**result,'status':'no_valid_pair_in_peak_gate'}
    index,peak = max(candidates,key=lambda pair:pair[1]['northward_m_s'])
    if peak['northward_m_s'] <= 0:
        return {**result,'status':'no_positive_northward_peak'}
    threshold = peak['northward_m_s']*fraction
    shore = crossing(bins,index,threshold,-1)
    offshore = crossing(bins,index,threshold,1)
    result.update(threshold_m_s=threshold,peak_bin_index=index,peak_northward_m_s=peak['northward_m_s'],
                  shoreward_boundary=shore,offshore_boundary=offshore,status='paired_boundary_unresolved')
    if shore['status']=='resolved' and offshore['status']=='resolved':
        width = GEOD.inv(*shore['coordinates_lon_lat'],*offshore['coordinates_lon_lat'])[2]/1000
        result.update(status='paired_component_span_resolved',survey_span_km=width,approximate_span_km=round(width/10)*10)
    return result


def build():
    source = pinned(SUBSET,SUBSET_SHA)
    cfg = pinned(INPUT,INPUT_SHA)
    if source['source_sha256'] != SOURCE_SHA or source['raw_shape'] != [100,6541] or source['conversion_factor'] != 0.01:
        raise ValueError('Changed shipboard source edition/units')
    rows = []
    left,right = cfg['longitude_window_degrees']
    spacing = cfg['spatial_bin_width_degrees']
    for occupation in cfg['occupations']:
        observations = [r for r in source['rows'] if r['occupation_id']==occupation['id']]
        for layer,depth in enumerate(cfg['depths_m']):
            bins = []
            valid = [r for r in observations if r['northward_m_s'][layer] is not None and r['eastward_m_s'][layer] is not None]
            for i in range(round((right-left)/spacing)):
                values = [r for r in valid if math.floor((r['longitude']-left)/spacing)==i]
                bins.append({'bin_index':i,'longitude_bounds':[left+i*spacing,left+(i+1)*spacing],
                             'coordinates_lon_lat':[median(r['longitude'] for r in values),median(r['latitude'] for r in values)] if values else None,
                             'northward_m_s':median(r['northward_m_s'][layer] for r in values) if values else None,
                             'eastward_m_s':median(r['eastward_m_s'][layer] for r in values) if values else None,
                             'paired_observation_count':len(values)})
            cases = [measure(bins,f,cfg['peak_longitude_gate_degrees']) for f in cfg['relative_thresholds']]
            central = cases[1]
            complete = all(c['survey_span_km'] is not None for c in cases)
            rows.append({'id':f'observed-span:antilles:{occupation["id"]}:{depth}m',
                         'current_id':'antilles','entity_id':'current:antilles',
                         'label':occupation['id'].replace('_',' ')+' · '+str(depth)+' m',
                         'occupation_id':occupation['id'],'depth_m':depth,
                         'metric':'northward_component_lobe_survey_span_of_spatial_bin_medians',
                         'source_clock_basis':source['time_basis'],
                         'selection_window':occupation,
                         'valid_sample_period':{'start':min(r['provider_time'] for r in valid),'end':max(r['provider_time'] for r in valid)} if valid else None,
                         'profile_bins':bins,'threshold_cases':cases,
                         'half_peak_span_km':central['approximate_span_km'],
                         'half_peak_status':central['status'],
                         'threshold_span_range_km':[math.floor(min(c['survey_span_km'] for c in cases)/10)*10,math.ceil(max(c['survey_span_km'] for c in cases)/10)*10] if complete else None,
                         'complete_threshold_envelope':complete,
                         'paired_observation_count':len(valid),'populated_bins':sum(b['paired_observation_count']>0 for b in bins),
                         'current_association_verified':False,'flow_normal_width':False,
                         'whole_current_width_km':None,'annual_width_range_km':None,
                         'is_confidence_interval':False,'measurement_uncertainty_km':None,
                         'width_rank_eligible':False,'seasonal_playback_eligible':False,
                         'source_file':OUTPUT,'source_pointer':f'/rows/{len(rows)}'})
    return {'schema':'osw.shipboard-layer-component-spans.v1','current_id':'antilles',
            'status':'derived_local_component_diagnostics_not_current_width_admission',
            'input_file':INPUT,'input_sha256':INPUT_SHA,'subset_file':SUBSET,'subset_sha256':SUBSET_SHA,
            'original_source_sha256':SOURCE_SHA,'original_source_bytes':11415152,
            'native_vertical_bin_m':16,'export_depth_spacing_m':10,'export_grid_is_native_resolution':False,
            'tidal_correction_status':'not_documented_by_source_metadata','current_association_verified':False,
            'whole_current_width_km':None,'annual_width_range_km':None,'width_geometry':None,
            'scope':'Two occupation composites at ten exact exported depth centres. Each bin is the median of paired finite observations; no data gaps bridged. Local northward-component spans, not flow-normal or whole-current widths. Threshold ranges are operator sensitivity, not errors or annual extrema.',
            'counts':{'occupation_profiles':2,'depths_per_occupation':10,'rows':len(rows),
                      'half_peak_resolved':sum(r['half_peak_span_km'] is not None for r in rows),
                      'complete_threshold_envelopes':sum(r['complete_threshold_envelope'] for r in rows),
                      'no_valid_depth_samples':sum(r['paired_observation_count']==0 for r in rows)},'rows':rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify-original', action='store_true')
    args = parser.parse_args()
    if args.verify_original:
        verify_original()
    document = build()
    (ROOT/OUTPUT).write_text(json.dumps(document,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n',encoding='utf8')
    print('Built Antilles shipboard diagnostics:',document['counts'])


def verify_original():
    """Verify every extracted observation against the retained provider MAT."""
    from datetime import datetime
    from scipy.io import loadmat
    import numpy as np
    path = ROOT/'research/source-data/noaa-wbts-ab0505-sadcp/original.mat'
    if hashlib.sha256(path.read_bytes()).hexdigest() != SOURCE_SHA:
        raise ValueError('Changed original shipboard MAT')
    original = loadmat(path, simplify_cells=True)['adp']
    source = pinned(SUBSET,SUBSET_SHA)
    cfg = pinned(INPUT,INPUT_SHA)
    assert original['u'].shape == original['v'].shape == (100,6541)
    assert original['notes']['velocity_units'] == 'cm/s'
    layers = [list(original['depth']).index(d) for d in cfg['depths_m']]
    expected = []
    for index, date in enumerate(original['date_string']):
        stamp = datetime.strptime(str(date),'%d-%b-%Y %H:%M:%S').isoformat()
        lon,lat = float(original['lon'][index]),float(original['lat'][index])
        if not (cfg['longitude_window_degrees'][0] <= lon < cfg['longitude_window_degrees'][1]
                and cfg['latitude_window_degrees'][0] <= lat <= cfg['latitude_window_degrees'][1]):
            continue
        for occupation in cfg['occupations']:
            if occupation['start_date'] <= stamp[:10] < occupation['end_exclusive_date']:
                def values(component):
                    return [float(original[component][layer,index])*0.01 if np.isfinite(original[component][layer,index]) else None for layer in layers]
                expected.append({'source_index_0':index,'occupation_id':occupation['id'],
                    'provider_time':stamp,'longitude':lon,'latitude':lat,
                    'eastward_m_s':values('u'),'northward_m_s':values('v')})
    if expected != source['rows']:
        raise ValueError('Regional extraction differs from original observations')
    print('Verified original shipboard observations:',len(expected))


if __name__ == '__main__': main()
