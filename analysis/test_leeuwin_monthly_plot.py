"""Pinned source regeneration and scope, rather than graph-readings as measurements."""
import copy
import json
import unittest
from unittest.mock import patch
from pathlib import Path
from build_leeuwin_monthly_plot import ROOT,OUTPUT,CONFIG,build
from build_motion_dashboard import build as dashboard

class LeeuwinPlotTests(unittest.TestCase):
    def test_pinned_source_regenerates_and_anchors_remain_separate(self):
        data=build()
        self.assertEqual(data,json.loads((ROOT/OUTPUT).read_text(encoding='utf-8')))
        self.assertEqual([m['month'] for m in data['months']],list(range(1,13)))
        for m in data['months']:
            self.assertLessEqual(abs(m['raw_plot_width_km']-m['approximate_width_km']),.5)
            self.assertLessEqual(m['selected_y_band_pixels'][0],m['selected_y_median_pixel'])
            self.assertGreaterEqual(m['selected_y_band_pixels'][1],m['selected_y_median_pixel'])
            if m['source_prose_width_km'] is not None:
                self.assertLessEqual(abs(m['source_prose_width_km']-m['approximate_width_km']),3)
        july,september=data['months'][6],data['months'][8]
        self.assertLessEqual(max(july['plot_reading_interval_km'][0],september['plot_reading_interval_km'][0]),min(july['plot_reading_interval_km'][1],september['plot_reading_interval_km'][1]))
        self.assertIsNone(data['annual_width_range_km'])
        self.assertFalse(data['geographic_playback_eligible'])

    def test_changed_pdf_rejected(self):
        original=Path.read_bytes
        source=ROOT/'research/source-data/leeuwin-deng-2008/journal-article.pdf'
        def read(path):return b'changed PDF' if path==source else original(path)
        with patch.object(Path,'read_bytes',read),self.assertRaisesRegex(ValueError,'Changed source PDF'):build()

    def test_dashboard_rejects_changed_or_promoted_plot(self):
        original=Path.read_bytes
        stored=json.loads(original(ROOT/OUTPUT))
        for key,value in [('annual_width_range_km',[89,132]),('is_confidence_interval',True),('source_pdf_sha256','0'*64),('months',stored['months'][:-1])]:
            with self.subTest(key=key):
                altered=copy.deepcopy(stored);altered[key]=value
                def read(path):return json.dumps(altered).encode() if path==ROOT/OUTPUT else original(path)
                with patch.object(Path,'read_bytes',read),self.assertRaisesRegex(ValueError,'Leeuwin monthly graph'):dashboard()

if __name__=='__main__':unittest.main()
