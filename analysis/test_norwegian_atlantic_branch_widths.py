import copy,json,unittest
from check_norwegian_atlantic_branch_widths import ROOT,AUDIT,validate

class NorwegianBranchWidths(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proposals=json.loads((ROOT/'research/ocean-current-inventory-expansion-candidates.json').read_bytes())
        cls.audit=json.loads((ROOT/AUDIT).read_bytes())

    def test_complete_branch_extraction_and_no_canonical_transfer(self):
        self.assertEqual(validate(self.proposals),{'records':3,'proposed_branch_owners':2})
        widths=json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())
        self.assertFalse(any(r['current_id']=='norwegian' for r in widths['measurements']))
        self.assertEqual(len(self.proposals['entries']),28)

    def test_numeric_time_layer_and_owner_promotions_rejected(self):
        for i,row in enumerate(self.audit['measurements']):
            for k,v in [('proposed_current_id','norwegian'),('current_id','norwegian'),('approximate_width_km',40),('width_range_km',[30,70]),('observed_period',{'start':'1995-04-01','end':'1999-02-28'}),('calendar_months',[1,2]),('fixed_layer_bounds_m',[0,400]),('section_geometry',{'type':'LineString'}),('annual_extrema_eligible',True),('seasonal_playback_eligible',True),('rank_eligible',True),('is_confidence_interval',True),('full_width_inference_eligible',True),('unit','m'),('source_publication_year',2026)]:
                bad=copy.deepcopy(self.audit);bad['measurements'][i][k]=v
                with self.subTest(id=row['id'],key=k),self.assertRaises(ValueError):validate(self.proposals,bad)
            for k,v in row['sampling_context'].items():
                bad=copy.deepcopy(self.audit);bad['measurements'][i]['sampling_context'][k]=True if v is False else 400 if v is None else None
                with self.subTest(id=row['id'],context=k),self.assertRaises(ValueError):validate(self.proposals,bad)

    def test_original_receipts_and_unquantified_front_mean_preserved(self):
        for k,v in [('source_document_sha256','0'*64),('source_document_file','other.pdf'),('acquisition_sha256','changed'),('measurement_protocol_sha256','changed'),('mean_front_width_km',60),('mean_front_width_range_km',[50,100])]:
            bad=copy.deepcopy(self.audit);bad[k]=v
            with self.subTest(key=k),self.assertRaises(ValueError):validate(self.proposals,bad)
        for owner in ['norwegian-atlantic','norwegian-atlantic-slope','norwegian-atlantic-front']:
            for k,v in [('width_evidence',[] if owner!='norwegian-atlantic' else [self.audit['measurements'][0]]),('whole_current_width_km',80),('annual_width_range_km',[30,50]),('rank_eligible',True)]:
                bad=copy.deepcopy(self.proposals);next(r for r in bad['entries'] if r['proposed_id']==owner)[k]=v
                with self.subTest(owner=owner,key=k),self.assertRaises(ValueError):validate(bad)

if __name__=='__main__':unittest.main()
