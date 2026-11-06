"""Prospective source-stage method; real-source execution requires frozen inputs."""
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
import copy
import argparse
import hashlib
import html
import json
import subprocess
from pathlib import Path
SOURCE_URL = 'https://www.met.nps.edu/~psguest/OC3570/CDROM/winter2008/Wallace/report.pdf'


NULL_FIELDS = ('whole_current_width_km', 'whole_current_length_km',
               'annual_width_range_km', 'seasonal_extrema', 'geometry')
TOP_FIELDS = set(NULL_FIELDS) | {
    'schema', 'status', 'current_id', 'source_review', 'source_sha256',
    'source_original_bytes', 'source_original_pdf_pages', 'source_type',
    'peer_review_verified', 'publication_date', 'reported_statements',
    'source_url', 'source_citation',
    'prospective_unit_convention', 'state_join_eligible',
    'physical_playback_eligible', 'canonical_admission_verified',
}
ROW_FIELDS = {
    'id', 'source_value', 'source_unit', 'source_unit_label', 'approximate', 'quantity_type',
    'depth_support', 'depth_interval_m', 'region', 'campaign_window',
    'exact_occupation_date', 'transect_normal_to_flow_verified',
    'paired_edge_coordinates', 'numeric_velocity_cutoff', 'uncertainty_nm',
    'converted_width_km_decimal', 'conversion_executed', 'source_locator',
    'independent_raw_values_reproduced', 'canonical_width_admitted',
}


def nautical_miles_to_km(value):
    if type(value) not in (int, str):
        raise ValueError('Use an integer or decimal source string, not bool or float')
    try:
        number = Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError('Invalid source quantity') from error
    if not number.is_finite() or number <= 0 or number > 1000:
        raise ValueError('Source quantity outside declared scope')
    with localcontext() as context:
        context.prec = 50
        return number * Decimal(1852) / Decimal(1000)


def validate(facts):
    if not isinstance(facts, dict) or set(facts)-TOP_FIELDS:
        raise ValueError('Unknown facts fields require a new reviewed method')
    if facts.get('schema') != 'osw.reported-regional-transect-width-facts.v1':
        raise ValueError('Unexpected facts schema')
    if facts.get('current_id') != 'davidson':
        raise ValueError('This method is scoped to Davidson')
    if facts.get('source_type') != 'course_cruise_report' or facts.get('peer_review_verified') is not False:
        raise ValueError('Preserve course-report support')
    if facts.get('publication_date') is not None:
        raise ValueError('Cruise dates are not publication dates')
    if facts.get('source_url') != SOURCE_URL or not isinstance(facts.get('source_citation'),str):
        raise ValueError('Preserve the directly inspected source and citation')
    for key in NULL_FIELDS:
        if key not in facts or facts[key] is not None:
            raise ValueError('No whole-current dimension, annual range or geometry')
    for key in ('state_join_eligible', 'physical_playback_eligible', 'canonical_admission_verified'):
        if facts.get(key) is not False:
            raise ValueError('Source production does not admit physical data')
    rows = facts.get('reported_statements')
    if not isinstance(rows, list) or len(rows) != 1:
        raise ValueError('Retain one source statement, not repeated samples')
    row = rows[0]
    if not isinstance(row, dict) or set(row)-ROW_FIELDS:
        raise ValueError('Unknown statement fields require a new reviewed method')
    if row.get('conversion_executed') is not False or row.get('converted_width_km_decimal') is not None:
        raise ValueError('Source facts cannot contain an already converted result')
    if row.get('source_unit') != 'nautical_mile' or row.get('source_unit_label') != 'NM' or row.get('approximate') is not True:
        raise ValueError('Keep the original approximate nautical-mile quantity')
    if row.get('quantity_type') != 'author_reported_regional_poleward_flow_transect_width':
        raise ValueError('Transect span is not an axis-normal width')
    if row.get('depth_support') != 'depth_averaged_interval' or row.get('depth_interval_m') != [27, 59]:
        raise ValueError('Preserve the explicitly associated depth average')
    if any(type(n) is not int for n in row['depth_interval_m']):
        raise ValueError('Invalid depth encoding')
    if row.get('campaign_window') != ['2008-01-23', '2008-01-30']:
        raise ValueError('Preserve the campaign window without inventing an occupation date')
    for key in ('exact_occupation_date', 'paired_edge_coordinates', 'numeric_velocity_cutoff', 'uncertainty_nm'):
        if key not in row or row[key] is not None:
            raise ValueError('Unspecified date, edges, cutoff and error must remain null')
    for key in ('transect_normal_to_flow_verified', 'independent_raw_values_reproduced', 'canonical_width_admitted'):
        if row.get(key) is not False:
            raise ValueError('No new axis, raw readback or canonical admission')
    if any(not isinstance(row.get(key), str) or not row[key].strip() for key in ('source_locator','region')):
        raise ValueError('Missing regional source scope')
    unit = facts.get('prospective_unit_convention')
    if (not isinstance(unit, dict) or type(unit.get('international_nautical_mile_m')) is not int
            or unit['international_nautical_mile_m'] != 1852
            or unit.get('exact_conversion_implies_exact_measurement') is not False):
        raise ValueError('Conversion convention or physical precision changed')
    nautical_miles_to_km(row['source_value'])


def products(facts):
    """Pure transform; actual source invocation must pass inspect_frozen_inputs."""
    validate(facts)
    report = copy.deepcopy(facts)
    report['schema'] = 'osw.reported-regional-transect-width-report.v1'
    report['status'] = 'source_stage_report_not_canonical_admission'
    row = report['reported_statements'][0]
    converted = nautical_miles_to_km(row['source_value'])
    row['converted_width_km_decimal'] = format(converted, 'f')
    row['conversion_executed'] = True
    row['conversion_factor_m_per_nautical_mile'] = 1852
    with localcontext() as context:
        context.prec = 50
        display = format(converted.quantize(Decimal(1), rounding=ROUND_HALF_UP), 'f')
    report['display_label'] = 'About ' + display + ' km'
    original = html.escape(str(row['source_value']))
    title = html.escape(report['display_label'])
    if converted > 100:
        raise ValueError('Source quantity exceeds the prospectively declared 0–100 km scalar diagram')
    with localcontext() as context:
        context.prec = 50
        marker = format((Decimal(50)+converted*5).quantize(Decimal('0.01')), 'f')
    figure = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 830" role="img" aria-labelledby="title description">
<title id="title">Davidson Current: reported regional transect width</title>
<desc id="description">Source reports about {original} nautical miles, normalized to {title}. An approximate poleward-flow transect span. Depth average 27–59 m, Line 67 off Monterey Bay. Campaign 23–30 January 2008; exact occupation date unknown. Course cruise report, not verified peer review. No paired edge coordinates, uncertainty or annual range supplied. No geographic axis or width footprint is drawn.</desc>
<rect width="600" height="830" fill="#08232b"/>
<g fill="#ecf4f2" font-family="sans-serif">
<text x="36" y="48" font-size="30">Davidson Current</text>
<text x="36" y="86" font-size="26">Line 67, Monterey Bay</text>
<text x="36" y="151" font-size="48">{title}</text>
<text x="36" y="192" font-size="26">Reported span · numerical scale</text>
<path d="M50 228H550 M50 220V236 M300 220V236 M550 220V236" fill="none" stroke="#b6c9ca" stroke-width="2"/>
<circle class="reported-value" cx="{marker}" cy="228" r="9" fill="#08232b" stroke="#68dfca" stroke-width="4"/>
<text x="50" y="273" font-size="26" text-anchor="middle">0</text>
<text x="300" y="273" font-size="26" text-anchor="middle">50 km</text>
<text x="550" y="273" font-size="26" text-anchor="middle">100</text>
<text x="36" y="319" font-size="26">Source: about {original} nautical miles</text>
<text x="36" y="362" font-size="26">27–59 m depth average</text>
<text x="36" y="402" font-size="26">Regional poleward-flow transect</text>
<text x="36" y="450" font-size="26">23–30 January 2008 campaign</text>
<text x="36" y="490" font-size="26">Exact occupation date unknown</text>
<text x="36" y="538" font-size="26">Edges/uncertainty unspecified</text>
<text x="36" y="578" font-size="26">No annual or whole-current width</text>
<text x="36" y="626" font-size="26">Coast-normal section.</text>
<text x="36" y="666" font-size="26">Flow-normal orientation not verified.</text>
<a href="{SOURCE_URL}" target="_blank" rel="noopener noreferrer"><text x="36" y="718" font-size="26" text-decoration="underline">Wallace · NPS-hosted course report</text></a>
<text x="36" y="758" font-size="26">Peer review unverified · PDF page 8</text>
<text x="36" y="802" font-size="26">Not a geographic width or footprint</text>
</g></svg>
'''
    return (json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False)+'\n').encode('utf-8'), figure.encode('utf-8')


def inspect_frozen_inputs(root, preflight_relative):
    """Fail closed before actual output if any pinned dependency differs."""
    root = Path(root).resolve()
    preflight = json.loads((root/preflight_relative).read_text(encoding='utf-8'))
    if preflight.get('schema') != 'osw.reported-regional-transect-width-preflight.v1':
        raise ValueError('Frozen preflight required')
    required = {'producer', 'tests', 'protocol', 'facts', 'acquisition',
                'unit_definition', 'width_rules', 'prose_rules',
                'source_review', 'environment', 'role_review'}
    if set(preflight.get('dependencies', {})) != required:
        raise ValueError('Incomplete frozen method or source dependencies')
    for expected in preflight['dependencies'].values():
        path = (root/expected['path']).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError('Input outside checkout or missing')
        data = path.read_bytes()
        if len(data) != expected['bytes'] or hashlib.sha256(data).hexdigest() != expected['sha256']:
            raise ValueError('Frozen input differs')
    facts_path = root/preflight['dependencies']['facts']['path']
    facts = json.loads(facts_path.read_text(encoding='utf-8'))
    expected_original = preflight['original']
    if (expected_original['sha256'] != 'e86d542866fcc58b593ced54815ec7bbc3e6bb7fb1f3b8d3079484bc22a3b037'
            or expected_original['bytes'] != 678350
            or facts.get('source_sha256') != expected_original['sha256']
            or facts.get('source_original_bytes') != expected_original['bytes']
            or facts.get('source_original_pdf_pages') != 30):
        raise ValueError('Wrong source edition or facts/source binding')
    anchors = preflight.get('source_page_anchors', [])
    if ({anchor['pdf_page'] for anchor in anchors} != {1, 8, 9, 22, 23}
            or len(anchors) != 5 or any(not anchor.get('anchors') for anchor in anchors)):
        raise ValueError('Complete selected-page anchors required')
    original = (root/preflight['original']['path']).resolve()
    if not original.is_relative_to(root) or not original.is_file():
        raise ValueError('Retained full original required')
    data = original.read_bytes()
    if len(data) != preflight['original']['bytes'] or hashlib.sha256(data).hexdigest() != preflight['original']['sha256']:
        raise ValueError('Original source differs')
    import pymupdf
    if pymupdf.VersionBind != preflight['runtime_requirements']['PyMuPDF']:
        raise ValueError('Use the pinned PDF parser for actual source verification')
    with pymupdf.open(stream=data, filetype='pdf') as document:
        if len(document) != 30:
            raise ValueError('Unexpected source edition/page count')
        for anchor in preflight['source_page_anchors']:
            text = ' '.join(document[anchor['pdf_page']-1].get_text().split())
            if any(' '.join(value.split()) not in text for value in anchor['anchors']):
                raise ValueError('Selected source passage differs')
    validate(facts)
    return facts


PREFLIGHT = 'research/davidson-wallace-2008-reported-width-preflight-v1.json'
REPORT = 'research/davidson-wallace-2008-reported-width-v1.json'
FIGURE = 'figures/davidson-wallace-2008-reported-width-v1.svg'


def verify_git_freeze(root, preflight_relative):
    preflight = json.loads((root/preflight_relative).read_text(encoding='utf-8'))
    paths = [preflight_relative] + [entry['path'] for entry in preflight['dependencies'].values()]
    for relative in paths:
        path = (root/relative).resolve()
        if not path.is_relative_to(root):
            raise ValueError('Frozen dependency outside checkout')
        committed = subprocess.check_output(
            ['git','-c','core.fsmonitor=false','show','HEAD:'+relative], cwd=root)
        if path.read_bytes() != committed:
            raise ValueError('Method must be committed unchanged before source execution: '+relative)
    return subprocess.check_output(['git','-c','core.fsmonitor=false','rev-parse','HEAD'],cwd=root,text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write',action='store_true',help='Create first immutable source report and scalar diagram')
    mode.add_argument('--verify',action='store_true',help='Replay and compare exact report and diagram bytes')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    commit = verify_git_freeze(root,PREFLIGHT)
    facts = inspect_frozen_inputs(root,PREFLIGHT)
    preflight_bytes = (root/PREFLIGHT).read_bytes()
    preflight = json.loads(preflight_bytes)
    raw,figure = products(facts)
    report = json.loads(raw)
    report['preflight_file'] = PREFLIGHT
    report['preflight_sha256'] = hashlib.sha256(preflight_bytes).hexdigest()
    report['input_sha256'] = {entry['path']:entry['sha256'] for entry in preflight['dependencies'].values()}
    raw = (json.dumps(report,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode('utf-8')
    expected = [(root/REPORT,raw),(root/FIGURE,figure)]
    exists = [path.exists() for path,_ in expected]
    if args.write and not any(exists):
        for path,data in expected:
            path.parent.mkdir(parents=True,exist_ok=True)
            with path.open('xb') as stream:stream.write(data)
    else:
        if not all(exists) or any(path.read_bytes()!=data for path,data in expected):
            raise ValueError('Source output missing or different; preserve executed products and version any correction')
    print(json.dumps({'status':'PASS','source_stage_only':True,'source_commit':commit,
                      'canonical_admission_verified':False,'independent_raw_values_reproduced':False,
                      'annual_width_range_admitted':False,'geometry_admitted':False,
                      'outputs':{str(path.relative_to(root)).replace('\\','/'):hashlib.sha256(data).hexdigest()
                                 for path,data in expected}},sort_keys=True))


if __name__ == '__main__':main()
