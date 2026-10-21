"""Source integrity and physical boundary failures for shipboard spans."""
from query_packet import read_bundle_bytes
import json
import unittest
import copy
import subprocess
import tempfile
import os
from pathlib import Path
from build_antilles_sadcp_layer_spans import ROOT, OUTPUT, build, measure
from compare_shipboard_reconstruction import matches as reconstruction_matches


class ShipboardSpansTests(unittest.TestCase):
    def test_native_loader_rejects_rebound_or_promoted_spans(self):
        bundle = json.loads(read_bundle_bytes(ROOT/'almanac/query-data.json'))
        cli = ROOT/'rust/osw-query/target/debug'/('osw-query-cli.exe' if os.name=='nt' else 'osw-query-cli')
        for field,value in [('current_id','gulf-stream'),('depth_m',400),
                            ('whole_current_width_km',50),('annual_width_range_km',[40,130]),
                            ('current_association_verified',True)]:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                changed = copy.deepcopy(bundle)
                changed['collections']['observed_section_spans'][0][field] = value
                path = Path(directory)/'bundle.json'
                path.write_text(json.dumps(changed,ensure_ascii=False),encoding='utf8')
                run = subprocess.run([str(cli),str(path),'-'],input='{"collection":"observed_section_spans"}',capture_output=True,text=True,encoding='utf8')
                self.assertNotEqual(run.returncode,0)
                self.assertIn('Observed shipboard spans or source scope changed',run.stderr)

    def test_checked_reconstruction(self):
        document = build()
        self.assertTrue(reconstruction_matches(json.loads((ROOT/OUTPUT).read_bytes()),document))
        self.assertEqual(document['counts']['half_peak_resolved'], 7)
        self.assertEqual(document['counts']['complete_threshold_envelopes'], 6)
        first, repeat = document['rows'][0], document['rows'][10]
        self.assertEqual(first['half_peak_span_km'], 50)
        self.assertEqual(first['threshold_span_range_km'], [40,130])
        self.assertEqual(repeat['half_peak_span_km'], 80)
        self.assertIsNone(repeat['threshold_span_range_km'])
        for row in document['rows']:
            self.assertIsNone(row['whole_current_width_km'])
            self.assertIsNone(row['annual_width_range_km'])
            self.assertFalse(row['width_rank_eligible'])
            self.assertFalse(row['current_association_verified'])
        self.assertEqual(document['rows'][3]['depth_m'],395)

    def test_gap_and_open_domain_are_not_edges(self):
        def bins(values):
            return [{'bin_index':i,'northward_m_s':v,'coordinates_lon_lat':[-76.8+i*.1,26.5] if v is not None else None} for i,v in enumerate(values)]
        gap = measure(bins([0,None,1,0]),.5,[-77,-76])
        self.assertEqual(gap['shoreward_boundary']['status'],'blocked_by_missing_bin')
        self.assertIsNone(gap['survey_span_km'])
        edge = measure(bins([1,.8,0]),.5,[-77,-76])
        self.assertEqual(edge['shoreward_boundary']['status'],'open_at_domain_edge')
        self.assertIsNone(edge['survey_span_km'])
        south = measure(bins([-.1,-.2,-.3]),.5,[-77,-76])
        self.assertEqual(south['status'],'no_positive_northward_peak')
        empty = measure(bins([None,None]),.5,[-77,-76])
        self.assertIsNone(empty['survey_span_km'])
