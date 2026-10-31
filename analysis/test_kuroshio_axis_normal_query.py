"""All source attempts retain identity, missingness and physical admission scope."""
import json
import subprocess
import unittest
import kuroshio_axis_normal_query as k


class NormalProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract,cls.doc=k.verify_inputs()
        cls.rows=k.samples(cls.doc)

    def test_complete_projection_and_source_pointer(self):
        self.assertEqual(len(self.rows),16470)
        self.assertEqual(len({r['id'] for r in self.rows}),16470)
        self.assertEqual(sum(r['status']=='resolved' for r in self.rows),14034)
        self.assertEqual(sum(r['is_primary_convention'] and r['status']=='resolved' for r in self.rows),4680)
        for row in self.rows:
            original=self.doc['cases'][row['report_case_index']]
            self.assertEqual(row['id'],original['id'])
            self.assertEqual(row['value_km'],original['span_km'])
            self.assertEqual(row['sample_date'],original['sample_date'])
            self.assertEqual(row['status']=='resolved',row['value_km'] is not None)
            for field in ['rank_eligible','physical_width_inventory_admitted','velocity_normal_verified','ocean_connectivity_verified']:
                self.assertFalse(row[field])
            for field in ['uncertainty_km','boundary_fallback_occurred','threshold_attained']:
                self.assertIsNone(row[field])

    def test_source_record_report_and_existing_inventories_unchanged(self):
        self.assertEqual(k.record(self.doc)['source_json'].encode(),(k.ROOT/k.source.FILE).read_bytes())
        self.assertEqual(self.contract['source_record'],json.loads((k.ROOT/k.prior.FILE).read_bytes())['source_record'])
        for path in [k.source.FILE,k.source.FIGURE,'research/ocean-current-working-measurements.json','research/ocean-current-width-inventory.json','research/ocean-current-working-reference-routes.json','research/ocean-current-working-reference-route-state-join.json']:
            with self.subTest(path=path):
                self.assertEqual(subprocess.check_output(['git','show','99892a4:'+path],cwd=k.ROOT),(k.ROOT/path).read_bytes())

    def test_ids_survive_reordering_and_insertion(self):
        before=k.samples({'cases':self.doc['cases'][:4]})
        after=k.samples({'cases':[self.doc['cases'][4],*reversed(self.doc['cases'][:4])]})
        for row in before:
            matching=next(r for r in after if r['id']==row['id'])
            self.assertEqual({a:b for a,b in row.items() if a!='report_case_index'}, {a:b for a,b in matching.items() if a!='report_case_index'})


if __name__=='__main__':unittest.main()
