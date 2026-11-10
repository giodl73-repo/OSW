import hashlib
import json
import unittest
import xml.etree.ElementTree as ET
import ponsoni_emc_2016_dimensions_v1 as subject

class SourceScopeTests(unittest.TestCase):
    def test_prepared_bytes_replay_and_source_pins(self):
        facts,width=subject.build()
        for path,raw in [(subject.FACTS,subject.encoded(facts)),(subject.PREPARED,subject.encoded(width)),
                         (subject.FIGURE,subject.figure(facts))]:
            self.assertEqual((subject.ROOT/path).read_bytes(),raw)
        self.assertEqual(width['source_report_sha256'],hashlib.sha256(subject.encoded(facts)).hexdigest())
        for path,pin in facts['input_sha256'].items():self.assertEqual(subject.sha(path),pin)

    def test_summary_is_not_seasonal_measurements(self):
        facts,width=subject.build()
        self.assertEqual(width['width_range_km'],[60,100])
        for key in ['approximate_width_km','uncertainty_km','annual_width_range_km','geographic_current_edges','fixed_layer_bounds_m']:
            self.assertIsNone(width[key])
        for key in ['width_rank_eligible','annual_extrema_eligible','seasonal_playback_eligible','is_confidence_interval','independent_width_samples_admitted']:
            self.assertFalse(width[key])
        self.assertEqual(facts['new_installed_measurement_records'],0)
        self.assertFalse(facts['prior_survey_comparison']['combined_annual_range_eligible'])
        self.assertEqual(facts['section']['moorings'][0]['coast_distance_km'],6.3)

    def test_event_dates_panels_and_missing_widths(self):
        facts,_=subject.build()
        events=facts['event_index']
        self.assertEqual([(e['date'],e['source_panel']) for e in events],[
            ('2010-11-17','Figure4h'),('2010-12-30','Figure4b'),('2011-01-19','Figure4i'),
            ('2011-06-02','Figure4g'),('2011-07-07','Figure4c'),('2012-07-22','Figure4f'),
            ('2012-11-28','Figure4d'),('2012-12-25','Figure4e')])
        for event in events:
            self.assertIsNone(event['width_km'])
            self.assertFalse(event['seasonal_playback_eligible'])
        root=ET.fromstring(subject.figure(facts))
        text=' '.join(root.itertext())
        for event in events:self.assertIn(event['date'],text)
        self.assertIn('not yet installed',text)
        self.assertEqual(root.attrib['viewBox'],'0 0 480 1040')

if __name__=='__main__':unittest.main()
