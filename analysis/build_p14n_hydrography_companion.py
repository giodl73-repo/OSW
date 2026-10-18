"""Join archived hydrography to nominally nearby observations, retaining ambiguity."""
from pathlib import Path
from datetime import datetime,timedelta,timezone
from collections import Counter
import hashlib,json,math,re
import numpy as np
import xarray as xr
import gsw
from pyproj import Geod
from build_aleutian_p14n_vector_section import verify as verify_vectors
from prepare_p14n_ctd_receipt import verify as verify_public_receipt

ROOT=Path(__file__).resolve().parents[1]
BASE='research/source-data/cchdo-p14n-1993/'
OUTPUT='research/aleutian-p14n-1993-hydrography-correspondence.json'
PROTOCOL='plans/aleutian-p14n-1993-hydrography-join-preflight-v1.md'
CLARIFICATIONS='plans/aleutian-p14n-1993-hydrography-metadata-clarifications-v1.md'
VECTOR='research/aleutian-p14n-1993-observed-vector-section.json'
FROZEN_INPUTS={'research/source-data/cchdo-p14n-1993/cruise-page.html': '98583d9aba689bcf8ddfe7e8079aa5c6218af5e6921c84c2cd5a5aded814d5d4', 'research/source-data/cchdo-p14n-1993/ctd-original.nc': '290d184ab64e0bf07d7dc1a208f34ccd3da765b22176d9392c6b907941234ad2', 'research/source-data/cchdo-p14n-1993/cruise-summary-original.txt': '2533722c212e74dcd58fcd990b6a97e682736cae68356732854786a15d7b82f1', 'research/source-data/cchdo-p14n-1993/cruise-report-original.txt': 'b584d11abb3cab37aeeb2fe0584974672b6b9c2b21050319a392436377f12e78', 'research/source-data/cchdo-p14n-1993/acquisition.json': '6d9d9aad7a5e5fbe222bbdd00ca00b5d415aa0e75ed8a7def8aa19020e8d1b38', 'analysis/acquire_p14n_1993_ctd.py': 'd12583061175b54befa2ccb0c4444ac8baff447421863ddcdf9bed4897d1efed', 'plans/aleutian-p14n-1993-hydrography-join-preflight-v1.md': 'e45b19a1b757747ad8f758a9a9b6bf0ca30406ecf5ecb09ea6d7a74017343d07', 'plans/aleutian-p14n-1993-hydrography-metadata-clarifications-v1.md': '6c2b05b0bd54c05bd5c0848458d4d3efb4bd646c28b7f2302185c65d97e53d29', 'research/aleutian-p14n-1993-observed-vector-section.json': 'c454ed7a8d1de2a83956d74b25dceeb88d2098b2ff339daeb46ea4c9d2415426', 'analysis/prepare_p14n_ctd_receipt.py': '821418c89a6a1285f82329698a318a40b5bb7c33c442967049c8f84b6bedc9c9'}

def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
def encoded(data):return (json.dumps(data,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def text(values):return np.asarray(values).tobytes().decode('utf8').strip('\x00 ')
def finite(value):return float(value) if math.isfinite(float(value)) else None

def summary_events(raw):
 events={}
 for line_number,line in enumerate(raw.splitlines(),1):
  fields=line.split()
  if len(fields)<15 or fields[4]!='ROS':continue
  expo,_,station,cast,_,date,time,event=fields[:8]
  try:
   when=datetime.strptime(date+time.zfill(4),'%m%d%y%H%M').replace(tzinfo=timezone.utc)
   lat=(float(fields[8])+float(fields[9])/60)*(-1 if fields[10]=='S' else 1)
   lon=(float(fields[11])+float(fields[12])/60)*(-1 if fields[13]=='W' else 1)
  except ValueError:continue
  row={'event_code':event,'time_utc':when.isoformat().replace('+00:00','Z'),'latitude_degrees_north':lat,'longitude_degrees_east':lon,'source_line':line_number}
  events.setdefault((expo,str(int(station)),int(cast)),[]).append(row)
 return events

def candidate_pairs(casts,vectors):
 geod=Geod(ellps='WGS84');pairs=[]
 for cast in casts:
  when=datetime.fromisoformat(cast['nominal_bottom_time_utc'])
  for vector in vectors:
   delta=(datetime.fromisoformat(vector['observed_at'])-when).total_seconds()
   _,_,metres=geod.inv(cast['longitude_degrees_east'],cast['latitude_degrees_north'],vector['longitude_degrees_east'],vector['latitude_degrees_north'])
   if abs(delta)<=10800 and metres<=15000:
    pairs.append({'ctd_source_profile_index':cast['source_profile_index'],'ctd_identity':cast['identity'],'adcp_source_time_index':vector['source_time_index'],'adcp_observed_at':vector['observed_at'],'adcp_minus_nominal_bottom_hours':delta/3600,'position_separation_km':metres/1000,'ctd_bottom_metadata_verified':cast['bottom_metadata_verified'],'adcp_layer_mean_available':vector['layer_mean']['eastward_m_s'] is not None,'same_depth_sampling_simultaneity_verified':False,'independent_width_validation':False})
 return pairs

def build():
 if len(FROZEN_INPUTS)!=10:raise ValueError('Missing reviewed hydrography inputs')
 for name,pin in FROZEN_INPUTS.items():
  if digest(name)!=pin:raise ValueError('Changed hydrography input: '+name)
 if gsw.__version__!='3.6.23':raise ValueError('Use the pinned GSW3.6.23 conversion')
 acquisition=verify_public_receipt()
 for row in acquisition['source_files']:
  if FROZEN_INPUTS[row['file']]!=row['sha256'] or (ROOT/row['file']).stat().st_size!=row['byte_count']:raise ValueError('Changed hydrography custody')
 if FROZEN_INPUTS[acquisition['producer_file']]!=acquisition['producer_sha256'] or FROZEN_INPUTS[PROTOCOL]!=acquisition['protocol_sha256']:raise ValueError('Changed acquisition declaration')
 vector=verify_vectors();events=summary_events((ROOT/(BASE+'cruise-summary-original.txt')).read_text(encoding='utf8'))
 casts=[];epoch=datetime(1950,1,1,tzinfo=timezone.utc)
 with xr.open_dataset(ROOT/(BASE+'ctd-original.nc'),decode_cf=False) as data:
  units={'time':'days since 1950-01-01T00:00:00+00:00','latitude':'degree_north','longitude':'degree_east','pressure':'dbar','ctd_temperature':'degC','ctd_salinity':'1'}
  for name,unit in units.items():
   if data[name].attrs['units']!=unit:raise ValueError('Changed units: '+name)
  if data.ctd_temperature.attrs['reference_scale']!='ITS-90' or data.ctd_salinity.attrs['reference_scale']!='PSS-78':raise ValueError('Changed thermodynamic scales')
  if data.pressure.dims!=('N_PROF','N_LEVELS') or data.ctd_temperature.dims!=data.pressure.dims or data.ctd_salinity.dims!=data.pressure.dims:raise ValueError('Changed hydrographic dimensions')
  for name in ['pressure_qc','ctd_temperature_qc','ctd_salinity_qc']:
   meanings=dict(zip(map(int,data[name].attrs['flag_values']),data[name].attrs['flag_meanings'].split()))
   if meanings.get(2)!='acceptable_measurement':raise ValueError('Changed source QC meanings')
  comments=data.attrs['comments'].split('----file_break----')
  if len(comments)!=data.sizes['N_PROF']:raise ValueError('Unaligned original profile headers')
  count=int(data.sizes['N_PROF']);levels=int(data.sizes['N_LEVELS'])
  for index in range(count):
   days=float(data.time.values[index]);lat=float(data.latitude.values[index]);lon=float(data.longitude.values[index])
   if not all(map(math.isfinite,[days,lat,lon])):continue
   when=epoch+timedelta(seconds=round(days*86400))
   if not(datetime(1993,7,7,tzinfo=timezone.utc)<=when<datetime(1993,7,19,tzinfo=timezone.utc) and 40<=lat<=48 and 178<=lon%360<=180):continue
   expo=text(data.expocode.values[index]);station=str(int(text(data.station.values[index])));cast=int(data.cast.values[index]);identity=f'{expo}:{station}:{cast}'
   rows=events.get((expo,station,cast),[]);bottom=[row for row in rows if row['event_code']=='BO']
   event_match=re.search(r'EVENT_CODE\s*:\s*(\S+)',comments[index])
   filename=re.search(r'CTDFILE_NAME\s*:\s*(\d{3})(\d{2})\.ctd',comments[index])
   if not event_match or event_match.group(1)!='BO' or not filename or (int(filename.group(1)),int(filename.group(2)))!=(int(station),cast):raise ValueError('Unmatched BO source profile identity')
   bottom_verified=len(bottom)==1 and abs((datetime.fromisoformat(bottom[0]['time_utc'])-when).total_seconds())<=1
   p=np.asarray(data.pressure.values[index],dtype=float);t=np.asarray(data.ctd_temperature.values[index],dtype=float);s=np.asarray(data.ctd_salinity.values[index],dtype=float)
   pq=np.asarray(data.pressure_qc.values[index],dtype=int);tq=np.asarray(data.ctd_temperature_qc.values[index],dtype=int);sq=np.asarray(data.ctd_salinity_qc.values[index],dtype=int)
   depth=np.full(p.shape,np.nan);mask=np.isfinite(p);depth[mask]=-gsw.z_from_p(p[mask],lat,0,0)
   cells=[]
   for sample in np.where(np.isfinite(depth)&(depth>=0)&(depth<=350))[0]:
    good=bool(pq[sample]==tq[sample]==sq[sample]==2 and all(map(math.isfinite,[p[sample],t[sample],s[sample]])))
    cells.append({'source_level_index':int(sample),'pressure_dbar':finite(p[sample]),'depth_m':finite(depth[sample]),'in_situ_temperature_its90_degC':finite(t[sample]),'practical_salinity_pss78':finite(s[sample]),'pressure_qc':int(pq[sample]),'temperature_qc':int(tq[sample]),'salinity_qc':int(sq[sample]),'joint_acceptable':good})
   casts.append({'source_profile_index':index,'identity':identity,'expocode':expo,'station':station,'cast':cast,'nominal_bottom_time_utc':when.isoformat().replace('+00:00','Z'),'source_time_days_since1950':days,'latitude_degrees_north':lat,'longitude_degrees_east':lon,'source_header_event':'BO','source_summary_events':rows,'bottom_metadata_verified':bottom_verified,'cells':cells,'context_cell_count':len(cells),'joint_acceptable_context_cells':sum(c['joint_acceptable'] for c in cells),'joint_acceptable_100_300m_cells':sum(c['joint_acceptable'] and 100<=c['depth_m']<=300 for c in cells)})
 if not casts:raise ValueError('No hydrography in declared source support')
 for cast in casts:cast['bottom_metadata_verification_scope']='Unique BO timestamp and original profile-header station/cast identity; summary and CF coordinates retained separately.'
 pairs=candidate_pairs(casts,vector['profiles']);cast_ids={r['ctd_source_profile_index'] for r in pairs};vector_ids={r['adcp_source_time_index'] for r in pairs}
 per_cast=Counter(r['ctd_source_profile_index'] for r in pairs);per_vector=Counter(r['adcp_source_time_index'] for r in pairs)
 inputs=dict(FROZEN_INPUTS);inputs.update(vector['input_sha256']);inputs[vector['generator_file']]=vector['generator_sha256']
 return {'velocity_section':vector,'schema':'osw.hydrography-correspondence.v1','status':'observed_metadata_correspondence_pending_named_flow_and_boundary_review','current_id':'aleutian','input_sha256':inputs,'generator_file':Path(__file__).relative_to(ROOT).as_posix(),'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'source_acquisition_file':BASE+'acquisition.json','vector_source_file':VECTOR,'source_profile_count':count,'source_level_dimension':levels,'selected_cast_count':len(casts),'selected_casts_with_verified_bottom_metadata':sum(c['bottom_metadata_verified'] for c in casts),'context_cells':sum(c['context_cell_count'] for c in casts),'joint_acceptable_context_cells':sum(c['joint_acceptable_context_cells'] for c in casts),'primary_layer_bounds_m':[100,300],'display_depth_support_m':[0,350],'depth_conversion':{'formula':'-gsw.z_from_p(pressure_dbar,latitude_degrees_north,0,0)','gsw_version':gsw.__version__,'dynamic_height_argument_m2_s2':0,'sea_surface_geopotential_argument_m2_s2':0,'pressure_is_depth':False},'temperature_kind':'in_situ_ITS90_not_potential_temperature','salinity_kind':'practical_PSS78_not_absolute_salinity','acceptable_source_quality_code':2,'matching_rules':{'maximum_absolute_bottom_time_offset_hours':3,'maximum_position_separation_km':15,'distance_model':'WGS84 geodesic','all_qualifying_pairs_retained':True,'nearest_only_selection_applied':False,'same_depth_time_alignment_verified':False},'candidate_pair_count':len(pairs),'casts_with_candidate_pairs':len(cast_ids),'adcp_profiles_with_candidate_pairs':len(vector_ids),'casts_with_multiple_candidate_adcp_profiles':sum(n>1 for n in per_cast.values()),'adcp_profiles_with_multiple_candidate_casts':sum(n>1 for n in per_vector.values()),'casts_without_candidate_pairs':[c['identity'] for c in casts if c['source_profile_index'] not in cast_ids],'adcp_source_indices_without_candidate_pairs':[r['source_time_index'] for r in vector['profiles'] if r['source_time_index'] not in vector_ids],'casts':casts,'candidate_pairs':pairs,'hydrographic_layer_means_computed':False,'hydrography_interpolated_to_adcp':False,'historical_temperature_correction_application_verified':False,'historical_temperature_correction_reapplied':False,'current_association_verified':False,'independent_width_validation':False,'new_width_record_admitted':False,'whole_current_width_km':None,'annual_width_range_km':None,'width_rank_eligible':False,'physical_edge_geometry_admitted':False,'seasonal_playback_supported':False,'scope_notes':['Nominal CF timestamps are checked against unique BO events in the original summary; BO is cast bottom, not passage through100–300m.','Temporal/spatial candidate correspondence does not establish simultaneity, flow association or a unique cast-to-hour pairing.','All source QC codes and finite raw values are retained. Only jointly acceptable WOCECTD2 samples count as supported water-property cells.','The current cruise page reports a2001temperature-correction issue; later conversion dates do not by themselves establish its resolution. Values are not silently corrected.','The upper-ocean display retains0–350m measured cells. Pressure remains available beside converted depth; no vertical or horizontal interpolation is applied.']}

def verify():
 report=build()
 if (ROOT/OUTPUT).read_bytes()!=encoded(report):raise ValueError('Stale hydrography correspondence')
 return report

if __name__=='__main__':
 report=build();(ROOT/OUTPUT).write_bytes(encoded(report));print(json.dumps({k:report[k] for k in ['selected_cast_count','context_cells','joint_acceptable_context_cells','candidate_pair_count','casts_with_candidate_pairs','adcp_profiles_with_candidate_pairs','selected_casts_with_verified_bottom_metadata']}))
