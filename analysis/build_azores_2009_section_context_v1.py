"""Validate existing section facts and draw their independently authored locator.

This source-only operation neither modifies measurement inventories nor builds
the runtime. --check refuses a stale figure. --verify-original checks custody
of the ignored, copyrighted original when it is available locally.
"""
import argparse
import hashlib
import json
from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / 'research/azores-2009-section-original-review-v1.json'
FIGURE = ROOT / 'figures/azores-2009-section-context-v1.svg'


def validate(doc, verify_original=False):
    inventory = json.loads((ROOT / doc['existing_inventory_file']).read_bytes())
    expected = {
        'azores-countercurrent-2009-section-width': ('azores-countercurrent', 42, 46, 36.25, 35.25, 'westward'),
        'azores-2009-section-width': ('azores', 49, 53, 34.5, 33.5, 'eastward'),
    }
    rows = doc['existing_measurement_enrichments']
    if len(rows) != 2 or {r['id'] for r in rows} != set(expected):
        raise ValueError('Require exactly the two existing section identities')
    for row in rows:
        facts = expected[row['id']]
        actual = (row['current_id'], row['north_boundary']['station'], row['south_boundary']['station'],
                  row['north_boundary']['latitude_deg_north'], row['south_boundary']['latitude_deg_north'],
                  row['flow_direction'])
        if actual != facts:
            raise ValueError('Section attribution differs from reviewed original')
        matches = [r for r in inventory['widths'] if r['id'] == row['id']]
        if len(matches) != 1:
            raise ValueError('Missing or duplicated existing width')
        old = matches[0]
        coordinates = [[-24.5, facts[4]], [-24.5, facts[3]]]
        if (old['current_id'] != facts[0] or old['approximate_width_km'] != 110
                or row['existing_approximate_width_km'] != 110
                or old['section_geometry']['coordinates'] != coordinates
                or old['observed_period'] != doc['shared_section_context']['observed_period']):
            raise ValueError('Existing section differs; re-review rather than overwrite')
    context = doc['shared_section_context']
    if (context['date_discrepancy']['resolved'] is not False
            or context['fixed_width_layer_bounds_m'] is not None
            or context['width_uncertainty_interval_km'] is not None):
        raise ValueError('Unresolved date/layer/uncertainty may not be promoted')
    decision = doc['decision']
    for key in ['new_measurement_records', 'numeric_width_changes', 'section_geometry_changes', 'new_whole_current_lengths']:
        if decision[key] != 0:
            raise ValueError('Provenance enrichment cannot create a measurement')
    for key in ['annual_ranges_admitted', 'new_physical_footprints_admitted', 'runtime_or_generated_packet_changed']:
        if decision[key] is not False:
            raise ValueError('Unsupported physical or runtime admission')
    if verify_original:
        raw = (ROOT / doc['source']['local_ignored_copy']).read_bytes()
        if len(raw) != doc['source']['bytes'] or hashlib.sha256(raw).hexdigest() != doc['source']['sha256']:
            raise ValueError('Original PDF custody mismatch')


def svg(doc):
    y = lambda latitude: 154 + (37 - latitude) * 91
    parts = []
    for lat in [37, 36, 35, 34, 33]:
        yy = y(lat)
        parts.append(f'<line x1="124" y1="{yy:g}" x2="746" y2="{yy:g}" stroke="#d9e3e8"/>'
                     f'<text x="108" y="{yy+5:g}" text-anchor="end" font-size="14">{lat} N</text>')
    for row in doc['existing_measurement_enrichments']:
        north, south = row['north_boundary'], row['south_boundary']
        yn, ys = y(north['latitude_deg_north']), y(south['latitude_deg_north'])
        mid = (yn + ys) / 2
        west = row['flow_direction'] == 'westward'
        color = '#006e91' if west else '#a13c19'
        start, end = (290, 205) if west else (410, 495)
        back = end + 10 if west else end - 10
        parts.append(f'''<g id="{escape(row['id'])}" fill="{color}">
<title>{escape(row['name'])}: about 110 km source-reported meridional section span</title>
<line x1="350" y1="{yn:g}" x2="350" y2="{ys:g}" stroke="{color}" stroke-width="8"/>
<line x1="{start}" y1="{mid:g}" x2="{end}" y2="{mid:g}" stroke="{color}" stroke-width="3"/>
<polygon points="{end},{mid:g} {back},{mid-6:g} {back},{mid+6:g}"/>
<text x="520" y="{mid-17:g}" font-size="18">{escape(row['name'])}</text>
<text x="520" y="{mid+7:g}" font-size="15">about 110 km / {row['flow_direction']}</text>
<text x="520" y="{mid+29:g}" font-size="13">{'Subsurface counterflow' if west else 'Thermocline / intermediate flow'}</text>
<circle cx="350" cy="{yn:g}" r="5" fill="white" stroke="{color}" stroke-width="2"/>
<circle cx="350" cy="{ys:g}" r="5" fill="white" stroke="{color}" stroke-width="2"/>
<text x="365" y="{yn-10:g}" font-size="13">Station {north['station']} / {north['latitude_deg_north']:g} N</text>
<text x="365" y="{ys+20:g}" font-size="13">Station {south['station']} / {south['latitude_deg_north']:g} N</text>
</g>''')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 760" role="img" aria-labelledby="title desc">
<title id="title">Azores: two dated width sections at 24.5 W</title>
<desc id="desc">Independent section locator, with north up and latitude to scale. The westward Azores Countercurrent is bounded by stations 42 and 46, 36.25 to 35.25 N. The eastward Azores Current is bounded by stations 49 and 53, 34.5 to 33.5 N. Each reported span is approximately 110 km. Arrows indicate direction only, not along-current length or speed. One survey, not a seasonal cycle. Methods occupation dates are 26 October to 1 November 2009; Figure 1 caption says 2010 and the conflict is unresolved.</desc>
<rect width="880" height="760" fill="#f7fafb"/>
<g font-family="Arial,sans-serif" fill="#203b4b">
<text x="36" y="44" font-size="25">Azores / a dated cross-current section</text>
<text x="36" y="77" font-size="16">24.5 W / 26 Oct-1 Nov 2009, as reported in the methods</text>
<text x="36" y="105" font-size="14">North up; latitude to scale. Horizontal arrows show flow direction only.</text>
<line x1="350" y1="154" x2="350" y2="518" stroke="#8095a2" stroke-dasharray="4 5"/>
{''.join(parts)}
<text x="350" y="553" text-anchor="middle" font-size="14">Meridional survey line / 24.5 W</text>
<text x="36" y="600" font-size="15">These are two source-delimited section spans, not whole-current lengths or footprints.</text>
<text x="36" y="628" font-size="15">No fixed width layer, numerical width error or annual width range is established.</text>
<text x="36" y="656" font-size="14">Date conflict retained: Figure 1 says fall 2010; methods specify the 2009 occupation.</text>
<text x="36" y="700" font-size="13">Source: Comas-Rodriguez et al. (2011), Figures 1,5,6,8 and Results / DOI:10.1029/2011JC007129.</text>
<text x="36" y="727" font-size="13">OSW independent locator. Source review prepared; runtime card integration pending.</text>
</g></svg>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--verify-original', action='store_true')
    args = parser.parse_args()
    doc = json.loads(REVIEW.read_bytes())
    validate(doc, args.verify_original)
    raw = svg(doc).encode('utf-8')
    ET.fromstring(raw)
    if args.check:
        if FIGURE.read_bytes() != raw:
            raise ValueError('Stale section diagram')
    else:
        FIGURE.write_bytes(raw)
    print(json.dumps({'existing_section_records_verified': 2, 'new_measurements': 0,
                      'original_custody_verified': args.verify_original,
                      'figure_checked': args.check, 'figure_sha256': hashlib.sha256(raw).hexdigest()}))


if __name__ == '__main__':
    main()
