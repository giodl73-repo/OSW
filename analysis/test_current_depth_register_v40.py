import copy,csv,io,json
import unittest
import build_current_depth_register_v39 as previous
import build_current_depth_register_v40 as depth


class BrazilModalMeanSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.rows=cls.data['evidence'][343:]
        cls.ids={r['entity_id'] for r in cls.data['records']};cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def reject(self,row,changes):
        for k,v in changes:
            r=copy.deepcopy(row);r[k]=v
            with self.subTest(id=row['id'],field=k),self.assertRaises(ValueError):depth.validate_reference(r,self.ids,self.metrics);depth.validate_context(r)

    def test_previous343_refs_and_normalizations_preserved(self):
        self.assertEqual(self.data['evidence'][:343],previous.build()['evidence'])
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':347,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0})
        self.assertEqual(self.data['metadata_correction_count'],3)

    def test_four_source_extents_keep_table1_nominal_locations(self):
        self.assertEqual([(r['source_mooring_id'],r['mooring_lon_lat'],r['approximate_value_m']) for r in self.rows],[('MARLIM',[-40.2,-22.7],350),('DFBS',[-42.4,-24.15],400),('C3',[-44.9,-25.5],550),('W333',[-46.7,-27.9],850)])
        for r in self.rows:self.assertEqual(r['metric'],'reported_vertical_extent')

    def test_record_month_bounds_not_common_calendar_or_woa_year(self):
        self.assertEqual([(r['source_record_month_bounds'],r['source_record_days']) for r in self.rows],[(['1992-02','1992-12'],308),(['2003-01','2004-05'],482),(['1992-12','1994-03'],455),(['1991-01','1992-11'],693)])
        for r in self.rows:
            self.assertIsNone(r['common_record_period']);self.assertFalse(r['source_stratification_year_is_record_year'])
            self.reject(r,[('source_record_month_bounds',['2009-01','2009-12']),('observed_period',{'start':'1991-01-01','end':'2004-05-31'}),('calendar_months',[1,2,3])])

    def test_dfbs_low_significance_is_retained(self):
        r=self.rows[1];self.assertEqual(r['source_mean_reliability'],'source_low_statistical_significance')
        self.reject(r,[('source_mean_reliability','statistically_significant'),('approximate_value_m',500)])

    def test_extent_is_not_bathymetry_sampling_depth_or_cruise_estimate(self):
        for r in self.rows:
            self.assertFalse(r['source_isobath_is_flow_depth'])
            self.reject(r,[('approximate_value_m',r['source_isobath_m']),('source_isobath_is_flow_depth',True),('thickness_m',r['approximate_value_m']),('volume_eligible',True),('uncertainty_m',175)])
        self.reject(self.rows[2],[('approximate_value_m',450)])
        self.reject(self.rows[3],[('approximate_value_m',885)])

    def test_modal_processing_and_figure_reading_scope(self):
        for r in self.rows:
            self.assertEqual(r['source_modal_fit']['number_of_gravest_dynamical_modes'],5);self.assertEqual(r['source_low_pass_filter']['cutoff_hours'],40)
            self.assertEqual(r['source_stratification_product'],'World_Ocean_Atlas_2009_climatology');self.assertFalse(r['source_figure_digitization_performed'])
            self.reject(r,[('evidence_kind','raw_observed_velocity_profile'),('source_modal_fit',{'kind':'linear_vertical_interpolation'}),('source_velocity_frame','fixed_meridional_velocity')])
        review=json.loads((depth.ROOT/depth.SOURCE).read_bytes())['source_reviews'][0]
        self.assertEqual(review['actual_reviewed_pdf_pages'],[2,6]);self.assertTrue(review['actual_original_pixels_viewed'])

    def test_json_csv_and_member_lookup_preserved(self):
        self.assertEqual(self.data,json.loads((depth.ROOT/depth.OUTPUT).read_bytes()))
        raw=depth.csv_bytes(self.data);self.assertEqual(raw,(depth.ROOT/depth.CSV).read_bytes())
        rows=list(csv.DictReader(io.StringIO(raw.decode('utf8'))))[-4:]
        for source,out in zip(self.rows,rows):
            self.assertEqual(json.loads(out['source_record_month_bounds']),source['source_record_month_bounds']);self.assertEqual(json.loads(out['source_modal_fit']),source['source_modal_fit'])
        index=json.loads((depth.ROOT/depth.MEMBER_OUTPUT).read_bytes());self.assertEqual(index['counts']['distinct_member_depth_references'],47)
        for row in index['records']:self.assertNotIn('current:brazil',[m['entity_id'] for m in row['members']])


if __name__=='__main__':unittest.main()
