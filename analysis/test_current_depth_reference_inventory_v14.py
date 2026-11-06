"""Preserve source review limitations, typed bands and all prior evidence."""
import copy,csv,io,json,unittest
from pathlib import Path
import build_current_depth_reference_inventory_v14 as build
import load_current_depth_reference_inventory_v14 as loader
import load_current_depth_reference_inventory_v13 as prior


class Admission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory,cls.addendum,cls.facts,cls.pieces,cls.view=build.build();cls.reader=lambda f:cls.pieces[f] if f in cls.pieces else (build.ROOT/f).read_bytes()
    def test_all791_prior_rows_contexts_and_manifest_parts_unchanged(self):
        old=json.loads((build.ROOT/'research/current-depth-reference-inventory-v13.json').read_bytes());view=prior.load_inventory(old,lambda f:(build.ROOT/f).read_bytes())
        self.assertEqual(self.view['evidence'][:791],view['evidence']);self.assertEqual(self.inventory['base'],old['base']);self.assertEqual(self.inventory['addenda'][:-1],old['addenda'])
        self.assertEqual({k:self.view['source_contexts'][k] for k in view['source_contexts']},view['source_contexts']);self.assertEqual(self.view['counts']['depth_references'],793)
    def test_exact_reported_bands_no_midpoint_or_layer_thickness(self):
        self.assertEqual([r['range_m'] for r in self.addendum['evidence']],[[750,875],[775,1015]])
        for row in self.addendum['evidence']:
            self.assertEqual(row['metric'],loader.METRIC)
            for field in ['approximate_value_m','upper_boundary_m','lower_boundary_m','thickness_m','annual_range_m','uncertainty_m']:self.assertIsNone(row[field])
    def test_provisional_review_and_missing_PDF_custody_explicit(self):
        for row in self.addendum['evidence']:
            self.assertFalse(row['source_pdf_bytes_verified']);self.assertIsNone(row['source_pdf_sha256']);self.assertEqual(row['source_pdf_pages_visually_reviewed'],[]);self.assertIn('PROVISIONAL',row['source_review_status'])
    def test_no_physical_annual_or_volume_promotions(self):
        for row in self.addendum['evidence']:
            for key in ['whole_current_representative','physical_current_bottom_established','volume_eligible','seasonal_playback_eligible','annual_extrema_eligible','independent_observation_count_claimed']:self.assertFalse(row[key])
        self.assertEqual(self.view['counts']['whole_route_depth_profiles'],0);self.assertEqual(self.view['counts']['volume_estimates'],0)
    def test_distinct_diagnostic_not_an_error_bar_or_extra_reference(self):
        self.assertEqual(len(self.addendum['evidence']),2);self.assertEqual(self.facts['alternate_deployment5_ellipse_transition_band_m'],[786,1090]);self.assertFalse(self.facts['alternate_diagnostic_band_is_uncertainty'])
    def test_common_record_windows_are_exact(self):
        self.assertEqual([r['observed_period'] for r in self.addendum['evidence']],[['2005-05-30','2006-02-12'],['2006-06-18','2007-03-20']])
    def test_wrong_source_endpoints_or_dates_rejected(self):
        for key,value in [('reported_transition_depth_band_m',[750,1000]),('diagnostic_common_record_dates',['2005-05-30','2006-05-25'])]:
            facts=copy.deepcopy(self.facts);facts['records'][0][key]=value
            with self.assertRaises(ValueError):loader.validate_facts(facts)
    def test_unperformed_visual_verification_rejected(self):
        for key,value in [('source_pdf_bytes_verified',True),('source_pdf_sha256','0'*64),('source_pdf_pages_visually_reviewed',[54]),('raw_mooring_data_reanalysed',True)]:
            facts=copy.deepcopy(self.facts);facts[key]=value
            with self.assertRaises(ValueError):loader.validate_facts(facts)
    def test_physical_or_uncertainty_promotion_in_facts_rejected(self):
        for key,value in [('volume_eligible',True),('physical_current_bottom_established',True),('uncertainty_m',10)]:
            facts=copy.deepcopy(self.facts);facts['records'][0][key]=value
            with self.assertRaises(ValueError):loader.validate_facts(facts)
    def test_JSON_CSV_all_typed_cells_roundtrip(self):
        incoming=csv.DictReader(io.StringIO(self.pieces[build.CSV].decode()));rows=list(incoming)
        self.assertEqual(len(rows),2)
        for raw,row in zip(self.addendum['evidence'],rows):self.assertEqual(row,{k:loader.base.cell(raw.get(k)) for k in incoming.fieldnames})
    def test_duplicate_context_rejected(self):
        parts=prior.read_parts(json.loads((build.ROOT/'research/current-depth-reference-inventory-v13.json').read_bytes()),lambda f:(build.ROOT/f).read_bytes())
        with self.assertRaises(ValueError):loader.assemble(*parts,[(self.addendum,self.facts),(self.addendum,self.facts)])
    def test_changed_reference_or_provisional_review_rejected(self):
        parts=prior.read_parts(json.loads((build.ROOT/'research/current-depth-reference-inventory-v13.json').read_bytes()),lambda f:(build.ROOT/f).read_bytes());a=copy.deepcopy(self.addendum);a['evidence'][0]['source_pdf_bytes_verified']=True
        with self.assertRaises(ValueError):loader.assemble(*parts,[(a,self.facts)])


if __name__=='__main__':unittest.main()
