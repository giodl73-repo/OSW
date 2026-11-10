"""A separate slope-current identity, scoped source reports and working ranks."""
import copy
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import current_identity_admissions as identities
import agulhas_reported_dimensions as previous
import north_atlantic_gate_bound as nac
from build_ocean_motion_claims import review_fingerprint

ROOT = Path(__file__).resolve().parents[1]
ID = 'norwegian-atlantic-slope'
ENTITY = 'current:' + ID
FILE = 'research/norwegian-atlantic-slope-working-admission.json'
CATALOGUE = 'research/ocean-current-effective-catalogue.json'
EXPORT = 'research/ocean-current-live-measurements.json'
PROTOCOL = 'plans/nwasc-working-admission-protocol-v1.md'
OPERATOR = 'analysis/nwasc_working_admission.py'
FIGURE = 'figures/norwegian-atlantic-slope-admitted-dimensions.svg'
CUSTODY = 'research/source-data/orvik-niiler-ices-2001/acquisition.json'
NAME_SOURCE = 'source:nwasc-baumann-2026'
LENGTH_SOURCE = 'source:nwasc-orvik-skagseth-2003'
CONTEXT_SOURCE = 'source:nwasc-orvik-niiler-2001-context'
MEASUREMENT_ID = 'measurement:norwegian-atlantic-slope:reported-extent'


def read(path):
    return json.loads((ROOT / path).read_bytes())


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def encoded(doc):
    return (json.dumps(doc, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')


def rank_assessments(rows):
    rows = copy.deepcopy(rows)
    ranked = [r for r in rows if r['rank_eligible']]
    for row in ranked:
        value = row['published_length_km']
        if value is None or value <= 0:
            raise ValueError('Ranked reported extent requires a positive value')
        row['published_rank'] = 1 + sum(r['published_length_km'] > value for r in ranked)
    return rows


def source_records():
    common = {'kind': 'external', 'material_use_class': 'source_scoped_factual_claim',
              'used_in_collections': ['entities', 'names', 'claims', 'measurements', 'widths', 'current_identity_admissions'],
              'metadata_status': 'Original source context inspected; working editorial admission, no external scientific approval.'}
    return [
        {**common, 'id': NAME_SOURCE, 'label': 'Baumann et al. (2026): Norwegian Atlantic Slope Current',
         'title': 'Reduced cooling in the Norwegian Atlantic Slope Current: investigating mechanisms of change from 30 years of observations',
         'doi': '10.5194/os-22-17-2026', 'url': 'https://os.copernicus.org/articles/22/17/2026/',
         'publication_date': '2026-01-05', 'rights_status': 'CC BY 4.0', 'provider_asset_redistributed': True,
         'repository_path': 'research/source-data/baumann-nwasc-2026/article.pdf',
         'credit_text': 'Baumann, Skagseth, Ingvaldsen and Mork (2026), Ocean Science 22, 17–29, CC BY 4.0.'},
        {**common, 'id': LENGTH_SOURCE, 'label': 'Orvik and Skagseth (2003): broad eastern shelf-edge branch extent',
         'title': 'The impact of the wind stress curl in the North Atlantic on the Atlantic inflow to the Norwegian Sea toward the Arctic',
         'doi': '10.1029/2003GL017932', 'url': 'https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2003GL017932',
         'publication_date': '2003-09-04', 'rights_status': 'Linked factual paraphrase; original article and figures not redistributed.',
         'provider_asset_redistributed': False, 'repository_path': None,
         'metadata_note': 'Original publisher full-text prose inspected through web retrieval. Direct HTML/PDF returned403. No original2003 PDF or figure custody claimed.'},
        {**common, 'id': CONTEXT_SOURCE, 'label': 'Orvik and Niiler (2001): eastern branch geographic context',
         'title': 'Circulation of Atlantic water in the northern North Atlantic and Nordic Seas',
         'doi': '10.17895/ices.pub.25636341.v1', 'url': 'https://doi.org/10.17895/ices.pub.25636341.v1',
         'publication_date': None, 'original_publication_year': 2001, 'repository_deposit_date': '2024-04-25',
         'rights_status': 'ICES Custom Licence. Only factual metadata and OSW paraphrase redistributed.',
         'provider_asset_redistributed': False, 'repository_path': CUSTODY,
         'metadata_note': 'Original17-page report verified against provider MD5 and locally inspected. Original PDF, rendered pages and abstract not redistributed; geographic context is not independent length measurement.'},
    ]


def historical_widths():
    from check_nordic_section_widths import proposed_records
    from nwasc_mean_core_widths import records
    rows = [r for r in proposed_records() + records() if r['proposed_current_id'] == ID]
    if len(rows) != 5 or len({r['id'] for r in rows}) != 5:
        raise ValueError('Renew slope-branch width migration review')
    return rows


def admitted_widths():
    rows = []
    for original in historical_widths():
        row = copy.deepcopy(original)
        old_id = row['id']
        row['id'] = 'admitted-width:nwasc:' + old_id
        row.pop('proposed_current_id')
        row.update(current_id=ID, canonical_current_id=ID,
                   status='working_scoped_source_report_admitted_not_historical_release',
                   admission_file=FILE, previous_proposed_record_id=old_id,
                   previous_proposed_source_file=original['source_file'],
                   previous_proposed_source_pointer=original['source_pointer'],
                   source_file=FILE, source_pointer='/width_records/' + str(len(rows)),
                   source_report_file=FILE, canonical_transfer_eligible=True,
                   whole_current_width_km=None, annual_width_range_km=None,
                   whole_current_representative=False, width_rank_eligible=False,
                   full_width_inference_eligible=False, rank_eligible=False,
                   annual_extrema_eligible=False, seasonal_playback_eligible=False,
                   is_confidence_interval=False, independent_new_observation=False,
                   geographic_current_edges=None, physical_current_envelope_admitted=False,
                   historical_release_admitted=False)
        row['phase_kind'] = row.get('phase_kind', 'source_scoped_width_description')
        row['phase_label'] = row.get('phase_label', 'Local source-reported width; no seasonal state')
        row['time_convention'] = row.get('time_convention', row.get('temporal_interpretation', 'Source timing unspecified.'))
        row['range_interpretation'] = row.get('range_interpretation', 'Source-reported regional span; not annual extrema, statistical error or a whole-current width range.')
        if 'original_regional_context' in row:
            context = row['original_regional_context']
            context['catalogue_identity_ambiguity_retained'] = False
            context['display_aria_label'] = 'Accepted Norwegian Atlantic Slope Current at Gimsøy: source-reported25–30km relative-geostrophic span; no annual extrema.'
            context['display_method_note'] = 'Surface-pressure reference; width integration limits unspecified. Effective20.1km mooring integration width and4km assumed error are separate. Identity admitted separately from Norwegian Current.'
        if 'source_quality_note' in row:
            row['source_quality_note'] = row['source_quality_note'].replace('Catalog naming ambiguity remains.', 'Slope-current identity admitted separately from the ambiguous Norwegian Current; physical edge geometry remains unresolved.')
        row['remaining_gates'] = ['Recover paired geographic edges and quantitative error before physical envelope admission.',
                                  'Acquire comparable repeated dated widths before seasonal or annual geometry.']
        rows.append(row)
    candidate = read('research/norwegian-atlantic-slope-orvik-2003-dimension-candidates.json')
    length, width = candidate['measurements']
    if (length['value_km'], width['value_km']) != (3500, 40):
        raise ValueError('Renew explicit Orvik prose dimensions')
    rows.append({'id':'admitted-width:nwasc:orvik2003-mean-flow-description','current_id':ID,
        'name':'Norwegian Atlantic Slope Current','status':'working_scoped_source_report_admitted_not_historical_release',
        'measurement_type':'published_mean_flow_width_description','width_metric':'width_of_described_annual_mean_flow',
        'approximate_width_km':40,'width_range_km':None,'range_kind':None,'unit':'km',
        'range_interpretation':'One contextual approximate mean-flow width, not annual extrema or mean instantaneous width.',
        'geographic_scope':'Svinøy section; not width along the full eastern shelf-edge branch.',
        'layer':'Unspecified. The200–900m isobaths describe slope bathymetry, not a fixed width layer.',
        'fixed_layer_bounds_m':None,'boundary_rule':'Author prose width of described annual-mean flow; edge cutoff and coordinates unspecified.',
        'observed_period':None,'calendar_months':None,'uncertainty_km':None,'section_geometry':None,
        'phase_kind':'published_mean_flow_width_description','phase_label':'Svinøy · undated annual-mean-flow description',
        'time_convention':'Averaging dates unspecified. Width of annual-mean flow is not mean instantaneous width.',
        'source_url':candidate['source']['url'],'source_citation':candidate['source']['citation'],
        'source_locator':'Introduction paragraph[4], Svinøy annual-mean description citing Orvik et al.(2001).',
        'source_access':'Original publisher full-text prose inspected through web retrieval2026-10-22. Direct HTML/PDF403; no original2003 PDF or figure custody.',
        'source_report_file':FILE,'source_file':FILE,'source_pointer':'/width_records/5','admission_file':FILE,
        'extraction_method':'Direct factual prose extraction; not a midpoint of the30–50km regional description.',
        'source_quality_note':'Cites earlier literature. Not independent corroboration of the related2001 width summary; bathymetry and transport periods are not width-layer or averaging metadata.',
        'related_measurement_ids':['admitted-width:nwasc:norwegian-atlantic-slope-orvik-2001-regional-width'],
        'source_report_type':'contextual_literature_mean_flow_description','is_mean_field_geometry':True,'is_mean_of_widths':False,
        'whole_current_representative':False,'whole_current_width_km':None,'annual_width_range_km':None,
        'annual_extrema_eligible':False,'seasonal_playback_eligible':False,'rank_eligible':False,'width_rank_eligible':False,
        'full_width_inference_eligible':False,'is_confidence_interval':False,'geographic_current_edges':None,
        'independent_new_observation':False,'physical_current_envelope_admitted':False,'historical_release_admitted':False})
    return rows


def figure():
    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1040 670" role="img" aria-labelledby="title desc">
<title id="title">Norwegian Atlantic Slope Current: separately scoped reported dimensions</title>
<desc id="desc">A source-reported approximate3500kilometre broad historical eastern-branch extent. Six local width records retain distinct definitions:30to50kilometre regional summary,50kilometre surface branch scale,25to30kilometre relative-geostrophic span two50kilometre static mean-core extents and one40kilometre contextual mean-flow width. These are not six independent new observations, a mapped axis, a whole-current width or a seasonal range.</desc>
<rect width="1040" height="670" fill="#eef6f8"/><g font-family="Arial, sans-serif" fill="#123c4b">
<text x="28" y="42" font-size="26" font-weight="bold">Norwegian Atlantic Slope Current · source reports</text>
<text x="28" y="91" font-size="34" font-weight="bold">≈ 3,500 km · broad historical eastern branch</text>
<text x="28" y="127" font-size="17">Orvik and Skagseth (2003), introduction [3]; not a dated or modern regional axis.</text>
<text x="28" y="158" font-size="17">Includes downstream context now named West Spitsbergen; lengths are not additive.</text>
<path d="M28 183H1012" stroke="#587681"/>
<text x="28" y="222" font-size="21" font-weight="bold">Six distinct local width records</text>
<text x="28" y="265" font-size="19">30–50 km · cited regional branch-width summary (Orvik et al., 2001)</text>
<text x="28" y="308" font-size="19">≈ 50 km · surface branch scale (Mork and Skagseth, 2010)</text>
<text x="28" y="351" font-size="19">25–30 km · Gimsøy relative-geostrophic span (Fer et al., 2020)</text>
<text x="28" y="394" font-size="19">≈ 50 km · Svinøy static mean core, 50 m plane (Baumann et al., 2026)</text>
<text x="28" y="437" font-size="19">≈ 50 km · Gimsøy static mean-core extent (Baumann et al., 2026)</text>
<text x="28" y="476" font-size="19">≈ 40 km · Svinøy mean-flow description (Orvik and Skagseth, 2003)</text>
<path d="M28 504H1012" stroke="#587681"/>
<text x="28" y="542" font-size="18">Distinct from Norwegian Current, Norwegian Coastal Current and western frontal branch.</text>
<text x="28" y="577" font-size="17">No paired geographic edges, annual range, whole-current width or physical state join.</text>
<text x="28" y="613" font-size="17">Historical proposal records remain traceable; six records are not six new observations.</text>
<text x="28" y="647" font-size="15">Original OSW scalar summary · primary source links and definitions in the working admission</text>
</g></svg>'''.encode('utf-8')


def build():
    from nwasc_mean_core_widths import verify_inputs as verify_mean, DIRECTORY
    mean, mean_pins = verify_mean()
    custody = read(CUSTODY)
    if (custody['verified_original_sha256'], custody['provider_md5'], custody['original_bytes']) != (
        '104ea7802b778a8bba44d44d74b01c43d96a7b59d109308c6449d4455354a93a',
        'c1aed50bebfb0c577d9203c938fbdc2f', 1090240):
        raise ValueError('Changed recovered ICES original custody')
    text = ' '.join(''.join(ET.parse(ROOT / (DIRECTORY + 'article.xml')).getroot().itertext()).split())
    for passage in ['Norwegian Atlantic Slope Current', 'Norwegian Atlantic Front Current', 'coastal current']:
        if passage not in text:
            raise ValueError('Missing primary identity distinction')
    proposal = next(r for r in read(identities.PROPOSALS)['entries'] if r['proposed_id'] == ID)
    if proposal['parent_proposed_id'] != 'norwegian-atlantic':
        raise ValueError('Changed proposed branch parent')
    sources = source_records()
    scope = ('Author-reported approximate3500km eastern shelf-edge branch extent in Orvik and Skagseth (2003). '
             'Historical broad branch geography from Shetland toward the Arctic west of Svalbard at80°N is described in Orvik and Niiler (2001), not an independent length measurement. '
             'This broad scope may overlap flow now named West Spitsbergen Current; not an additive component length or a modern regional axis. '
             'No fixed layer, reference period, paired endpoint coordinates, error or annual range supplied.')
    entity = {'id': ENTITY, 'label': 'Norwegian Atlantic Slope Current', 'type': 'named_current',
              'source_record_id': ID, 'source_id': NAME_SOURCE, 'source_kind': 'source-defined Atlantic-water slope current',
              'identity_level': 'current', 'setting': 'polar_or_subpolar_margin', 'time_behavior': 'persistent_variable',
              'basin': 'Norwegian Sea / Nordic Seas',
              'identity_scope_note': 'Atlantic-water eastern slope branch along the Norwegian continental margin, with northern bifurcation. Distinct from ambiguous Norwegian Current, coastal current and western frontal branch. Parent Norwegian Atlantic Current remains a separately proposed identity.',
              'almanac_url': 'reference-routes.html#inventory-addition-' + ID,
              'catalogue_version': '0.3.0-draft-nwasc', 'identity_admission_id': 'current_admission:' + ID}
    measurement = {'id': MEASUREMENT_ID, 'claim_id': 'claim:' + MEASUREMENT_ID, 'entity_id': ENTITY,
                   'quantity': 'reported_length', 'value': 3500, 'unit': 'km', 'approximate': True,
                   'rank_eligible': True, 'evidence_status': 'published_estimate', 'source_id': LENGTH_SOURCE,
                   'source_locator': 'Introduction paragraph[3], eastern NwASC branch description.', 'scope': scope,
                   'geometry_id': None, 'observation_time': None, 'fixed_layer_bounds_m': None,
                   'endpoint_coordinates_lon_lat': None, 'reference_period': None, 'uncertainty_km': None,
                   'annual_length_range_km': None, 'source_report_type': 'contextual_broad_branch_extent_not_new_axis_measurement',
                   'supporting_source_ids': [CONTEXT_SOURCE], 'historical_release_admitted': False}
    assessment = {'id': 'length_assessment:' + ID, 'entity_id': ENTITY, 'evidence_status': 'published_estimate',
                  'rank_eligible': True, 'published_length_km': 3500, 'published_rank': None,
                  'lower_bound_km': None, 'proposed_system_length_km': None, 'source_id': NAME_SOURCE,
                  'length_source_id': LENGTH_SOURCE, 'length_source_locator': measurement['source_locator'],
                  'scope': scope, 'measurement_id': MEASUREMENT_ID, 'measurement_admission_file': FILE,
                  'gate_distance_method_source_id': None, 'gate_distance_sensitivity': None,
                  'illustrated_span_km': None, 'illustrated_span_rank': None}
    old_export = previous.effective_export()
    nac_doc, nac_pins = nac.verify_inputs()
    earlier = [nac_doc['length_assessment'] if r['entity_id'] == nac.ENTITY else r for r in old_export['length_assessments']]
    ranked = rank_assessments(earlier + [assessment])
    updates = [{'id': r['id'], 'entity_id': r['entity_id'], 'previous_rank': old['published_rank'], 'working_rank': r['published_rank']}
               for old, r in zip(earlier, ranked) if old['published_rank'] != r['published_rank']]
    assessment = ranked[-1]
    claim = {'id': measurement['claim_id'], 'subject_id': ENTITY, 'object_id': None, 'predicate': 'reported_length',
             'value': 3500, 'unit': 'km', 'target_collection': 'measurements', 'target_id': MEASUREMENT_ID,
             'source_id': LENGTH_SOURCE, 'source_locator': measurement['source_locator'], 'source_locator_status': 'specific',
             'source_date': '2003-09-04', 'source_snapshot_id': None, 'support_claim_id': None,
             'evidence_class': 'published_estimate', 'assertion_status': 'reported_or_derived_measurement',
             'scope': scope, 'observation_time': None, 'method': 'Linked factual extraction; reported extent not a new path calculation.',
             'method_source_id': LENGTH_SOURCE, 'method_status': 'described', 'review_status': 'not_individually_reviewed',
             'reviewer': None, 'review_date': None, 'review_note': 'Internal editorial source review; external scientific review remains pending.'}
    claim['review_fingerprint'] = review_fingerprint(claim)
    planning = {'current_id': ID, 'name': entity['label'], 'candidate_ids': [], 'published_length_rank_eligible': True,
                'route_strategy_id': 'source_gated_boundary_current', 'route_strategy_label': 'Source-gated slope-current route',
                'reference_path_decision': 'not_constructed', 'next_action': 'Recover a source-supported axis with branch, layer, endpoint and time conventions.',
                'existing_scope': scope, 'planning_status': 'editorial_planning_crosswalk_not_scientific_classification_approval',
                'name_source_url': sources[0]['url'], 'existing_length_evidence_status': 'published_estimate', 'ledger_kind': 'current',
                'planning_basis': 'Reported branch extent and scoped local widths do not supply source geometry.',
                'strategy_next_action': 'Recover independent route geometry; do not trace a physical route from scalar prose.',
                'known_component_currents': [], 'component_inventory_status': 'parent_and_downstream_name_boundaries_retained'}
    entry = {'id': entity['identity_admission_id'], 'proposal_id': ID, 'entity_id': ENTITY, 'entity': entity,
             'source': sources[0], 'status': 'working_identity_and_separately_scoped_dimensions_admitted',
             'admission_date': '2026-10-22', 'review_type': 'internal_editorial_primary_source_review',
             'identity_evidence': proposal['evidence'], 'canonical_measurements_admitted': True, 'rank_eligible': True,
             'physical_edges_admitted': False, 'geometry': None, 'annual_width_range_km': None,
             'annual_length_range_km': None, 'seasonal_playback_eligible': False, 'external_scientific_review_claimed': False,
             'remaining_measurement_gates': ['Acquire a layer- and time-defined axis before mapped length and physical joins.',
                                             'Acquire comparable repeated dated dimensions before annual envelopes and seasonal animation.'],
             'identity_figure_file': FIGURE, 'route_planning_decision': planning}
    paths = [PROTOCOL, OPERATOR, CUSTODY, identities.PATH, identities.CATALOGUE, identities.PROPOSALS,
             previous.EXPORT, previous.FILE, 'research/norwegian-atlantic-slope-orvik-2003-dimension-candidates.json',
             'research/norwegian-atlantic-branch-width-scope-audit.json', 'research/norwegian-fer-2020-gimsoy-width-scope-audit.json',
             'analysis/check_nordic_section_widths.py', 'analysis/build_ocean_motion_claims.py']
    for audit_path in ['research/norwegian-atlantic-branch-width-scope-audit.json', 'research/norwegian-fer-2020-gimsoy-width-scope-audit.json']:
        audit = read(audit_path)
        for key, path in audit.items():
            if key.endswith('_file') and key[:-5] + '_sha256' in audit:
                if digest(path) != audit[key[:-5] + '_sha256']:
                    raise ValueError('Changed audited width source: ' + path)
                paths.append(path)
    pins = {**mean_pins, **nac_pins, **{p: digest(p) for p in paths}, FIGURE: hashlib.sha256(figure()).hexdigest()}
    widths = admitted_widths()
    return {'schema': 'osw.nwasc-working-admission.v1', 'version': '1', 'id': 'current_measurement_admission:' + ID,
            'entity_id': ENTITY, 'current_id': ID, 'entity': entity, 'identity_entry': entry,
            'entries': identities.verify()['entries'] + [entry], 'source_records': sources,
            'measurement': measurement, 'claim': claim, 'length_assessment': assessment,
            'width_records': widths, 'width_migrations': [{'previous_proposed_record_id': r['previous_proposed_record_id'], 'admitted_record_id': r['id']} for r in widths if 'previous_proposed_record_id' in r],
            'rank_updates': updates, 'working_length_assessments': ranked,
            'working_published_ranks': {r['entity_id']: r['published_rank'] for r in ranked if r['rank_eligible']},
            'accepted_current_count': 102, 'pending_current_proposals': 27, 'ranked_length_count': 13,
            'scoped_width_count': 164, 'scoped_width_owners': 84, 'unresolved_proposed_width_records': 2,
            'figure_file': FIGURE, 'catalogue_file': CATALOGUE, 'measurement_export_file': EXPORT,
            'historical_proposed_records_retained': True, 'new_independent_width_observations': 0,
            'physical_current_edges_admitted': False, 'annual_extrema_admitted': False,
            'external_scientific_review_claimed': False, 'input_sha256': pins}


def catalogue(doc):
    old = identities.catalogue()
    return {**old, 'version': '0.3.0-draft-nwasc', 'admitted_current_count': 2, 'current_count': 102,
            'previous_catalogue_file': identities.CATALOGUE, 'admission_file': FILE,
            'input_sha256': {FILE: digest(FILE), identities.CATALOGUE: digest(identities.CATALOGUE)},
            'entries': old['entries'] + [doc['entity']]}


def working_export(doc):
    old = previous.effective_export()
    return {**old, 'schema': 'osw.live-current-measurements.v1', 'version': '0.3.0-draft-nwasc',
            'base_working_export': previous.EXPORT, 'working_catalogue_file': CATALOGUE,
            'admission_file': FILE, 'previous_admission_file': old['admission_file'],
            'additional_admission_files': [nac.FILE, FILE], 'ranked_length_count': 13,
            'scoped_width_count': 164, 'scoped_width_owners': 84,
            'input_sha256': {**old['input_sha256'], FILE: digest(FILE), CATALOGUE: digest(CATALOGUE), nac.FILE: digest(nac.FILE), OPERATOR: digest(OPERATOR)},
            'measurements': old['measurements'] + [nac.verify_inputs()[0]['measurement'], doc['measurement']],
            'length_assessments': doc['working_length_assessments'],
            'widths': old['widths'] + doc['width_records'], 'sources': old['sources'] + [nac.verify_inputs()[0]['method_source']] + doc['source_records']}


def verify_inputs():
    doc = build()
    for path, value in [(FILE, doc), (CATALOGUE, catalogue(doc)), (EXPORT, working_export(doc))]:
        if (ROOT / path).read_bytes() != encoded(value):
            raise ValueError('Changed slope-current admission/export: ' + path)
    if (ROOT / FIGURE).read_bytes() != figure():
        raise ValueError('Changed slope-current scalar figure')
    return doc, {**doc['input_sha256'], **{p: digest(p) for p in [FILE, CATALOGUE, EXPORT]}}


def append(collections, doc):
    for name, values in [('entities', [doc['entity']]), ('names', [{'id': 'name:current:' + ID,
                         'entity_id': ENTITY, 'label': doc['entity']['label'], 'preferred': True, 'source_id': NAME_SOURCE}]),
                         ('sources', doc['source_records']), ('current_identity_admissions', [doc['identity_entry']]),
                         ('measurements', [doc['measurement']]), ('claims', [doc['claim']]),
                         ('widths', doc['width_records']), ('current_measurement_admissions', [doc])]:
        existing = collections.setdefault(name, [])
        if {r['id'] for r in existing} & {r['id'] for r in values}:
            raise ValueError('Duplicate slope-current admission in ' + name)
        existing.extend(copy.deepcopy(values))
    collections['length_assessments'] = copy.deepcopy(doc['working_length_assessments'])


if __name__ == '__main__':
    doc = build()
    (ROOT / FILE).write_bytes(encoded(doc))
    (ROOT / FIGURE).write_bytes(figure())
    (ROOT / CATALOGUE).write_bytes(encoded(catalogue(doc)))
    (ROOT / EXPORT).write_bytes(encoded(working_export(doc)))
    print(json.dumps({k: doc[k] for k in ['accepted_current_count', 'ranked_length_count', 'scoped_width_count', 'scoped_width_owners']}))
