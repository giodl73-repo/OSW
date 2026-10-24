"""Fixed Euler streamline tests of retained offshore mean fields, not current axes."""
from collections import Counter
import json
import math

import numpy as np
from pyproj import Geod

from acquire_west_australian_oscar_2d import ROOT, DIRECTORY, digest, load
from build_west_australian_oscar_2d_source import REPORT as SOURCE_REPORT, verify as verify_source

PROTOCOL = 'plans/west-australian-regional-streamline-protocol-v1.md'
OPERATOR = 'analysis/west_australian_regional_streamlines.py'
REPORT = 'research/west-australian-regional-streamlines.json'
GEOD = Geod(ellps='WGS84')
STEPS = (5, 10, 20)
OFFSETS = (-1, 0, 1)


def readback(value, digits):
    result = round(float(value), digits)
    return 0.0 if result == 0 else result


class Field:
    def __init__(self, longitude, latitude, u, v):
        self.x = np.asarray(longitude, dtype=float)
        self.y = np.asarray(latitude, dtype=float)
        self.u = np.asarray(u, dtype=float); self.v = np.asarray(v, dtype=float)
        if np.any(np.diff(self.y) < 0):
            self.y = self.y[::-1]; self.u = self.u[::-1]; self.v = self.v[::-1]
        if self.u.shape != (len(self.y), len(self.x)) or self.v.shape != self.u.shape:
            raise ValueError('Inconsistent field shape')
        if len(self.x) < 2 or len(self.y) < 2 or not np.all(np.diff(self.x) > 0) or not np.all(np.diff(self.y) > 0):
            raise ValueError('Invalid native coordinates')
        if not np.all(np.isfinite(self.x)) or not np.all(np.isfinite(self.y)) or np.isinf(self.u).any() or np.isinf(self.v).any():
            raise ValueError('Invalid source coordinate/vector')
        self.bounds = (float(self.x[0]), float(self.x[-1]), float(self.y[0]), float(self.y[-1]))

    def cell(self, lon, lat):
        west, east, south, north = self.bounds
        if not west <= lon <= east or not south <= lat <= north:
            return None
        return (max(0, min(len(self.y)-2, int(np.searchsorted(self.y, lat, side='right'))-1)),
                max(0, min(len(self.x)-2, int(np.searchsorted(self.x, lon, side='right'))-1)))

    def sample(self, lon, lat):
        cell = self.cell(lon, lat)
        if cell is None: return None
        yi, xi = cell
        a = float((lon-self.x[xi])/(self.x[xi+1]-self.x[xi])); b = float((lat-self.y[yi])/(self.y[yi+1]-self.y[yi]))
        weights = [(1-a)*(1-b), a*(1-b), (1-a)*b, a*b]
        corners = [(yi,xi), (yi,xi+1), (yi+1,xi), (yi+1,xi+1)]
        if any(not np.isfinite(self.u[y,x]) or not np.isfinite(self.v[y,x]) for y,x in corners): return None
        return tuple(sum(w*float(array[y,x]) for w,(y,x) in zip(weights,corners)) for array in [self.u,self.v])

    def supported_rectangle(self, start, end):
        left = self.cell(min(start[0],end[0]), min(start[1],end[1]))
        right = self.cell(max(start[0],end[0]), max(start[1],end[1]))
        if left is None or right is None: return False
        yi,xi = left; yj,xj = right
        return bool(np.isfinite(self.u[yi:yj+2,xi:xj+2]).all() and np.isfinite(self.v[yi:yj+2,xi:xj+2]).all())


def angular_step(point, velocity, direction, step_km):
    lon,lat = point; u,v = velocity
    speed = math.hypot(u,v)
    phi = math.radians(lat); eccentricity2 = (1/298.257223563)*(2-1/298.257223563)
    denominator = 1-eccentricity2*math.sin(phi)**2
    prime = 6378137/math.sqrt(denominator)
    meridional = 6378137*(1-eccentricity2)/denominator**1.5
    return (lon+math.degrees(direction*step_km*1000*u/speed/(prime*math.cos(phi))),
            lat+math.degrees(direction*step_km*1000*v/speed/meridional))


def first_exit(start, end, bounds):
    west,east,south,north = bounds
    candidates = []
    for axis,low,high,names in [(0,west,east,('west','east')),(1,south,north,('south','north'))]:
        delta = end[axis]-start[axis]
        if delta < 0 and end[axis] <= low: candidates.append(((low-start[axis])/delta,names[0],axis,low))
        if delta > 0 and end[axis] >= high: candidates.append(((high-start[axis])/delta,names[1],axis,high))
    if not candidates: return end,None
    fraction,name,axis,value = min(candidates)
    point = [start[i]+fraction*(end[i]-start[i]) for i in range(2)]
    point[axis] = value
    # A corner exit is retained as a side exit if either simultaneous side is lateral.
    simultaneous = [row[1] for row in candidates if abs(row[0]-fraction) < 1e-12]
    if any(side in simultaneous for side in ['west','east']): name = next(side for side in ['west','east'] if side in simultaneous)
    return tuple(point),name


def trace(field, seed, direction, step_km, limit_km=10000, return_after_km=300):
    if direction not in [-1,1] or step_km <= 0: raise ValueError('Invalid tracing convention')
    point = tuple(seed); vertices = [point]; distance = 0.; stop = None; last_velocity = None
    proposed_failure = None; exit_side = None
    target = 'north' if direction == 1 else 'south'
    for _ in range(math.ceil(limit_km/step_km)*2+5):
        velocity = field.sample(*point)
        if velocity is None: stop='missing_paired_corner'; break
        if math.hypot(*velocity) < .005: stop='weak_speed_guard'; break
        proposed = angular_step(point,velocity,direction,step_km)
        candidate,exit_side = first_exit(point,proposed,field.bounds)
        proposed_failure = candidate
        if not field.supported_rectangle(point,candidate): stop='unsupported_segment_rectangle'; break
        endpoint_velocity = field.sample(*candidate)
        if endpoint_velocity is None: stop='missing_paired_corner'; break
        if math.hypot(*endpoint_velocity) < .005: stop='weak_endpoint_speed_guard'; break
        _,_,length_m = GEOD.inv(*point,*candidate)
        length = length_m/1000
        if not math.isfinite(length) or length <= 0: stop='nonadvancing_step'; break
        if distance+length > limit_km: stop='next_step_exceeds_distance_limit'; break
        distance += length; point=candidate; vertices.append(point); last_velocity=endpoint_velocity
        if exit_side:
            stop = 'matching_gate_reached' if exit_side == target and endpoint_velocity[1] > 0 else 'gate_velocity_not_northward' if exit_side == target else 'viewport_'+exit_side+'_exit'
            break
        if distance >= return_after_km and GEOD.inv(*seed,*point)[2]/1000 <= max(20,2*step_km):
            stop='seed_return_guard'; break
    if stop is None: stop='iteration_limit_guard'
    return {'status':stop,'target_gate':target,'traced_distance_km':readback(distance,6),
            'vertices_lon_lat':[[readback(x,8),readback(y,8)] for x,y in vertices],
            'accepted_segments':len(vertices)-1,
            'proposed_exit_side':exit_side,
            'reached_viewport_side':exit_side if stop=='matching_gate_reached' or stop=='gate_velocity_not_northward' or stop.startswith('viewport_') else None,
            'first_rejected_proposal_lon_lat':None if stop in ['matching_gate_reached','seed_return_guard','gate_velocity_not_northward'] or stop.startswith('viewport_') or proposed_failure is None else [readback(v,8) for v in proposed_failure],
            'matching_gate_original_northward_positive':bool(last_velocity[1] > 0) if stop == 'matching_gate_reached' else None,
            'last_accepted_velocity_m_s':None if last_velocity is None else [readback(v,8) for v in last_velocity]},distance


def period_mean(arrays):
    paired = np.isfinite(arrays['u']) & np.isfinite(arrays['v'])
    eligible = paired.all(axis=0); u=np.full(eligible.shape,np.nan); v=np.full_like(u,np.nan)
    for yi,xi in zip(*np.where(eligible)):
        u[yi,xi] = sum(float(value) for value in arrays['u'][:,yi,xi])/72
        v[yi,xi] = sum(float(value) for value in arrays['v'][:,yi,xi])/72
    return u,v,eligible


def build():
    source,pins = verify_source(); arrays,_ = load(); u,v,eligible = period_mean(arrays)
    fields = [('source-period-mean',None,Field(arrays['longitude'],arrays['latitude'],u,v))]
    fields += [(f'month-{row["month"]:02d}',row['month'],Field(arrays['longitude'],arrays['latitude'],row['eastward_m_s'],row['northward_m_s'])) for row in source['months']]
    cases=[]; anchors=[]
    for field_id,month,field in fields:
        yi = int(np.flatnonzero(field.y == -32)[0])
        indices = [i for i,x in enumerate(field.x) if 80 <= x <= 105 and np.isfinite(field.v[yi,i])]
        peak = max(indices,key=lambda i:(field.v[yi,i],-i)) if indices else None
        anchors.append({'field_id':field_id,'month':month,'latitude':-32,
                        'source_longitude_index':peak,'longitude':None if peak is None else float(field.x[peak]),
                        'northward_m_s':None if peak is None else float(field.v[yi,peak])})
        for step in STEPS:
            for offset in OFFSETS:
                row={'id':f'{field_id}:step-{step}:seed-{offset:+d}','field_id':field_id,'month':month,
                     'step_km':step,'native_seed_offset':offset,'primary':step==10 and offset==0,
                     'seed_lon_lat':None,'backward':None,'forward':None,
                     'conditional_regional_path_length_km':None,'rounded_regional_path_length_km':None}
                if peak is None or field.v[yi,peak] < .02:
                    row['status']='anchor_missing_or_below_northward_threshold'
                else:
                    xi=peak+offset;seed=(float(field.x[xi]),-32.)
                    row['seed_lon_lat']=list(seed);velocity=field.sample(*seed)
                    if velocity is None or velocity[1] < .02: row['status']='seed_missing_or_below_northward_threshold'
                    else:
                        backward,back_length=trace(field,seed,-1,step);forward,forward_length=trace(field,seed,1,step)
                        row.update(backward=backward,forward=forward)
                        if backward['status']==forward['status']=='matching_gate_reached':
                            length=back_length+forward_length
                            row.update(status='both_regional_gates_reached',conditional_regional_path_length_km=readback(length,6),
                                       rounded_regional_path_length_km=math.floor(length/10+.5)*10)
                        else: row['status']='unresolved_regional_gate_pair'
                cases.append(row)
    def nullable(values):return [[None if not np.isfinite(v) else float(v) for v in row] for row in values]
    return {'schema':'osw.west-australian-regional-streamlines.v1','status':'exploratory_mean_field_paths_not_named_current_axes',
            'current_id':'west-australian','entity_id':'current:west-australian',
            'input_sha256':{**pins,PROTOCOL:digest((ROOT/PROTOCOL).read_bytes()),OPERATOR:digest((ROOT/OPERATOR).read_bytes())},
            'source_monthly_file':SOURCE_REPORT,'source_period_mean':{'rule':'equal_record_mean_all72paired_required',
                'source_time_indices':list(range(72)),'source_times':arrays['times'],'eligible_cells':int(eligible.sum()),
                'eastward_m_s':nullable(u),'northward_m_s':nullable(v)},
            'anchors':anchors,'cases':cases,'counts':{'fields':13,'attempts':117,'status_counts':dict(sorted(Counter(c['status'] for c in cases).items())),
                'primary_resolved_fields':sum(c['primary'] and c['status']=='both_regional_gates_reached' for c in cases)},
            'length_metric':'sum_of_WGS84_polygon_segments_between_fixed_regional_latitude_gates',
            'tracing_convention':{'method':'direction_normalized_first_order_Euler_in_geographic_coordinates',
                'nominal_steps_km':list(STEPS),'native_seed_offsets':list(OFFSETS),'seed_latitude':-32,
                'anchor_search_longitude_bounds':[80,105],'seed_minimum_northward_m_s':.02,
                'state_minimum_speed_m_s':.005,'maximum_traced_leg_km':10000,'seed_return_after_km':300,
                'seed_return_radius_rule':'max_20_km_or_twice_nominal_step',
                'source_mask_guard':'all_corners_in_segment_bounding_rectangle_must_be_finite'},
            'derived_readback_precision':{'trace_coordinate_decimal_places':8,'distance_km_decimal_places':6,
                'interpolated_endpoint_velocity_decimal_places':8,'decisions_precede_readback':True},
            'source_bounds':{'longitude':[60,116],'latitude':[-36,-28]},
            'gates':{'south_latitude':-36,'north_latitude':-28,'not_physical_current_endpoints':True},
            'current_association_verified':False,'partial_traced_distance_is_current_length':False,
            'comparison_figure':'figures/west-australian-regional-streamlines.svg',
            'path_figure':'figures/west-australian-regional-streamline-paths.svg',
            'physical_current_axis_admitted':False,'width_rank_eligible':False,'length_rank_eligible':False,
            'whole_current_length_km':None,'whole_current_width_km':None,'annual_physical_length_range_km':None,
            'physical_state_join_eligible':False,'seed_return_guard_identifies_an_eddy':False}


def encoded(document): return (json.dumps(document,separators=(',',':'),allow_nan=False)+'\n').encode()


if __name__=='__main__':
    document=build();(ROOT/REPORT).write_bytes(encoded(document));print(json.dumps(document['counts']),flush=True)
