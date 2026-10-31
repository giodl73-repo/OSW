"""Names can be admitted without silently admitting dimensions or rewriting the base."""
import copy,unittest
import current_identity_admissions as a

class CurrentIdentityAdmissionTests(unittest.TestCase):
    def test_effective_inventory_preserves_all_base_rows(self):
        doc,inputs=a.verify_inputs();catalogue=a.catalogue(doc)
        baseline=[r for r in a.read(a.BASE+'entities.json') if r['type']=='named_current']
        self.assertEqual(catalogue['entries'][:-1],baseline)
        self.assertEqual(catalogue['current_count'],101)
        self.assertEqual(catalogue['entries'][-1]['id'],a.ENTITY)
        self.assertEqual(len(inputs[a.PATH]),64)

    def test_scope_and_identity_promotions_reject(self):
        for key,value in [('rank_eligible',True),('canonical_measurements_admitted',True),('annual_width_range_km',[100,140]),('geometry',{'type':'Point','coordinates':[48,-24]})]:
            doc=a.verify();doc['entries'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):a.validate(doc)
        doc=a.verify();doc['entries'][0]['source_dimensions']['records'][0]['value_km']=120
        with self.assertRaises(ValueError):a.validate(doc)

    def test_typed_append_preserves_base_and_rejects_collisions(self):
        base={k:a.read(a.BASE+k+'.json') for k in ['entities','sources','names','length_assessments']}
        prior=copy.deepcopy(base);a.append(base)
        for name,rows in prior.items():self.assertEqual(base[name][:-1],rows)
        self.assertEqual(base['current_identity_admissions'][0]['entity_id'],a.ENTITY)
        with self.assertRaisesRegex(ValueError,'collision'):a.append(base)

    def test_no_width_or_observation_date_is_created(self):
        rows=a.additions();self.assertNotIn('widths',rows);self.assertNotIn('geometries',rows)
        record=rows['length_assessments'][0]
        self.assertIsNone(record['published_length_km']);self.assertFalse(record['rank_eligible'])
        decision,=a.decision_rows();self.assertEqual(decision['measurement_ids'],[])
        self.assertIsNone(decision['annual_width_range_km'])

if __name__=='__main__':unittest.main()
