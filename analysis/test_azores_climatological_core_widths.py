"""Preserve the reported core metric, atlas quarters and unknown width errors."""
import copy,unittest
from unittest.mock import patch
from pathlib import Path
from build_azores_climatological_core_width_figure import load,validate,verify_originals,RECORD,ROOT

class ClimatologicalCoreTests(unittest.TestCase):
    def test_source_pair_and_season_support(self):
        doc=load();validate(doc)
        self.assertEqual([(r['approximate_width_km'],r['calendar_months']) for r in doc['measurements']],[(240,[4,5,6]),(400,[10,11,12])])
        self.assertIsNone(doc['annual_width_range_km'])
        self.assertIsNone(doc['observed_period'])
        self.assertFalse(doc['model_support']['integration_grid_is_native_observation_resolution'])
        self.assertFalse(doc['source_transport_error_is_width_error'])

    def test_changed_quantities_and_promoted_ranges_rejected(self):
        base=load()
        for key,value in [('annual_width_range_km',[240,400]),('whole_current_width_km',320),('width_rank_eligible',True),('seasonal_map_playback_eligible',True),('source_transport_error_is_width_error',True),('current_id','azores-countercurrent')]:
            with self.subTest(key=key):
                bad=copy.deepcopy(base);bad[key]=value
                with self.assertRaises(ValueError):validate(bad)
        bad=copy.deepcopy(base);bad['measurements'][0]['calendar_months']=[3,4,5]
        with self.assertRaises(ValueError):validate(bad)
        bad=copy.deepcopy(base);bad['measurements'][0]['measurement_uncertainty_interval_km']=[230,250]
        with self.assertRaises(ValueError):validate(bad)

    def test_changed_record_bytes_rejected(self):
        original=RECORD.read_bytes();read=Path.read_bytes
        with patch.object(Path,'read_bytes',lambda p:original+b'\n' if p==RECORD else read(p)):
            with self.assertRaisesRegex(ValueError,'reviewed seasonal'):load()

    def test_optional_original_review_rejects_corrupt_document(self):
        doc=load();source=ROOT/doc['source_document_file'];read=Path.read_bytes
        with patch.object(Path,'read_bytes',lambda p:b'%PDF-corrupt' if p==source else read(p)):
            with self.assertRaisesRegex(ValueError,'source original'):verify_originals(doc)

if __name__=='__main__':unittest.main()
