"""Actual original and saved-product checks independent of the producer."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import pymupdf

ROOT = Path(__file__).resolve().parents[1]


def test_algerian_report_retains_original_regional_claim_and_custody():
    report = json.loads((ROOT/'research/algerian-arnone-1990-reported-reach-v1.json').read_bytes())
    source = report['source']
    raw = (ROOT/source['original_file']).read_bytes()
    assert len(raw) == source['original_bytes'] == 853466
    assert hashlib.sha256(raw).hexdigest() == source['original_sha256']
    receipt = json.loads((ROOT/'research/source-data/arnone-algerian-1990/acquisition.json').read_bytes())
    assert hashlib.md5(raw).hexdigest() == receipt['md5']
    assert hashlib.sha1(raw).hexdigest() == receipt['sha1']
    with pymupdf.open(stream=raw, filetype='pdf') as original:
        assert len(original) == source['original_pdf_pages'] == 11
        abstract = ' '.join(original[1].get_text().split())
        results = ' '.join(original[4].get_text().split())
        cover = ' '.join(original[0].get_text().split())
        assert 'for over 300 km, between Oran and Algiers.' in abstract
        assert 'within 30 km of the Algerian coast' in abstract
        assert 'for 300 km.' in results
        assert 'May 1 and 22, 1986' in cover
    assert source['source_copy_complete'] is False
    assert source['missing_printed_journal_pages'] == [1596, 1597]
    assert report['entity_id'] == 'current:algerian'
    c = report['constraint']
    assert (c['threshold_km'], c['relation'], c['unit']) == (300, 'gt', 'km')
    assert c['study_window'] == ['1986-05-01', '1986-05-22']
    assert source['ship_cruise_window'] == ['1986-05-01', '1986-05-21']
    assert c['regional_support'] == ['Oran', 'Algiers']
    assert c['coast_proximity_context_km'] == 30
    assert c['coast_proximity_is_current_width'] is False
    for key in ['upper_bound_km', 'reported_uncertainty_km',
                'whole_current_length_km', 'physical_length_lower_bound_km']:
        assert c[key] is None
    assert c['rank_eligible'] is False
    for key in ['whole_current_length_admitted', 'physical_width_admitted',
                'annual_or_seasonal_range_admitted', 'current_geometry_admitted']:
        assert report[key] is False


def test_saved_schematic_has_open_threshold_and_explicit_scope():
    root = ET.fromstring((ROOT/'figures/algerian-arnone-1990-reported-reach-v1.svg').read_bytes())
    text = ' '.join(root.itertext())
    for claim in ['>300 km', '1–22 May 1986', 'Oran–Algiers',
                  'not current width', 'no finite upper bound',
                  'arrow is not geography', '1596–1597']:
        assert claim in text
    circle = root.find('.//{http://www.w3.org/2000/svg}circle')
    assert circle is not None and circle.get('fill') == '#f3f8fa'
    assert root.get('role') == 'img'
    for path, expected in json.loads((ROOT/'research/algerian-arnone-1990-reported-reach-v1.json').read_bytes())['input_sha256'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == expected
