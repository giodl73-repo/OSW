import copy,unittest
from build_current_depth_evidence_cards_v1 import cards

def fixture():
    return {'records':[{'entity_id':'current:a','name':'A','identity_level':'current'},{'entity_id':'current:family','name':'Family','identity_level':'system'}],
        'evidence':[{'id':'core','entity_id':'current:a','metric':'core_depth','unit':'m','approximate_value_m':50},
                    {'id':'bound','entity_id':'current:a','metric':'derived_supported_component_penetration_lower_bound','unit':'m','lower_bound_m':200,'lower_bound_exclusive':False},
                    {'id':'layer','entity_id':'current:a','metric':'reported_advected_atlantic_water_layer_thickness','unit':'m','range_m':[300,400]}]}

class EvidenceSemantics(unittest.TestCase):
    def test_core_censor_and_thickness_never_become_a_current_depth(self):
        view=fixture();before=copy.deepcopy(view);report=cards(view);r=report['records'][0]
        self.assertEqual([e['quantity_role'] for e in r['references']],['core_position_not_bottom','scoped_boundary_or_flow_proxy','layer_thickness_not_depth_below_surface'])
        self.assertEqual(r['references'][1]['lower_bound_m'],200);self.assertFalse(r['references'][1]['lower_bound_exclusive'])
        self.assertEqual(r['references'][2]['range_m'],[300,400])
        self.assertIsNone(r['headline_whole_current_depth_m']);self.assertIsNone(r['annual_depth_range_m']);self.assertIsNone(r['volume_km3'])
        self.assertEqual(view,before)

    def test_parent_does_not_inherit_member_evidence_and_missing_is_not_zero(self):
        r=cards(fixture())['records'][1]
        self.assertEqual(r['references'],[]);self.assertEqual(r['status'],'not_assessed_no_zero_implied')
        self.assertFalse(r['members_inherited_or_aggregated']);self.assertIsNone(r['headline_whole_current_depth_m'])

    def test_pressure_and_transport_selection_stay_distinct(self):
        view=fixture();view['evidence']=[{'id':'p','entity_id':'current:a','metric':'transport_selected_depth_extent','unit':'dbar','lower_bound_m':None,'source_definition':'selected integration pressure, not a current bottom'}]
        r=cards(view)['records'][0];self.assertEqual(r['status'],'context_or_core_only')
        self.assertEqual(r['references'][0]['unit'],'dbar');self.assertIsNone(r['references'][0]['lower_bound_m'])
        self.assertEqual(r['references'][0]['source_definition'],view['evidence'][0]['source_definition'])

    def test_duplicate_or_unknown_reference_rejected(self):
        view=fixture();view['evidence'].append(copy.deepcopy(view['evidence'][0]))
        with self.assertRaises(ValueError):cards(view)
        view=fixture();view['evidence'][0]['entity_id']='current:unknown'
        with self.assertRaises(ValueError):cards(view)

if __name__=='__main__':unittest.main()
