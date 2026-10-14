"""Extract one dated author width while retaining unresolved range units."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = 'research/caribbean-duncan-1982-dated-width-scope-audit.json'
PROTOCOL = 'plans/caribbean-dated-width-protocol-v1.md'
DIRECTORY = 'research/source-data/duncan-caribbean-1982'
SOURCE_SHA = 'df7041ed36e8e2d4019f4a0a8e59bdbd76ab1e516c2d9e6f423bf1a69f666377'

def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()

def write(path, value):
    destination = ROOT / path
    # Preserve the established file's line endings.
    newline = '\r\n' if destination.exists() and b'\r\n' in destination.read_bytes() else '\n'
    destination.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + '\n').replace('\n', newline).encode('utf8'))

def build():
    import pymupdf
    source = DIRECTORY + '/journal-article.pdf'
    if digest(source) != SOURCE_SHA:
        raise ValueError('Changed Caribbean original PDF')
    with pymupdf.open(ROOT / source) as pdf:
        text = ' '.join(pdf[10].get_text().split())
        if len(pdf) != 12 or not all(term in text for term in ['410', 'October 1974', '108 nautical', '225 miles', 'Los Roques']):
            raise ValueError('Original Caribbean width passage differs')
    context = {
        'description_kind': 'dated_geostrophic_mainstream_section',
        'width_passage_visually_inspected': True,
        'underlying_width_methods_reviewed': False,
        'full_study_reproduced': False,
        'source_observed_month': '1974-10',
        'section_longitude_degrees_east': -67,
        'southern_limit_latitude_degrees_north': 12,
        'southern_limit_kind': 'author_selected_Los_Roques_geographic_limit',
        'reference_pressure_dbar': 1600,
        'reference_pressure_is_width_layer': False,
        'typical_station_spacing_nautical_miles': 60,
        'station_spacing_is_width_uncertainty': False,
        'boundary_coordinates_extracted': False,
        'map_buffer_eligible': False,
        'historical_maximum_is_annual_extremum': False,
        'range_context': {'raw_endpoints': [108,225], 'raw_units': ['nautical_miles','miles_unqualified'],
                          'upper_unit_resolved': False, 'normalized_range_km': None,
                          'source_figure_year_labels': [1973,1974,1975]},
        'speed_context': {'associated_october_1974_cm_s': 66, 'associated_october_1974_m_s': 0.66,
                          'reported_mainstream_speed_range_cm_s': [41,76],
                          'reported_mainstream_speed_range_m_s': [0.41,0.76],
                          'operator': 'author_reported_geostrophic_station_pair_surface_speeds',
                          'is_width_uncertainty': False},
        'protocol_file': PROTOCOL, 'protocol_sha256': digest(PROTOCOL),
        'display_title': 'October 1974 mainstream section',
        'display_aria_label': 'Caribbean Current: approximately 410 km reported mainstream span at 67 W in October 1974. Southern limit fixed at Los Roques; paired velocity boundaries unresolved. No annual range or uncertainty supplied.',
        'display_caption': 'October 1974 at 67 W: approximately 410 km author-reported mainstream span, with associated surface-geostrophic speed 0.66 m/s. Reference pressure 1600 dbar is not a depth slab. Numerical uncertainty and annual range unknown.',
        'display_method_note': 'Southern limit fixed at Los Roques, 12 N; typical stations 60 nautical miles apart. The separate historical 108 nautical miles to 225 miles range retains an unresolved upper unit. No mapped edges or seasonal animation inferred.',
    }
    measurement = {
        'id': 'caribbean-duncan-1982-october-1974-mainstream-width',
        'current_id': 'caribbean', 'name': 'Caribbean Current',
        'status': 'editorial_source_extraction_not_canonical',
        'measurement_type': 'published_regional_summary', 'width_metric': 'author_reported_current_width',
        'width_metric_label': 'dated meridional mainstream span',
        'approximate_width_km': 410, 'width_range_km': None,
        'range_kind': 'dated_reported_point_with_unresolved_separate_range_units',
        'range_interpretation': 'One reported October value. Separate historical range has unresolved upper units; no numerical range, confidence interval or annual extrema admitted.',
        'geographic_scope': 'Southern Caribbean mainstream on the Puerto Rico-Venezuela meridian, 67 W.',
        'section_geometry': None, 'section_orientation': 'Meridional section; no perpendicular-to-axis correction reproduced.',
        'layer': 'Geostrophic sea-surface current relative to 1600 dbar. No fixed numerical width layer.',
        'time_convention': 'October 1974 author-reported section description. Exact observation day unknown; not a climatology or an annual maximum.',
        'boundary_rule': 'Southern limit selected geographically at Los Roques, 12 N. Northern edge method not independently reproduced; no paired velocity-boundary coordinates extracted.',
        'source_url': 'https://journals.lib.unb.ca/index.php/ihr/article/view/23548',
        'source_citation': 'Duncan, Schladow and Williams (1982), Surface Currents Near the Greater and Lesser Antilles, International Hydrographic Review 59(2), 67-78. Archive upload 2015.',
        'source_locator': 'Printed p77 / PDF p11, mainstream width bullet; p76 / PDF p10 methods and Figure 10 caption.',
        'source_retrieved_date': '2026-10-13', 'source_evidence_kind': 'published_original_dated_section_description',
        'extraction_method': 'Explicit kilometre value transcribed from visually inspected original prose; no figure boundary digitization.',
        'whole_current_representative': False, 'width_rank_eligible': False, 'full_width_inference_eligible': False,
        'annual_extrema_eligible': False, 'seasonal_playback_eligible': False, 'is_confidence_interval': False,
        'phase_label': 'October 1974 mainstream at 67 W', 'phase_kind': 'regional_summary',
        'observed_month': '1974-10', 'time_precision': 'month', 'observed_period': None, 'calendar_months': None,
        'fixed_layer_bounds_m': None, 'uncertainty_km': None,
        'source_quality_note': 'Original paper inspected. Coarse station sampling and geographic southern boundary limit interpretation. Underlying 1976 section study and raw stations not independently reproduced; mixed range units unresolved.',
        'remaining_gates': ['Recover original section stations and paired velocity-edge rule.',
                            'Resolve the historical upper-endpoint mile unit.',
                            'Obtain compatible repeats before annual margins; independent scientific review.'],
        'original_regional_context': context,
    }
    audit = {'schema':'osw.caribbean-dated-width-scope-audit.v1', 'status':'editorial_source_review_not_scientific_admission',
             'source_document_file':source, 'source_document_sha256':SOURCE_SHA, 'source_document_bytes':1523058,
             'source_document_pages':12, 'acquisition_file':DIRECTORY+'/acquisition.json',
             'acquisition_sha256':digest(DIRECTORY+'/acquisition.json'), 'protocol_file':PROTOCOL,
             'protocol_sha256':digest(PROTOCOL), 'visually_inspected_pdf_pages':[1,7,9,10,11],
             'publication_year':1982, 'archive_upload_date':'2015-07-14', 'measurement':measurement}
    write(AUDIT,audit)
    row=copy.deepcopy(measurement)
    row['original_regional_context'].update(audit_file=AUDIT,audit_sha256=digest(AUDIT))
    inventory=json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())
    inventory['as_of']='2026-10-13'
    inventory['measurements']=[r for r in inventory['measurements'] if r['id'] != row['id']]+[row]
    decision=next(r for r in inventory['current_decisions'] if r['current_id']=='caribbean')
    decision.update(width_decision='scoped_width_evidence_present',measurement_ids=[row['id']],
                    next_action='Resolve historical range units and paired boundaries; obtain compatible repeated widths before annual margins.')
    inventory['counts']['measurements']=len(inventory['measurements'])
    inventory['counts']['currents_with_scoped_width_evidence']=len({r['current_id'] for r in inventory['measurements']})
    inventory['counts']['currents_not_assessed']=sum(r['width_decision']=='width_not_assessed' for r in inventory['current_decisions'])
    write('research/ocean-current-width-inventory.json',inventory)
    print('Caribbean: dated 410 km description; 128 records / 68 owners / 23 unassessed. Annual margins unresolved.')

if __name__ == '__main__':
    build()
