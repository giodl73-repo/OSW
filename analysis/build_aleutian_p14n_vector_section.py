"""Retain an observed Subarctic-region section without inventing current edges."""
from scientific_readback import canonicalize
import hashlib,json,math
from datetime import datetime,timedelta,timezone
from pathlib import Path
import numpy as np
import xarray as xr
from pyproj import Geod

ROOT=Path(__file__).resolve().parents[1]
BASE='research/source-data/jasadcp-p14n-1993/'
OUTPUT='research/aleutian-p14n-1993-observed-vector-section.json'
PROTOCOL='plans/aleutian-p14n-1993-vector-section-preflight-v1.md'
FROZEN_INPUTS={'research/source-data/jasadcp-p14n-1993/gateway.html': 'e2ada40a24ef2674d7c3c243936648f0b8cc7fad56682fb95afdbe6367b89f2b', 'research/source-data/jasadcp-p14n-1993/cruise-metadata.bft': '7eed121cf793101fce0d89f41a9608b1e14e00949b93d50364c3dee3ab5e9ca8', 'research/source-data/jasadcp-p14n-1993/format-template.txt': 'b3cabab21fa7e9fc8e2132cbd5284d54727994fe0adc2c03d7415e0773086a7c', 'research/source-data/jasadcp-p14n-1993/hourly-vector-original.nc': '5dd5e1dbaa52630294fa905f35c7262cb6522d4c82bcf4daf4f736459af40132', 'research/source-data/jasadcp-p14n-1993/acquisition.json': '1aac36510a4857b02f3adcebaf47fc0d97366b33e48943ae6fc16212ac921ae3', 'analysis/acquire_jasadcp_p14n_1993.py': 'a17c2fa206115a230425d686b7102b6fb386520c3e4f5df5d402be6a759e1c3b', 'plans/aleutian-p14n-1993-vector-section-preflight-v1.md': '6cdf46f01ed0487f78c1b5ca0b3205f97b350f4671b2c4f9da197f519eb47703'}

def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def encoded(data):return (json.dumps(data,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()

def valid_values(variable):
 values=np.asarray(variable.values,dtype=float)
 valid=np.isfinite(values)
 for key in ['_FillValue','missing_value']:
  if key in variable.attrs:valid&=values!=variable.attrs[key]
 if 'valid_min' in variable.attrs:valid&=values>=variable.attrs['valid_min']
 if 'valid_max' in variable.attrs:valid&=values<=variable.attrs['valid_max']
 return values,valid

def layer_mean(depth,u,v):
 """Joint vector support with centre-cell thickness clipped to [100,300] m."""
 depth=np.asarray(depth,dtype=float);u=np.asarray(u,dtype=float);v=np.asarray(v,dtype=float)
 if depth.ndim!=1 or len(depth)<2 or not np.all(np.isfinite(depth)) or np.any(np.diff(depth)<=0):raise ValueError('Invalid or unordered depths')
 if u.shape!=depth.shape or v.shape!=depth.shape:raise ValueError('Unpaired vector shape')
 edges=np.r_[depth[0]-(depth[1]-depth[0])/2,(depth[:-1]+depth[1:])/2,depth[-1]+(depth[-1]-depth[-2])/2]
 weights=np.maximum(0,np.minimum(edges[1:],300)-np.maximum(edges[:-1],100))
 if not np.isclose(sum(weights),200):raise ValueError('Source does not cover requested layer')
 valid=np.isfinite(u)&np.isfinite(v)&(weights>0)
 coverage=float(weights[valid].sum())
 if coverage<160:return {'joint_valid_thickness_m':coverage,'eastward_m_s':None,'northward_m_s':None}
 return {'joint_valid_thickness_m':coverage,'eastward_m_s':float(np.dot(weights[valid],u[valid])/coverage),'northward_m_s':float(np.dot(weights[valid],v[valid])/coverage)}

def build():
 if len(FROZEN_INPUTS)!=7:raise ValueError('Missing original source or declaration pins')
 for path,pin in FROZEN_INPUTS.items():
  if digest(path)!=pin:raise ValueError('Changed observed-section dependency: '+path)
 receipt=json.loads((ROOT/(BASE+'acquisition.json')).read_bytes())
 for row in receipt['source_files']:
  if FROZEN_INPUTS[row['file']]!=row['sha256'] or (ROOT/row['file']).stat().st_size!=row['byte_count']:raise ValueError('Changed acquisition binding')
 if receipt['producer_sha256']!=FROZEN_INPUTS[receipt['producer_file']]:raise ValueError('Changed acquisition producer')
 with xr.open_dataset(ROOT/(BASE+'hourly-vector-original.nc'),decode_cf=False) as data:
  if (data.attrs['DAC_ID'],data.attrs['CRUISE_NAME'],data.attrs['EXPOCODE'].strip())!=('00016','TT9306','325023_1'):raise ValueError('Wrong cruise identity')
  for name,unit in [('u','meters per second'),('v','meters per second'),('depth','meters'),('latitude','degrees_N'),('longitude','degrees_E'),('time','minutes since 1980-1-1 0:0:0')]:
   if data[name].attrs['units']!=unit:raise ValueError('Changed units: '+name)
  if data.u.dims!=('time','depth') or data.v.dims!=data.u.dims:raise ValueError('Changed paired vector dimensions')
  depth=np.asarray(data.depth.values,dtype=float)
  u,umask=valid_values(data.u);v,vmask=valid_values(data.v)
  lat,latmask=valid_values(data.latitude);lon,lonmask=valid_values(data.longitude)
  minutes=np.asarray(data.time.values,dtype=int)
  if np.any(np.diff(minutes)<=0):raise ValueError('Unordered source times')
  epoch=datetime(1980,1,1,tzinfo=timezone.utc)
  times=[epoch+timedelta(minutes=int(t)) for t in minutes]
  indices=[i for i,t in enumerate(times) if datetime(1993,7,7,tzinfo=timezone.utc)<=t<datetime(1993,7,19,tzinfo=timezone.utc) and latmask[i] and lonmask[i] and 40<=lat[i]<=48 and 178<=lon[i]%360<=180]
  if not indices:raise ValueError('No declared section samples')
  profiles=[]
  for index in indices:
   valid_u=np.where(umask[index],u[index],np.nan);valid_v=np.where(vmask[index],v[index],np.nan)
   layer=layer_mean(depth,valid_u,valid_v)
   cells=[{'depth_m':float(z),'eastward_m_s':float(uu) if ok_u else None,'northward_m_s':float(vv) if ok_v else None,'joint_valid':bool(ok_u and ok_v)} for z,uu,vv,ok_u,ok_v in zip(depth,u[index],v[index],umask[index],vmask[index])]
   profiles.append({'source_time_index':index,'observed_at':times[index].isoformat().replace('+00:00','Z'),'latitude_degrees_north':float(lat[index]),'longitude_degrees_east':float(lon[index]),'profile':cells,'layer_mean':layer})
 native_gaps=[int(minutes[b]-minutes[a]) for a,b in zip(indices,indices[1:])]
 geod=Geod(ellps='WGS84');legs=[]
 for a,b,gap in zip(profiles,profiles[1:],native_gaps):
  heading,_,distance=geod.inv(a['longitude_degrees_east'],a['latitude_degrees_north'],b['longitude_degrees_east'],b['latitude_degrees_north'])
  legs.append({'from_source_time_index':a['source_time_index'],'to_source_time_index':b['source_time_index'],'time_gap_minutes':gap,'straight_distance_between_hourly_mean_positions_km':distance/1000,'bearing_between_hourly_mean_positions_degrees_true':heading%360 if distance>0 else None,'gap_over90minutes':gap>90,'bearing_is_flow_direction':False})
 north_steps=sum(b['latitude_degrees_north']>a['latitude_degrees_north'] for a,b in zip(profiles,profiles[1:]))
 branches=[]
 for label,low,high in [('southern',41,43),('northern',44,46)]:
  rows=[r for r in profiles if low<=r['latitude_degrees_north']<=high]
  branches.append({'branch':label,'latitude_search_window_degrees_north':[low,high],'window_is_measured_boundary':False,'samples':len(rows),'joint_layer_means':sum(r['layer_mean']['eastward_m_s'] is not None for r in rows),'current_association_verified':False,'physical_width_km':None})
 return canonicalize({'track_legs':legs,'track_geometry_role':'WGS84 straight segments between hourly mean source positions; not sailed distance, a current axis, flow orientation or physical current edges. Bearings near stationary positions are unstable.','maximum_position_spacing_km':max(r['straight_distance_between_hourly_mean_positions_km'] for r in legs),'median_position_spacing_km':float(np.median([r['straight_distance_between_hourly_mean_positions_km'] for r in legs])),'schema':'osw.observed-vector-section.v1','status':'observed_section_pending_named_current_boundary_review','current_id':'aleutian','label':'Aleutian / Subarctic region: July1993 observed vector section','source':'JASADCP SAC_ID00016 / TT9306 / P14N / 325023_1','source_url':receipt['source_files'][-1]['source_url'],'acquisition_file':BASE+'acquisition.json','input_sha256':dict(FROZEN_INPUTS),'generator_file':Path(__file__).relative_to(ROOT).as_posix(),'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'protocol_file':PROTOCOL,'provider_units':'meters per second','velocity_frame':'earth coordinates: eastward u and northward v','source_product':'hourly reduced product at10m intervals; not native5minute/4m ensembles','source_time_count':len(minutes),'source_depth_count':len(depth),'retained_time_count':len(profiles),'retained_vector_positions':len(profiles)*len(depth),'joint_valid_vector_positions':sum(cell['joint_valid'] for row in profiles for cell in row['profile']),'layer_bounds_m':[100,300],'minimum_layer_joint_coverage_fraction':0.8,'layer_weighting':'Midpoint cell thickness, clipped at100and300m; jointly valid u/v; coverage<160m produces null means. No vertical interpolation.','layer_means_with_complete_required_support':sum(row['layer_mean']['eastward_m_s'] is not None for row in profiles),'first_observed_at':profiles[0]['observed_at'],'last_observed_at':profiles[-1]['observed_at'],'maximum_adjacent_time_gap_minutes':max(native_gaps),'gaps_over90minutes':sum(gap>90 for gap in native_gaps),'northward_latitude_steps':int(north_steps),'monotone_crossing_assumed':False,'gap_interpolation_applied':False,'observed_track_reordered_by_latitude':False,'branches':branches,'profiles':profiles,'new_width_record_admitted':False,'current_association_verified':False,'cold_water_companion_acquired':False,'whole_current_width_km':None,'annual_width_range_km':None,'width_rank_eligible':False,'annual_extrema_eligible':False,'physical_edge_geometry_admitted':False,'seasonal_playback_supported':False,'source_processing_cautions':['GPS selective availability and heading corrections described in provider metadata; velocities already processed by the University of Hawaii.','Provider metadata record CTD wire interference editing and missing bins. The hourly product has no per-cell native editing history; nulls and joint support are retained.','100–300m follows the published regional comparison, not an assumed depth-independent current width.','Track includes small northward steps and a two-hour gap. Preserve acquisition order; do not silently form a single monotone width crossing.','Northern and southern branch windows follow Chen and Firing(2006), section3 paragraph7. Windows are association context, not detected edges.'],'citation':'University of Hawaii / NOAA JASADCP, SAC_ID00016, Gunnar Roden, processed E.Kestenare and E.Firing. Chen,S.,and E.Firing(2006), JGR111,C03001, doi:10.1029/2005JC003064.'})

def verify():
 expected=build()
 if (ROOT/OUTPUT).read_bytes()!=encoded(expected):raise ValueError('Stale observed vector section')
 return expected

if __name__=='__main__':
 report=build();(ROOT/OUTPUT).write_bytes(encoded(report));print(json.dumps({k:report[k] for k in ['retained_time_count','retained_vector_positions','joint_valid_vector_positions','northward_latitude_steps','gaps_over90minutes','new_width_record_admitted']}))
