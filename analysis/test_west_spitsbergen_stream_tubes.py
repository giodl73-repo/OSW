"""Threshold pairs, source definitions and false sampling promotions are distinct."""
import copy,json,unittest
from check_west_spitsbergen_stream_tubes import ROOT,AUDIT,validate_row

class WscStreamTubes(unittest.TestCase):
    def test_source_table_and_no_alias_transfer(self):
        inventory=json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())
        rows=[r for r in inventory['measurements'] if r['current_id']=='west-spitsbergen']
        self.assertEqual([r['approximate_width_km'] for r in rows],[24,24,21,61,35,10])
        self.assertEqual(len(rows),6)
        self.assertFalse(any(r['current_id']=='spitsbergen-atlantic' for r in inventory['measurements']))
        for row in rows:validate_row(row)

    def test_scope_and_source_copy_mutations(self):
        rows=json.loads((ROOT/AUDIT).read_bytes())['measurements']
        inventory=json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())
        records={r['id']:r for r in inventory['measurements']}
        for row in rows:
            for key,value in [('current_id','spitsbergen-atlantic'),('width_range_km',[11,61]),('approximate_width_km',100),('calendar_months',[8]),('fixed_layer_bounds_m',[45,475]),('observed_period',{'start':'2015-08-12','end':'2015-08-21'}),('seasonal_playback_eligible',True),('width_rank_eligible',True)]:
                bad=copy.deepcopy(records[row['id']]);bad[key]=value
                with self.subTest(id=row['id'],key=key),self.assertRaises(ValueError):validate_row(bad)
            for key,value in [('threshold_sensitivity_cases',[{'velocity_m_s':0.02,'width_km':11}]),('transport_tolerance_is_width_error',True),('reference_pressure_is_width_depth',True),('boundary_coordinates_extracted',True),('shared_observation_group','independent'),('audit_sha256','0'*64)]:
                bad=copy.deepcopy(records[row['id']]);bad['stream_tube_context'][key]=value
                with self.subTest(id=row['id'],context=key),self.assertRaises(ValueError):validate_row(bad)

if __name__=='__main__':unittest.main()
