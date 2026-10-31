"""Validate a source-stage historical width constraint; no packet/field access."""
import json
from pathlib import Path

FACTS='research/eacc-dekeyzer-2012-cited-width-lower-bound-source-facts-v1.json'
ROOT=Path(__file__).resolve().parents[1]


def validate(facts):
    if (facts.get('schema')!='osw.review-cited-current-width-constraint-facts.v1'
        or facts.get('entity_id')!='current:east-african-coastal'
        or facts.get('current_id')!='east-african-coastal'):
        raise ValueError('Exact EACC source identity required')
    if (facts['original_sha256']!='2181591aeebb0dd1d0a0c701c48763ad5aa42e6d9dc59595e0171a627712a293'
        or facts['original_bytes']!=13230011 or facts['original_pdf_pages']!=154
        or facts['source']['urn']!='urn:nbn:de:gbv:46-00102543-14'
        or facts['source']['repository_publication_date']!='2012-02-09'
        or facts['source']['cover_date']!='2011-10'):
        raise ValueError('Original custody or date convention differs')
    if any(facts['passage'][k]!=v for k,v in {'pdf_page':74,'printed_page':56,'reference_pdf_page':95,'reference_printed_page':77}.items()):
        raise ValueError('Passage or reference locator differs')
    cited=facts['underlying_cited_work']
    if (cited['year_as_cited']!=1972 or cited['original_full_text_reviewed'] is not False
        or cited['original_file_sha256'] is not None or cited['edition_or_pagination_independently_verified'] is not False):
        raise ValueError('Unavailable original methods or edition promoted')
    if len(facts['records'])!=1:raise ValueError('One dependent historical constraint required')
    row=facts['records'][0]
    if (row['id']!='eacc-dekeyzer-2012-bell-cited-width-lower-bound'
        or row['entity_id']!=facts['entity_id'] or row['current_id']!=facts['current_id']
        or row['quantity']!='review_cited_regional_current_width_lower_bound'
        or row['reported_operator']!='gt' or type(row['reported_bound_km']) is not int
        or row['reported_bound_km']!=160 or row['lower_bound_km']!=160
        or row['lower_bound_exclusive'] is not True):
        raise ValueError('Exclusive source lower bound differs')
    unknown=['upper_bound_km','reported_width_km','width_range_km','annual_width_range_km',
        'reported_width_uncertainty_km','confidence_interval_km','observed_period','calendar_months',
        'section_latitude','fixed_layer_bounds_m','fixed_depth_level_m','geographic_edge_coordinates',
        'geometry','velocity_boundary_cutoff_m_s','sample_count']
    if any(key not in row or row[key] is not None for key in unknown):
        raise ValueError('Unknown support must remain explicitly null')
    for key in ['independent_observational_sample','underlying_original_measurement_methods_verified',
                'width_ranking_eligible','annual_extrema_eligible','seasonal_playback_eligible','whole_current_representative']:
        if row[key] is not False:raise ValueError('Dependent context promoted: '+key)
    if facts['installed_width_records_added']!=0 or facts['new_independent_observations']!=0 or facts['source_stage_only'] is not True:
        raise ValueError('Source preparation cannot claim runtime admission')
    return facts


if __name__=='__main__':
    validate(json.loads((ROOT/FACTS).read_bytes()))
    print('PASS: original-bound cited EACC constraint; no installed measurement added.')
