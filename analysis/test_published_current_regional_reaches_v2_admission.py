"""Independent checks of the actual retained original and frozen v2 products."""
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
REPORT = 'research/brazil-tomczak-initial-reach-v2.json'
FIGURE = 'figures/brazil-tomczak-initial-reach-v2.svg'


def digest(path):
    with (ROOT/path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def test_actual_original_supports_only_the_reported_initial_reach():
    report = json.loads((ROOT/REPORT).read_bytes())
    source = report['source']; constraint = report['constraint']
    assert source['original_sha256'] == digest(source['original_file'])
    assert source['original_sha256'] == '35e36f9b834c9c31c2cee64abc36d0c687d71e3d388c2cf1c40bc026e613738b'
    with pymupdf.open(ROOT/source['original_file']) as doc:
        assert len(doc) == 401
        text = ' '.join(doc[253].get_text().split())
        version = ' '.join(doc[1].get_text().split())
    assert source['source_quote'] in text
    assert 'the Brazil Current, begins near 10°S' in text
    assert int(re.search(r'Over the next ([0-9]+) km', text).group(1)) == constraint['reported_value_km'] == 1500
    assert '1.2 published September 2002' in version
    assert source['chapter_pdf_version_month'] == '2002-09'
    assert source['first_printed_edition_year'] == 1994
    assert constraint['study_window'] is None
    assert constraint['relation'] == 'source_reported_value'
    assert constraint['upstream_latitude_qualifier'] == 'near'
    assert constraint['upstream_latitude_context_degrees_north'] == -10


def test_actual_products_keep_unknowns_and_match_frozen_source_method_pins():
    report = json.loads((ROOT/REPORT).read_bytes()); c = report['constraint']
    for key in ['reported_uncertainty_km', 'whole_current_length_km',
                'physical_length_lower_bound_km', 'physical_width_km', 'annual_or_seasonal_range',
                'upstream_longitude_degrees_east', 'downstream_endpoint_coordinates',
                'current_geometry', 'state_intersections']:
        assert c[key] is None, key
    assert c['rank_eligible'] is False
    for key in ['whole_current_length_admitted', 'physical_width_admitted',
                'annual_or_seasonal_range_admitted', 'current_geometry_admitted',
                'state_intersections_admitted', 'rank_eligible', 'new_calculation_performed']:
        assert report[key] is False, key
    assert all(digest(path) == expected for path, expected in report['input_sha256'].items())
    assert digest(REPORT) == '47e7dba6a54d94afe5b3c700e445cfe8156236cc956ca094577a169ea4953b24'
    assert digest(FIGURE) == '0b7a2088558132674a753d28335f3c3a5d314d6418539125110fee7deee39e22'
    root = ET.fromstring((ROOT/FIGURE).read_bytes())
    text = ' '.join(root.itertext())
    assert root.attrib['role'] == 'img' and root.attrib['aria-labelledby'] == 'title desc'
    assert '1500 km' in text and 'observation dates unspecified' in text
    assert 'not a geographic axis or a physical length lower bound' in text
    assert 'Downstream coordinates unspecified' in text
    assert 'numerical uncertainty not reported' in text
