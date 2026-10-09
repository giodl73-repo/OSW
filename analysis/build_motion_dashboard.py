"""Build an evidence-coverage dashboard without promoting research candidates."""
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from check_persian_gulf_scope import validate as validate_persian_gulf_scope
from check_red_sea_scope import validate as validate_red_sea_scope
from build_pacific_necc_oscar_section_diagnostic import build as build_necc_diagnostic, diagnostic_matches
from build_leeuwin_monthly_plot import build as build_leeuwin_plot
from check_current_width_inventory import validate as validate_width_inventory
from build_kuroshio_seasonal_width_profiles import build as build_kuroshio_profiles

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'research/ocean-motion-dashboard.json'


def build_ground():
    """Reuse the atlas coastline and its equirectangular projection."""
    atlas = ET.parse(ROOT / 'figures/osw-province-atlas-interactive.svg').getroot()
    land = next(e for e in atlas if e.get('class') == 'land-context')
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    svg = ET.Element('{http://www.w3.org/2000/svg}svg', {'viewBox': '60 90 1480 740'})
    ET.SubElement(svg, 'title').text = 'OSW ocean motion atlas ground'
    ET.SubElement(svg, 'desc').text = 'Coarse coastline reused from the OSW province atlas. Not suitable for coastal measurement.'
    ET.SubElement(svg, 'rect', {'x': '60', 'y': '90', 'width': '1480', 'height': '740', 'fill': '#092b39'})
    svg.append(next(e for e in atlas if e.tag.endswith('defs')))
    svg.append(next(e for e in atlas if e.tag.endswith('style')))
    svg.append(next(e for e in atlas if e.get('class') == 'province-field'))
    for lon in range(-180, 181, 30):
        x = 60 + (lon + 180) / 360 * 1480
        ET.SubElement(svg, 'path', {'d': f'M{x},90V830', 'stroke': '#214652', 'stroke-width': '1'})
    for lat in range(-60, 90, 30):
        y = 90 + (90 - lat) / 180 * 740
        ET.SubElement(svg, 'path', {'d': f'M60,{y}H1540', 'stroke': '#214652', 'stroke-width': '1'})
    ET.SubElement(svg, 'path', {'d': land.get('d'), 'fill': '#33515b', 'stroke': '#56737a', 'stroke-width': '1', 'fill-rule': 'evenodd'})
    svg.append(next(e for e in atlas if e.get('class') == 'province-labels'))
    (ROOT / 'figures/ocean-motion-dashboard-ground.svg').write_text(ET.tostring(svg, encoding='unicode') + '\n', encoding='utf-8')
    closeup = ET.Element('{http://www.w3.org/2000/svg}svg', {'viewBox': '60 90 1480 740'})
    ET.SubElement(closeup, 'title').text = 'OSW coastline context for dated section closeups'
    ET.SubElement(closeup, 'desc').text = 'Same coarse atlas coastline and projection; state labels and graticules omitted for local section readability.'
    ET.SubElement(closeup, 'rect', {'x':'60','y':'90','width':'1480','height':'740','fill':'#092b39'})
    ET.SubElement(closeup, 'path', {'d':land.get('d'),'fill':'#33515b','stroke':'#56737a','stroke-width':'.15','fill-rule':'evenodd'})
    (ROOT / 'figures/ocean-motion-closeup-ground.svg').write_text(ET.tostring(closeup,encoding='unicode')+'\n',encoding='utf-8')


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(',', ':')).encode()).hexdigest()


def latest_observation_date(values):
    """Only explicit observation dates; no publication or retrieval fallback."""
    dates = []
    for value in values:
        if isinstance(value, dict):
            dates.extend(filter(None, [latest_observation_date([value.get('start')]), latest_observation_date([value.get('end')])]))
        elif isinstance(value, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}(?:T.*)?', value):
            try:
                datetime.fromisoformat(value.replace('Z', '+00:00'))
                dates.append(value[:10])
            except ValueError:
                pass
    return max(dates, default=None)


def build():
    inputs = {}
    inputs['figures/osw-province-atlas-interactive.svg'] = hashlib.sha256((ROOT / 'figures/osw-province-atlas-interactive.svg').read_bytes()).hexdigest()

    def read(path):
        raw = (ROOT / path).read_bytes()
        inputs[path] = hashlib.sha256(raw).hexdigest()
        return json.loads(raw)

    base = 'almanac/release/v0.1.0/'
    entities = read(base + 'entities.json')
    measurements = read(base + 'measurements.json')
    geometries = read(base + 'geometries.json')
    claims = read(base + 'claims.json')
    media = read(base + 'media.json')
    sources = {source['id']: source for source in read(base + 'sources.json')}
    routes = read('research/ocean-current-reference-path-candidates.json')['candidates']
    width_inventory = read('research/ocean-current-width-inventory.json')
    validate_width_inventory(width_inventory, read('research/ocean-current-almanac.json'))
    widths = width_inventory['measurements']
    width_audits={}
    for record in widths:
        audit_file=record.get('extraction_file') or (record.get('stream_mean_context') or record.get('eulerian_section_context') or record.get('width_statistics_context') or record.get('regional_range_context') or record.get('regional_scalar_context') or record.get('mean_offshore_context') or record.get('adcp_threshold_context') or {}).get('audit_file')
        if audit_file and audit_file not in width_audits:width_audits[audit_file]=read(audit_file)
    phases = read('research/ocean-current-seasonal-route-frames.json')['frames']
    proposals_document = read('research/ocean-current-inventory-expansion-candidates.json')
    from check_norwegian_atlantic_branch_widths import validate as validate_proposed_widths, AUDIT, ACQUISITION, SOURCE
    validate_proposed_widths(proposals_document)
    read(AUDIT);read(ACQUISITION)
    inputs[SOURCE]=hashlib.sha256((ROOT/SOURCE).read_bytes()).hexdigest()
    proposals = proposals_document['entries']
    timeline = read('research/ocean-current-dated-timeline.json')
    annual = read('research/ocean-current-dated-timeline-2025.json')
    norkyst = read('research/norkyst-ingoy-2024-section-timeline.json')
    norkyst_maps = read('research/norkyst-ingoy-2024-map-frames.json')
    derived_width = read('research/gulf-stream-section-width-series.json')
    necc_path='research/pacific-necc-oscar-2013-section-diagnostic.json'
    necc=read(necc_path)
    if not diagnostic_matches(necc,build_necc_diagnostic()):raise ValueError('NECC monthly diagnostic differs from pinned source calculation')
    read(necc['source_inventory_file'])
    kuroshio_profile_path='research/kuroshio-ecs-seasonal-width-profile-extraction.json'
    kuroshio_profiles=read(kuroshio_profile_path)
    if kuroshio_profiles!=build_kuroshio_profiles():raise ValueError('Kuroshio seasonal profile differs from pinned extraction')
    for key in ['source_pdf_file','config_file','protocol_file','scope_audit_file']:
        path=kuroshio_profiles[key];inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()

    florida_path='research/florida-monthly-width-plot-extraction.json'
    florida_plot=read(florida_path)
    from build_florida_monthly_plot import build as rebuild_florida
    if florida_plot!=rebuild_florida():raise ValueError('Florida monthly graph differs from pinned extraction')
    for key in ['source_pdf_file','config_file','protocol_file','scope_audit_file']:
        path=florida_plot[key];inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    leeuwin_path='research/leeuwin-a101-monthly-plot-extraction.json'
    leeuwin_plot=read(leeuwin_path)
    if leeuwin_plot!=build_leeuwin_plot():raise ValueError('Leeuwin monthly graph differs from pinned extraction')
    for key in ['source_pdf_file','config_file','protocol_file','scope_audit_file']:
        path=leeuwin_plot[key];inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()

    antilles_section_path='research/antilles-ab0505-400m-section-diagnostic.json'
    antilles_sections=read(antilles_section_path)
    antilles_inventory=read(antilles_sections['inventory_file'])
    if (antilles_sections.get('schema')!='osw.ladcp-section-diagnostic.v1' or antilles_sections.get('current_id')!='antilles'
        or antilles_sections.get('inventory_sha256')!=inputs[antilles_sections['inventory_file']]
        or antilles_sections.get('status')!='derived_local_diagnostic_requires_review'
        or len(antilles_sections.get('sections',[]))!=2
        or any(row.get('half_peak_diagnostic',{}).get('full_width_km') is not None for row in antilles_sections.get('sections',[]))
        or antilles_sections.get('geographic_role')!='transverse_observation_section_not_current_axis'
        or any(antilles_sections.get(key) is not None for key in ['whole_current_length_km','whole_current_width_km','annual_length_range_km','annual_width_range_km'])
        or antilles_sections.get('width_rank_eligible') is not False or antilles_sections.get('seasonal_playback_eligible') is not False):
        raise ValueError('Antilles section diagnostic must preserve scoped, unadmitted evidence and inventory checksum')
    eddy_geography = {e['id']: e for e in read('research/named-eddy-geography.json')['entries']}
    somali_width_audit=read('research/somali-schott-2001-premonsoon-width-scope-audit.json')
    guinea_width_audit=read('research/guinea-djakoure-2017-model-width-source-review.json')
    algerian_width_audit=read('research/algerian-cotroneo-2019-regional-width-scope-audit.json')
    alaska_width_audit=read('research/alaska-weingartner-2002-regional-width-scope-audit.json')
    zeehan_width_audit=read('research/zeehan-cresswell-2000-width-section-scope-audit.json');read('research/source-data/cresswell-zeehan-2000/acquisition.json')
    for path in ['research/source-data/cresswell-zeehan-2000/journal-article.pdf','plans/zeehan-width-source-separation-protocol-v1.md']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    tsushima_modal_audit=read('research/tsushima-matsuyama-1990-modal-width-scope-audit.json');read('research/source-data/matsuyama-tsushima-1990/acquisition.json')
    for path in ['research/source-data/matsuyama-tsushima-1990/journal-article.pdf','plans/campaign-modal-decay-width-protocol-v1.md','analysis/check_tsushima_modal_width.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    ngcu_width_audit=read('research/ngcu-zenk-1999-width-constraint-scope-audit.json')
    kuroshio_extension_width_audit=read('research/kuroshio-extension-sasaki-2013-width-averaging-scope-audit.json')
    atlantic_euc_width_audit=read('research/atlantic-euc-gouriou-1988-background-width-scope-audit.json')
    pacific_euc_width_audit=read('research/pacific-euc-wang-2022-background-width-scope-audit.json')
    ring_radius_audit=read('research/agulhas-guerra-2022-ring-radius-scope-audit.json')
    from build_agulhas_ring_radius_audit import validate as validate_ring_radii
    validate_ring_radii(ring_radius_audit, {'entries':list(eddy_geography.values())})
    astrid_audit=read('research/astrid-2000-radial-scale-scope-audit.json')
    from check_astrid_radial_scales import validate as validate_astrid
    validate_astrid(astrid_audit, {'entries':list(eddy_geography.values())})
    from build_black_sea_eddy_recurrence import validate as validate_recurrence
    recurrence_document=read('research/black-sea-eddy-recurrence.json')
    validate_recurrence(recurrence_document)
    recurrence={r['entity_id']:r for r in recurrence_document['entries']}
    loop_context = read('research/named-loop-eddy-nasa-context.json')
    loop_entries = {e['id']: e for e in loop_context['entries']}
    eddy_state_assessments = read(base + 'named_eddy_state_assessments.json')
    operational_state_observations = read(base + 'operational_eddy_state_observations.json')
    geography_states = read('research/named-eddy-geography-join.json')['entries']
    state_names = {code: state['name'] for code, state in read('research/ocean-motion-state-join.json')['states'].items()}
    route_shapes = {r['id']: read(r['candidate_file']) for r in routes}
    from build_current_reference_path_catalog import validate_source_receipt
    for shape in route_shapes.values():
        inputs.update(validate_source_receipt(shape))
    connections = read('research/ocean-current-connectivity-candidates.json')['entries']
    scope_notes = read('research/ocean-current-scope-notes.json')['entries']
    scope_audits = {note['audit_file']: read(note['audit_file']) for note in scope_notes}
    for audit in scope_audits.values():
        if audit.get('current_id')=='persian-gulf-saline-overflow':validate_persian_gulf_scope(audit)
        if audit.get('current_id')=='red-sea-saline-overflow':validate_red_sea_scope(audit)
    from check_zeehan_seasonal_calendar import validate as validate_zeehan_calendar
    validate_zeehan_calendar(scope_audits['research/zeehan-ridgway-2007-seasonal-scope-audit.json'])
    from check_atlantic_euc_section_properties import validate as validate_atlantic_sections
    validate_atlantic_sections(scope_audits['research/atlantic-euc-layer-island-scope-audit.json'])
    from build_flow_network import validate as validate_network
    network_path = 'research/indonesian-throughflow-network-input.json'
    network = validate_network(read(network_path))
    loop_repeat = read('research/loop-current-recorded-date-comparison.json')
    read(loop_repeat['source_manifest'])
    if inputs[loop_repeat['source_manifest']] != loop_repeat['source_manifest_sha256']:
        raise ValueError('Loop source manifest receipt mismatch')
    if loop_repeat['rank_eligible'] is not False:
        raise ValueError('Loop diagnostics must remain unranked')
    loop_files = [(f'research/loop-current-{method}-20260925.json', '2026-09-25', None)
                  for method in ['dated-streamline', 'adt-contours']]
    for day in loop_repeat['dates']:
        for method in ['noaa', 'adt']:
            loop_files.append((day[method+'_diagnostic_file'], day['date'], day[method+'_diagnostic_sha256']))
    loop_documents = []
    for path, date, expected_sha in loop_files:
        document = read(path)
        if (document['current_id'] != 'loop' or document['observation_date'] != date
                or document['rank_eligible'] is not False
                or any(document[k] is not None for k in ['whole_current_length_km','width_km','annual_length_range_km'])
                or (expected_sha is not None and inputs[path] != expected_sha)):
            raise ValueError('Loop dashboard diagnostic identity/date/receipt mismatch')
        source_key, hash_key = ('source_subset','source_subset_sha256') if 'source_subset' in document else ('source_file','source_sha256')
        for key, sha_key in [(source_key,hash_key),('protocol_file','protocol_sha256')]:
            inputs[document[key]]=hashlib.sha256((ROOT/document[key]).read_bytes()).hexdigest()
            if inputs[document[key]] != document[sha_key]:
                raise ValueError('Loop dashboard source or protocol receipt mismatch')
        loop_documents.append((path, document))
    from build_loop_current_section_spans import build as rebuild_loop_sections, output as loop_section_output
    loop_sections=[]
    for method in ['noaa','adt']:
        path=loop_section_output(method).relative_to(ROOT).as_posix();document=read(path)
        if document!=rebuild_loop_sections(method):raise ValueError('Stale Loop section span diagnostic')
        loop_sections.append(document)
    current_ids = {e['id'] for e in entities if e['type'] == 'named_current'}
    if network['entity_id'] not in current_ids:
        raise ValueError('Unknown flow network owner')
    if any('current:' + note['current_id'] not in current_ids or scope_audits[note['audit_file']]['current_id'] != note['current_id'] for note in scope_notes):
        raise ValueError('Source scope notes must resolve to their released current identity')
    if any(not isinstance(note.get('related_current_ids',[]),list) or any(not isinstance(ident,str) or 'current:'+ident not in current_ids or ident==note['current_id'] for ident in note.get('related_current_ids',[])) for note in scope_notes):
        raise ValueError('Related scope records must use distinct released current identities')
    proposal_names = {row['proposed_id']: row['name'] for row in proposals}
    for note in scope_notes:
        related_proposals = note.get('related_proposed_current_ids', [])
        if (not isinstance(related_proposals, list)
                or any(not isinstance(ident, str) or ident not in proposal_names for ident in related_proposals)
                or len(set(related_proposals)) != len(related_proposals)):
            raise ValueError('Related proposed scope records must use unique pending identities')
        if related_proposals:
            note['related_proposed_currents'] = [{'id': ident, 'name': proposal_names[ident]} for ident in related_proposals]
        supporting_sources = note.get('supporting_sources', [])
        if not isinstance(supporting_sources, list) or any(
            not isinstance(source, dict)
            or any(not isinstance(source.get(key), str) or not source[key].strip()
                   for key in ('label', 'url', 'locator', 'access'))
            or not source['url'].startswith('https://')
            for source in supporting_sources
        ):
            raise ValueError('Supporting scope sources require HTTPS citation, locator and access limits')
    allowed_connections = {'source_described_downstream_continuation', 'source_described_feeding_relation', 'source_described_branching_relation'}
    if len({c['id'] for c in connections}) != len(connections) or any(c['subject_id'] not in current_ids or c['object_id'] not in current_ids or c['subject_id'] == c['object_id'] or c['predicate'] not in allowed_connections or c['canonical_admission'] is not False or c['junction_coordinate'] is not None for c in connections):
        raise ValueError('Connectivity candidates must use distinct released current identities and retain their research scope')
    rows = []
    for entity in entities:
        if entity['type'] not in {'named_current', 'named_eddy', 'operational_eddy_detection'}:
            continue
        ident = entity['id']
        own_connections = [c for c in connections if ident in (c['subject_id'], c['object_id'])]
        own_notes = [note for note in scope_notes if ident == 'current:' + note['current_id']]
        own_audits = [scope_audits[note['audit_file']] for note in own_notes]
        current_id = entity['source_record_id'] if entity['type'] == 'named_current' else None
        own_measures = [m for m in measurements if m['entity_id'] == ident]
        own_routes = [r for r in routes if current_id and r['current_id'] == current_id]
        own_widths = [w for w in widths if current_id and w['current_id'] == current_id]
        own_geometry = [g for g in geometries if g['entity_id'] == ident and g['role'] != 'editorial_locator']
        map_features = []
        for g in geometries:
            if g['entity_id'] == ident:
                feature = {'geometry': g['geometry'], 'role': g['role'],
                           'note': (f"Observation date: {g['observation_date']}. " if g.get('observation_date') else '') + g['method']}
                if g['role'] in {'dated_partial_geostrophic_streamline', 'dated_analyzed_surface_front'}:
                    feature.update({'geometry_id': g['id'], 'observation_date': g.get('observation_date'),
                                    'front_side': g.get('front_side'),
                                    'source_url': sources[g['source_id']].get('url'),
                                    'receipt_file': sources.get(g.get('source_snapshot_id'), {}).get('repository_path')})
                map_features.append(feature)
        for route in own_routes:
            shape = route_shapes[route['id']]
            map_features.append({'geometry': {'type': 'LineString', 'coordinates': shape['coordinates_lon_lat']},
                                 'role': 'editorial_reference_route', 'note': route['scope']})
        geography = eddy_geography.get(entity['source_record_id']) if entity['type'] == 'named_eddy' else None
        if geography:
            map_features.append({'geometry': {'type': 'Point', 'coordinates': geography['locator']},
                                 'role': 'source_geography_locator', 'note': geography['locator_basis']})
        loop = loop_entries.get(entity['source_record_id']) if entity['type'] == 'named_eddy' else None
        if loop or (entity['type'] == 'named_eddy' and not map_features and entity.get('basin') == 'Gulf of Mexico'):
            map_features.append({'geometry': {'type': 'Point', 'coordinates': loop_context['region_locator']},
                                 'role': 'shared_regional_gateway', 'group': 'Gulf of Mexico regional gateway',
                                 'note': loop_context['region_locator_basis'] if loop else 'OSW editorial gateway for a source-scoped Gulf of Mexico name. This shared point is not an observed position, center, separation location or footprint.'})
        if loop and loop.get('published_observed_position'):
            position = loop['published_observed_position']
            map_features.append({'geometry': {'type': 'Point', 'coordinates': position['coordinate']},
                                 'role': position['position_evidence'], 'note': position['note']})
        state_evidence = []
        def state_record(code, kind, label, date, source_file, source_record):
            if code not in state_names:
                raise ValueError(f'Unknown state in eddy evidence: {code}')
            state_evidence.append({'state_code': code, 'state_name': state_names[code],
                                   'kind': kind, 'label': label, 'observation_date': date,
                                   'source_file': source_file, 'source_record_id': source_record})
        if loop:
            for code in loop['state_locator_candidates']:
                state_record(code, 'shared_regional_gateway', 'Shared source-region gateway; individual containment unresolved', None,
                             'research/named-loop-eddy-nasa-context.json', loop['id'])
            position = loop.get('published_observed_position')
            if position:
                for code in position['state_point_candidates']:
                    state_record(code, 'reported_center_point', 'Approximate reported center; no footprint or containment', None,
                                 'research/named-loop-eddy-nasa-context.json', loop['id'])
        if geography:
            joined = geography_states[entity['source_record_id']]
            for code in joined['state_locator_candidates']:
                state_record(code, 'source_geography_locator', 'Source geography locator; no whole-eddy containment', None,
                             'research/named-eddy-geography-join.json', entity['source_record_id'])
            for visit in joined.get('additional_observed_position_joins', []):
                for code in visit['state_center_candidates']:
                    state_record(code, 'source_reported_position', visit['evidence_type'].replace('_', ' ') + '; point only, no footprint', visit.get('date'),
                                 'research/named-eddy-geography-join.json', entity['source_record_id'])
        for assessment in eddy_state_assessments:
            if assessment['eddy_id'] != ident or assessment['physical_relation'] == 'unknown_no_dated_eddy_footprint':
                continue
            proxy = assessment['dated_ssh_contour_assessment'] is not None
            state_record(assessment['state_id'].removeprefix('state:'), 'dated_ssh_contour_proxy' if proxy else 'observed_center_point',
                         'Dated SSH contour proxy intersection candidate; whole-eddy relation unresolved' if proxy else 'Observed center point; no whole-eddy containment',
                         assessment['dated_ssh_contour_observation_date'] if proxy else assessment['observed_center_date'],
                         base + 'named_eddy_state_assessments.json', assessment['id'])
        for observation in operational_state_observations:
            if observation['operational_eddy_id'] == ident:
                state_record(observation['state_id'].removeprefix('state:'), 'dated_provider_polygon',
                             observation['relation'].replace('_', ' ') + '; dated provider polygon, exact datum unspecified', observation['observation_date'],
                             base + 'operational_eddy_state_observations.json', observation['id'])
        own_claims = [c for c in claims if ident in (c.get('subject_id'), c.get('object_id'), c.get('entity_id'))]
        own_media = [m for m in media if m['entity_id'] == ident]
        own_phases = [p for p in phases if current_id and p['current_id'] == current_id]
        source_ids = {row.get(key) for row in [entity, *own_measures, *own_geometry, *own_claims, *own_media] for key in ['source_id', 'source_snapshot_id', 'method_source_id'] if row.get(key)}
        if source_ids - sources.keys():
            raise ValueError(f'Unresolved dashboard sources for {ident}')
        own_sources = [sources[key] for key in sorted(source_ids)]
        linked_widths = {ident for phase in own_phases for ident in phase['width_measurement_ids']}
        temporal_widths = [w for w in own_widths if w['id'] not in linked_widths and w.get('phase_kind') in {'seasonal_summary', 'dated_section', 'survey_summary', 'ensemble_summary', 'survey_profile_composite', 'monthly_climatological_fit'}]
        temporal_widths += [w for w in own_widths if w.get('phase_kind')=='stream_mean_threshold_summary' and w.get('stream_mean_context',{}).get('season') is not None]
        series = []
        if current_id == kuroshio_profiles['current_id']:
            temporal_widths=[w for w in temporal_widths if w['id'] not in kuroshio_profiles['regional_prose_measurement_ids']]
            series.append({'label':'Four historical ECS seasonal width profiles (graph extraction)',
                           'url':'reference-routes.html?atlas-layout=map&atlas-feature=current%3Akuroshio#route-atlas',
                           'frames':len(kuroshio_profiles['seasons']),'evidence_role':'seasonal_width_profile_plot_extraction',
                           'diagnostic_url':'../'+kuroshio_profile_path,'evidence_sha256':inputs[kuroshio_profile_path],
                           'source_pdf_sha256':kuroshio_profiles['source_pdf_sha256'],'protocol_sha256':kuroshio_profiles['protocol_sha256'],
                           'config_sha256':kuroshio_profiles['config_sha256']})
        if current_id == florida_plot['current_id']:
            series.append({'label':'2005-2006 monthly surface-jet widths at 25.42 N (graph readings)',
                           'url':'query.html?q=%7B%22collection%22%3A%22width_samples%22%2C%22filters%22%3A%5B%7B%22field%22%3A%22current_id%22%2C%22op%22%3A%22eq%22%2C%22value%22%3A%22florida%22%7D%5D%2C%22limit%22%3A100%7D',
                           'frames':12,'evidence_role':'monthly_half_peak_width_plot_extraction',
                           'diagnostic_url':'../'+florida_path,'evidence_sha256':inputs[florida_path]})
        if current_id == leeuwin_plot['current_id']:
            # Prose anchors describe two of the twelve months, not extra time samples.
            temporal_widths=[w for w in temporal_widths if w['id'] not in leeuwin_plot['prose_measurement_ids']]
            series.append({'label':'Historical monthly fitted widths at a101 (graph extraction)',
                           'url':'reference-routes.html?atlas-layout=map&atlas-feature=current%3Aleeuwin#route-atlas',
                           'frames':len(leeuwin_plot['months']),'evidence_role':'monthly_fitted_width_plot_extraction',
                           'diagnostic_url':'../'+leeuwin_path,'evidence_sha256':inputs[leeuwin_path],
                           'source_pdf_sha256':leeuwin_plot['source_pdf_sha256'],
                           'protocol_sha256':leeuwin_plot['protocol_sha256'],'config_sha256':leeuwin_plot['config_sha256']})
        if current_id == necc['current_id']:
            series.append({'label':'2013 monthly surface-section diagnostics (not climatology)','url':'necc-section.html','frames':len(necc['months']),
                           'evidence_role':'monthly_mean_section_width_candidate','diagnostic_url':'../'+necc_path,
                           'evidence_sha256':inputs[necc_path],'inventory_sha256':inputs[necc['source_inventory_file']]})
        if current_id == timeline['current_id']:
            series.append({'label': 'Dated surface diagnostics', 'url': 'dated-current.html', 'frames': len(timeline['frames']) + len(annual['frames'])})
        if current_id == 'norwegian-coastal':
            series.append({'label': 'Regional model samples (not current footprint)', 'url': 'norkyst-section.html', 'frames': len(norkyst['frames'])})
        if current_id == 'antilles':
            series.append({'label':'Observed May 2005 sections (not an annual cycle)','url':'antilles-sections.html','frames':2,
                           'evidence_role':'observed_sections_with_unadmitted_one_sided_span',
                           'diagnostic_url':'../research/antilles-ab0505-400m-section-diagnostic.json',
                           'evidence_sha256':inputs[antilles_section_path],'inventory_sha256':inputs[antilles_sections['inventory_file']]})
        if current_id == 'loop':
            for document in loop_sections:
                series.append({'label':'Yucatan inflow section spans — '+document['product_key'].upper(),
                    'url':'query.html?q='+quote(json.dumps({'collection':'width_samples','filters':[{'field':'diagnostic_id','op':'eq','value':'diagnostic:yucatan-'+document['product_key']+'-sections'}],'limit':50},separators=(',',':')),safe=''),
                    'frames':len(document['frames']),'evidence_role':'local_component_section_span_not_whole_current_width'})
        capabilities = {
            'radius_evidence': len(geography.get('published_ring_radius_evidence',geography.get('radial_scale_evidence',[]))) if geography else 0,
            'reported_length': sum(m.get('rank_eligible') is True for m in own_measures),
            'reference_route': len(own_routes),
            'scoped_width': len(own_widths),
            'geometry': len(own_geometry),
            'time_samples': sum(s['frames'] for s in series) + len(own_phases) + len(temporal_widths),
            'source_connectivity': len(own_connections),
            'scope_notes': len(own_notes),
            'dated_diagnostics': len(loop_documents) if current_id == 'loop' else 0,
            'flow_network': int(ident == network['entity_id']),
            'passage_transport': len(network['passage_samples']) if ident == network['entity_id'] else 0,
        }
        payload = {'entity': entity, 'measurements': own_measures, 'routes': own_routes,
                   'widths': own_widths, 'geometry': own_geometry, 'claims': own_claims,
                   'media': own_media, 'phases': own_phases, 'series': series, 'sources': own_sources,
                   'map_features': map_features, 'connections': own_connections}
        evidence_links = []
        def query_link(label, collection, record_id=None, filters=None):
            query = {'collection': collection, 'limit': 50}
            if record_id: query['filters'] = [{'field':'id','op':'eq','value':record_id}]
            elif filters: query['filters'] = filters
            url = 'query.html?q=' + quote(json.dumps(query,separators=(',',':')),safe='')
            if record_id: url += '&inspect=' + quote(record_id,safe='')
            evidence_links.append({'label':label,'url':url})
        radius_evidence=next((e for e in ring_radius_audit['entities'].values() if e['entity_id']==ident),None)
        if radius_evidence:
            payload['published_ring_radius_evidence']=radius_evidence
            groups['measurements'].append(radius_evidence['measurements'])
            groups['sources'].append(ring_radius_audit)
            groups['time_evidence'].append(radius_evidence['measurements'])
            evidence_links.append({'label':'Inspect published radius claims and conflicts','url':'reference-routes.html?atlas-feature='+quote(ident,safe='')+'#route-atlas'})
        if ident == astrid_audit['entity_id']:
            payload['radial_scale_evidence']=astrid_audit
            groups['measurements'].append(astrid_audit['measurements'])
            groups['sources'].append(astrid_audit)
        if ident in recurrence:
            payload['eddy_recurrence']=recurrence[ident]
            query_link('Inspect published occurrence and event lifetime', 'eddy_recurrence', recurrence[ident]['id'])
        if current_id == 'loop':
            payload['section_spans'] = loop_sections
            capabilities['scoped_width'] += len(loop_sections)
            payload['dated_diagnostics'] = loop_documents
            query_link('Open mapped Loop Current card', 'objects', ident)
            query_link('Query all ten method diagnostics', 'diagnostics', filters=[{'field':'current_id','op':'eq','value':'loop'},{'field':'observation_date','op':'exists','value':True}])
            evidence_links.append({'label':'Play the four recorded dates','url':'loop-current-recorded-dates.html'})
        if ident == network['entity_id']:
            payload['flow_network'] = network
            query_link('Open passage network card', 'flow_networks', network['id'])
            query_link('Map exit transport mooring sites', 'passage_samples', filters=[{'field':'network_id','op':'eq','value':network['id']}])
        if own_notes:
            payload.update({'scope_notes': own_notes, 'scope_audits': own_audits})
        if current_id == 'zeehan':
            calendar = scope_audits['research/zeehan-ridgway-2007-seasonal-scope-audit.json']['seasonal_calendar']
            evidence_links.append({'label':'Explore the qualitative seasonal calendar','url':'reference-routes.html#zeehan-reference-path-candidate'})
        if state_evidence:
            payload['state_evidence'] = state_evidence
        observation_dates = [c.get('observation_time') for c in own_claims] + [g.get('observation_date') for g in own_geometry] + [w.get('observed_period') for w in own_widths]
        observation_dates += [note.get('observed_period') for note in own_notes]
        if current_id == 'loop': observation_dates += [d['observation_date'] for _, d in loop_documents]
        # Pin the actual time series contents, not just their frame counts.
        if current_id == timeline['current_id']:
            payload['time_series'] = [timeline, annual]
            payload['derived_width_series'] = derived_width
            capabilities['scoped_width'] += 1
            observation_dates += [frame['date'] for doc in [timeline, annual, derived_width] for frame in doc['frames']]
        if current_id == 'norwegian-coastal':
            payload['regional_series'] = norkyst
            payload['regional_maps'] = norkyst_maps
            observation_dates += [frame['date'] for frame in norkyst['frames']]
        if current_id == necc['current_id']:
            payload['derived_width_series']=necc
            capabilities['scoped_width']+=1
            observation_dates += [time for month in necc['months'] for time in month['sample_times']]
        if current_id == florida_plot['current_id']:payload['monthly_width_plot']=florida_plot
        if current_id == leeuwin_plot['current_id']:
            payload['monthly_width_plot']=leeuwin_plot
        if current_id == kuroshio_profiles['current_id']:payload['seasonal_width_profiles']=kuroshio_profiles
        own_width_audits=[width_audits[path] for path in sorted({context['audit_file'] for w in own_widths for context in [w.get('stream_mean_context') or w.get('eulerian_section_context') or w.get('width_statistics_context') or w.get('regional_range_context') or w.get('regional_scalar_context') or w.get('mean_offshore_context') or w.get('adcp_threshold_context')] if context})]
        if own_width_audits:payload['width_scope_audits']=own_width_audits
        groups = {
            'identity': entity, 'sources': [own_sources, own_notes, own_audits] if own_notes else own_sources, 'claims': own_claims,
            'measurements': [own_measures, own_widths, payload.get('derived_width_series')],
            'routes_geometry': [own_routes, own_geometry, map_features, own_connections], 'media': own_media,
            'time_evidence': [own_phases, payload.get('time_series'), payload.get('regional_series'), payload.get('regional_maps')],
        }
        if current_id == 'zeehan':groups['time_evidence'].append(calendar)
        if current_id == florida_plot['current_id']:
            groups['measurements'].append(florida_plot);groups['time_evidence'].append(florida_plot)
            groups['sources']=[groups['sources'],{key:florida_plot[key] for key in ['source_pdf_sha256','source_url','source_locator','config_sha256','protocol_sha256','scope_audit_sha256']}]
        if current_id == leeuwin_plot['current_id']:
            groups['measurements'].append(leeuwin_plot)
            groups['time_evidence'].append(leeuwin_plot)
            groups['sources']=[groups['sources'],{key:leeuwin_plot[key] for key in ['source_pdf_sha256','source_url','source_locator','config_sha256','protocol_sha256','scope_audit_sha256']}]
        if current_id == kuroshio_profiles['current_id']:
            groups['measurements'].append(kuroshio_profiles)
            groups['time_evidence'].append(kuroshio_profiles)
            groups['sources']=[groups['sources'],{key:kuroshio_profiles[key] for key in ['source_pdf_sha256','source_url','source_locator','config_sha256','protocol_sha256','scope_audit_sha256']}]
        if own_width_audits:
            groups['sources']=[groups['sources'],own_width_audits]
            groups['measurements'].append(own_width_audits)
            groups['time_evidence'].append(own_width_audits)
        if current_id in {'algerian','alaska','pacific-equatorial-undercurrent','atlantic-equatorial-undercurrent','kuroshio-extension','new-guinea-coastal-undercurrent','zeehan'}:
            original_width_audit={'algerian':algerian_width_audit,'alaska':alaska_width_audit,'pacific-equatorial-undercurrent':pacific_euc_width_audit,'atlantic-equatorial-undercurrent':atlantic_euc_width_audit,'kuroshio-extension':kuroshio_extension_width_audit,'new-guinea-coastal-undercurrent':ngcu_width_audit,'zeehan':zeehan_width_audit}[current_id]
            payload['original_regional_width_scope']=original_width_audit
            groups['measurements'].append(original_width_audit)
            groups['sources'].append(original_width_audit)
            groups['time_evidence'].append(original_width_audit)
        if current_id == 'tsushima':
            payload['modal_decay_width_scope']=tsushima_modal_audit
            for group in ['measurements','sources','time_evidence']:groups[group].append(tsushima_modal_audit)
        if current_id == 'guinea':
            payload['model_width_scope']=guinea_width_audit
            groups['measurements'].append(guinea_width_audit)
            groups['sources'].append(guinea_width_audit)
            groups['time_evidence'].append(guinea_width_audit)
        if current_id == 'somali':
            payload['seasonal_width_scope']=somali_width_audit
            groups['measurements'].append(somali_width_audit)
            groups['sources'].append(somali_width_audit)
            groups['time_evidence'].append(somali_width_audit)
        if current_id == 'loop':
            groups['time_evidence'].append(loop_documents)
            groups['time_evidence'].append(loop_sections)
            groups['measurements'].append(loop_sections)
            groups['sources'].append([{k:d[k] for k in ['source_url','protocol_file','protocol_sha256','generator_sha256']}
                                      for _,d in loop_documents])
        if ident == network['entity_id']:
            groups['routes_geometry'].append([network['nodes'],network['edges']])
            groups['measurements'].append(network['passage_samples'])
            groups['sources'].append({'source_url':network['source_url'],'source_file_sha256':inputs[network_path]})
        if series:
            groups['time_evidence'].append(series)
        if ident in recurrence:
            groups['time_evidence'].append(recurrence[ident])
            groups['sources'].append(recurrence[ident])
        if state_evidence:
            groups['routes_geometry'].append(state_evidence)
        rows.append({'id': ident, 'label': entity['label'], 'type': entity['type'],
                     'identity_level': entity.get('identity_level','unresolved'),
                     'source_kind': entity.get('source_kind'),
                     'setting': entity.get('setting','unresolved'),
                     'time_behavior': entity.get('time_behavior','unresolved'),
                     'basin': entity.get('basin', 'Not specified'), 'capabilities': capabilities,
                     'recorded_claims': len(own_claims), 'nasa_links': sum('nasa' in m.get('url', '') for m in own_media),
                     'fingerprint': fingerprint(payload), 'series': series,
                     'section_fingerprints': {key: fingerprint(value) for key, value in groups.items()},
                     'latest_observation_date': latest_observation_date(observation_dates),
                     'claim_review_counts': dict(sorted(Counter(c['review_status'] for c in own_claims).items())),
                     'linked_source_count': len(own_sources),
                     'map_features': map_features,
                     'state_evidence': state_evidence,
                     'connections': own_connections,
                     'scope_notes': own_notes,
                     'evidence_links': evidence_links,
                     'object_url': 'object.html?id=' + quote(ident, safe=''),
                     'route_url': 'reference-routes.html#' + own_routes[0]['id'] if own_routes else None,
                     'season_url': 'seasons.html?current=' + current_id if current_id else None})
        if current_id in {'persian-gulf-saline-overflow','red-sea-saline-overflow'}:
            rows[-1]['scope_audits']=own_audits
        if ident in recurrence:
            rows[-1]['eddy_recurrence_ids']=[recurrence[ident]['id']]
    order = {'named_current': 0, 'named_eddy': 1, 'operational_eddy_detection': 2}
    rows.sort(key=lambda row: (order[row['type']], row['label'].casefold(), row['id']))
    counts = {kind: sum(r['type'] == kind for r in rows) for kind in ['named_current', 'named_eddy', 'operational_eddy_detection']}
    if counts != {'named_current': 100, 'named_eddy': 136, 'operational_eddy_detection': 4} or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('Dashboard inventory must reconcile with the release ledger')
    return {'schema': 'osw.motion-dashboard.v1', 'status': 'local_research_coverage_not_scientific_approval',
            'counts': counts, 'proposed_current_additions': len(proposals), 'input_sha256': inputs,
            'snapshot_fingerprint': fingerprint(rows), 'entries': rows,
            'connections': connections,
            'fingerprint_version': 2,
            'coverage_meaning': 'Presence of stored evidence, not confidence, currency of observations or scientific approval. Regional samples and editorial routes retain their separate scopes.'}


def main():
    result = build()
    build_ground()
    result['built_at_utc'] = datetime.now(timezone.utc).isoformat()
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"Built {len(result['entries'])} dashboard records; {result['proposed_current_additions']} proposed current additions")


if __name__ == '__main__':
    main()
