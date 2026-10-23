"""Frozen reported regional constraint, never an inferred whole-current length."""
import argparse
import copy
from datetime import date
import hashlib
import html
import json
import math
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
FACTS = 'research/algerian-arnone-1990-reach-source-facts.json'
FOLDER = 'research/source-data/arnone-algerian-1990'
REPORT = 'research/algerian-arnone-1990-reported-reach-v1.json'
FIGURE = 'figures/algerian-arnone-1990-reported-reach-v1.svg'
PREFLIGHT = 'research/published-current-regional-reaches-preflight-v1.json'
PROTOCOL = 'plans/published-current-regional-reaches-protocol-v1.md'
INPUTS = ['analysis/published_current_regional_reaches_v1.py',
          'analysis/test_published_current_regional_reaches_v1.py', PROTOCOL, FACTS,
          FOLDER+'/dtic-ada223991.pdf', FOLDER+'/acquisition.json', FOLDER+'/README.md']


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+'\n').encode('utf8')


def pin(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def input_pins():
    return {path: pin(path) for path in INPUTS}


def constraint(facts):
    value = facts['reported_threshold_km']
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError('Positive finite reported km threshold required')
    if (facts['quantity'] != 'reported_nearshore_regional_extent' or facts['relation'] != 'gt'
            or facts['unit'] != 'km'):
        raise ValueError('Unchanged regional quantity and strict source comparison required')
    if facts['reported_upper_bound_km'] is not None or facts['source_uncertainty_km'] is not None:
        raise ValueError('Source supplies no upper endpoint or numerical uncertainty')
    for field in ['whole_current_length_admitted', 'physical_width_admitted',
                  'annual_or_seasonal_range_admitted', 'current_geometry_admitted',
                  'coast_proximity_is_current_width']:
        if facts[field] is not False:
            raise ValueError('Unsupported physical promotion: '+field)
    start, end = map(date.fromisoformat, facts['reported_study_window'])
    ship_start, ship_end = map(date.fromisoformat, facts['ship_cruise_window'])
    if not start <= ship_start <= ship_end <= end or end.year > facts['publication_year']:
        raise ValueError('Invalid declared study/ship/publication chronology')
    if facts['entity_id'] != 'current:'+facts['current_id'] or len(facts['spatial_support']) != 2:
        raise ValueError('Current identity and two named regional support locations required')
    return {'quantity': facts['quantity'], 'threshold_km': value, 'relation': 'gt', 'unit': 'km',
            'upper_bound_km': None, 'reported_uncertainty_km': None,
            'uncertainty_kind': 'not_reported_not_zero',
            'display': f'>{value:g} km', 'rank_eligible': False,
            'whole_current_length_km': None, 'physical_length_lower_bound_km': None,
            'regional_support': copy.deepcopy(facts['spatial_support']),
            'study_window': copy.deepcopy(facts['reported_study_window']),
            'time_support_kind': facts['time_support_kind'],
            'coast_proximity_context_km': facts['coast_proximity_context_km'],
            'coast_proximity_is_current_width': False}


def source_check(facts):
    receipt = json.loads((ROOT/FOLDER/'acquisition.json').read_bytes())
    original = ROOT/facts['original_file']
    raw = original.read_bytes()
    if (len(raw) != facts['original_bytes'] or hashlib.sha256(raw).hexdigest() != facts['original_sha256']
            or hashlib.md5(raw).hexdigest() != receipt['md5']
            or hashlib.sha1(raw).hexdigest() != receipt['sha1']):
        raise ValueError('Original custody changed')
    if facts['source_copy_complete'] is not False or facts['missing_printed_journal_pages'] != [1596, 1597]:
        raise ValueError('Changed archive completeness scope')
    if receipt['provider_size_md5_sha1_verified'] is not True or receipt['archive_pdf_pages'] != 11:
        raise ValueError('Missing original provider custody')
    with pymupdf.open(original) as doc:
        if len(doc) != facts['original_pdf_pages'] or len(doc) != 11:
            raise ValueError('Original page count changed')
        abstract = ' '.join(doc[1].get_text().split())
        results = ' '.join(doc[4].get_text().split())
        if (facts['source_quote'] not in abstract or 'for 300 km.' not in results
                or 'This paper is not subject to U S. copyright.' not in abstract):
            raise ValueError('Selected original source assertion or rights statement changed')


def build():
    preflight = json.loads((ROOT/PREFLIGHT).read_bytes())
    if input_pins() != preflight['input_sha256']:
        raise ValueError('Frozen source/method inputs changed')
    facts = json.loads((ROOT/FACTS).read_bytes())
    source_check(facts)
    value = constraint(facts)
    return {'schema': 'osw.published-current-regional-reach.v1',
            'id': 'regional-reach:algerian:arnone-1990',
            'entity_id': facts['entity_id'], 'current_id': facts['current_id'],
            'status': 'source_reported_dated_regional_constraint',
            'constraint': value, 'whole_current_evidence_status': 'unmeasured',
            'whole_current_length_admitted': False, 'physical_width_admitted': False,
            'annual_or_seasonal_range_admitted': False, 'current_geometry_admitted': False,
            'source': {key: copy.deepcopy(facts[key]) for key in [
                'source_doi', 'source_title', 'authors', 'publication_year', 'source_locator',
                'original_file', 'original_sha256', 'original_bytes', 'original_pdf_pages',
                'source_copy_complete', 'missing_printed_journal_pages',
                'selected_pages_visually_reviewed', 'source_quote', 'ship_cruise_window', 'source_window_note']},
            'scope': 'Source-reported coastal reach during a combined ship/satellite study; no whole-current centreline length, finite upper endpoint, physical width or seasonal envelope.',
            'derivation': 'No distance calculation, unit conversion, statistical estimate or graphic digitization; retain the published strict threshold.',
            'source_facts_phase': 'reviewed_before_frozen_report_execution',
            'protocol_file': PROTOCOL, 'input_sha256': preflight['input_sha256']}


def figure(report):
    c = report['constraint']
    description = ('Dated source-reported regional coastal reach strictly greater than '
                   f"{c['threshold_km']:g}km. No finite upper endpoint or numerical uncertainty reported. "
                   'Not whole-current length or a geographic route; coast proximity is not width.')
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 470" width="1000" height="470" role="img" aria-labelledby="title desc">',
        '<title id="title">Algerian Current: published May 1986 coastal reach</title>',
        '<desc id="desc">'+html.escape(description)+'</desc>',
        '<rect width="1000" height="470" rx="14" fill="#f3f8fa"/>',
        '<g font-family="Arial,sans-serif" fill="#173342">',
        '<text x="45" y="47" font-size="25">Algerian Current · source-reported coastal reach</text>',
        '<text x="45" y="80" font-size="17">Oran–Algiers · combined observations 1–22 May 1986</text>',
        '<text x="45" y="158" font-size="44" font-weight="bold">'+html.escape(c['display'])+'</text>',
        '<text x="45" y="190" font-size="16">Strict reported threshold; no finite upper bound</text>',
        '<circle cx="385" cy="155" r="9" fill="#f3f8fa" stroke="#0c6b82" stroke-width="3"/>',
        '<path d="M395 155H880M858 141L880 155 858 169" fill="none" stroke="#0c6b82" stroke-width="4"/>',
        '<text x="385" y="198" font-size="15">Open threshold</text>',
        '<text x="648" y="198" font-size="15">Larger reaches unspecified</text>',
        '<text x="45" y="255" font-size="17">30 km in the source describes proximity to the coast, not current width.</text>',
        '<text x="45" y="288" font-size="17">Whole-current length and seasonal ranges remain unmeasured.</text>',
        '<text x="45" y="343" font-size="14">Arnone, Wiesenburg &amp; Saunders 1990 · doi:10.1029/JC095iC02p01587</text>',
        '<text x="45" y="371" font-size="14">Verified abstract and results pages; archive copy lacks printed pages 1596–1597.</text>',
        '<text x="45" y="399" font-size="14">Schematic constraint display; arrow is not geography or a traced current axis.</text>',
        '<text x="45" y="427" font-size="14">No confidence interval, whole-current rank, geometry or physical width inferred.</text>',
        '</g></svg>']
    return ('\n'.join(lines)+'\n').encode('utf8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['build', 'check'])
    args = parser.parse_args()
    report = build()
    outputs = {REPORT: encoded(report), FIGURE: figure(report)}
    for path, raw in outputs.items():
        target = ROOT/path
        if args.command == 'check':
            if target.read_bytes() != raw:
                raise ValueError('Changed frozen product: '+path)
        else:
            if target.exists() and target.read_bytes() != raw:
                raise ValueError('Refusing to overwrite frozen product: '+path)
            target.write_bytes(raw)
    print(json.dumps({'status': 'PASS', 'products': {p: hashlib.sha256(b).hexdigest() for p,b in outputs.items()}}))


if __name__ == '__main__':
    main()
