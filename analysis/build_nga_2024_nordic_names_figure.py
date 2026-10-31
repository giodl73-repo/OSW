"""Source-specific nomenclature connections; no geographic or dimensional map."""
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = 'research/nga-2024-current-name-and-dimension-review.json'
FIGURE = 'figures/nga-2024-nordic-current-names.svg'
MANIFEST = 'research/nga-2024-nordic-current-names-figure.json'


def build():
    doc = json.loads((ROOT/REVIEW).read_bytes())
    if any(doc[key] is not False for key in ['canonical_identity_admitted',
            'name_equivalence_between_modern_currents_admitted','new_width_record_admitted',
            'new_length_record_admitted','physical_geometry_admitted','annual_extrema_admitted']):
        raise ValueError('Source nomenclature figure cannot admit physical measurements')
    expected = {('North Atlantic Current', 'Norway Current', 'northern_branch_continues_as'),
                ('Norway Coastal Current', 'Norway Current', 'joins_near_63N'),
                ('Norway Current', 'North Cape Current', 'northeastern_branch_continues_as'),
                ('Norway Current', 'Spitzbergen Atlantic Current', 'northwestern_branch_continues_as'),
                ('Spitzbergen Atlantic Current', 'East Greenland Current', 'gradually_merges_with_in_Greenland_Sea')}
    if {(r['from'], r['to'],r['relation']) for r in doc['source_connections']} != expected:
        raise ValueError('Source connection set changed; review figure layout')
    aliases = {r['source_name']:r['source_aliases'] for r in doc['source_conventions']}
    if aliases != {'Norway Current':['Norwegian Current'], 'Norway Coastal Current':[],
                   'Spitzbergen Atlantic Current':['Spitzbergen Current']}:
        raise ValueError('Source alias convention changed; review figure labels')
    metadata = json.loads((ROOT/doc['source']).read_bytes())
    if metadata['sha256'] != doc['source_sha256'] or metadata['edition'] != 2024:
        raise ValueError('Source publication identity changed')
    dimensions = {r['id']: r for r in doc['dimension_candidates']}
    coastal = dimensions['nga2024-norway-coastal-typical-width']
    wider = dimensions['nga2024-norway-coastal-63n-width']
    if any(r['source_name'] != 'Norway Coastal Current' or r['unit_as_printed'] != 'mile'
           or r['kilometers'] is not None for r in [coastal, wider]):
        raise ValueError('Coastal raw-unit scope changed')
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 700" role="img" aria-labelledby="title desc">',
           '<title id="title">Nordic current names in the NGA 2024 glossary</title>',
           '<desc id="desc">Conceptual source connections. Norwegian Current is an alias of Norway Current in this edition. The separate Norway Coastal Current joins it near63 degrees north. Norway Current branches into North Cape and Spitzbergen Atlantic currents; the latter joins East Greenland Current. No modern identity equivalence, map scale, observed boundaries or seasonal dimensions are established.</desc>',
           '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#526b7c"/></marker></defs>',
           '<style>text{font-family:Arial,sans-serif;fill:#153346}.title{font-size:25px;font-weight:700}.sub{font-size:15px}.name{font-size:19px;font-weight:700}.note{font-size:14px}.edge{fill:none;stroke:#526b7c;stroke-width:2.5;marker-end:url(#arrow)}.box{fill:#f1f6f9;stroke:#52778c;stroke-width:1.5}.coast{fill:#f5f8ed;stroke:#657b43;stroke-width:1.5}</style>',
           '<rect width="1080" height="700" fill="white"/>',
           '<text x="32" y="36" class="title" font-family="Arial,sans-serif" font-size="25" font-weight="700" fill="#153346">Nordic current names: the NGA 2024 source convention</text>',
           '<text x="32" y="64" class="sub" font-family="Arial,sans-serif" font-size="15" fill="#153346">Conceptual connections • publication year, not observation date • no geographic scale</text>']

    def text(x, y, value, cls='note', anchor='middle'):
        out.append(f'<text x="{x}" y="{y}" class="{cls}" font-family="Arial,sans-serif" font-size="{19 if cls == "name" else 14}" font-weight="{700 if cls == "name" else 400}" fill="#153346" text-anchor="{anchor}">{html.escape(value)}</text>')

    def box(x, y, w, h, lines, coastal=False):
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{"#f5f8ed" if coastal else "#f1f6f9"}" stroke="{"#657b43" if coastal else "#52778c"}" stroke-width="1.5"/>')
        for i, line in enumerate(lines): text(x+w/2, y+27+i*21, line, 'name' if i == 0 else 'note')

    for path in ['M610 159V235', 'M350 277H460',
                 'M610 319V352H365V395', 'M610 319V352H885V395', 'M365 479V545']:
        out.append(f'<path class="edge" fill="none" stroke="#526b7c" stroke-width="2.5" d="{path}"/>')
    for x,y,horizontal in [(610,235,False),(460,277,True),(365,395,False),(885,395,False),(365,545,False)]:
        triangle = f'M{x-10} {y-5}L{x-10} {y+5}L{x} {y}Z' if horizontal else f'M{x-5} {y-10}L{x+5} {y-10}L{x} {y}Z'
        out.append(f'<path d="{triangle}" fill="#526b7c"/>')
    box(460, 95, 300, 64, ['North Atlantic Current'])
    box(460, 235, 300, 84, ['Norway Current', 'Alias: Norwegian Current'])
    box(40, 235, 310, 84, ['Norway Coastal Current',
        f"About {coastal['value']} miles", f"May approach {wider['value']} miles near 63°N"], coastal=True)
    box(160, 395, 410, 84, ['Spitzbergen Atlantic Current', 'Alias: Spitzbergen Current'])
    box(740, 395, 290, 70, ['North Cape Current'])
    box(160, 545, 410, 70, ['East Greenland Current'])
    text(620, 195, 'Northern branch continues', anchor='start')
    text(405, 260, 'Joins ~63°N')
    text(435, 340, 'Northwest branch')
    text(805, 340, 'Northeast branch')
    text(385, 516, 'Gradual merge in Greenland Sea', anchor='start')
    text(32, 645, 'Coastal width statements stay with the coastal entry. Raw mile units retain an unresolved conversion.', anchor='start')
    text(32, 669, 'Source: American Practical Navigator, Vol II (2024), glossary pp.463–464 and497. Modern identity joins need further evidence.', anchor='start')
    out.append('</svg>')
    raw = ('\n'.join(out)+'\n').encode()
    (ROOT/FIGURE).write_bytes(raw)
    manifest = {'schema': 'osw.source-nomenclature-figure.v1', 'figure': FIGURE,
                'figure_sha256': hashlib.sha256(raw).hexdigest(), 'source_review': REVIEW,
                'source_review_sha256': hashlib.sha256((ROOT/REVIEW).read_bytes()).hexdigest(),
                'producer': 'analysis/build_nga_2024_nordic_names_figure.py',
                'producer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'source_publication_sha256': doc['source_sha256'],
                'conceptual_not_geographic': True, 'modern_current_identity_equivalence_admitted': False,
                'physical_width_admitted': False, 'physical_length_admitted': False}
    (ROOT/MANIFEST).write_bytes((json.dumps(manifest, indent=2)+'\n').encode())
    return manifest


if __name__ == '__main__':
    print(json.dumps(build(), indent=2))
