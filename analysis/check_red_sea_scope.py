"""Separate REDSOX velocity reach, channel dimensions and named-flow extent."""
from datetime import date

def validate(document):
 if document.get('current_id')!='red-sea-saline-overflow' or document.get('schema')!='osw.current-source-scope-audit.v1' or document.get('status')!='editorial_source_scope_not_scientific_approval':raise ValueError('Red Sea scope identity mismatch')
 if any(document.get(key) is not None for key in ['whole_current_length_km','whole_current_width_km','annual_length_range_km','annual_width_range_km']) or any(document.get(key) is not False for key in ['channel_values_are_current_dimensions','channel_value_spread_is_uncertainty_interval','seasonal_route_playback_supported']):raise ValueError('Channel dimensions promoted to current or annual measurements')
 reach=document.get('reported_reach',{})
 expected={'approximate_length_km':130,'length_metric':'author_reported_winter_velocity_supported_descending_plume_reach','branch_id':'redsox-northern-channel-plume','source_velocity_quantity':'plume_speed_magnitude','velocity_threshold_m_s':.2,'threshold_operator':'>','layer_thickness_range_m':[100,250],'fixed_depth_bounds_m':None,'observed_period':None,'is_synoptic_snapshot':False,'geometry':None,'length_range_km':None,'rank_eligible':False,'whole_current_representative':False}
 if any(reach.get(k)!=v or type(reach.get(k))!=type(v) for k,v in expected.items()):raise ValueError('Reported reach lost speed, thickness, time or length scope')
 period=reach.get('campaign_context',{})
 if period.get('is_exact_reach_sampling_period') is not False or date.fromisoformat(period['start'])>date.fromisoformat(period['end']):raise ValueError('Invalid reach campaign context')
 branches=document.get('branches',[])
 ids={r.get('id') for r in branches}
 if len(branches)!=3 or len(ids)!=3 or reach['branch_id'] not in ids:raise ValueError('Incomplete source branch taxonomy')
 for row in branches:
  if row.get('parent_component') not in ids|{'red-sea-saline-overflow'} or row.get('parent_component')==row['id'] or row.get('canonical_identity') is not False or any(row.get(k) is not None for k in ['geometry','whole_branch_length_km','width_km']):raise ValueError('Unsupported branch identity or dimensions')
  seen=set();node=row['id'];lookup={r['id']:r['parent_component'] for r in branches}
  while node in lookup:
   if node in seen:raise ValueError('Cyclic branch taxonomy')
   seen.add(node);node=lookup[node]
 values=document.get('channel_dimension_context',[])
 if len(values)!=3 or [r.get('approximate_length_km') for r in values]!=[130,120,115] or any(r.get('approximate_width_km')!=5 for r in values):raise ValueError('Source channel conventions changed; review required')
