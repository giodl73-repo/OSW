"""Prepare two explicitly regional NEC schematic reaches without ocean fields."""
import copy
import hashlib
import itertools
import json
import math
from pathlib import Path

from atlantic_nsec_reference_reaches_v1 import GEOD,length_km

ROOT=Path(__file__).resolve().parents[1]
INPUT='research/atlantic-nec-schematic-reference-reach-input-v1.json'
OUTPUT='research/atlantic-nec-schematic-reference-reaches-prepared-v1.json'


def truncate(coords,west):
    if coords[0][0]!=-30 or any(a[0]<=b[0] for a,b in zip(coords,coords[1:])):
        raise ValueError('Expected strictly westward support from30W')
    result=[list(p) for p in coords if p[0]>=west]
    if len(result)<2 or result[-1][0]!=west:raise ValueError('Gate is not an explicit support vertex')
    return result


def prepare(source):
    if source['current_id']!='atlantic-north-equatorial' or source['entity_id']!='current:atlantic-north-equatorial':
        raise ValueError('Atlantic NEC identity required; not nSEC or a cross-basin family')
    if any(source['eligibility'].values()) or source['installed'] is not False:
        raise ValueError('Editorial regional preparation only')
    if any(source[k] is not None for k in ['whole_current_length_km','annual_length_range_km','numerical_length_uncertainty_km']):
        raise ValueError('Unsupported physical dimension')
    result=copy.deepcopy(source);cases=[];routes=[]
    for route in source['routes']:
        support=route['support_waypoints_lon_lat'];length_km(support)
        nominal=truncate(support,source['gate_convention']['nominal_west_longitude'])
        values=[]
        for west,uniform,interior in itertools.product(source['gate_convention']['alternative_west_longitudes'],source['scenario_rule']['uniform_latitude_shifts_degrees'],source['scenario_rule']['interior_latitude_shifts_degrees']):
            coords=truncate(support,west)
            coords=[[lon,lat+uniform+(interior if 0<i<len(coords)-1 else 0)] for i,(lon,lat) in enumerate(coords)]
            value=length_km(coords);values.append(value)
            cases.append({'route_id':route['id'],'west_gate':west,'uniform_shift_degrees':uniform,'interior_shift_degrees':interior,'coordinates_lon_lat':coords,'reference_length_km':round(value,3)})
        routes.append({**route,'coordinates_lon_lat':nominal,'calculated_reference_length_km':round(length_km(nominal),3),
            'approximate_display_length_km':100*round(length_km(nominal)/100),
            'drawing_and_gate_envelope_km':[100*math.floor(min(values)/100),100*math.ceil(max(values)/100)],
            'studied_reach_only':True,'reference_route_ordering_eligible':False})
    result.update(schema='osw.atlantic-nec-schematic-reaches-prepared.v1',status='EDITORIAL_INTERIOR_REACHES_PREPARED_NOT_COAST_CHECKED_OR_INSTALLED',routes=routes,
        measurement_method='Sum WGS84 shortest ellipsoidal geodesic segments through declared OSW vertices.',
        editorial_sensitivity_cases=cases,editorial_sensitivity_case_count=len(cases),
        installed_reference_routes_added=0,physical_length_records_added=0,comparison_of_phases_is_measured_seasonal_change=False,
        remaining_gates=['Source-bound fine and coarse land-mask checks for every scenario at<=1km geodesic steps in one cloud job.','Exact installed duplicate audit and typed query/card/source pointer verification.','Native/WASM and actual desktop/mobile browser acceptance in a batched delivery.','Whole-current endpoints, other NEC flowlines, physical axes, widths and annual ranges remain unresolved.'])
    return result


def svg(result,compact=False):
    width,height=(360,1000) if compact else (1000,650)
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Atlantic NEC interior reference reaches</title><desc id="desc">Two editorial schematic lines from30W to55W. Gates are not current endpoints; lengths do not establish a whole-current ranking.</desc>',
        f'<rect width="{width}" height="{height}" fill="#f2f7f8"/><g font-family="Arial,sans-serif" fill="#163b49">']
    if compact:
        parts+=['<text x="14" y="30" font-size="22" font-weight="bold">Atlantic NEC</text>','<text x="14" y="58" font-size="19">Two interior reference reaches</text>']
    else:
        parts+=['<text x="30" y="38" font-size="25" font-weight="bold">Atlantic North Equatorial Current · interior references</text>','<text x="30" y="70" font-size="18">One NEC-labelled schematic curve per phase; other parallel flows are excluded.</text>']
    for i,r in enumerate(result['routes']):
        left=57 if compact else 75+475*i;top=150+305*i if compact else 165
        pw=280 if compact else 375;ph=170 if compact else 210
        title='Northern spring' if r['phase']=='northern_spring' else 'Northern fall'
        parts.append(f'<text x="{left-35}" y="{top-35}" font-size="{20 if compact else 22}" font-weight="bold">{title} schematic</text>')
        for lat in [12,16,20]:
            y=top+(20-lat)/9*ph
            parts.append(f'<path d="M{left} {y}H{left+pw}" stroke="#d0dfe4"/><text x="{left-7}" y="{y+5}" text-anchor="end" font-size="17">{lat}°N</text>')
        for lon in [-55,-40,-30]:
            x=left+(lon+55)/25*pw
            parts.append(f'<path d="M{x} {top}V{top+ph}" stroke="#d0dfe4"/><text x="{x}" y="{top+ph+27}" text-anchor="middle" font-size="17">{abs(lon)}°W</text>')
        coords=r['coordinates_lon_lat'];points=[(left+(lon+55)/25*pw,top+(20-lat)/9*ph) for lon,lat in coords]
        path=' '.join(('M' if j==0 else 'L')+f'{x:.2f},{y:.2f}' for j,(x,y) in enumerate(points))
        parts.append(f'<path d="{path}" fill="none" stroke="#087f8c" stroke-width="4"/>')
        for x,y in [points[0],points[-1]]:parts.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#98621c"/>')
        parts.append(f'<text x="{left-35}" y="{top+ph+61}" font-size="20" font-weight="bold">About {r["approximate_display_length_km"]:,} km</text>')
    lines=['Brown points: chosen interior gates.','Not current origin or termination.','Rounded editorial lines, not observed axes.','Drawing/gate spread is not uncertainty.','Not measured seasonal length changes.','Whole-current length and annual range','remain unknown. No physical footprint.','Source: Stramma &amp; Schott (1999), Fig.4','doi:10.1016/S0967-0645(98)00109-X'] if compact else [
        'Chosen30°W and55°W gates are not current origin or termination. Studied reaches excluded from ranking.',
        'WGS84 path sums; rounded editorial vertices, not velocity cores. Drawing/gate spread is not physical uncertainty.',
        'Whole-current length, width, annual ranges and physical footprint remain unresolved.',
        'Source: Stramma &amp; Schott (1999), Figure4 · doi:10.1016/S0967-0645(98)00109-X · OSW redraw',
        'Differences between these schematic paths are not measured seasonal length changes.']
    start=765 if compact else 485;step=23 if compact else 34
    for i,line in enumerate(lines):parts.append(f'<text x="{14 if compact else 30}" y="{start+i*step}" font-size="{17 if compact else 18}">{line}</text>')
    return '\n'.join(parts+['</g></svg>'])+'\n'


if __name__=='__main__':
    raw=(ROOT/INPUT).read_bytes();result=prepare(json.loads(raw));result['input_sha256']=hashlib.sha256(raw).hexdigest()
    (ROOT/OUTPUT).write_bytes((json.dumps(result,indent=2)+'\n').encode())
    for compact,name in [(False,'figures/atlantic-nec-regional-reference-reaches-v1.svg'),(True,'figures/atlantic-nec-regional-reference-reaches-compact-v1.svg')]:
        (ROOT/name).write_bytes(svg(result,compact).encode())
    print(json.dumps({'reference_lengths_km':[r['calculated_reference_length_km'] for r in result['routes']],'editorial_scenarios':len(result['editorial_sensitivity_cases']),'installed':False}))
