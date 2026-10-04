"""Source projection invariants, missing readings and separate uncertainty roles."""
import copy
import json
from pathlib import Path
import unittest
from build_query_width_samples import build

ROOT=Path(__file__).resolve().parents[1]

def documents():
    return [{'id':identifier,'document':json.loads((ROOT/path).read_bytes())} for identifier,path in [
        ('diagnostic:leeuwin-monthly-width','research/leeuwin-a101-monthly-plot-extraction.json'),
        ('diagnostic:kuroshio-seasonal-width','research/kuroshio-ecs-seasonal-width-profile-extraction.json'),
        ('diagnostic:necc-monthly-section','research/pacific-necc-oscar-2013-section-diagnostic.json')]]

class QueryWidthSamplesTests(unittest.TestCase):
    def test_dated_section_samples_retain_day_sensitivity_and_resolution(self):
        document=json.loads((ROOT/'research/gulf-stream-section-width-series.json').read_bytes())
        rows=build([{'id':'diagnostic:gulf-stream-widths','document':document}])
        self.assertEqual(len(rows),17)
        for row,frame in zip(rows,document['frames']):
            self.assertEqual(row['observation_date'],frame['date'])
            self.assertEqual(row['month'],int(frame['date'][5:7]));self.assertEqual(row['year'],int(frame['date'][:4]))
            self.assertEqual(row['value_km'],frame['approximate_section_span_km'])
            self.assertEqual(row['source_sample'],frame)
            self.assertEqual(row['diagnostic_sensitivity_interval_km'],frame['threshold_sensitivity_span_km'])
            self.assertEqual(row['sampling_bracket_interval_km'],frame['nominal']['grid_bracket_span_km'])
            self.assertIsNone(row['plot_reading_interval_km']);self.assertIsNone(row['measurement_uncertainty_interval_km'])
            self.assertEqual(row['source_algorithm'],frame['source_algorithm'])
            self.assertEqual(row['current_id'],'gulf-stream-system')
            self.assertEqual(row['source_context'],{k:v for k,v in document.items() if k!='frames'})
        missing=copy.deepcopy(document);missing['frames'][0]['approximate_section_span_km']=None
        self.assertIsNone(build([{'id':'diagnostic:gulf-stream-widths','document':missing}])[0]['value_km'])
        invalid=copy.deepcopy(document);invalid['frames'][0]['date']='2025-02-29'
        with self.assertRaises(ValueError):build([{'id':'diagnostic:gulf-stream-widths','document':invalid}])
    def test_complete_source_samples_and_context(self):
        docs=documents();rows=build(docs);self.assertEqual(len(rows),88)
        self.assertEqual(len({r['id'] for r in rows}),88)
        self.assertEqual({c:sum(r['current_id']==c for r in rows) for c in ['kuroshio','leeuwin','pacific-north-equatorial-countercurrent']},{'kuroshio':64,'leeuwin':12,'pacific-north-equatorial-countercurrent':12})
        for row in rows:
            document=next(d['document'] for d in docs if d['id']==row['diagnostic_id'])
            sample=document
            for part in row['sample_path'].strip('/').split('/'):sample=sample[int(part)] if isinstance(sample,list) else sample[part]
            self.assertEqual(row['source_sample'],sample)
            self.assertEqual(row['source_context'],{k:v for k,v in document.items() if k not in ['months','seasons']})
            self.assertFalse(row['width_rank_eligible']);self.assertFalse(row['whole_current_representative'])

    def test_missing_readings_and_month_membership_are_not_filled(self):
        rows=build(documents());kuro=[r for r in rows if r['current_id']=='kuroshio']
        self.assertEqual(sum(r['value_km'] is None for r in kuro),5)
        self.assertTrue(all(r['month'] is None and r['year'] is None and r['source_phase']['calendar_months'] is None for r in kuro))
        for r in kuro:
            if r['value_km'] is None:self.assertIsNone(r['plot_reading_interval_km'])
        self.assertTrue(all(r['year'] is None for r in rows if r['current_id']=='leeuwin'))

    def test_plot_allowance_does_not_become_diagnostic_uncertainty(self):
        rows=build(documents());necc=[r for r in rows if r['sample_family']=='necc_monthly_connected_component']
        self.assertEqual(len(necc),12)
        for row in rows:
            self.assertIsNone(row['measurement_uncertainty_interval_km']);self.assertFalse(row['is_confidence_interval']);self.assertIsNone(row['annual_width_range_km'])
        for row in necc:
            self.assertIsNone(row['plot_reading_interval_km']);self.assertEqual(row['year'],2013)
            self.assertEqual(len(row['source_sample']['threshold_sensitivity']),2)
            self.assertEqual(row['value_km'],row['source_sample']['zero_crossing']['span_km'])

    def test_rejects_scope_promotion_and_preserves_original(self):
        original=documents();snapshot=copy.deepcopy(original);rows=build(original)
        rows[0]['source_sample']['approximate_width_km']=9999
        self.assertEqual(original,snapshot)
        for key,value in [('whole_current_representative',True),('width_rank_eligible',True),('is_confidence_interval',True),('annual_width_range_km',[1,999])]:
            bad=copy.deepcopy(original);bad[0]['document'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):build(bad)

if __name__=='__main__':unittest.main()
