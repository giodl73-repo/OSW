"""Inventory dated publisher figure panels; never infer a ring footprint."""
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PATH = 'research/thor-ursa-2022-dated-source-panels.json'
SOURCE = 'research/source-data/exley-loop-2022/journal-article.xml'
ACQUISITION = 'research/source-data/exley-loop-2022/acquisition.json'
PROTOCOL = 'plans/thor-ursa-source-panel-protocol-v1.md'
URL = 'https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2022.1049645/full'
PINS = {
    SOURCE: ('028757a8727a183ce8a4e2f4d06de969d9a74dcd1d7d21fda968529c5c904c2c',90312),
    'figures/exley-loop-2022-source-figure-2.webp': ('ab125ebdf2f642f3a21dd59516c90775f3a87d2ea3ba4a55a964591d1cf30fa8',1728874),
    'figures/exley-loop-2022-source-figure-3.webp': ('c4f4c650ef6c675feeac53298b3969a3af7852bf8fcef4e87d37e7e2fd44a4d1',1788820),
}
DATES = {
    'thor': '01-01 01-08 01-16 01-23 01-31 02-07 02-15 02-22 03-01 03-08 03-16 03-23 03-31 04-07 04-15 04-22 04-30 05-07 05-15 05-22 05-30 06-06 06-14 06-21 06-29'.split(),
    'ursa': '01-01 01-06 01-11 01-16 01-21 01-26 01-31 02-05 02-10 02-15 02-20 02-25 03-02 03-07 03-12 03-17 03-22 03-27 04-01 04-06 04-11 04-16 04-21 04-26 05-01'.split(),
}

def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()

def build():
    for path,(digest,size) in PINS.items():
        if sha(path)!=digest or (ROOT/path).stat().st_size!=size:
            raise ValueError('Changed pinned Thor/Ursa original: '+path)
    source = ET.parse(ROOT/SOURCE).getroot()
    # Complete original acquisition, including the literal unit discrepancy.
    text = ' '.join(source.itertext())
    if '0.65' not in text or 'Thor' not in text or 'Ursa' not in text:
        raise ValueError('Missing original event or contour definition')
    acquisition = json.loads((ROOT/ACQUISITION).read_bytes())
    if acquisition['source_document_sha256'] != sha(SOURCE):
        raise ValueError('Changed complete publisher XML')
    events = []
    for name, year, number in [('thor', 2020, 2), ('ursa', 2021, 3)]:
        figure = f'figures/exley-loop-2022-source-figure-{number}.webp'
        with Image.open(ROOT/figure) as image:
            if image.size != (2008,1651):
                raise ValueError('Changed source figure dimensions')
        panels = []
        for i, day in enumerate(DATES[name]):
            row, col = divmod(i, 5)
            # Visually reviewed publisher image: each map and its printed date.
            x = [71,422,771,1120,1470][col]
            y = [0,321,642,963,1284][row]
            panels.append({'id': f'{name}-{year}-{day}', 'observation_date': f'{year}-{day}',
                'source_panel_index': i, 'source_row': row+1, 'source_column': col+1,
                'crop_pixels_xywh': [x,y,264,288],
                'support_kind': 'regional_source_field_during_named_shedding_event',
                'ring_identity_from_panel_alone': False, 'geometry_lon_lat': None,
                'center_lon_lat': None, 'radius_km': None, 'area_km2': None,
                'physical_state_relations': [], 'annual_extrema_eligible': False,
                'seasonal_playback_eligible': False})
        events.append({'entity_id': f'eddy:published:{name}-{year}', 'name': name.title(),
            'figure_number': number, 'source_image_file': figure,
            'source_image_sha256': sha(figure), 'source_image_bytes': (ROOT/figure).stat().st_size,
            'source_image_size_pixels': [2008,1651], 'panel_count': 25,
            'source_locator': f'Figure {number}; Sections 2 and 3.{number-1}',
            'source_caption': ' '.join(next(f for f in source.iter('fig') if f.attrib['id']==f'f{number}').find('caption').itertext()).strip(),
            'panels': panels})
    return {'schema':'osw.named-eddy-dated-source-panels.v1','as_of':'2026-10-09',
        'status':'editorial_original_source_panel_inventory_scientific_review_pending',
        'source_url':URL, 'source_doi':'10.3389/fmars.2022.1049645',
        'source_citation':'Johnson Exley, Donohue, Watts, Tracey and Kennelly (2022), Generation of high-frequency topographic Rossby waves in the Gulf of Mexico, Frontiers in Marine Science 9:1049645.',
        'source_document_file':SOURCE,'source_document_sha256':sha(SOURCE),
        'source_document_bytes':(ROOT/SOURCE).stat().st_size,
        'acquisition_file':ACQUISITION,'acquisition_sha256':sha(ACQUISITION),
        'protocol_file':PROTOCOL,'protocol_sha256':sha(PROTOCOL),
        'license':'CC BY 4.0','license_url':'https://creativecommons.org/licenses/by/4.0/',
        'copyright':'Copyright 2022 Johnson Exley, Donohue, Watts, Tracey and Kennelly.',
        'display_transformation':'Selected source-image panel crop; original complete figures retained unchanged.',
        'field_definition':'Colors: mapped deep reference pressure expressed as sea surface height (SSH_ref), not surface ring boundaries. Bold black curve: surface Loop Current contour. Dots: CPIES instruments. Gray contours: bathymetry.',
        'contour_definition':{'source_literal':'0.65 cm','source_locator':'Section 2, final paragraph',
            'unit_status':'unresolved_source_printed_unit_not_normalized','normalized_contour_value_m':None,
            'provider_context':'Historical Copernicus daily near-real-time mapped multi-mission altimeter SSH product, source-reported 25 km horizontal resolution; numerical fields not acquired.'},
        'claim_limit':'These are regional field panels during named shedding events. They do not establish 50 independent eddy positions, closed ring footprints, annual ranges or physical OSW state joins. Many curves extend beyond their frames. Event dates are irregular and are not a recurring seasonal cycle.',
        'contour_review_lead':{'entity_id':'eddy:published:ursa-2021','date':'2021-03-07',
            'status':'visually_closed_curve_candidate_for_subsequent_boundary_review',
            'geometry_lon_lat':None,'scientific_admission':'pending'},
        'event_count':2,'panel_count':50,'new_closed_footprint_count':0,'events':events}

def validate(doc):
    if doc != build():
        raise ValueError('Thor/Ursa source panels differ from original dates, crop, identity or scope')
    return doc

if __name__ == '__main__':
    data=build()
    (ROOT/PATH).write_bytes((json.dumps(data,indent=2,ensure_ascii=False)+'\n').encode('utf8'))
    print('Built 50 dated source panels; zero admitted footprints or state relations')
