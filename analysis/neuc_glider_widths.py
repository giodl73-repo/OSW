"""Two source-reported jet ranges, not annual envelopes or new observations."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = 'research/neuc-glider-2015-width-source-input.json'
REVIEW = 'research/neuc-glider-2015-source-review.json'
PROTOCOL = 'plans/neuc-glider-width-admission-protocol-v1.md'
OPERATOR = 'analysis/neuc_glider_widths.py'
FILE = 'research/neuc-glider-2015-width-admissions.json'
EXPORT = 'research/ocean-current-measurements-neuc-edition.json'
BASE = 'research/ocean-current-measurements-asar-edition.json'
FIGURE = 'figures/neuc-glider-2015-width-ranges.svg'
SOURCE = 'source:neuc-schonau-rudnick-2015'
ID = 'diagnostic:neuc-glider-2015-width-ranges'
CURRENT = 'pacific-north-equatorial-undercurrent'


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode('utf8')


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def figure():
    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 650" role="img" tabindex="0" aria-labelledby="title desc">
<title id="title">Two NEUC jet width ranges at134.3E</title>
<desc id="desc">Southern jet near9.6N:100-350km; northern jet near13.1N:0-200km. Source-reported multi-year ranges from2009-2014, not annual envelopes or uncertainty. Zero is a source lower bound, not missing data. Southern broad cases may combine jets. No dated width samples or new current boundaries.</desc>
<rect width="1000" height="650" fill="#eef5f8"/>
<g fill="#123c50" font-family="system-ui,sans-serif">
<text x="32" y="44" font-size="26" font-weight="700">NEUC glider jet widths · 134.3°E</text>
<text x="32" y="78" font-size="19">Reported ranges · June2009–January2014 study window</text>
<text x="32" y="115" font-size="16">North–south extent of eastward geostrophic flow; density context26.7–27.3kg/m³.</text>
<text x="32" y="151" font-size="17">Southern jet · mean core9.6°N</text>
<path d="M222 183H697M222 173V193M697 173V193" stroke="#007c87" stroke-width="4"/>
<text x="730" y="190" font-size="22">100–350km</text>
<text x="32" y="231" font-size="16">Above300km: possible combined jets; not isolated edges at every section.</text>
<text x="32" y="279" font-size="17">Northern jet · mean core13.1°N</text>
<path d="M32 312H412M32 302V322M412 302V322" stroke="#8c5420" stroke-width="4"/>
<text x="460" y="319" font-size="22">0–200km</text>
<text x="32" y="360" font-size="16">Zero is the reported range endpoint. It does not supply a dated disappearance.</text>
<path d="M32 396H792" stroke="#6b8291"/>
<g font-size="16"><text x="32" y="420">0</text><text x="222" y="420">100</text><text x="412" y="420">200</text><text x="602" y="420">300</text><text x="792" y="420">400km</text></g>
<text x="32" y="466" font-size="17">These are different local jets, not one0–350km current envelope.</text>
<text x="32" y="501" font-size="17">No mean width, width error, annual extrema or seasonal animation inferred.</text>
<text x="32" y="536" font-size="16">Density levels are not fixed metre depths. Core excursions are not width edges.</text>
<text x="32" y="574" font-size="15">Schönau and Rudnick2015 · doi:10.1002/2014JC010595 · section3.1/Figure6</text>
<text x="32" y="607" font-size="15">Primary HTML inspected; no original file retained. Own scalar figure; no field reproduction.</text>
</g></svg>'''.encode('utf8')


def build():
    s = json.loads((ROOT / INPUT).read_bytes())
    review = json.loads((ROOT / REVIEW).read_bytes())
    if (s['current_id'], s['longitude_degrees_east'], s['density_averaging_source_values_kg_m3'], s['study_window']) != (
            CURRENT, 134.3, [26.7, 27.3], {'start_month': '2009-06', 'end_month': '2014-01'}):
        raise ValueError('Changed source identity, section, layer or study window')
    if [(r['jet'], r['mean_core_latitude_degrees_north'], r['width_range_km']) for r in s['reported_ranges']] != [
            ('southern', 9.6, [100, 350]), ('northern', 13.1, [0, 200])]:
        raise ValueError('Changed source ranges or jet assignments')
    if (s['raw_original_retained'] is not False or review['original_file_retained'] is not False
            or s['original_file_sha256'] is not None or review['original_file_sha256'] is not None
            or s['new_native_fields_acquired'] is not False or s['seasonal_playback_eligible'] is not False):
        raise ValueError('Invented source original or observation/playback admission')
    period = {**s['study_window'], 'interpretation': 'Study observation window; extrema dates and annual/seasonal extrema are not supplied.'}
    widths = []
    for r in s['reported_ranges']:
        widths.append({'id': 'neuc-glider-2015-' + r['jet'] + '-jet-range', 'current_id': CURRENT,
            'name': 'Pacific North Equatorial Undercurrent', 'jet': r['jet'],
            'status': 'editorial_source_extraction_not_historical_release',
            'measurement_type': 'published_regional_summary',
            'phase_kind': 'multi_year_jet_width_range', 'phase_label': r['jet'].title() + ' jet, 2009-2014 study',
            'definition': 'Meridional extent of eastward geostrophic velocity in source density context26.7-27.3kg/m3.',
            'time_convention': 'Repeat sections during June2009-January2014; no extrema dates or annual envelope.',
            'width_metric': 'source_reported_meridional_eastward_geostrophic_flow_extent',
            'approximate_width_km': None, 'width_range_km': r['width_range_km'], 'unit': 'km',
            'range_interpretation': 'Source-reported multi-year local jet variability; not annual bounds, uncertainty, a mean or full-current width.',
            'geographic_scope': f"134.3E section, {r['jet']} jet with mean core near{r['mean_core_latitude_degrees_north']}N",
            'source_reference_position_lon_lat': [134.3, r['mean_core_latitude_degrees_north']],
            'source_position_is_current_edge': False, 'source_position_is_approximate': True,
            'core_excursion_latitude_degrees_north': r['core_excursion_latitude_degrees_north'],
            'core_excursion_is_width': False, 'merging_context': r['merging_context'],
            'layer': 'Source potential-density averaging notation26.7-27.3kg/m3; no fixed metre-depth slab.',
            'density_averaging_source_values_kg_m3': [26.7, 27.3], 'fixed_layer_bounds_m': None,
            'boundary_rule': 'North/south extent of eastward absolute zonal geostrophic velocity in the source density averaging context.',
            'orientation': 'meridional section span, not independently diagnosed flow-normal width',
            'observed_period': None, 'reference_period': copy.deepcopy(period), 'calendar_months': None,
            'time_statistic': 'source_reported_range_across_repeat_sections', 'extrema_dates': None,
            'source_zero_lower_bound': r['width_range_km'][0] == 0,
            'source_file': FILE, 'source_pointer': f'/width_records/{len(widths)}',
            'source_id': SOURCE, 'source_url': s['source_url'], 'source_locator': s['source_locator'],
            'whole_current_representative': False, 'rank_eligible': False, 'annual_extrema_eligible': False,
            'seasonal_playback_eligible': False, 'physical_edges_admitted': False,
            'full_width_inference_eligible': False, 'independent_new_observation': False})
    source = {'id': SOURCE, 'kind': 'external', 'label': review['attribution'], 'url': s['source_url'],
        'doi': s['doi'], 'source_locator': s['source_locator'], 'source_review_file': REVIEW,
        'source_review_sha256': digest(REVIEW), 'factual_input_file': INPUT, 'factual_input_sha256': digest(INPUT),
        'original_file_retained': False, 'original_file_sha256': None,
        'provider_asset_redistributed': False, 'rights_status': review['rights'],
        'material_use_class': 'source_scoped_factual_claim', 'used_in_collections': ['widths', 'diagnostics'],
        'metadata_status': 'Primary HTML inspected; factual transcription pinned. No archived source original, raw-field reproduction or external scientific approval.'}
    return {'schema': 'osw.neuc-glider-width-admissions.v1', 'version': '1', 'id': ID,
        'status': 'source_reported_local_ranges_not_field_reproduction', 'current_id': CURRENT,
        'source_record': source, 'source_url': s['source_url'], 'width_records': widths,
        'reference_period': period, 'figure_file': FIGURE, 'source_original_retained': False,
        'new_native_fields_acquired': False, 'new_geometry_admitted': False,
        'whole_current_width_km': None, 'annual_width_range_km': None, 'width_uncertainty_km': None,
        'seasonal_playback_eligible': False, 'independent_new_observations': 0,
        'sampling_context': {'profile_spacing_approximate_km': 6, 'objective_mapping_gaussian_scale_km': 80,
            'sampling_scale_is_width_error': False, 'sections_are_instantaneous': False},
        'input_sha256': {**{p: digest(p) for p in [INPUT, REVIEW, PROTOCOL, OPERATOR]}, FIGURE: hashlib.sha256(figure()).hexdigest()}}


def export(doc):
    old = json.loads((ROOT / BASE).read_bytes())
    result = copy.deepcopy(old)
    result.update(version='0.5.0-draft-neuc', previous_measurement_export=BASE, admission_file=FILE,
        additional_admission_files=old['additional_admission_files'] + [FILE],
        widths=old['widths'] + doc['width_records'], sources=old['sources'] + [doc['source_record']],
        scoped_width_count=len(old['widths']) + 2)
    result['scoped_width_owners'] = len({w['current_id'] for w in result['widths']})
    result['input_sha256'].update({BASE: digest(BASE), FILE: digest(FILE), OPERATOR: digest(OPERATOR)})
    return result


def verify_inputs():
    d = build()
    for path, raw in [(FILE, encoded(d)), (FIGURE, figure()), (EXPORT, encoded(export(d)))]:
        if (ROOT / path).read_bytes() != raw:
            raise ValueError('Changed NEUC factual report/export: ' + path)
    return d, {**d['input_sha256'], **{p: digest(p) for p in [FILE, EXPORT, BASE]}}


def diagnostic(doc):
    return {'id': ID, 'label': 'NEUC glider jet width ranges: two local jets',
        'entity_id': 'current:' + CURRENT, 'current_id': CURRENT, 'rank_eligible': False,
        'source_file': FILE, 'source_file_sha256': digest(FILE), 'source_json': (ROOT / FILE).read_text(encoding='utf8'),
        'summary': {'local_jet_ranges': 2, 'reference_period': doc['reference_period'],
            'annual_width_range_km': None, 'source_original_retained': False, 'source_field_reproduction': False}}


if __name__ == '__main__':
    doc = build()
    (ROOT / FILE).write_bytes(encoded(doc))
    (ROOT / FIGURE).write_bytes(figure())
    (ROOT / EXPORT).write_bytes(encoded(export(doc)))
    print(json.dumps({'widths': 169, 'owners': 84, 'new_local_jet_ranges': 2}))
