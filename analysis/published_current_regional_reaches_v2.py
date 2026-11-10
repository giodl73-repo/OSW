"""Prospective source-reported initial reach; no inferred physical dimensions."""
import argparse
import copy
import hashlib
import html
import json
import math
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
FACTS = 'research/brazil-tomczak-initial-reach-source-facts-v1.json'
PROTOCOL = 'plans/published-current-regional-reaches-protocol-v2.md'
PREFLIGHT = 'research/published-current-regional-reaches-preflight-v2.json'
REPORT = 'research/brazil-tomczak-initial-reach-v2.json'
FIGURE = 'figures/brazil-tomczak-initial-reach-v2.svg'
ORIGINAL = 'research/source-data/tomczak-regional-2005/journal-article.pdf'
ACQUISITION = 'research/source-data/tomczak-regional-2005/acquisition.json'
INPUTS = ['analysis/published_current_regional_reaches_v2.py',
          'analysis/test_published_current_regional_reaches_v2.py',
          FACTS, PROTOCOL, ORIGINAL, ACQUISITION]
PROHIBITED = ['whole_current_length_admitted', 'physical_width_admitted',
              'annual_or_seasonal_range_admitted', 'current_geometry_admitted',
              'state_intersections_admitted', 'rank_eligible', 'new_calculation_performed']


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+'\n').encode('utf8')


def sha(path):
    with (ROOT/path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def input_pins():
    return {path: sha(path) for path in INPUTS}


def constraint(facts):
    """Pure validation/projection, also usable with prospective synthetic facts."""
    value = facts['reported_value_km']
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError('Positive finite source-reported km value required')
    if (facts['quantity'] != 'reported_initial_regional_reach'
            or facts['relation'] != 'source_reported_value'):
        raise ValueError('Preserve the reported initial reach; no inequality or physical equality inferred')
    if facts['source_uncertainty_km'] is not None or facts['physical_length_lower_bound_km'] is not None:
        raise ValueError('Unreported uncertainty and physical floor must remain null, not zero')
    if facts['reported_observation_window'] is not None or facts['time_support_kind'] != 'unspecified_textbook_synthesis_not_publication_or_revision_date':
        raise ValueError('No observation window is supplied for this textbook statement')
    if facts['upstream_longitude_degrees_east'] is not None or facts['downstream_endpoint_coordinates'] is not None:
        raise ValueError('The reach statement supplies no longitude or downstream endpoint')
    latitude = facts['upstream_latitude_context_degrees_north']
    if (isinstance(latitude, bool) or not isinstance(latitude, (int, float))
            or not math.isfinite(latitude) or not -90 <= latitude <= 90
            or facts['upstream_latitude_qualifier'] != 'near'):
        raise ValueError('Retain approximate latitude context, never a precise geographic gate')
    if facts['entity_id'] != 'current:'+facts['current_id']:
        raise ValueError('Current identity mismatch')
    if facts['source_kind'] != 'textbook_synthesis_not_a_new_observation_campaign':
        raise ValueError('Retain textbook synthesis evidence class')
    for field in PROHIBITED:
        if facts[field] is not False:
            raise ValueError('Unsupported promotion: '+field)
    return {'quantity': facts['quantity'], 'reported_value_km': value,
            'relation': facts['relation'], 'unit': 'km', 'display': f'{value:g} km',
            'reported_uncertainty_km': None, 'uncertainty_kind': 'not_reported_not_zero',
            'numeric_precision': facts['numeric_precision'],
            'study_window': None, 'time_support_kind': facts['time_support_kind'],
            'upstream_latitude_context_degrees_north': latitude,
            'upstream_latitude_qualifier': 'near',
            'upstream_longitude_degrees_east': None, 'downstream_endpoint_coordinates': None,
            'vertical_support': facts['vertical_support'], 'rank_eligible': False,
            'whole_current_length_km': None, 'physical_length_lower_bound_km': None,
            'physical_width_km': None, 'annual_or_seasonal_range': None,
            'current_geometry': None, 'state_intersections': None}


def source_check(facts):
    original = ROOT/ORIGINAL
    receipt = json.loads((ROOT/ACQUISITION).read_bytes())
    if (facts['original_file'] != ORIGINAL or facts['existing_acquisition_receipt'] != ACQUISITION
            or original.stat().st_size != facts['original_bytes']
            or sha(ORIGINAL) != facts['original_sha256']
            or facts['original_sha256'] != receipt['sha256']
            or receipt['bytes'] != facts['original_bytes']):
        raise ValueError('Original or existing custody differs')
    if (facts['current_id'] != 'brazil' or facts['entity_id'] != 'current:brazil'
            or facts['chapter_pdf_version'] != '1.2' or facts['chapter_pdf_version_month'] != '2002-09'
            or facts['first_printed_edition_year'] != 1994
            or facts['upstream_latitude_context_degrees_north'] != -10
            or facts['selected_pages_visually_reviewed_for_this_passage'] != [254, 255]):
        raise ValueError('Changed registered identity, approximate context or chapter version')
    with pymupdf.open(original) as doc:
        if len(doc) != facts['original_pdf_pages'] or len(doc) != 401:
            raise ValueError('Changed source compilation')
        passage = ' '.join(doc[253].get_text().split())
        continuation = ' '.join(doc[254].get_text().split())
        history = ' '.join(doc[1].get_text().split())
        if (facts['source_quote'] not in passage
                or f"Over the next {facts['reported_value_km']:g} km" not in facts['source_quote']
                or 'the Brazil Current, begins near 10°S' not in passage
                or 'between 33 and 38°S' not in continuation
                or '1.2 published September 2002' not in history
                or 'first edition was published by Pergamon in 1994' not in history):
            raise ValueError('Changed original number, object, continuation or version support')


def build():
    preflight = json.loads((ROOT/PREFLIGHT).read_bytes())
    if preflight['input_sha256'] != input_pins():
        raise ValueError('Frozen source or method inputs changed')
    facts = json.loads((ROOT/FACTS).read_bytes())
    value = constraint(facts)
    source_check(facts)
    return {'schema': 'osw.published-current-regional-reach.v2',
            'id': 'regional-reach:brazil:tomczak-ch14-2002-initial',
            'entity_id': facts['entity_id'], 'current_id': facts['current_id'],
            'status': 'source_reported_initial_regional_reach_observation_epoch_unspecified',
            'constraint': value,
            'source': {key: copy.deepcopy(facts[key]) for key in [
                'source_title', 'authors', 'first_printed_edition_year', 'chapter',
                'chapter_pdf_version', 'chapter_pdf_version_month', 'source_url', 'source_locator',
                'original_file', 'original_sha256', 'original_bytes', 'original_pdf_pages',
                'existing_acquisition_receipt', 'source_kind', 'source_copy_scope',
                'selected_pages_visually_reviewed_for_this_passage', 'source_quote',
                'upstream_context', 'downstream_context', 'redistribution']},
            'whole_current_evidence_status': 'unmeasured',
            **{key: False for key in PROHIBITED},
            'scope': 'Published initial regional reach beginning near 10 degrees south; no uniform observation epoch or measured endpoint coordinates supplied.',
            'derivation': 'Literal source value only. No distance calculation, unit conversion, digitization, piecewise sum or statistical inference.',
            'source_facts_phase': 'reviewed_before_frozen_report_execution',
            'protocol_file': PROTOCOL, 'input_sha256': preflight['input_sha256']}


def figure(report):
    c = report['constraint']
    display = html.escape(c['display'])
    description = ('Brazil Current initial regional reach reported as '+c['display']+
                   '. Beginning near 10 degrees south; downstream coordinates, observation dates and uncertainty unspecified. '
                   'Schematic only, not a map, whole-current length, physical lower bound, width or seasonal range.')
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 510" width="1000" height="510" role="img" aria-labelledby="title desc">',
        '<title id="title">Brazil Current: source-reported initial reach</title>',
        '<desc id="desc">'+html.escape(description)+'</desc>',
        '<rect width="1000" height="510" rx="14" fill="#f3f8fa"/>',
        '<g font-family="Arial,sans-serif" fill="#173342">',
        '<text x="45" y="48" font-size="25">Brazil Current · source-reported initial reach</text>',
        '<text x="45" y="83" font-size="17">Textbook synthesis · observation dates unspecified</text>',
        '<text x="45" y="153" font-size="44" font-weight="bold">'+display+'</text>',
        '<text x="45" y="188" font-size="17">Published round number; numerical uncertainty not reported</text>',
        '<path d="M100 244H885" stroke="#0c6b82" stroke-width="5"/>',
        '<path d="M100 232V256M885 232V256" stroke="#0c6b82" stroke-width="3"/>',
        '<text x="45" y="285" font-size="16">Begins near 10°S</text>',
        '<text x="568" y="285" font-size="16">Downstream coordinates unspecified</text>',
        '<text x="45" y="334" font-size="17">Whole-current length, physical width and seasonal ranges remain unknown.</text>',
        '<text x="45" y="370" font-size="15">Schematic segment, not a geographic axis or a physical length lower bound.</text>',
        '<text x="45" y="406" font-size="14">Tomczak &amp; Godfrey · Regional Oceanography: An Introduction · chapter 14, printed p244</text>',
        '<text x="45" y="437" font-size="14">Chapter PDF v1.2, September 2002; first printed edition 1994. Neither dates this reach.</text>',
        '<text x="45" y="468" font-size="14">Selected source pages reviewed; whole-book completeness has not been audited.</text>',
        '</g></svg>']
    return ('\n'.join(lines)+'\n').encode('utf8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['build', 'check'])
    args = parser.parse_args()
    report = build()
    outputs = {REPORT: encoded(report), FIGURE: figure(report)}
    # Validate the entire publication set before writing either product.
    for path, raw in outputs.items():
        target = ROOT/path
        if args.command == 'check' and (not target.exists() or target.read_bytes() != raw):
            raise ValueError('Changed or missing frozen product: '+path)
        if args.command == 'build' and target.exists() and target.read_bytes() != raw:
            raise ValueError('Refusing to overwrite a different frozen product: '+path)
    if args.command == 'build':
        for path, raw in outputs.items():
            (ROOT/path).write_bytes(raw)
    print(json.dumps({'status': 'PASS', 'products': {p: hashlib.sha256(b).hexdigest() for p, b in outputs.items()}}))


if __name__ == '__main__':
    main()
