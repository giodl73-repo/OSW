"""A published strict regional width constraint; no finite mean or width axis."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = 'research/aleutian-onishi-2001-width-input.json'
ACQUISITION = 'research/source-data/onishi-aleutian-2001/acquisition.json'
PROTOCOL = 'plans/aleutian-onishi-width-admission-protocol-v1.md'
OPERATOR = 'analysis/aleutian_onishi_width.py'
NAMING = 'research/aleutian-alaskan-stream-naming-scope-audit.json'
FILE = 'research/aleutian-onishi-2001-width-admission.json'
CONTRACT = 'research/aleutian-onishi-2001-width-contract.json'
EXPORT = 'research/ocean-current-measurements-aleutian-edition.json'
BASE = 'research/ocean-current-measurements-neuc-edition.json'
FIGURE = 'figures/aleutian-onishi-2001-width-constraint.svg'
SOURCE = 'source:aleutian-onishi-2001'
ID = 'diagnostic:aleutian-onishi-2001-width-constraint'
WIDTH = 'aleutian-onishi-2001-published-width-constraint'
CURRENT = 'aleutian'
URL = 'https://doi.org/10.1023/A:1011178821299'


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode('utf8')


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def figure():
    # ASCII XML entities also keep units readable across locale-sensitive tooling.
    return b'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 560" role="img" tabindex="0" aria-labelledby="title desc">
<title id="title">Aleutian/Subarctic Current: published width greater than400km</title>
<desc id="desc">Onishi2001 describes the eastward Subarctic Current as wider than400km. An open circle at400 and rightward arrow show a strict lower constraint with unknown upper extent. No400km mean, finite range, width error, seasonal envelope or mapped edges. The westward Alaskan Stream is excluded.</desc>
<rect width="1000" height="560" fill="#edf5f8"/>
<g fill="#153e50" font-family="system-ui,sans-serif">
<text x="32" y="44" font-size="26" font-weight="700">Aleutian / Subarctic Current</text>
<text x="32" y="82" font-size="23">Published regional description: width &gt;400km</text>
<text x="32" y="121" font-size="17">Central subarctic North Pacific &#183; width layer and epoch unspecified</text>
<path d="M52 214H872" stroke="#93a5ae"/>
<path d="M548 200H871M855 190L872 200L855 210" stroke="#007d87" fill="none" stroke-width="4"/>
<circle cx="548" cy="200" r="7" fill="#edf5f8" stroke="#007d87" stroke-width="3"/>
<g font-size="17"><text x="46" y="248">0</text><text x="286" y="248">200</text><text x="529" y="248">400km</text></g>
<text x="610" y="176" font-size="18">Upper extent unknown</text>
<text x="32" y="300" font-size="18">Open threshold: greater than400, with no finite upper bound supplied.</text>
<text x="32" y="339" font-size="17">Southern front is diffuse and moves between years; no annual range or error.</text>
<text x="32" y="378" font-size="17">Study section/dates/reference depth are separate from this general width claim.</text>
<text x="32" y="417" font-size="17">No scalar mean, width buffer, state passage or seasonal animation inferred.</text>
<text x="32" y="467" font-size="15">Onishi2001 &#183; Journal of Oceanography57,79&#8211;91 &#183; Introduction,p79</text>
<text x="32" y="500" font-size="15">doi:10.1023/A:1011178821299 &#183; archived publisher PDF reviewed &#183; own scalar diagram</text>
</g></svg>'''


def build():
    s = json.loads((ROOT / INPUT).read_bytes())
    a = json.loads((ROOT / ACQUISITION).read_bytes())
    naming = json.loads((ROOT / NAMING).read_bytes())
    if (s['current_id'], s['source_name'], s['operator'], s['value_km']) != (CURRENT, 'Subarctic Current', '>', 400):
        raise ValueError('Changed source owner or strict width qualifier')
    if naming['alias'] != s['source_name'] or naming['distinct_proposed_current'] != 'alaskan-stream':
        raise ValueError('Changed current naming association')
    if a['sha256'] != 'be6298bc640d759c320b996d2249bd011795f50b799d8b832288ed0498e472ee' or a['bytes'] != 3403099 or a['pages'] != 13:
        raise ValueError('Changed archived publisher original')
    for key in ['approximate_width_km', 'width_range_km', 'reference_period', 'fixed_layer_bounds_m']:
        if s[key] is not None:
            raise ValueError('Invented finite width/period/layer: ' + key)
    for key in ['width_statement_is_study_estimator', 'rank_eligible', 'annual_extrema_eligible', 'seasonal_playback_eligible', 'new_geometry_admitted']:
        if s[key] is not False:
            raise ValueError('Promoted source constraint: ' + key)
    width = {'id': WIDTH, 'current_id': CURRENT, 'name': 'Aleutian Current',
        'status': 'editorial_source_extraction_not_historical_release', 'measurement_type': 'published_regional_summary',
        'phase_kind': 'source_reported_current_width_constraint', 'phase_label': 'Published regional lower constraint',
        'width_metric': 'author_reported_current_width_constraint', 'approximate_width_km': None, 'width_range_km': None,
        'reported_width_constraint': {'kind': 'author_reported_greater_than_current_width', 'operator': '>',
            'value_km': 400, 'source_notation': '>400 km', 'upper_bound_km': None, 'is_measured_extremum': False},
        'range_interpretation': 'Strict source-reported regional lower constraint; no finite upper bound, mean, annual range or width error.',
        'geographic_scope': 'Central subarctic North Pacific; general introductory width description, not a dated section estimate.',
        'layer': 'Width-evaluation layer unspecified. The hydrographic study reference depth does not supply a width slab.',
        'fixed_layer_bounds_m': None, 'reference_period': None, 'observed_period': None, 'calendar_months': None,
        'time_convention': 'Source publication2001; width observation epoch and annual/seasonal coverage unspecified.',
        'boundary_rule': s['boundary_context'], 'definition': 'Author-reported width greater than400km; paired numeric width edges unspecified.',
        'unit': 'km', 'source_file': FILE, 'source_pointer': '/width_records/0', 'source_id': SOURCE,
        'source_url': URL, 'source_locator': s['source_locator'], 'source_original_sha256': a['sha256'],
        'whole_current_representative': False, 'rank_eligible': False, 'width_rank_eligible': False,
        'annual_extrema_eligible': False, 'seasonal_playback_eligible': False, 'physical_edges_admitted': False,
        'full_width_inference_eligible': False, 'independent_new_observation': False}
    source = {'id': SOURCE, 'kind': 'external', 'label': a['attribution'], 'url': URL, 'doi': a['doi'],
        'source_url': a['url'], 'original_publisher_url': a['original_publisher_url'], 'source_file_sha256': a['sha256'],
        'source_pdf_bytes': a['bytes'], 'source_pages': a['pages'], 'archive_capture': a['archive_capture'],
        'source_locator': s['source_locator'], 'provider_asset_redistributed': False, 'rights_status': a['rights'],
        'material_use_class': 'source_scoped_factual_claim', 'used_in_collections': ['widths', 'diagnostics'],
        'metadata_status': 'Original publisher PDF recovered from archive and visually reviewed; factual extraction, no raw-field reproduction or independent approval.'}
    return {'schema': 'osw.aleutian-published-width-admission.v1', 'version': '1', 'id': ID,
        'status': 'source_reported_regional_constraint_not_field_reproduction', 'current_id': CURRENT,
        'width_records': [width], 'source_record': source, 'source_url': URL, 'figure_file': FIGURE,
        'excluded_neighbor': s['excluded_neighbor'], 'width_statement_is_study_estimator': False,
        'study_context': {'longitude_degrees_east': 180, 'start_year': 1990, 'end_year': 1998,
            'sampling_season': 'late June', 'geostrophic_reference_depth_m': 3000, 'is_width_support': False},
        'whole_current_width_km': None, 'annual_width_range_km': None, 'width_uncertainty_km': None,
        'new_geometry_admitted': False, 'seasonal_playback_eligible': False,
        'previous_component_diagnostics_promoted': False, 'independent_new_observations': 0,
        'input_sha256': {**{p: digest(p) for p in [INPUT, ACQUISITION, PROTOCOL, OPERATOR, NAMING]}, FIGURE: hashlib.sha256(figure()).hexdigest()}}


def export(doc):
    old = json.loads((ROOT / BASE).read_bytes())
    result = copy.deepcopy(old)
    result.update(version='0.6.0-draft-aleutian', previous_measurement_export=BASE, admission_file=FILE,
        additional_admission_files=old['additional_admission_files'] + [FILE], widths=old['widths'] + doc['width_records'],
        sources=old['sources'] + [doc['source_record']], scoped_width_count=len(old['widths']) + 1)
    result['scoped_width_owners'] = len({r['current_id'] for r in result['widths']})
    result['input_sha256'].update({BASE: digest(BASE), FILE: hashlib.sha256(encoded(doc)).hexdigest(), OPERATOR: digest(OPERATOR)})
    return result


def contract(doc):
    return {'schema': 'osw.aleutian-width-export-contract.v1', 'report_file': FILE,
        'report_sha256': hashlib.sha256(encoded(doc)).hexdigest(), 'export_file': EXPORT,
        'export_sha256': hashlib.sha256(encoded(export(doc))).hexdigest(),
        'previous_export_file': BASE, 'previous_export_sha256': digest(BASE)}


def verify_inputs():
    d = build()
    for p, raw in [(FILE, encoded(d)), (FIGURE, figure()), (EXPORT, encoded(export(d))), (CONTRACT, encoded(contract(d)))]:
        if (ROOT / p).read_bytes() != raw:
            raise ValueError('Changed Aleutian source admission: ' + p)
    return d, {**d['input_sha256'], **{p: digest(p) for p in [FILE, EXPORT, BASE, CONTRACT]}}


def diagnostic(doc):
    return {'id': ID, 'label': 'Aleutian published width: strict regional lower constraint',
        'entity_id': 'current:aleutian', 'current_id': CURRENT, 'rank_eligible': False,
        'source_file': FILE, 'source_file_sha256': digest(FILE), 'source_json': (ROOT / FILE).read_text(encoding='utf8'),
        'summary': {'source_constraint': '>400 km', 'finite_width_km': None, 'annual_width_range_km': None,
            'width_layer': None, 'width_epoch': None, 'source_field_reproduction': False}}


if __name__ == '__main__':
    doc = build()
    for p, raw in [(FILE, encoded(doc)), (FIGURE, figure()), (EXPORT, encoded(export(doc))), (CONTRACT, encoded(contract(doc)))]:
        (ROOT / p).write_bytes(raw)
    print(json.dumps({'widths': 170, 'owners': 85, 'strict_constraint': '>400 km'}))
