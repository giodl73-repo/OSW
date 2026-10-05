"""Network support, transport aggregation, positions and admission boundaries."""
import copy
import json
import unittest
from build_flow_network import build,validate,INPUT
class FlowNetworkTests(unittest.TestCase):
 def test_sections_and_coords_preserve_source_support(self):
  records=build();doc=records['flow_networks'][0]['document']
  self.assertEqual(len(doc['nodes']),12);self.assertEqual(len(doc['edges']),14)
  self.assertEqual([s['value'] for s in doc['passage_samples']],[-2.6,-4.9,-7.5])
  self.assertEqual(sum(s['value'] for s in doc['passage_samples']),-15)
  self.assertEqual([s['transport_integration_width_km'] for s in doc['passage_samples']],[35,35,160])
  self.assertEqual(sum(len(s['moorings']) for s in doc['passage_samples']),8)
  for s in records['passage_samples']:
   self.assertFalse(s['integration_width_is_physical_current_width']);self.assertIsNone(s['whole_current_width_km'])
   self.assertEqual(len(s['map_features']),len(s['moorings']))
  for edge in doc['edges']:self.assertIsNone(edge['geometry']);self.assertIsNone(edge['length_km'])
 def test_corrupt_admissions_topology_coordinates_and_transport_fail(self):
  for mutation in ['edge','length','sum','coordinate','width']:
   doc=json.loads(INPUT.read_bytes())
   if mutation=='edge':doc['edges'][0]['to_id']='missing'
   elif mutation=='length':doc['length_km']=100
   elif mutation=='sum':doc['passage_samples'][0]['value']=99
   elif mutation=='coordinate':doc['passage_samples'][0]['moorings'][0]['coordinates_lon_lat'][0]=0
   else:doc['passage_samples'][0]['integration_width_is_physical_current_width']=True
   with self.assertRaises(ValueError):validate(doc)
if __name__=='__main__':unittest.main()
