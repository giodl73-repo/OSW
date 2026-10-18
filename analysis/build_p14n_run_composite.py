"""Conditional cross-run component spans; temporal comparability is assumed."""
from datetime import datetime
from pathlib import Path
import hashlib,json,math
from build_p14n_native_field_audit import verify as verify_native
from build_p14n_underway_averages import average_bin,separation,stamp

ROOT=Path(__file__).resolve().parents[1]
OUTPUT='research/aleutian-p14n-1993-run-composite.json'
PROTOCOL='plans/aleutian-p14n-run-composite-protocol-v1.md'
INPUTS={PROTOCOL:'7558e6794d811f287cf9e708624abb7e89b6e16e4d3af01d528fc73f0e151edb',
 'research/aleutian-p14n-1993-native-vector-support.json':'b41d6f82bc60475de67c3bfb6e596dad0f72a726034126ae67bbed29cfd82962',
 'analysis/build_p14n_native_field_audit.py':'887ee7629dff09d25211f6544f8ba2558f7c89e5ee3c1c67b986289f72b6b83a',
 'analysis/build_p14n_underway_averages.py':'90e0118a2aa11ba97ca50d961a8e3d3579c0dd4d3ab7e5ba1917f5634131a2c7',
 'research/aleutian-p14n-1993-underway-averages.json':'92d6d3fc8717b010051b0fbbd96fe3b3955f7a86b2e0cf87cd6b5ed74783d626'}

def encoded(v):return (json.dumps(v,indent=2,allow_nan=False)+'\n').encode()
def moment(v):return datetime.fromisoformat(v)
def digest(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()

def summarize(rows,index):
 start=moment(rows[0]['ensemble_start_utc']);end=moment(rows[-1]['ensemble_end_utc'])
 value=average_bin(rows,start,(end-start).total_seconds(),0)
 value.pop('bin_index')
 return dict(value,run_index=index,
  first_source_time_index=rows[0]['source_time_index'],last_source_time_index=rows[-1]['source_time_index'],
  first_position={k:rows[0][k] for k in ['latitude_degrees_north','longitude_degrees_east']},
  last_position={k:rows[-1][k] for k in ['latitude_degrees_north','longitude_degrees_east']},
  northward_steps=sum(b['latitude_degrees_north']>a['latitude_degrees_north'] for a,b in zip(rows,rows[1:])),
  summary_position_is_instantaneous_observation=False)

def eligibility(row,window):
 if row['union_coverage_seconds']<3600:return 'less_than_one_hour_covered'
 if not row['boundary_eligible_coverage']:return 'insufficient_time_coverage'
 if row['northward_steps']:return 'nonmonotone_source_track'
 low,high=row['contributor_latitude_range']
 if low<window[0] or high>window[1]:return 'outside_branch_footprint'
 return 'eligible'

def gap(a,b,profiles):
 indices=list(range(a['last_source_time_index'],b['first_source_time_index']+1))
 result={'before_run_index':a['run_index'],'after_run_index':b['run_index'],
  'unobserved_time_gap_hours':(moment(b['window_start_utc'])-moment(a['window_end_utc'])).total_seconds()/3600,
  'unobserved_endpoint_distance_km':separation(a['last_position'],b['first_position']),
  'intervening_profile_count':max(0,len(indices)-2),
  'intervening_ctd_event_overlapping_profiles':sum(bool(profiles[i].get('ctd_event_overlaps')) for i in indices[1:-1] if i in profiles)}
 if len(indices)<2:return dict(result,status='source_indices_not_forward')
 if any(i not in profiles for i in indices):return dict(result,status='missing_source_profile')
 if any(profiles[i]['layer_mean']['eastward_m_s'] is None or profiles[i]['layer_mean']['northward_m_s'] is None for i in indices):
  return dict(result,status='unsupported_source_layer')
 if any(not 0<(moment(profiles[j]['ensemble_end_utc'])-moment(profiles[i]['ensemble_end_utc'])).total_seconds()<=450 for i,j in zip(indices,indices[1:])):
  return dict(result,status='source_clock_gap_or_reversal')
 if a['contributor_latitude_range'][0]<b['contributor_latitude_range'][1]:return dict(result,status='overlapping_or_reversed_footprints')
 if result['unobserved_time_gap_hours']<0:return dict(result,status='overlapping_time_support')
 if result['unobserved_endpoint_distance_km']>25:return dict(result,status='unobserved_distance_exceeds_25km')
 return dict(result,status='eligible_subject_to_time_cap')

def walk(rows,gaps,peak,step,window,threshold,cap):
 inside=peak
 while True:
  outside=inside+step
  if not 0<=outside<len(rows):return {'status':'run_list_end','run_index':inside}
  state=eligibility(rows[outside],window)
  if state!='eligible':return {'status':state,'run_index':outside}
  gi=min(inside,outside);link=gaps[gi]
  if link['status']!='eligible_subject_to_time_cap':return {'status':link['status'],'gap_index':gi}
  if link['unobserved_time_gap_hours']>cap:return {'status':'unobserved_time_gap_exceeds_cap','gap_index':gi}
  a,b=rows[inside],rows[outside]
  if b['mean']['eastward_m_s']<=threshold:
   fraction=(threshold-a['mean']['eastward_m_s'])/(b['mean']['eastward_m_s']-a['mean']['eastward_m_s'])
   point={key:a['mean'][key]+fraction*(b['mean'][key]-a['mean'][key]) for key in ['latitude_degrees_north','longitude_degrees_east']}
   return {'status':'resolved','inside_run_index':inside,'outside_run_index':outside,
    'gap_index':gi,'fraction_from_inside':fraction,'crossing':point,
    'mean_position_bracket_km':separation(a['mean'],b['mean']),
    'unobserved_time_gap_hours':link['unobserved_time_gap_hours'],
    'unobserved_endpoint_distance_km':link['unobserved_endpoint_distance_km'],
    'conditional_summary_interpolation':True}
  inside=outside

def branch(rows,gaps,name,window,cap):
 candidates=[i for i,r in enumerate(rows) if eligibility(r,window)=='eligible']
 result={'branch':name,'latitude_window':window,'maximum_unobserved_time_gap_hours':cap,
  'eligible_run_indices':candidates,'selected_peak':None,'scenarios':[]}
 if not candidates:return dict(result,status='no_eligible_runs')
 peak=max(candidates,key=lambda i:(rows[i]['mean']['eastward_m_s'],-i));speed=rows[peak]['mean']['eastward_m_s']
 result['selected_peak']={'run_index':peak,'eastward_m_s':speed}
 if speed<.02:return dict(result,status='below_peak_floor')
 for fraction,offset in [(.4,0),(.5,0),(.6,0),(.5,-.06),(.5,-.02),(.5,.02),(.5,.06)]:
  threshold=speed*fraction+offset
  scenario={'fraction_of_peak':fraction,'threshold_displacement_m_s':offset,'comparison_threshold_m_s':threshold,
   'before_peak':None,'after_peak':None,'endpoint_separation_km':None,'rounded_endpoint_separation_km':None,
   'full_bracketing_observation_period_utc':None}
  if not 0<threshold<speed:scenario['status']='ineligible_threshold'
  else:
   before=walk(rows,gaps,peak,-1,window,threshold,cap);after=walk(rows,gaps,peak,1,window,threshold,cap)
   scenario.update(status='unresolved',before_peak=before,after_peak=after)
   if before['status']==after['status']=='resolved':
    km=separation(before['crossing'],after['crossing']);first=before['outside_run_index'];last=after['outside_run_index']
    begin=moment(rows[first]['window_start_utc']);end=moment(rows[last]['window_end_utc'])
    scenario.update(status='resolved_under_declared_comparability_assumption',endpoint_separation_km=km,
     rounded_endpoint_separation_km=math.floor(km/10+.5)*10,
     full_bracketing_observation_period_utc={'start':stamp(begin),'end':stamp(end),'hours':(end-begin).total_seconds()/3600})
  result['scenarios'].append(scenario)
 return dict(result,status='evaluated')

def build():
 for p,pin in INPUTS.items():
  if digest(p)!=pin:raise ValueError('Changed conditional run-composite input: '+p)
 native=verify_native();profiles={r['source_time_index']:r for r in native['profiles']};experiments=[]
 for speed in native['run_sensitivity']:
  rows=[summarize([profiles[i] for i in run['source_time_indices']],j) for j,run in enumerate(speed['runs'])]
  gaps=[gap(a,b,profiles) for a,b in zip(rows,rows[1:])]
  cases=[branch(rows,gaps,name,window,cap) for cap in [3,6,12] for name,window in [('northern',[44,46]),('southern',[41,43])]]
  experiments.append({'ship_speed_cutoff_m_s':speed['ship_speed_cutoff_m_s'],'run_summaries':rows,'adjacent_gaps':gaps,'cases':cases})
 scenarios=[s for e in experiments for case in e['cases'] for s in case['scenarios']]
 return {'schema':'osw.conditional-run-component-composite.v1','current_id':'aleutian',
  'status':'exploratory_conditional_summary_interpolation_not_physical_width',
  'input_sha256':dict(INPUTS),'protocol_file':PROTOCOL,'generator_file':Path(__file__).relative_to(ROOT).as_posix(),
  'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'experiments':experiments,
  'primary_assumption':{'ship_speed_cutoff_m_s':2,'maximum_unobserved_time_gap_hours':6,'fraction_of_peak':.5,'threshold_displacement_m_s':0},
  'scenario_counts':{'total':len(scenarios),'conditionally_resolved':sum(s['endpoint_separation_km'] is not None for s in scenarios),
    'unresolved_or_ineligible':sum(s['endpoint_separation_km'] is None for s in scenarios)},
  'temporal_comparability_verified':False,'source_values_filled':False,'latitude_sorting_applied':False,
  'across_run_summary_interpolation_tested':True,'existing_no_bridge_result_replaced':False,
  'source_gap_profiles_used_as_velocity_samples':False,'current_association_verified':False,
  'flow_normal_width_estimated':False,'new_width_record_admitted':False,'physical_edge_geometry_admitted':False,
  'whole_current_width_km':None,'annual_width_range_km':None,'width_rank_eligible':False,'seasonal_playback_supported':False,
  'sensitivity_is_confidence_interval':False,
  'cautions':['Conditional interpolation assumes temporal comparability; the complete bracket may span much longer than the permitted individual gap.',
   'Whole-run means have moving spatial footprints and different durations, not instantaneous point support.',
   'A resolved eastward-component span does not identify a physical current boundary, flow-normal width or southern branch versus eddy.',
   'GPS-related estimates do not calibrate total uncertainty of this composite. Missing or ineligible source support remains a hard barrier.']}

def verify():
 result=build()
 if (ROOT/OUTPUT).read_bytes()!=encoded(result):raise ValueError('Stale conditional run-composite report')
 return result

if __name__=='__main__':
 result=build();(ROOT/OUTPUT).write_bytes(encoded(result));print(json.dumps(result['scenario_counts']))
