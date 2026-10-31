"""Prepare a source-described angular width without inventing paired edges."""
import hashlib
import json
import math
from pathlib import Path
from pyproj import Geod

ROOT=Path(__file__).resolve().parents[1]
FACTS='research/qiu-pacific-nec-2015-source-facts-v1.json'
FILE='research/pacific-nec-nominal-width-prepared-v1.json'
FIGURE='figures/pacific-nec-nominal-width-v1.svg'
PROTOCOL='plans/pacific-nec-nominal-width-protocol-v1.md'


def meridional_km(south,north):
    if (type(south) not in [int,float] or type(north) not in [int,float]
            or not math.isfinite(south) or not math.isfinite(north) or not -90<=south<north<=90):
        raise ValueError('Ordered finite latitude limits required')
    return Geod(ellps='WGS84').inv(0,south,0,north)[2]/1000


def prepare(facts):
    span=facts['nominal_surface_width'];context=facts['underlying_study_context']
    if (facts['entity_id']!='current:pacific-north-equatorial' or facts['doi']!='10.5670/oceanog.2015.78'
            or span['latitude_bounds_deg_north']!=[8,17] or span['angular_span_deg']!=9
            or span['source_reported_width_km'] is not None or span['edge_operator'] is not None
            or span['paired_physical_edge_coordinates'] is not None
            or span['single_section_longitude_deg_east'] is not None
            or span['sampling_dates'] is not None or span['annual_width_range_km'] is not None
            or span['numerical_width_uncertainty_km'] is not None
            or span['whole_current_representative'] is not False or span['seasonal_playback_eligible'] is not False
            or span['independent_new_observation'] is not False
            or context['reported_surface_flow_band_deg_north']!=[7,17]
            or context['second_width_record_prepared'] is not False):
        raise ValueError('Exact source-specific nominal width scope required')
    value=meridional_km(*span['latitude_bounds_deg_north'])
    return {'schema':'osw.scoped-width-candidate.v1','id':'pacific-nec-qiu2015-nominal-surface-span',
        'entity_id':facts['entity_id'],'current_id':'pacific-north-equatorial',
        'status':'PREPARED_PENDING_EXACT_INSTALLED_DUPLICATE_AUDIT',
        'measurement_type':'published_nominal_regional_angular_width',
        'width_metric':'nominal_meridional_latitude_separation',
        'approximate_width_km':round(value,-2),'display':'about1000km',
        'source_reported_width_km':None,'source_reported_latitude_bounds_deg_north':[8,17],
        'calculation':{'ellipsoid':'WGS84','method':'inverse_geodesic_on_same_arbitrary_meridian',
            'audit_distance_km':round(value,6),'display_rounding_km':100,
            'arbitrary_meridian_is_physical_location':False,'numerical_precision_is_measurement_precision':False},
        'geographic_scope':span['geographic_scope'],'layer':span['layer'],
        'boundary_rule':None,'paired_edge_coordinates':None,'section_geometry':None,
        'observed_period':None,'sampling_dates':None,'calendar_months':None,
        'annual_width_range_km':None,'numerical_width_uncertainty_km':None,
        'time_statistic':span['time_statistic'],'whole_current_representative':False,
        'flow_normal_width_diagnosed':False,'width_rank_eligible':False,'annual_extrema_eligible':False,
        'seasonal_playback_eligible':False,'independent_new_observation':False,
        'source_doi':facts['doi'],'source_url':facts['original_url'],'source_locator':span['locator'],
        'source_file':FACTS,'source_pointer':'/nominal_surface_width',
        'source_quality_note':'Nominal author-described band; exact velocity-edge operator and uniform historical sampling period unknown. Related JPO7-17N description remains separate, not an annual or uncertainty range.',
        'source_figure_digitized':False,'figure':FIGURE,'installed':False,'full_goal_complete':False}


def figure():
    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 410" role="img" aria-labelledby="title desc">
<title id="title">Pacific NEC nominal near-surface span</title>
<desc id="desc">Qiu et al.2015 project synthesis describes a nominal8-17 degrees north band west of the dateline. WGS84 meridional conversion gives about1000km. Regional approximation; no paired physical edges, annual range or numerical uncertainty. The related JPO7-17N band is separate source context.</desc>
<rect width="960" height="410" rx="12" fill="#eef5f8"/>
<g font-family="system-ui,sans-serif" fill="#14394b">
<text x="28" y="42" font-size="25" font-weight="700">Pacific North Equatorial Current</text>
<text x="28" y="76" font-size="18">Nominal near-surface span · western Pacific, west of the dateline</text>
<text x="28" y="119" font-size="30" font-weight="700">About 1,000 km</text>
<text x="28" y="150" font-size="17">Derived meridional distance from the reported 8–17°N band</text>
<path d="M100 187H820M100 178V196M820 178V196" stroke="#007b86" stroke-width="5"/>
<text x="100" y="220" font-size="18" text-anchor="middle">8°N</text>
<text x="820" y="220" font-size="18" text-anchor="middle">17°N</text>
<text x="28" y="260" font-size="17">Regional summary · near-surface context shallower than 100 m</text>
<text x="28" y="291" font-size="16">Paired physical edges, annual range and numerical uncertainty: unknown</text>
<text x="28" y="322" font-size="16">Related JPO paper describes 7–17°N; keep that source context separate.</text>
<text x="28" y="355" font-size="15">Qiu et al.2015 · Oceanography 28(4), p25 · doi:10.5670/oceanog.2015.78</text>
<text x="28" y="385" font-size="15">Nominal width candidate · whole-current length and seasonal playback unresolved</text>
</g></svg>'''


def main():
    facts=json.loads((ROOT/FACTS).read_bytes());candidate=prepare(facts)
    candidate['input_sha256']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [FACTS,PROTOCOL,'analysis/pacific_nec_nominal_width_v1.py']}
    for path,data in [(FILE,(json.dumps(candidate,indent=2,ensure_ascii=False)+'\n').encode()),(FIGURE,figure().encode())]:
        target=ROOT/path
        if target.exists():raise ValueError('Refuse to overwrite prepared evidence: '+path)
        target.write_bytes(data)
    print(json.dumps({'status':candidate['status'],'audit_distance_km':candidate['calculation']['audit_distance_km'],'approximate_width_km':candidate['approximate_width_km'],'new_installed_measurements':0}))


if __name__=='__main__':main()
