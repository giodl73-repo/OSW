"""Source-custody and missing-profile semantics for seasonal graph readings."""
import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from build_kuroshio_seasonal_width_profiles import ROOT,OUTPUT,build
from build_motion_dashboard import build as dashboard

class ProfileTests(unittest.TestCase):
    def test_deterministic_readings_keep_missing_and_no_regional_mean(self):
        doc=build();self.assertEqual(doc,json.loads((ROOT/OUTPUT).read_text(encoding='utf-8')))
        self.assertEqual([s['label'] for s in doc['seasons']],['winter','spring','summer','autumn'])
        self.assertEqual(sum(s['resolved_samples'] for s in doc['seasons']),59)
        for season in doc['seasons']:
            self.assertIsNone(season['regional_mean_width_km'])
            self.assertIsNone(season['calendar_months'])
            self.assertIsNone(season['geographic_edge_coordinates'])
            for sample in season['samples']:
                if sample['approximate_width_km'] is None:
                    self.assertIsNone(sample['plot_reading_interval_km'])
                    self.assertIn(sample['candidate_band_count'],[0,2])
                else:
                    self.assertLessEqual(abs(sample['raw_plot_width_km']-sample['approximate_width_km']),2.5)
                    self.assertEqual(sample['candidate_band_count'],1)
                    self.assertEqual(sample['plot_reading_interval_km'],[sample['approximate_width_km']-10,sample['approximate_width_km']+10])
        self.assertFalse(doc['geographic_playback_eligible'])
        self.assertIsNone(doc['annual_width_range_km'])

    def test_dashboard_rejects_missing_fill_and_scope_promotion(self):
        original=Path.read_bytes;stored=json.loads(original(ROOT/OUTPUT))
        missing=next(r for s in stored['seasons'] for r in s['samples'] if r['approximate_width_km'] is None)
        for key,value in [('annual_width_range_km',[140,265]),('is_confidence_interval',True),('geographic_playback_eligible',True)]:
            altered=copy.deepcopy(stored);altered[key]=value
            def read(path):return json.dumps(altered).encode() if path==ROOT/OUTPUT else original(path)
            with self.subTest(key=key),patch.object(Path,'read_bytes',read),self.assertRaisesRegex(ValueError,'Kuroshio seasonal profile'):dashboard()
        altered=copy.deepcopy(stored)
        row=next(r for s in altered['seasons'] for r in s['samples'] if r['approximate_width_km'] is None)
        row.update(approximate_width_km=0,plot_reading_interval_km=[0,0])
        def read(path):return json.dumps(altered).encode() if path==ROOT/OUTPUT else original(path)
        with patch.object(Path,'read_bytes',read),self.assertRaisesRegex(ValueError,'Kuroshio seasonal profile'):dashboard()

if __name__=='__main__':unittest.main()
