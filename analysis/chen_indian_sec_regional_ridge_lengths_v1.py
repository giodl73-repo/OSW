"""Offline WGS84 lengths of reviewed regional model-core grid traces; no whole-current claim."""
import hashlib
import json
import math
from pathlib import Path
import pyproj
from pyproj import Geod

ROOT=Path(__file__).resolve().parents[1]
PREFLIGHT='research/chen-indian-sec-ridge-length-preflight-v1.json'
SOURCE='research/chen-indian-sec-axis-feasibility-run-v2/report.json'
REVIEW='research/chen-indian-sec-passing-map-visual-review-v1.json'
FILE='research/chen-indian-sec-regional-ridge-lengths-v1.json'
FIGURE='figures/chen-indian-sec-regional-ridge-lengths-v1.svg'
STRIDES=(1,2,4,8)
GEOD=Geod(ellps='WGS84')


def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def verify():
    freeze=json.loads((ROOT/PREFLIGHT).read_bytes())
    if freeze['actual_target_lengths_calculated'] is not False:
        raise ValueError('Prospective freeze declaration required')
    if freeze['pyproj_version']!=pyproj.__version__ or freeze['proj_version']!=pyproj.proj_version_str:
        raise ValueError('Frozen geodesic runtime changed')
    for path,expected in freeze['input_sha256'].items():
        if digest(path)!=expected:raise ValueError('Frozen length input changed: '+path)


def selected_indices(count,stride,phase):
    if count<2 or stride not in STRIDES or not 0<=phase<stride:
        raise ValueError('Invalid declared resolution scenario')
    return sorted({0,count-1,*range(phase,count,stride)})


def polyline_km(points):
    if len(points)<2:raise ValueError('At least two geographic vertices required')
    for lon,lat in points:
        if not math.isfinite(lon) or not math.isfinite(lat) or not -180<=lon<=180 or not -90<=lat<=90:
            raise ValueError('Invalid longitude/latitude')
    total=0.0
    for a,b in zip(points,points[1:]):
        if abs(a[0]-b[0])>=180:raise ValueError('Ambiguous longitude leg')
        total+=GEOD.inv(a[0],a[1],b[0],b[1])[2]/1000
    return total


def scenarios(points):
    return [{'stride':stride,'phase':phase,'retained_vertices':len(indices),
             'length_km':polyline_km([points[i] for i in indices])}
            for stride in STRIDES for phase in range(stride)
            for indices in [selected_indices(len(points),stride,phase)]]


def nearest_100(value):return int(math.floor(value/100+0.5)*100)


def build():
    verify()
    source=json.loads((ROOT/SOURCE).read_bytes())
    reviewed=json.loads((ROOT/REVIEW).read_bytes())
    allowed={(r['case'],r['kernel_cells']) for r in reviewed['qualified_model_grid_traces']}
    passing={(c['id'],r['kernel_cells']) for c in source['cases'] for r in c['routes'] if not r['failures']}
    if allowed!=passing or len(passing)!=8:raise ValueError('Complete reviewed passing set required; no selective year admission')
    rows=[]
    for case in source['cases']:
        for route in case['routes']:
            key=(case['id'],route['kernel_cells'])
            row={'id':case['id']+':kernel-'+str(route['kernel_cells']),
                 'case':case['id'],'source_slice_index':case['source_slice_index'],'kernel_cells':route['kernel_cells'],
                 'sampled_gate_longitudes':route['sampled_gate_longitudes'],'flags':route['failures'],
                 'quantity':'regional_model_core_grid_polyline_length','length_km':None,'approximate_length_km':None,
                 'resolution_scenarios':[],'physical_current_axis_admitted':False,'whole_current_length_km':None,
                 'annual_extrema_eligible':False,'published_length_rank_eligible':False,'independent_observation':False}
            if key in allowed:
                if route['status']!='TRACE_FEASIBILITY_PASSED_REQUIRES_PHYSICAL_REVIEW' or any(p is None for p in route['points']):
                    raise ValueError('Reviewed trace is incomplete')
                points=[(p['longitude'],p['latitude']) for p in route['points']]
                if not all(a[0]>b[0] for a,b in zip(points,points[1:])):raise ValueError('East-to-west native ordering required')
                row.update(status='PREPARED_REGIONAL_MODEL_GRID_LENGTH',length_km=polyline_km(points),
                           approximate_length_km=nearest_100(polyline_km(points)),resolution_scenarios=scenarios(points),
                           coordinates=[list(p) for p in points])
            else:row['status']='WITHHELD_TRACE_FAILED_SOURCE_CONTINUITY_SCREEN'
            rows.append(row)
    cases=[]
    for case in source['cases']:
        selected=[r for r in rows if r['case']==case['id'] and r['length_km'] is not None]
        nominal=next((r for r in selected if r['kernel_cells']==3),None)
        readings=[s['length_km'] for r in selected for s in r['resolution_scenarios']]
        cases.append({'case':case['id'],'source_slice_index':case['source_slice_index'],
                      'nominal_grid_length_km':nominal['length_km'] if nominal else None,
                      'approximate_nominal_km':nominal['approximate_length_km'] if nominal else None,
                      'qualified_kernel_count':len(selected),'evaluated_kernel_count':3,
                      'computed_method_resolution_span_km':[min(readings),max(readings)] if readings else None,
                      'rounded_method_resolution_span_km':[int(math.floor(min(readings)/100)*100),int(math.ceil(max(readings)/100)*100)] if readings else None,
                      'span_is_physical_uncertainty':False,'span_is_annual_range':False})
    return {'schema':'osw.chen-indian-sec-regional-model-grid-lengths.v1','entity_id':'current:indian-south-equatorial',
            'status':'PREPARED_DERIVED_REGIONAL_MODEL_QUANTITY_PENDING_QUERY_ATLAS_DELIVERY',
            'source_doi':'10.1029/2022JC018969','source_product':'HYCOM_CR upper100m SON provider-described1993–2016',
            'source_file_sha256':source['custody']['sha256'],'frozen_trace_report_sha256':digest(SOURCE),
            'frozen_preflight_sha256':digest(PREFLIGHT),'source_year_label_basis':'Provider support corroborated by inferred MATLAB serial dates; not exact observation dates.',
            'method':'WGS84 inverse-geodesic leg sum on reviewed native-grid core ridges; nominal3x3 zonal-component smoothing',
            'gate_role':'Editorial regional comparison gates; not physical current endpoints',
            'intended_gate_longitudes':[105,65],'sampled_gate_longitudes':[105.15,64.76700000000017],
            'source_latitude_search_band':[-18,-6],'display_rounding_km':100,
            'resolution_method':'All phases of strides1,2,4,8 with both regional endpoints retained. Differences reflect grid/method choices, not physical error bounds.',
            'rows':rows,'cases':cases,'evaluated_traces':len(rows),'qualified_grid_lengths':8,
            'qualified_years':3,'source_years':24,'rejected_mean_field':True,
            'whole_current_length_km':None,'physical_current_axis_admitted':False,'annual_length_range_km':None,
            'width_km':None,'physical_uncertainty_km':None,'published_length_rank_eligible':False,
            'seasonal_dimension_playback_eligible':False,'new_independent_observations':0,
            'installed_measurements_added':0,'full_goal_complete':False}


def figure(report):
    selected=[c for c in report['cases'] if c['nominal_grid_length_km'] is not None]
    colors=['#2563eb','#b45309','#7c3aed']
    parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 800" role="img" aria-labelledby="title desc">',
           '<title id="title">Indian SEC regional model-core ridge lengths</title>',
           '<desc id="desc">Three of24 model years provide qualified regional grid traces. Eight of75 method cases pass;67 are withheld. These are upper100m SON model-core grid lengths, not whole-current lengths. Shaded method and resolution spans are not physical uncertainty or annual ranges.</desc>',
           '<rect width="1120" height="800" fill="#f8fafc"/>',
           '<g font-family="sans-serif" fill="#0f172a">',
           '<text x="42" y="38" font-size="23" font-weight="bold">Indian SEC · regional model-core ridge lengths</text>',
           '<text x="42" y="65" font-size="15">Upper 100 m · September–November · HYCOM model · about 65–105°E</text>',
           '<text x="42" y="90" font-size="14">Prepared regional estimates. Whole-current length, width and physical uncertainty remain unknown.</text>']
    x=lambda lon:70+(lon-64)*23
    y=lambda lat:135+(-6-lat)*20
    for lon in [65,75,85,95,105]:
        parts.append(f'<path d="M{x(lon):.2f} 120V390" stroke="#cbd5e1"/><text x="{x(lon)-13:.2f}" y="410" font-size="12">{lon}°E</text>')
    for lat in [-6,-10,-14,-18]:
        parts.append(f'<path d="M70 {y(lat):.2f}H1036" stroke="#cbd5e1"/><text x="29" y="{y(lat)+4:.2f}" font-size="12">{-lat}°S</text>')
    for case,color in zip(selected,colors):
        row=next(r for r in report['rows'] if r['case']==case['case'] and r['kernel_cells']==3)
        dense=[]
        for a,b in zip(row['coordinates'],row['coordinates'][1:]):
            distance=GEOD.inv(*a,*b)[2]
            additions=max(0,math.ceil(distance/10000)-1)
            dense.append(a)
            if additions:dense.extend(GEOD.npts(*a,*b,additions))
        dense.append(row['coordinates'][-1])
        path=' '.join(('M' if i==0 else 'L')+f'{x(p[0]):.2f},{y(p[1]):.2f}' for i,p in enumerate(dense))
        parts.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2.5"/>')
    parts.append('<text x="42" y="449" font-size="17" font-weight="bold">Nominal grid length and computed method/resolution span</text>')
    for i,(case,color) in enumerate(zip(selected,colors)):
        lower,upper=case['rounded_method_resolution_span_km']
        parts.append(f'<circle cx="52" cy="{483+i*36}" r="5" fill="{color}"/><text x="68" y="{488+i*36}" font-size="16">{case["case"].split("-")[-1]}: about {case["approximate_nominal_km"]:,} km · computed span {lower:,}–{upper:,} km · {case["qualified_kernel_count"]}/3 operators qualified</text>')
    parts.append('<text x="42" y="609" font-size="14">24 model years;21 have no qualified nominal estimate. Mean-field route also fails continuity.</text>')
    for year in range(1993,2017):
        xx=70+(year-1993)*41
        case=next(c for c in report['cases'] if c['case']=='provider-year-'+str(year))
        color=colors[[c['case'] for c in selected].index(case['case'])] if case['nominal_grid_length_km'] is not None else '#cbd5e1'
        parts.append(f'<circle cx="{xx}" cy="640" r="6" fill="{color}"/>')
        if year in [1993,1995,2000,2005,2010,2011,2016]:parts.append(f'<text x="{xx-15}" y="668" font-size="11">{year}</text>')
    parts.extend(['<text x="42" y="708" font-size="13">Colored dots: qualified model years. Gray: withheld. No interpolation across missing years.</text>',
                  '<text x="42" y="734" font-size="13">The spans combine smoothing and grid sampling choices. They are not confidence intervals or annual extrema.</text>',
                  '<text x="42" y="760" font-size="12">Chen et al.2022 · doi:10.1029/2022JC018969 · source and all failed traces retained in the frozen report</text>',
                  '</g></svg>'])
    return '\n'.join(parts)+'\n'


def main():
    report=build()
    for path,raw in [(FILE,(json.dumps(report,indent=2)+'\n').encode()),(FIGURE,figure(report).encode())]:
        target=ROOT/path
        if target.exists():raise ValueError('Frozen output already exists: '+path)
        target.write_bytes(raw)
    print(json.dumps({'status':report['status'],'qualified_grid_lengths':8,'cases':[c for c in report['cases'] if c['nominal_grid_length_km'] is not None]}))


if __name__=='__main__':main()
