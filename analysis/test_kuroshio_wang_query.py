"""Complete typed projection and unchanged measurement inventories."""
import json
from pathlib import Path
import subprocess
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import kuroshio_wang_query as k


class QueryProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract,cls.doc=k.verify_inputs();cls.rows=k.samples(cls.doc)

    def test_complete_cases_and_unknowns_preserved(self):
        self.assertEqual(len(self.rows),6588)
        self.assertEqual(len({r['id'] for r in self.rows}),6588)
        axes=[r for r in self.rows if r['quantity']=='regional_axis_length']
        spans=[r for r in self.rows if r['quantity']=='fixed_latitude_boundary_span']
        self.assertEqual((len(axes),len(spans)),(1098,5490))
        self.assertEqual(sum(r['value_km'] is not None for r in axes),908)
        self.assertEqual(sum(r['value_km'] is not None for r in spans),4976)
        for r in self.rows:
            self.assertEqual(r['status']=='resolved',r['value_km'] is not None)
            self.assertFalse(r['rank_eligible']);self.assertEqual(r['evidence_class'],'model_derived')
            self.assertEqual(r['diagnostic_id'],k.ID)
            self.assertIsNone(r['uncertainty_km'])
            if r['quantity']=='fixed_latitude_boundary_span':self.assertIsNone(r['boundary_fallback_occurred'])

    def test_every_record_resolves_exact_daily_source(self):
        for r in self.rows:
            src=self.doc['daily'][r['report_case_index']]
            self.assertEqual((r['sample_date'],r['source_level'],r['nominal_depth_m']),(src['date'],src['source_level'],src['nominal_depth_m']))
            if r['quantity']=='regional_axis_length':self.assertEqual(r['value_km'],src['axis']['length_km'])
            else:self.assertEqual(r['value_km'],next(s['span_km'] for s in src['sections'] if s['latitude']==r['section_latitude']))

    def test_scientific_cases_frames_statistics_and_scope_preserved(self):
        expected=json.loads(subprocess.check_output(['git','show','b2b6556:'+k.source.FILE],cwd=k.ROOT))
        for key in ['daily','summaries','display_frames','counts','axis_status_counts','section_status_counts','conventions','source']:
            with self.subTest(key=key):self.assertEqual(expected[key],self.doc[key])
        self.assertNotIn('native_wasm_ui_integrated',self.doc)
        self.assertEqual(k.record(self.doc)['source_json'].encode(),(k.ROOT/k.source.FILE).read_bytes())

    def test_inventory_and_canonical_measurement_bytes_unchanged(self):
        for path in ['research/ocean-current-working-measurements.json','research/ocean-current-width-inventory.json','research/ocean-current-working-reference-routes.json','research/ocean-current-working-reference-route-state-join.json']:
            with self.subTest(path=path):self.assertEqual(subprocess.check_output(['git','show','b2b6556:'+path],cwd=k.ROOT),(k.ROOT/path).read_bytes())

    def test_source_and_projection_contract_are_bound(self):
        self.assertEqual(self.contract['sample_count'],len(self.rows))
        self.assertEqual(self.contract['source_record']['id'],k.SOURCE_ID)
        self.assertTrue(self.contract['source_record']['provider_asset_redistributed'])
        self.assertEqual(self.contract['source_record']['license'],'CC BY4.0')
        self.assertEqual(self.contract['source_report_sha256'],k.source.digest(k.source.FILE))

    def test_ids_survive_insertion_and_reordering_of_source_cases(self):
        before=k.samples({'daily':self.doc['daily'][:3]})
        after=k.samples({'daily':[self.doc['daily'][3],*reversed(self.doc['daily'][:3])]})
        def keyed(rows):return {(r['sample_date'],r['source_level'],r['quantity'],r.get('section_latitude')):r['id'] for r in rows}
        first,later=keyed(before),keyed(after)
        for key,id in first.items():self.assertEqual(later[key],id)
        self.assertEqual(before[0]['id'],'dimension:kuroshio:wang-v1:2024-01-01:z01:axis-18n-30n-v1')
        self.assertEqual(before[1]['id'],'dimension:kuroshio:wang-v1:2024-01-01:z01:span-18p5n-v1')


if __name__=='__main__':unittest.main()
