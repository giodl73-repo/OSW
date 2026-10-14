"""Source scaling, complete leap-year support, geometry and scope regression."""
import calendar,json,unittest
from unittest.mock import patch
from pyproj import Geod
import acquire_south_australian_hycom_section as acquire
import build_south_australian_hycom_spans as spans
from build_basin_surface_section_spans import diagnostic_matches,measure

class SouthAustralianTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=spans.source_inventory();cls.report=spans.build()

    def test_original_scaling_masks_coordinates_and_leap_year(self):
        source=self.source
        self.assertEqual(source['counts']['vector_positions'],27816)
        self.assertEqual(source['frames'][0]['time'],'2012-01-01T00:00:00Z')
        self.assertEqual(source['frames'][-1]['time'],'2012-12-31T00:00:00Z')
        self.assertEqual(source['frames'][59]['time'],'2012-02-29T00:00:00Z')
        self.assertEqual(source['source_layer_m'],100)
        masked=0
        for frame in source['frames']:
            self.assertEqual(len(frame['samples']),76)
            for cell in frame['samples']:
                self.assertEqual(cell['longitude'],132)
                for raw,decoded in [('source_u_int16','eastward_m_s'),('source_v_int16','northward_m_s')]:
                    if cell[raw]==-30000:self.assertIsNone(cell[decoded]);masked+=1
                    else:self.assertAlmostEqual(cell[decoded],cell[raw]/1000,places=12)
        self.assertGreater(masked,0)

    def test_monthly_pair_support_and_independent_distance(self):
        for month in self.report['months']:
            days=calendar.monthrange(2012,month['month'])[1]
            self.assertEqual(len(month['source_times']),days)
            required=(4*days+4)//5
            self.assertEqual(month['minimum_required_pairs'],required)
            for cell in month['profile']:
                self.assertEqual(cell['component_m_s'] is None,cell['paired_source_samples']<required)
            for scenario in month['threshold_scenarios']:
                if scenario['span_km'] is None:continue
                a,b=[scenario['boundaries'][k]['longitude_latitude'] for k in ['low_coordinate','high_coordinate']]
                self.assertAlmostEqual(scenario['span_km'],Geod(ellps='WGS84').inv(*a,*b)[2]/1000,places=8)
                self.assertAlmostEqual(scenario['native_cell_spacings'],(b[1]-a[1])/.08,places=9)
                self.assertEqual(scenario['resolution_review_required'],scenario['native_cell_spacings']<4)

    def test_receipt_matches_and_no_current_width_promotion(self):
        self.assertTrue(diagnostic_matches(json.loads(spans.OUTPUT.read_bytes()),self.report))
        self.assertEqual(self.report['summary']['resolved_nominal_months'],12)
        self.assertEqual(self.report['summary']['sample_monthly_mean_span_range_km'],[30,130])
        for field in ['current_association_verified','whole_current_representative','width_rank_eligible','annual_extrema_eligible','is_climatology','seasonal_playback_eligible']:
            self.assertIs(self.report[field],False)
        self.assertIsNone(self.report['annual_width_range_km'])

    def test_wrong_index_owner_or_layer_is_rejected(self):
        config=json.loads(acquire.CONFIG.read_bytes())
        for field,value in [('longitude_index',1650),('depth_m',0),('year',2013),('current_id','leeuwin'),('component','northward')]:
            with self.subTest(field=field),patch.object(acquire.json,'loads',return_value=dict(config,**{field:value})):
                with self.assertRaises(ValueError):acquire.source_urls()

    def test_coastal_hole_is_not_closed_or_doubled(self):
        profile=[{'coordinate':-36+i*.08,'component_m_s':v} for i,v in enumerate([0,.1,.2,None,None])]
        section={'fixed_axis':'longitude','fixed_coordinate':132,'varying_axis':'latitude','peak_search':[-36,-35],'component':'eastward'}
        result=measure(profile,section,.5)
        self.assertIsNone(result['span_km'])
        self.assertEqual(result['boundaries']['high_coordinate']['status'],'missing_before_crossing')

if __name__=='__main__':unittest.main()
