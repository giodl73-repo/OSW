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
    if document['inputs_sha256'] != {path: hashlib.sha256((ROOT/path).read_bytes()).hexdigest() for path in expected}:
        raise ValueError('Stale endpoint-context inputs')
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


if __name__ == '__main__':
    unittest.main()
