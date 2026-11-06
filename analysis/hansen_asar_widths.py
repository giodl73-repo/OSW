"""Curated source reports; mixed profiles are not separate-current widths."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILE = 'research/hansen-2011-asar-surface-width-admissions.json'
EXPORT = 'research/ocean-current-measurements-asar-edition.json'
BASE = 'research/ocean-current-live-measurements.json'
PROTOCOL = 'plans/hansen-asar-width-admission-protocol-v1.md'
OPERATOR = 'analysis/hansen_asar_widths.py'
ACQUISITION = 'research/source-data/hansen-asar-2011/acquisition.json'
FIGURE = 'figures/hansen-2011-asar-surface-widths.svg'
SOURCE = 'source:hansen-asar-2011'
ID = 'diagnostic:hansen-asar-2011-surface-widths'
URL = 'https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2011JC007375'
PERIOD = {'start_month': '2007-08', 'end_month': '2010-07',
          'interpretation': 'Weighted mean surface field, not instantaneous width averaging or a seasonal sequence.'}


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode('utf8')


def figure():
    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 620" role="img" aria-labelledby="title desc" tabindex="0">
<title id="title">ASAR local surface-width reports, August2007–July2010 mean</title>
<desc id="desc">Three separately scoped reports: NwASC at P1,60km FWHM; NwASC at S1,36km conditional on an isobath partition; NCC near64N,30km with unspecified width boundary rule. Mixed45km P2 and60km S1 profiles are excluded from separate-current widths. No annual envelope or width error is supplied.</desc>
<rect width="1000" height="620" fill="#081c2c"/>
<g fill="#eef6ff" font-family="system-ui,sans-serif">
<text x="36" y="45" font-size="25" font-weight="700">Local surface widths from an ASAR mean field</text>
<text x="36" y="76" font-size="17">August2007–July2010 · source reports · different local operators</text>
<text x="36" y="122" font-size="18">Norwegian Atlantic Slope Current · P1</text>
<rect x="36" y="140" width="480" height="20" fill="#61d8e8"/>
<text x="535" y="157" font-size="20">60km FWHM</text>
<text x="36" y="190" font-size="16">62°N,0.5°W · projected surface Doppler profile</text>
<text x="36" y="238" font-size="18">Norwegian Atlantic Slope Current · S1</text>
<rect x="36" y="256" width="288" height="20" fill="#e6ba72"/>
<text x="345" y="273" font-size="20">36km · conditional partition</text>
<text x="36" y="306" font-size="16">62.8°N,4.25°E · separates signals using the200m isobath</text>
<text x="36" y="354" font-size="18">Norwegian Coastal Current · Haltenbanken–Frøya</text>
<rect x="36" y="372" width="240" height="20" fill="#9be2bb"/>
<text x="297" y="389" font-size="20">~30km · boundary rule unspecified</text>
<text x="36" y="422" font-size="16">Near64°N,9°E · local surface-jet description</text>
<path d="M36 453H964" stroke="#7992a7"/>
<text x="36" y="484" font-size="17">Excluded mixed profiles: P2,45km; S1,60km (NwASC + NCC).</text>
<text x="36" y="516" font-size="16">Widths of a mean field. No seasonal range, physical edges or width error.</text>
<text x="36" y="548" font-size="16">Bars share8px/km; colors separate operators, not confidence levels.</text>
<text x="36" y="589" font-size="15">Hansen etal(2011),doi:10.1029/2011JC007375,paragraphs9–12. OSW factual summary.</text>
</g></svg>
'''.encode('utf8')


def build():
    a = json.loads((ROOT / ACQUISITION).read_bytes())
    if (a['doi'], a['sha256'], a['bytes'], a['pages']) != (
            '10.1029/2011JC007375', 'd17a4411e92d5603c1692583a7740b1dcde0048a794617118cfa9fa606027584', 3067007, 13):
        raise ValueError('Changed ASAR source identity or original custody')
    rows = []
    for suffix, current, name, value, location, position, metric, rule, conditional, locator in [
        ('p1-fwhm', 'norwegian-atlantic-slope', 'Norwegian Atlantic Slope Current', 60,
         'P1', [-.5, 62], 'source_reported_surface_range_doppler_fwhm',
         'Full width at half maximum of the mean surface range-Doppler profile; not a flow-normal in-situ boundary.', False, 'Paragraph10; original PDF page3'),
        ('s1-isobath-partition', 'norwegian-atlantic-slope', 'Norwegian Atlantic Slope Current', 36,
         'S1, Svinoy section', [4.25, 62.8], 'source_reported_surface_isobath_partition_width',
         'Authors partition NwASC and NCC signals at the200m isobath. Bathymetric separation assumption, not a sampling depth or observed current interface.', True, 'Paragraph10; original PDF page3'),
        ('ncc-haltenbanken-froya', 'norwegian-coastal', 'Norwegian Coastal Current', 30,
         'Between Haltenbanken and Froya, near64N9E', [9, 64], 'source_reported_local_surface_jet_width',
         'Local jet width description; source paragraph12 does not explicitly restate FWHM or numeric edge positions.', False, 'Paragraph12; original PDF page5')]:
        rows.append({'id': 'hansen-asar-2011-' + suffix, 'current_id': current, 'name': name,
            'status': 'editorial_source_extraction_not_historical_release',
            'measurement_type': 'published_regional_summary', 'width_metric': metric,
            'approximate_width_km': value, 'width_range_km': None, 'unit': 'km',
            'range_interpretation': 'One local width description of a weighted mean field; no width error or variability range supplied.',
            'geographic_scope': location, 'source_reference_position_lon_lat': position,
            'source_position_is_current_edge': False, 'source_position_is_approximate': current == 'norwegian-coastal',
            'layer': 'Radar surface-scattering current signal; no fixed subsurface integration slab.',
            'fixed_layer_bounds_m': None, 'boundary_rule': rule,
            'conditional_on_isobath_partition': conditional,
            'observed_period': None, 'reference_period': copy.deepcopy(PERIOD),
            'time_statistic': 'width_description_of_weighted_mean_surface_velocity_field',
            'mean_instantaneous_width': False, 'calendar_months': None,
            'source_file': FILE, 'source_pointer': f'/width_records/{len(rows)}',
            'source_id': SOURCE, 'source_url': URL, 'source_locator': locator,
            'whole_current_representative': False, 'rank_eligible': False,
            'annual_extrema_eligible': False, 'seasonal_playback_eligible': False,
            'physical_edges_admitted': False, 'full_width_inference_eligible': False,
            'independent_new_observation': False})
    source = {'id': SOURCE, 'kind': 'external', 'label': a['attribution'], 'url': URL,
              'doi': a['doi'], 'source_url': a['source_url'], 'repository_record_url': a['repository_record_url'],
              'source_file_sha256': a['sha256'], 'source_pdf_bytes': a['bytes'],
              'provider_asset_redistributed': False, 'rights_status': a['source_license'],
              'source_locator': 'Original PDF pages3-5,paragraphs9-12 and Figure2',
              'material_use_class': 'source_scoped_factual_claim',
              'used_in_collections': ['widths', 'diagnostics'], 'metadata_status': 'Original source inspected; internal editorial extraction, no external scientific approval.'}
    return {'schema': 'osw.hansen-asar-width-admissions.v1', 'version': '1', 'id': ID,
            'status': 'source_reported_local_widths_not_source_field_reproduction',
            'source_record': source, 'source_url': URL, 'width_records': rows,
            'reference_period': copy.deepcopy(PERIOD), 'figure_file': FIGURE,
            'mixed_contexts': [
                {'id': 'p2-possibly-mixed', 'width_km': 45, 'source_reference_position_lon_lat': [3, 62 + 40 / 60],
                 'scope': 'P2 where slope and coastal signals align; possible mixing is not resolved by an independently isolated profile.', 'separate_current_width_admitted': False},
                {'id': 's1-combined-profile', 'width_km': 60, 'source_reference_position_lon_lat': [4.25, 62.8],
                 'scope': 'S1 explicitly combines NwASC and NCC surface drift; ASAR does not automatically separate the signals.', 'separate_current_width_admitted': False}],
            'output_grid_km': [5, 5], 'source_stated_spatial_resolution_km': 10,
            'velocity_rmse_is_width_error': False, 'whole_current_width_km': None,
            'annual_width_range_km': None, 'seasonal_playback_eligible': False,
            'independent_new_observations': 0, 'new_geometry_admitted': False,
            'input_sha256': {**{p: digest(p) for p in [PROTOCOL, OPERATOR, ACQUISITION]}, FIGURE: hashlib.sha256(figure()).hexdigest()}}


def export(doc):
    old = json.loads((ROOT / BASE).read_bytes())
    result = copy.deepcopy(old)
    result.update(version='0.4.0-draft-asar', previous_measurement_export=BASE,
                  admission_file=FILE, additional_admission_files=old['additional_admission_files'] + [FILE],
                  widths=old['widths'] + doc['width_records'], sources=old['sources'] + [doc['source_record']],
                  scoped_width_count=len(old['widths']) + 3)
    result['scoped_width_owners'] = len({r['current_id'] for r in result['widths']})
    result['input_sha256'].update({BASE: digest(BASE), FILE: digest(FILE), OPERATOR: digest(OPERATOR)})
    return result


def verify_inputs():
    doc = build()
    for p, data in [(FILE, encoded(doc)), (FIGURE, figure()), (EXPORT, encoded(export(doc)))]:
        if (ROOT / p).read_bytes() != data:
            raise ValueError('Changed ASAR source report/export: ' + p)
    return doc, {**doc['input_sha256'], **{p: digest(p) for p in [FILE, EXPORT, BASE]}}


def diagnostic(doc, current='norwegian-atlantic-slope'):
    if current not in ['norwegian-atlantic-slope', 'norwegian-coastal']:
        raise ValueError('Unknown ASAR diagnostic owner')
    return {'id': ID if current == 'norwegian-atlantic-slope' else ID + ':coastal',
            'label': 'ASAR local surface widths: separate and mixed signals',
            'entity_id': 'current:' + current, 'current_id': current, 'rank_eligible': False,
            'source_file': FILE, 'source_file_sha256': digest(FILE),
            'source_json': (ROOT / FILE).read_text(encoding='utf8'),
            'summary': {'admitted_local_widths': sum(r['current_id'] == current for r in doc['width_records']),
                        'comparison_total_widths': 3, 'excluded_mixed_profiles': 2,
                        'reference_period': PERIOD, 'annual_width_range_km': None,
                        'source_field_reproduction': False}}


if __name__ == '__main__':
    doc = build()
    (ROOT / FILE).write_bytes(encoded(doc))
    (ROOT / FIGURE).write_bytes(figure())
    (ROOT / EXPORT).write_bytes(encoded(export(doc)))
    print(json.dumps({'width_records': 3, 'excluded_mixed_profiles': 2, 'scoped_width_total': 167, 'width_owners': 84}))
