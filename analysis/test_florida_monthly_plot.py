"""Protect original-source identity and graph-reading semantics."""
import copy,json,unittest
from pathlib import Path
from unittest.mock import patch
from build_florida_monthly_plot import ROOT,OUTPUT,build
from build_motion_dashboard import build as dashboard
class FloridaMonthlyPlotTests(unittest.TestCase):
    def test_original_curve_rebuilds_without_false_uncertainty_or_edges(self):
        d=build();self.assertEqual(d,json.loads((ROOT/OUTPUT).read_bytes()))
        self.assertEqual([r['month'] for r in d['months']],list(range(1,13)))
        self.assertEqual(d['curve_role'],'source_plotted_overall_average_of_monthly_means')
        for r in d['months']:
            self.assertLessEqual(abs(r['raw_plot_width_km']-r['approximate_width_km']),.5)
            self.assertEqual(r['plot_reading_interval_km'],[r['approximate_width_km']-1,r['approximate_width_km']+1])
        self.assertFalse(d['source_variability_envelope_extracted'])
        self.assertIsNone(d['annual_width_range_km']);self.assertIsNone(d['section_geometry'])
        self.assertFalse(d['geographic_playback_eligible']);self.assertTrue(d['chart_playback_eligible'])
        # Independently read broad bands from the rendered figure, not exact implementation outputs.
        self.assertLess(d['months'][1]['approximate_width_km'],55)
        self.assertGreater(d['months'][7]['approximate_width_km'],63)
        self.assertEqual(d['months'][0]['sample_x_pixel']-d['months'][0]['tick_x_pixel'],8)
    def test_changed_original_rejected(self):
        original=Path.read_bytes;source=ROOT/'research/source-data/florida-archer-2017/journal-article.pdf'
        with patch.object(Path,'read_bytes',lambda p:b'changed' if p==source else original(p)),self.assertRaisesRegex(ValueError,'Changed Florida source PDF'):build()
    def test_missing_curve_and_promoted_range_rejected_by_dashboard(self):
        stored=json.loads((ROOT/OUTPUT).read_bytes());original=Path.read_bytes
        for key,value in [('months',stored['months'][:-1]),('annual_width_range_km',[53,64]),('source_variability_envelope_extracted',True),('is_confidence_interval',True)]:
            altered=copy.deepcopy(stored);altered[key]=value
            with self.subTest(key=key),patch.object(Path,'read_bytes',lambda p:json.dumps(altered).encode() if p==ROOT/OUTPUT else original(p)),self.assertRaisesRegex(ValueError,'Florida monthly graph'):dashboard()
if __name__=='__main__':unittest.main()
