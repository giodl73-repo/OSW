"""Frozen qualitative annual descriptions, never measured monthly flow."""
import argparse
import copy
import hashlib
import html
import json
from pathlib import Path
import re
import unicodedata

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
FACTS = 'research/indian-current-direction-calendar-source-facts-v1.json'
IDENTITIES = 'research/indian-coastal-current-identity-review-v1.json'
PROTOCOL = 'plans/reported-current-direction-calendar-protocol-v1.md'
PREFLIGHT = 'research/reported-current-direction-calendar-preflight-v1.json'
REPORT = 'research/indian-current-reported-direction-calendars-v1.json'
FIGURE = 'figures/indian-current-reported-direction-calendars-v1.svg'
ORIGINAL = 'research/source-data/vinayachandran-indian-upwelling-2021/article.pdf'
ACQUISITION = 'research/source-data/vinayachandran-indian-upwelling-2021/acquisition.json'
INPUTS = ['analysis/reported_current_direction_calendars_v1.py',
          'analysis/test_reported_current_direction_calendars_v1.py',
          FACTS, IDENTITIES, PROTOCOL, ORIGINAL, ACQUISITION]
MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+'\n').encode('utf8')


def pin(path):
    with (ROOT/path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def input_pins():
    return {path: pin(path) for path in INPUTS}


def interval(start, end):
    for value in [start, end]:
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 12:
            raise ValueError('Integer source month1–12 required')
    return list(range(start, end+1)) if start <= end else list(range(start, 13))+list(range(1, end+1))


def calendar(profile):
    if not isinstance(profile['entity_id'], str) or not profile['entity_id'].startswith('current:'):
        raise ValueError('Current owner required')
    if profile['time_support_kind'] != 'source_described_annual_direction_pattern_not_monthly_observations':
        raise ValueError('Unsupported temporal evidence class')
    for key in ['observation_window', 'observation_year', 'velocity_m_s', 'length_km', 'width_km', 'annual_dimension_ranges']:
        if profile[key] is not None:
            raise ValueError('Unsupported observed or physical quantity: '+key)
    for key in ['physical_geometry_admitted', 'geographic_seasonal_playback_eligible', 'ranking_eligible']:
        if profile[key] is not False:
            raise ValueError('Unsupported promotion: '+key)
    directions = {}
    periods = profile['reported_periods']
    if not isinstance(periods, list) or not periods:
        raise ValueError('At least one explicit source period required')
    for period in periods:
        direction = period['direction']
        if direction not in ['northward', 'southward']:
            raise ValueError('Unsupported reported direction')
        for month in interval(period['start_month'], period['end_month']):
            if month in directions:
                raise ValueError('Overlapping or duplicate source periods')
            directions[month] = direction
    return [{'id': f"direction-description:{profile['id']}:{month:02d}",
             'entity_id': profile['entity_id'], 'month': month, 'month_label': MONTHS[month-1],
             'direction': directions.get(month),
             'value_status': 'reported_direction_regime' if month in directions else 'not_specified_by_source',
             'is_observation': False, 'observation_date': None, 'observation_year': None,
             'observed_velocity_m_s': None, 'physical_geometry': None, 'ranking_eligible': False}
            for month in range(1, 13)]


def normalized(page):
    return unicodedata.normalize('NFKC', ' '.join(re.sub(r'-\s*\n\s*', '', page.get_text()).split()))


def source_check(facts):
    retained = facts['retained_review_original']
    if retained['file'] != ORIGINAL or pin(ORIGINAL) != retained['sha256'] or (ROOT/ORIGINAL).stat().st_size != retained['bytes']:
        raise ValueError('Changed retained review original')
    acquisition = json.loads((ROOT/ACQUISITION).read_bytes())
    source_file = next(row for row in acquisition['files'] if row['path'] == ORIGINAL)
    if source_file['sha256'] != retained['sha256'] or source_file['bytes'] != retained['bytes']:
        raise ValueError('Changed original custody')
    wicc, eacc = facts['profiles']
    if (wicc['entity_id'] != 'current:west-india-coastal' or wicc['source_doi'] != '10.1007/BF02744586'
            or wicc['publication_year'] != 1998
            or wicc['access_scope'] != 'publisher_abstract_only_short_excerpt_retained'
            or wicc['full_original_asset_retained'] is not False or wicc['full_paper_reviewed'] is not False
            or wicc['full_original_asset_redistributed'] is not False
            or wicc['reported_periods'] != [dict(start_month=11, end_month=2, direction='northward'),
                                           dict(start_month=4, end_month=9, direction='southward')]):
        raise ValueError('Changed registered abstract support or period semantics')
    if hashlib.sha256(wicc['source_quote'].encode('utf8')).hexdigest() != '15794269fb9c2e7ad6bfb04c168d91cc770149b8eee90d993d745debf4af3c4c':
        raise ValueError('Changed retained abstract excerpt')
    if (eacc['entity_id'] != 'current:east-african-coastal' or eacc['source_doi'] != '10.5194/bg-18-5967-2021'
            or eacc['publication_year'] != 2021 or eacc['full_original_asset_retained'] is not True
            or eacc['full_original_asset_redistributed'] is not True or eacc['full_paper_reviewed'] is not False
            or eacc['reported_periods'] != [dict(start_month=1, end_month=12, direction='northward')]
            or eacc['access_scope'] != 'retained_full_original_selected_section_reviewed'):
        raise ValueError('Changed registered EACC support')
    with pymupdf.open(ROOT/ORIGINAL) as doc:
        if (eacc['source_quote'] not in normalized(doc[16])
                or 'current could flow in either direction' not in normalized(doc[25])
                or 'Creative Commons Attribution 4.0 License' not in normalized(doc[0])):
            raise ValueError('Original annual orientation, variability or rights support changed')
    identities = json.loads((ROOT/IDENTITIES).read_bytes())
    supported = {row['proposed_entity_id'] for row in identities['decisions']}
    if not {wicc['entity_id'], eacc['entity_id']} <= supported or facts['new_measurements_admitted'] != 0:
        raise ValueError('Missing separately gated identities or promoted measurements')


def build():
    preflight = json.loads((ROOT/PREFLIGHT).read_bytes())
    if preflight['input_sha256'] != input_pins():
        raise ValueError('Frozen scientific inputs changed')
    facts = json.loads((ROOT/FACTS).read_bytes())
    source_check(facts)
    profiles = []
    for source in facts['profiles']:
        rows = calendar(source)
        profile = {key: copy.deepcopy(source[key]) for key in [
            'id', 'entity_id', 'display_name', 'source_title', 'source_author', 'source_doi',
            'source_url', 'publication_year', 'source_locator', 'access_scope',
            'full_original_asset_retained', 'full_original_asset_redistributed',
            'full_paper_reviewed', 'rights_note', 'figure_source_label', 'time_support_kind']}
        profile.update(months=rows, source_quote_file=FACTS,
                       full_original_independently_checked=source['full_original_asset_retained'])
        profiles.append(profile)
    return {'schema': 'osw.reported-current-direction-calendars.v1',
            'quantity': 'qualitative_source_annual_direction_descriptions',
            'profiles': profiles, 'month_rows': sum(len(p['months']) for p in profiles),
            'independent_observations_added': 0, 'new_measurements_admitted': 0,
            'observation_window': None, 'annual_width_range_km': None, 'annual_length_range_km': None,
            'physical_geometry_admitted': False, 'geographic_seasonal_playback_eligible': False,
            'ranking_eligible': False, 'calendar_month_highlight_eligible': True,
            'canonical_identity_admission_status': facts['canonical_identity_admission_status'],
            'source_facts_file': FACTS, 'protocol_file': PROTOCOL,
            'unknown_month_meaning': facts['unassigned_month_rule'],
            'variability_note': facts['retained_review_original']['wicc_variability_note'],
            'input_sha256': preflight['input_sha256']}


def figure(report):
    desc = ('Source-described directions, not observations or forecasts. WICC: northward January, February, '
            'November, December; southward April to September; March and October unspecified. '
            'EACC: source-described northward orientation throughout the year. WICC can reverse on shorter timescales. '
            'No velocity, dimensions, seasonal envelope or physical geometry inferred.')
    lines = ['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="520" viewBox="0 0 1000 520" role="img" aria-labelledby="title desc">',
             '<title id="title">Source-described current direction calendars</title>',
             '<desc id="desc">'+html.escape(desc)+'</desc>',
             '<rect width="1000" height="520" rx="14" fill="#f3f8fa"/>',
             '<g font-family="Arial,sans-serif" fill="#173342">',
             '<text x="32" y="43" font-size="25">Source-described directions through the year</text>',
             '<text x="32" y="77" font-size="16">Annual descriptions, not monthly measurements or daily predictions</text>']
    for i, month in enumerate(MONTHS):
        lines.append(f'<text x="{311+53*i}" y="125" text-anchor="middle" font-size="14">{month}</text>')
    for index, profile in enumerate(report['profiles']):
        y = 146+80*index
        lines.extend([f'<text x="32" y="{y+27}" font-size="17">'+html.escape(profile['display_name'])+'</text>',
                      f'<text x="32" y="{y+50}" font-size="12">'+html.escape(profile['figure_source_label'])+'</text>'])
        for i, month in enumerate(profile['months']):
            direction = month['direction']
            symbol, fill = ('N', '#d4e9f0') if direction == 'northward' else ('S', '#eadfc9') if direction == 'southward' else ('?', '#e0e5e8')
            lines.extend([f'<rect x="{286+53*i}" y="{y}" width="49" height="57" rx="5" fill="{fill}"/>',
                          f'<text x="{311+53*i}" y="{y+37}" text-anchor="middle" font-size="24" font-weight="bold">{symbol}</text>'])
    lines.extend([
        '<text x="32" y="327" font-size="15">N: northward</text><text x="230" y="327" font-size="15">S: southward</text>',
        '<text x="425" y="327" font-size="15">?: not specified in the source summary</text>',
        '<text x="32" y="365" font-size="16">WICC can flow either way on shorter timescales; these labels are not guarantees.</text>',
        '<text x="32" y="395" font-size="16">Unspecified months are unknown, not zero flow or inferred transition phases.</text>',
        '<text x="32" y="433" font-size="13">WICC: Shetye 1998, publisher abstract only · doi:10.1007/BF02744586</text>',
        '<text x="32" y="459" font-size="13">EACC and WICC variability: Vinayachandran et al.2021 · doi:10.5194/bg-18-5967-2021</text>',
        '<text x="32" y="491" font-size="14">No velocity, width, length, annual dimension range or geographic flow field inferred.</text>',
        '</g></svg>'])
    return ('\n'.join(lines)+'\n').encode('utf8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['build', 'check'])
    args = parser.parse_args()
    report = build()
    outputs = {REPORT: encoded(report), FIGURE: figure(report)}
    for path, raw in outputs.items():
        target = ROOT/path
        if args.command == 'check' and (not target.exists() or target.read_bytes() != raw):
            raise ValueError('Changed frozen product: '+path)
        if args.command == 'build' and target.exists() and target.read_bytes() != raw:
            raise ValueError('Refusing to overwrite a different frozen product: '+path)
    if args.command == 'build':
        for path, raw in outputs.items():
            (ROOT/path).write_bytes(raw)
    print(json.dumps({'status': 'PASS', 'products': {p: hashlib.sha256(b).hexdigest() for p, b in outputs.items()}}))


if __name__ == '__main__':
    main()
