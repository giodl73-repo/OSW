"""Retain local inflow extent and historical Hiri decay scales separately."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = 'plans/hiri-east-adriatic-local-width-protocol-v1.md'
SOURCES = {
    'hiri-current': ('hughes-hiri-1993', '587b39c55e7bdc9f2256e0c1d1634c504d4f7562bd5e0a9681e27300907a955d', 306),
    'east-adriatic': ('pasaric-adriatic-2019', 'dacc8e17c91b6cf5404a9e512f98e9f29047929ade0fb57862790f6315bc2ae5', 290),
}
AUDITS = {
    'hiri-current': 'research/hiri-hughes-1993-local-decay-scales-scope-audit.json',
    'east-adriatic': 'research/east-adriatic-pasaric-2019-inflow-extent-scope-audit.json',
}

def digest(file):
    return hashlib.sha256((ROOT / file).read_bytes()).hexdigest()

def write(file, value):
    path = ROOT / file
    eol = '\r\n' if path.exists() and b'\r\n' in path.read_bytes() else '\n'
    path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + '\n').replace('\n', eol).encode('utf8'))

def measurement(owner, name, ident, value, metric, label, scope, layer, time, boundary, locator, context):
    name_source, _, _ = SOURCES[owner]
    acq = json.loads((ROOT / f'research/source-data/{name_source}/acquisition.json').read_bytes())
    return {
        'id': ident, 'current_id': owner, 'name': name,
        'status': 'editorial_source_extraction_not_canonical',
        'measurement_type': 'published_regional_summary', 'phase_kind': 'regional_summary',
        'width_metric': metric, 'width_metric_label': label,
        'approximate_width_km': value, 'width_range_km': None,
        'range_kind': 'dated_local_point_descriptor_not_temporal_range',
        'range_interpretation': 'Author-reported local descriptor. No statistical error, full-current inference or annual range supplied.',
        'geographic_scope': scope, 'layer': layer, 'time_convention': time,
        'boundary_rule': boundary, 'section_geometry': None,
        'section_orientation': 'Author cross-section descriptor; no independent perpendicular correction or paired edge extraction.',
        'source_url': acq['source_url'] + ('#page=38' if owner == 'east-adriatic' else ''), 'source_citation': acq['attribution'],
        'source_locator': locator, 'source_retrieved_date': '2026-10-13',
        'source_evidence_kind': context['evidence_class'],
        'extraction_method': 'Numerical prose descriptor transcribed from reviewed original. Source figures inspected for context only; no curve or velocity boundaries digitized.',
        'whole_current_representative': False, 'width_rank_eligible': False,
        'full_width_inference_eligible': False, 'annual_extrema_eligible': False,
        'seasonal_playback_eligible': False, 'is_confidence_interval': False,
        'phase_label': context['display_title'],
        'observed_month': context.get('observed_month'),
        'time_precision': context['time_precision'], 'observed_period': None,
        'calendar_months': None, 'fixed_layer_bounds_m': None, 'uncertainty_km': None,
        'source_quality_note': context['quality_note'],
        'remaining_gates': ['Independent review of source naming, metric and local support before canonical admission.',
                            'Acquire raw sections and paired velocity edges for any full width; obtain compatible repeats before annual ranges.'],
        'original_regional_context': context,
    }

def build():
    import pymupdf
    for owner, (name, expected_sha, pages) in SOURCES.items():
        file = f'research/source-data/{name}/journal-article.pdf'
        if digest(file) != expected_sha:
            raise ValueError('Changed local measurement original: ' + owner)
        with pymupdf.open(ROOT / file) as pdf:
            if len(pdf) != pages:
                raise ValueError('Changed source page count')
            checks = [(28, ['Hiri Current', 'Chapter 3']), (85, ['50 km', 'e–folding']), (88, ['75 km', '350 m'])] if owner == 'hiri-current' else [(37, ['24-28 May 2017', 'first ~10 km', 'East Adriatic Current', '10 and 70 m'])]
            for index, terms in checks:
                text = ' '.join(pdf[index].get_text().split())
                if not all(term in text for term in terms):
                    raise ValueError('Changed reviewed numerical or ownership passage: ' + owner)
    common = {'description_kind': 'dated_local_descriptor', 'protocol_file': PROTOCOL,
              'protocol_sha256': digest(PROTOCOL), 'width_range_is_annual': False,
              'boundary_coordinates_extracted': False, 'source_figures_digitized': False,
              'full_width_conversion_admitted': False}
    hiri = []
    for year, value, section, locator, geography in [
        (1987, 50, 'TEW287 A87', 'Printed p70 / PDF86; Figure 3.15 printed p69 / PDF85; methods pp65-67 / PDF81-83.', 'A87 northern transect near Rossel Island, southern Papua coast, looking from the east.'),
        (1990, 75, 'Fr0690 B90', 'Printed p73 / PDF89; Figure 3.18 printed p75 / PDF91; July 1990 cruise map printed p74 / PDF90.', 'Eastern B90 transect across the Coral Sea between southern Papua and Queensland Plateau; detached current core context about 160 km offshore.'),
    ]:
        context = {**common,
            'evidence_class': 'primary_thesis_author_reported_local_geostrophic_decay_scale',
            'observed_month': f'{year}-07', 'time_precision': 'month',
            'historical_name_scope': 'Hughes introduction p13 / PDF29 calls chapter 3 Hiri Current. Chapter3 uses NGCU for a broader Coral Sea circulation under presumed Vitiaz connectivity. Only this southern-Papua study reach is indexed under Hiri; no modern north-coast NGCU alias or whole-circulation equivalence admitted.',
            'source_named_flow': 'Hiri in introduction; Coral Sea NGCU convention in chapter 3',
            'source_section': section, 'is_e_folding_scale': True,
            'is_full_edge_to_edge_width': False, 'is_gaussian_sigma': False,
            'numerical_width_error_supplied': False, 'same_site_repeat_pair': False,
            'two_july_cases_are_seasonal_extrema': False,
            'transport_reference_pressure_is_width_layer': False,
            'velocity_operator': 'author thermal-wind/geostrophic section analysis with reference-velocity assumptions; not independently reconstructed absolute ADCP velocity edges',
            'display_title': f'July {year} {section} e-folding scale',
            'display_aria_label': f'Hiri under Hughes historical southern-Papua convention: {value} km reported local e-folding scale in July {year}. Not full current width or annual range.',
            'display_caption': f'July {year}, {section}: approximately {value} km author-reported decay scale. A decay scale describes how rapidly the cross-section velocity decreases; it is not a full edge-to-edge width.',
            'display_method_note': 'Historical Hiri/Coral Sea NGCU source convention; northern modern NGCU is not assigned this value. July 1987 and July 1990 are different years and reaches, not seasonal extrema. Width depth support and paired boundaries unresolved.',
            'quality_note': 'Primary thesis inspected. Cross-section e-folding scalar has no supplied numeric error or reconstructed edges. Historical source naming and reference velocity require scope-specific interpretation.'}
        if year == 1990:
            context['core_depth_context_m'] = 350
            context['core_depth_is_width_layer'] = False
        hiri.append(measurement('hiri-current', 'Hiri Current', f'hiri-hughes-1993-{year}-07-local-decay-scale', value,
            'author_reported_e_folding_scale', 'local e-folding scale', geography,
            'Thermal-wind cross-section context; no numerical fixed-depth width layer. Transport integration to 1500 dbar does not define the width support.',
            f'July {year} cruise occupation; exact day unresolved. Different reaches and years are not a recurring seasonal series.',
            'Author e-folding scaling width; lateral fit, reference velocity and paired velocity edges not independently reconstructed. No theoretical full-width multiplier.',
            locator, context))
    context = {**common, 'evidence_class': 'primary_conference_abstract_local_ADCP_inflow_description',
        'time_precision': 'cruise_interval_context_exact_width_day_unresolved',
        'cruise_period': {'start': '2017-05-24', 'end': '2017-05-28'},
        'figure_section_date': '2017-05-28', 'figure_date_is_exact_width_day': False,
        'instrument_sample_depth_bounds_m': [10,70], 'instrument_bin_size_m': 4,
        'instrument_depth_bounds_are_fixed_width_layer': False,
        'figure_vector_depth_m': 10, 'figure_surface_placement_is_measurement_depth': False,
        'comparison_cruise_period': {'start': '2018-06-04', 'end': '2018-06-08'},
        'comparison_cruise_numeric_current_width_km': None,
        'pycnocline_upwelling_extent_km': 20, 'pycnocline_extent_is_current_width': False,
        'is_full_edge_to_edge_width': False, 'numerical_width_error_supplied': False,
        'display_title': 'May 2017 C1 coastal inflow extent',
        'display_aria_label': 'East Adriatic Current: about 10 km coastal inflow extent during 24-28 May 2017 near Primosten. Local ADCP description, not whole-current or annual width.',
        'display_caption': 'C1, 24-28 May 2017: inflow identified as part of EAC was confined to roughly the first 10 km offshore. This is a local coastal extent, with exact width occupation day unresolved.',
        'display_method_note': 'ADCP sampled 10-70 m; plotted surface arrows represent 10 m. The 20 km upwelling/pycnocline extent is a different object. C2 supplies no numeric EAC width, so no annual or seasonal range is inferred.',
        'quality_note': 'Author conference abstract and figure inspected; one local reported extent, no raw ADCP data or thresholded boundary pair. Exact width day and width at each sampled depth not independently resolved.'}
    eac = measurement('east-adriatic', 'East Adriatic Current', 'east-adriatic-pasaric-2019-c1-coastal-inflow-extent', 10,
        'author_reported_coastal_inflow_extent', 'local coastal inflow extent',
        'Primosten southwestward cross-section over the Middle Adriatic Pit, between Blitvenica and Jabuka; first approximately 10 km from the eastern coast.',
        'Vessel ADCP sampled 10-70 m in 4 m bins; author does not specify paired edges at a fixed depth. Figure 1 arrows represent 10 m despite surface placement.',
        'C1 cruise 24-28 May 2017; plotted section28 May 2017. Numeric prose extent belongs to C1; exact width occupation day unresolved. C2 June 2018 is not a second numeric width.',
        'Author-described limit of coastal inflow belonging to EAC; no numerical velocity threshold, coastline-edge reconstruction or perpendicular correction extracted.',
        'CIESM volume 42 (2019), printed p38 / PDF 38, methods and final current paragraph; Figure 1 caption.', context)
    rows_by_owner = {'hiri-current': hiri, 'east-adriatic': [eac]}
    all_rows = []
    for owner, rows in rows_by_owner.items():
        name, sha, pages = SOURCES[owner]
        directory = f'research/source-data/{name}'
        audit = {'schema': 'osw.local-current-width-descriptors-scope-audit.v1',
                 'status': 'editorial_source_review_not_scientific_admission', 'current_id': owner,
                 'source_document_file': directory+'/journal-article.pdf', 'source_document_sha256': sha,
                 'source_document_bytes': (ROOT/(directory+'/journal-article.pdf')).stat().st_size,
                 'source_document_pages': pages, 'acquisition_file': directory+'/acquisition.json',
                 'acquisition_sha256': digest(directory+'/acquisition.json'),
                 'protocol_file': PROTOCOL, 'protocol_sha256': digest(PROTOCOL),
                 'measurements': rows, 'visually_inspected_pdf_pages': [29,61,62,85,86,89,91] if owner == 'hiri-current' else [38]}
        write(AUDITS[owner], audit)
        for i, original in enumerate(rows):
            row = copy.deepcopy(original)
            row['original_regional_context'].update(audit_file=AUDITS[owner], audit_sha256=digest(AUDITS[owner]), audit_pointer=f'/measurements/{i}')
            all_rows.append(row)
    file = 'research/ocean-current-width-inventory.json'
    inventory = json.loads((ROOT/file).read_bytes())
    added_ids = {r['id'] for r in all_rows}
    inventory['measurements'] = [r for r in inventory['measurements'] if r['id'] not in added_ids] + all_rows
    for decision in inventory['current_decisions']:
        if decision['current_id'] in rows_by_owner:
            decision.update(width_decision='scoped_width_evidence_present',
                measurement_ids=[r['id'] for r in all_rows if r['current_id']==decision['current_id']],
                next_action='Resolve paired velocity boundaries, fixed width layers and compatible repeats. Current local descriptors are not full widths or annual ranges.')
    inventory['as_of'] = '2026-10-13'
    inventory['counts'].update(measurements=len(inventory['measurements']),
        currents_with_scoped_width_evidence=len({r['current_id'] for r in inventory['measurements']}),
        currents_not_assessed=sum(r['width_decision']=='width_not_assessed' for r in inventory['current_decisions']))
    write(file, inventory)
    print('Added local EAC inflow extent and two historical Hiri decay scales; annual/full-width values remain unresolved.')

if __name__ == '__main__':
    build()
