"""Two published prose reports fill scoped gaps without manufacturing envelopes."""
import copy,unittest
from unittest.mock import patch
import current_measurement_admissions as m
import current_identity_admissions as identity

class ProseDimensionAdmissionTests(unittest.TestCase):
    def test_source_values_rank_and_scope_remain_distinct(self):
        doc,inputs=m.verify_inputs()
        self.assertEqual(doc['measurement']['value'],650)
        self.assertEqual(doc['length_assessment']['published_rank'],12)
        width=doc['width_record'];self.assertEqual(width['approximate_width_km'],120)
        self.assertEqual(width['observed_period'],'2001-04')
        self.assertIsNone(width['fixed_layer_bounds_m']);self.assertIsNone(width['uncertainty_km'])
        self.assertFalse(width['velocity_averaging_layer_is_verified_width_layer'])
        self.assertFalse(width['seasonal_playback_eligible']);self.assertIsNone(width['annual_width_range_km'])
        self.assertIsNone(doc['original_source_file_sha256']);self.assertFalse(doc['source_figures_digitized'])
        self.assertIn(m.EXPORT,inputs)

    def test_working_export_preserves_original_records_and_ranks(self):
        doc=m.verify();export=m.working_export(doc)
        self.assertEqual(export['measurements'][:-1],identity.read(identity.BASE+'measurements.json'))
        self.assertEqual(export['length_assessments'][:-1],identity.read(identity.BASE+'length_assessments.json'))
        self.assertEqual(export['widths'][:-1],identity.read('research/ocean-current-width-inventory.json')['measurements'])
        self.assertEqual(len(export['widths']),157)
        self.assertEqual(len({r['current_id'] for r in export['widths']}),83)
        self.assertEqual(sum(r['rank_eligible'] for r in export['length_assessments']),12)
        sources={r['id'] for r in export['sources']}
        self.assertTrue(all(r['source_id'] in sources for r in export['measurements']))
        self.assertEqual(export['sources'][-1],doc['source_record'])

    def test_changed_values_and_promotions_reject_even_with_unchanged_inputs(self):
        original=m.ROOT/m.PATH;read=m.Path.read_bytes
        for field,value in [('approximate_width_km',140),('annual_width_range_km',[100,140]),('seasonal_playback_eligible',True),('fixed_layer_bounds_m',[0,100])]:
            doc=m.verify();doc['width_record'][field]=value
            def altered(path):return m.encoded(doc) if path==original else read(path)
            with self.subTest(field=field),patch.object(m.Path,'read_bytes',altered),self.assertRaisesRegex(ValueError,'Stale'):
                m.verify()

    def test_append_replaces_only_current_assessment_and_rejects_duplicate(self):
        collections={key:identity.read(identity.BASE+key+'.json') for key in ['entities','sources','names','length_assessments','measurements','claims']}
        identity.append(collections);collections['widths']=identity.read('research/ocean-current-width-inventory.json')['measurements']
        before=copy.deepcopy(collections);m.append(collections)
        for name in ['measurements','claims','widths']:self.assertEqual(collections[name][:-1],before[name])
        self.assertEqual(collections['length_assessments'][:-1],before['length_assessments'][:-1])
        self.assertEqual(collections['length_assessments'][-1]['entity_id'],m.ENTITY)
        with self.assertRaisesRegex(ValueError,'Duplicate'):m.append(collections)

if __name__=='__main__':unittest.main()
