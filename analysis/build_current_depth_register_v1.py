"""Build a source-only depth inventory; never load ocean fields or runtime data."""
import csv
import hashlib
import io
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'research/current-depth-source-facts-v1.json'
RULES = 'research/current-depth-rules-v1.json'
INVENTORY = 'research/current-length-estimate-register-v1.json'
OUTPUT = 'research/current-depth-register-v1.json'
CSV = 'research/current-depth-register-v1.csv'


def validate_reference(row, identities, metrics):
    if row['entity_id'] not in identities or row['metric'] not in metrics:
        raise ValueError('Unknown identity or depth metric')
    if row['unit'] != 'm' or row['vertical_datum'] != 'local_sea_surface_positive_down':
        raise ValueError('Metre-depth reference cannot silently normalize pressure or another datum')
    point = row['approximate_value_m']
    if not isinstance(point, (int, float)) or isinstance(point, bool) or not math.isfinite(point) or point < 0:
        raise ValueError('Invalid depth value')
    for key in ['geographic_scope', 'temporal_scope', 'source_definition', 'source_url', 'source_locator', 'source_citation', 'qualification']:
        if not row.get(key):
            raise ValueError('Missing source support: ' + key)
    for key in ['upper_boundary_m', 'lower_boundary_m', 'thickness_m', 'uncertainty_m', 'annual_range_m', 'calendar_months']:
        if row[key] is not None:
            raise ValueError('Initial prose references cannot fabricate paired bounds, thickness or annual coverage')
    for key in ['whole_current_representative', 'volume_eligible', 'physical_state_join_eligible', 'seasonal_playback_eligible', 'annual_extrema_eligible']:
        if row[key] is not False:
            raise ValueError('Unreviewed promotion of scoped depth reference')
    if row['observed_period'] is not None:
        import datetime
        start, end = (datetime.date.fromisoformat(row['observed_period'][key]) for key in ['start', 'end'])
        if start > end or row['evidence_kind'] != 'published_observed_section':
            raise ValueError('Invalid occupation period')


def build(root=ROOT):
    pins = {}
    def read(path):
        raw = (root/path).read_bytes()
        pins[path] = hashlib.sha256(raw).hexdigest()
        return json.loads(raw)
    inventory = read(INVENTORY)
    identities = {r['entity_id']: r for r in inventory['records']}
    if len(identities) != 111 or len(inventory['records']) != 111:
        raise ValueError('Complete 111-current inventory required')
    rules = read(RULES)
    source = read(SOURCE)
    evidence, seen = [], set()
    for i, raw in enumerate(source['references']):
        validate_reference(raw, identities, rules['metric_types'])
        if raw['id'] in seen:
            raise ValueError('Duplicate reference ID')
        seen.add(raw['id'])
        evidence.append(dict(raw, source_file=SOURCE, source_pointer=f'/references/{i}', source_sha256=pins[SOURCE]))
    records = []
    for entity in sorted(identities.values(), key=lambda r: (r['name'].casefold(), r['entity_id'])):
        refs = [r['id'] for r in evidence if r['entity_id'] == entity['entity_id']]
        records.append({'entity_id': entity['entity_id'], 'name': entity['name'], 'basin': entity['basin'], 'identity_level': entity['identity_level'], 'depth_reference_ids': refs, 'status': 'scoped_depth_reference' if refs else 'not_yet_assessed', 'whole_route_depth_m': None, 'annual_depth_range_m': None, 'volume_km3': None, 'current_card_url': entity['current_card_url']})
    owners = sum(bool(r['depth_reference_ids']) for r in records)
    return {'schema': 'osw.current-depth-register.v1', 'status': 'INITIAL_SCOPED_DEPTH_REFERENCES_NOT_WHOLE_ROUTE_PROJECTIONS', 'rules_file': RULES, 'generator_file': 'analysis/build_current_depth_register_v1.py', 'generator_sha256': hashlib.sha256((root/'analysis/build_current_depth_register_v1.py').read_bytes()).hexdigest(), 'input_sha256': pins, 'counts': {'identities': len(records), 'depth_references': len(evidence), 'identities_with_scoped_depth_reference': owners, 'identities_not_yet_assessed': len(records)-owners, 'whole_route_depth_profiles': 0, 'volume_estimates': 0}, 'records': records, 'evidence': evidence, 'runtime_changed': False, 'full_goal_complete': False}


def csv_bytes(document):
    columns = ['id', 'entity_id', 'metric', 'approximate_value_m', 'unit', 'vertical_datum', 'phase_label', 'geographic_scope', 'temporal_scope', 'source_definition', 'evidence_kind', 'source_url', 'source_locator', 'qualification']
    out = io.StringIO(newline='')
    writer = csv.DictWriter(out, fieldnames=columns, lineterminator='\n', extrasaction='ignore')
    writer.writeheader()
    writer.writerows(document['evidence'])
    return out.getvalue().encode('utf8')


if __name__ == '__main__':
    document = build()
    (ROOT/OUTPUT).write_bytes((json.dumps(document, indent=2, ensure_ascii=False)+'\n').encode('utf8'))
    (ROOT/CSV).write_bytes(csv_bytes(document))
    print(json.dumps(document['counts']))
