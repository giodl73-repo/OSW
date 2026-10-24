"""Actual qualitative source calendars retain access limits and no measurements."""
import hashlib
import json
from pathlib import Path
import re
import unicodedata
import xml.etree.ElementTree as ET

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
REPORT = 'research/indian-current-reported-direction-calendars-v1.json'
FIGURE = 'figures/indian-current-reported-direction-calendars-v1.svg'


def read(path):
    return json.loads((ROOT/path).read_bytes())


def digest(path):
    with (ROOT/path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def normalized(page):
    return unicodedata.normalize('NFKC', ' '.join(re.sub(r'-\s*\n\s*', '', page.get_text()).split()))


def test_actual_calendars_preserve_exact_reported_periods_and_access_scope():
    report = read(REPORT); facts = read(report['source_facts_file'])
    wicc, eacc = report['profiles']
    assert hashlib.sha256(facts['profiles'][0]['source_quote'].encode()).hexdigest() == '15794269fb9c2e7ad6bfb04c168d91cc770149b8eee90d993d745debf4af3c4c'
    assert {r['month'] for r in wicc['months'] if r['direction'] == 'northward'} == {1, 2, 11, 12}
    assert {r['month'] for r in wicc['months'] if r['direction'] == 'southward'} == set(range(4, 10))
    assert {r['month'] for r in wicc['months'] if r['direction'] is None} == {3, 10}
    assert wicc['access_scope'] == 'publisher_abstract_only_short_excerpt_retained'
    assert wicc['full_original_independently_checked'] is False
    assert wicc['full_paper_reviewed'] is False
    source = facts['retained_review_original']
    assert digest(source['file']) == source['sha256']
    with pymupdf.open(ROOT/source['file']) as doc:
        assert facts['profiles'][1]['source_quote'] in normalized(doc[16])
        assert 'current could flow in either direction' in normalized(doc[25])
    assert eacc['full_original_independently_checked'] is True
    assert eacc['full_paper_reviewed'] is False
    assert [r['direction'] for r in eacc['months']] == ['northward']*12


def test_actual_products_keep_all_unknowns_and_frozen_inputs_exact():
    report = read(REPORT); rows = [r for p in report['profiles'] for r in p['months']]
    assert len(rows) == report['month_rows'] == 24
    assert len({r['id'] for r in rows}) == 24
    assert report['independent_observations_added'] == report['new_measurements_admitted'] == 0
    assert report['calendar_month_highlight_eligible'] is True
    for key in ['physical_geometry_admitted', 'geographic_seasonal_playback_eligible', 'ranking_eligible']:
        assert report[key] is False
    for key in ['observation_window', 'annual_width_range_km', 'annual_length_range_km']:
        assert report[key] is None
    for row in rows:
        assert row['is_observation'] is False
        assert all(row[key] is None for key in ['observation_date', 'observation_year', 'observed_velocity_m_s', 'physical_geometry'])
    assert all(digest(path) == expected for path, expected in report['input_sha256'].items())
    assert digest(REPORT) == 'ea1399d45121884279686675d0cc8f42200fd59ac14e9203d38f77e40c401374'
    assert digest(FIGURE) == 'a9528d58a4af9a34fead12d50d47642c6f31ac6b6a182f17712f2cfa9fa34cac'
    tree = ET.fromstring((ROOT/FIGURE).read_bytes()); text = ' '.join(tree.itertext())
    assert tree.attrib['aria-labelledby'] == 'title desc'
    assert 'publisher abstract only' in text
    assert 'not monthly measurements or daily predictions' in text
    assert 'not zero flow or inferred transition phases' in text


def test_named_identity_decisions_are_source_supported_and_still_separately_gated():
    document = read('research/indian-coastal-current-identity-review-v1.json')
    assert digest(document['source_original_file']) == document['source_original_sha256']
    assert digest(document['candidate_file']) == document['candidate_sha256']
    assert digest(document['protocol_file']) == document['protocol_sha256']
    assert document['identity_decisions_prepared'] == len(document['decisions']) == 4
    assert document['canonical_current_count_delta_admitted'] == document['dimensions_admitted'] == 0
    with pymupdf.open(ROOT/document['source_original_file']) as doc:
        naming = normalized(doc[3])
    for row in document['decisions']:
        assert row['preferred_name']+' ('+row['abbreviation']+')' in naming
        assert row['canonical_admitted'] is False and row['ranking_eligible'] is False
        assert row['geometry'] is None and row['length_km'] is None and row['width_km'] is None
        assert row['annual_length_range_km'] is None and row['annual_width_range_km'] is None
        assert row['seasonal_playback_eligible'] is False
    assert document['unresolved_candidate']['canonical_admitted'] is False
    assert document['unresolved_candidate']['full_existing_identity_source_reviewed_now'] is False
