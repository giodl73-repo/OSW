"""Complete existing-object taxonomy projection, source identity and graph integrity."""
import copy,json,unittest
from pathlib import Path
from build_query_taxonomy import build,ROOT
class TaxonomyProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    def projected(self,objects=None,entities=None,ledger=None):
        def read(path):
            return ledger if path.endswith('ocean-current-almanac.json') and ledger is not None else json.loads((ROOT/path).read_bytes())
        c=self.bundle['collections'];return build(c['objects'] if objects is None else objects,c['entities'] if entities is None else entities,read)
    def test_complete_inventory_and_existing_ledger_projection(self):
        edges,meta=self.projected();self.assertEqual(edges,self.bundle['collections']['taxonomy_links']);self.assertEqual(meta,self.bundle['manifest']['taxonomy'])
        self.assertEqual(meta['node_count'],240);self.assertEqual(meta['link_count'],20)
        self.assertTrue(all(e['measurement_inheritance_eligible'] is False and e['physical_connectivity_eligible'] is False and e['naming_source_is_parent_relation_evidence'] is False for e in edges))
    def test_missing_identity_and_inconsistent_facets_rejected(self):
        c=self.bundle['collections']
        with self.assertRaises(ValueError):self.projected(objects=c['objects'][:-1])
        bad=copy.deepcopy(c['objects']);bad[0]['identity_level']='family'
        with self.assertRaises(ValueError):self.projected(objects=bad)
    def test_invalid_parents_and_cycles_rejected(self):
        source=json.loads((ROOT/'research/ocean-current-almanac.json').read_bytes())
        for target in ['missing-current','gulf-stream']:
            bad=copy.deepcopy(source);next(r for r in bad['entries'] if r['id']=='gulf-stream')['part_of_system']=target
            with self.subTest(target=target),self.assertRaises(ValueError):self.projected(ledger=bad)
        bad=copy.deepcopy(source);next(r for r in bad['entries'] if r['id']=='gulf-stream-system')['part_of_system']='north-atlantic'
        with self.assertRaises(ValueError):self.projected(ledger=bad)
if __name__=='__main__':unittest.main()
