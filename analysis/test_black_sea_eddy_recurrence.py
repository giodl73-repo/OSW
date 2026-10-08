import copy, json, unittest
from build_black_sea_eddy_recurrence import build, validate, ROOT, OUTPUT

class RecurrenceTests(unittest.TestCase):
    def test_pinned_extraction_and_units(self):
        d=json.loads((ROOT/OUTPUT).read_bytes());validate(d)
        by_id={r['id'].split(':')[-1]:r for r in d['entries']}
        self.assertEqual(len(by_id),9)
        self.assertEqual(by_id['bosphorus']['reported_occurrence_days_per_year_approx'],260)
        self.assertEqual(by_id['bosphorus']['reported_event_lifetime_approx'],85)
        self.assertIsNone(by_id['batumi']['reported_event_lifetime_approx'])
        self.assertEqual(by_id['sukhumi']['event_lifetime_unit'],'month')
        self.assertEqual(by_id['crimea']['event_lifetime_statistic'],'mean')
        for key,value in [('reported_occurrence_days_per_year_approx',85),('reported_event_lifetime_approx',260),('event_lifetime_unit','month'),('entity_id','eddy:geography:danube-eddy-region'),('calendar_months',[3,4,5]),('seasonal_playback_eligible',True),('physical_state_join_eligible',True),('geometry',{'type':'Point','coordinates':[29,41]})]:
            bad=copy.deepcopy(d);bad['entries'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate(bad)
        bad=copy.deepcopy(d);bad['source_document_sha256']='changed'
        with self.assertRaises(ValueError):validate(bad)

if __name__=='__main__':unittest.main()
