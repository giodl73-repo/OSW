"""Regional branching diagnostics must not become whole-current dimensions."""
import copy
import hashlib
import json
import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / 'research/equatorial-bifurcation-endpoint-scope-audit.json'


def validate(document):
    if document['schema'] != 'osw.equatorial-bifurcation-endpoint-scope-audit.v1' or document['status'] != 'source_reported_regional_bifurcation_context_not_current_dimensions':
        raise ValueError('Invalid endpoint-context scope')
    expected = ['research/equatorial-basin-family-inventory-audit.json', 'research/ocean-current-inventory-expansion-candidates.json', 'plans/ocean-current-measurement-protocol-v1.md']
    binding = json.loads((ROOT/'research/equatorial-endpoint-context-binding-review-v2.json').read_bytes())
    current = {path: hashlib.sha256((ROOT/path).read_bytes()).hexdigest() for path in expected}
    if (binding['schema'] != 'osw.equatorial-endpoint-context-binding-review.v2'
            or binding['all_original_proposals_unchanged'] is not True
            or binding['new_physical_measurements_admitted'] is not False
            or binding['audit_sha256'] != hashlib.sha256(AUDIT.read_bytes()).hexdigest()
            or document['inputs_sha256'] != binding['historical_input_sha256']
            or current != binding['current_input_sha256']):
        raise ValueError('Stale endpoint-context inputs')
    candidate_path = expected[1]
    prior_raw = binding['previous_candidate_document_source_json'].encode('utf8')
    prior = json.loads(prior_raw)
    candidates = json.loads((ROOT/candidate_path).read_bytes())
    if (hashlib.sha256(prior_raw).hexdigest() != document['inputs_sha256'][candidate_path]
            or candidates['entries'][:-1] != prior['entries']
            or len(prior['entries']) != binding['preserved_proposal_count']
            or [candidates['entries'][-1]['proposed_id']] != binding['added_proposed_ids']
            or binding['added_proposed_ids'] != ['southern-east-madagascar']
            or any(document['inputs_sha256'][p] != current[p] for p in expected if p != candidate_path)):
        raise ValueError('Unreviewed endpoint-context dependency change')
    proposals = {row['proposed_id']: row for row in json.loads((ROOT/expected[1]).read_bytes())['entries']}
    sources = {row['id']: row for row in document['sources']}
    for row in document['entries']:
        if row['source_id'] not in sources or proposals[row['proposed_current_id']]['parent_current_id'] != row['parent_current_id']:
            raise ValueError('Unresolved endpoint-context provenance')
        if row['metric'] != 'regional_bifurcation_latitude' or row['units'] != 'degrees_north_signed' or row['rank_eligible'] is not False or any(row[key] is not None for key in ['geometry', 'whole_current_length_km', 'current_width_km']):
            raise ValueError('Regional diagnostic admitted as current dimensions')
        for reported in row['reported_values']:
            values = reported.get('range', [reported.get('value')])
            if not values or any(type(value) not in (int,float) or not math.isfinite(value) or not -90 <= value <= 90 for value in values):
                raise ValueError('Invalid latitude')
            if 'range' in reported and (len(values) != 2 or values != sorted(values) or reported['uncertainty_type'] not in ['climatological_cycle_span_not_confidence_interval', 'filtered_time_variation_not_annual_range']):
                raise ValueError('Invalid range or uncertainty role')
            if not reported.get('locator') or not (reported.get('layer') or row.get('layer')):
                raise ValueError('Missing reported-value scope')
        timing = row['seasonal_timing']
        if timing['supports_annual_route_geometry'] is not False:
            raise ValueError('Seasonal timing promoted to annual geometry')
        for key in ['northernmost_months', 'southernmost_months']:
            months = timing[key]
            if not months or len(set(months)) != len(months) or any(type(month) is not int or not 1 <= month <= 12 for month in months):
                raise ValueError('Invalid seasonal window')


class EndpointScopeTests(unittest.TestCase):
    def test_scope_and_rejected_promotions(self):
        document = json.loads(AUDIT.read_bytes())
        validate(document)
        for key,value in [('metric','current_width'),('units','km'),('whole_current_length_km',1000),('current_width_km',100),('rank_eligible',True)]:
            invalid=copy.deepcopy(document);invalid['entries'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate(invalid)
        invalid=copy.deepcopy(document);invalid['entries'][0]['reported_values'][1]['uncertainty_type']='confidence_interval'
        with self.assertRaises(ValueError):validate(invalid)
        invalid=copy.deepcopy(document);invalid['entries'][0]['seasonal_timing']['supports_annual_route_geometry']=True
        with self.assertRaises(ValueError):validate(invalid)
        invalid=copy.deepcopy(document);invalid['inputs_sha256'][next(iter(invalid['inputs_sha256']))]='0'*64
        with self.assertRaises(ValueError):validate(invalid)


    def test_dependency_review_cannot_hide_changed_proposals_or_pins(self):
        from unittest.mock import patch
        review_path=ROOT/'research/equatorial-endpoint-context-binding-review-v2.json'
        review=json.loads(review_path.read_bytes())
        original=Path.read_bytes
        for key,value in [('audit_sha256','0'*64),('preserved_proposal_count',27),
                          ('previous_candidate_document_source_json','{}'),
                          ('added_proposed_ids',['other-current']),
                          ('all_original_proposals_unchanged',False),
                          ('new_physical_measurements_admitted',True)]:
            bad=copy.deepcopy(review);bad[key]=value
            def altered(path):
                return json.dumps(bad).encode() if path==review_path else original(path)
            with self.subTest(key=key),patch.object(Path,'read_bytes',altered),self.assertRaises(ValueError):
                validate(json.loads(AUDIT.read_bytes()))


if __name__ == '__main__':
    unittest.main()
