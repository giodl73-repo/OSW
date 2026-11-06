import copy,csv,hashlib,io,json,tempfile,unittest
from pathlib import Path
import build_current_depth_reference_inventory_v6 as p
import load_current_depth_reference_inventory_v5 as prior
import load_current_depth_reference_inventory_v6 as loader
from derive_jutland_area_mean_depth_reference_v1 import audit_and_derive


class RegionalInventoryMeanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes());cls.inventory,cls.addendum,cls.report,cls.pieces,cls.view=p.build();read=lambda f:json.loads((p.ROOT/f).read_bytes());cls.previous=read(cls.op['previous_inventory_file']);cls.before=prior.load_inventory(cls.previous,lambda f:(p.ROOT/f).read_bytes());cls.parts=prior.read_parts(cls.previous,lambda f:(p.ROOT/f).read_bytes());cls.facts=read(cls.op['source_facts_file'])
    def reader(self,f):return self.pieces[f] if f in self.pieces else (p.ROOT/f).read_bytes()
    def assembled(self,a=None,report=None):return loader.assemble(*self.parts,[(a or self.addendum,report or self.report)])
    def test_all735_prior_refs_contexts_and_record_fields_preserved(self):
        self.assertEqual(self.view['evidence'][:735],self.before['evidence']);self.assertEqual(self.inventory['base'],self.previous['base']);self.assertEqual(self.inventory['addenda'][:-1],self.previous['addenda'])
        for k,v in self.before['source_contexts'].items():self.assertEqual(self.view['source_contexts'][k],v)
        for old in self.before['records']:
            new=next(r for r in self.view['records'] if r['entity_id']==old['entity_id']);self.assertEqual(new['depth_reference_ids'][:len(old['depth_reference_ids'])],old['depth_reference_ids']);self.assertEqual({k:v for k,v in old.items() if k!='depth_reference_ids'},{k:v for k,v in new.items() if k!='depth_reference_ids'})
    def test_source_reported22_preserved_separately_from_quotient_and_freshwater_depth(self):
        r=self.addendum['evidence'][0];self.assertEqual(r['approximate_value_m'],22);self.assertEqual(self.report['arithmetic_check']['rounded_at_source_precision_m'],22);self.assertTrue(self.report['arithmetic_check']['computed_quotient_m_for_consistency_only'].startswith('22.012'));self.assertFalse(self.report['arithmetic_check']['reported_value_replaced']);self.assertEqual(self.facts['reported_average_freshwater_depth_Hf_m'],.55);self.assertNotEqual(r['approximate_value_m'],.55)
    def test_dimensioned_source_volume_area_context_not_new_volume_estimate(self):
        self.assertEqual(self.report['arithmetic_check']['dimension'],'m3/m2=m');self.assertEqual(self.report['reported_total_water_volume'],{'table_coefficient':350000,'table_multiplier_power_of_ten':6,'unit':'m3'});self.assertEqual(self.report['reported_total_area'],{'coefficient':1.59,'multiplier_power_of_ten':10,'unit':'m2'});self.assertFalse(self.report['new_OSW_volume_estimate']);self.assertEqual(len(self.addendum['evidence']),1)
    def test_salinity_domain_and_cruise_not_exact_occupations_or_calendar(self):
        r=self.addendum['evidence'][0];self.assertEqual(r['source_selection']['salinity_comparator'],'<');self.assertEqual(r['source_selection']['salinity_threshold_source_value'],34);self.assertEqual(r['source_cruise_window'],{'start_date':'1989-11-27','end_date':'1989-12-06'});self.assertIsNone(r['observed_period']);self.assertIsNone(r['calendar_months']);self.assertIn('Limfjord',r['geographic_scope']);self.assertFalse(self.facts['exact_inventory_occupation_dates_resolved'])
    def test_no_bottom_thickness_annual_rounding_error_or_volume_promotion(self):
        for key,value in [('lower_boundary_m',22),('thickness_m',22),('range_m',[21.5,22.5]),('uncertainty_m',.5),('annual_range_m',[10,30]),('observed_period',{'start':'1989-11-27'}),('calendar_months',[11,12]),('source_sampled_lon_lat',[8,56]),('same_source_width_reference_id','wrong-width'),('physical_current_bottom_established',True),('source_value_replaced_by_computed_quotient',True),('source_rounding_is_uncertainty',True),('volume_eligible',True),('reference_route_projection_eligible',True)]:
            a=copy.deepcopy(self.addendum);a['evidence'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.assembled(a)
    def test_source_mean_selection_units_period_and_owner_cannot_be_substituted(self):
        for kind in ['freshwater','quotient','owner','metric','selection','area','period','datum','pointer']:
            a=copy.deepcopy(self.addendum);r=a['evidence'][0]
            if kind=='freshwater':r['approximate_value_m']=.55
            elif kind=='quotient':r['approximate_value_m']=22.0125786
            elif kind=='owner':r['entity_id']='current:norwegian-coastal'
            elif kind=='metric':r['metric']='reported_vertical_thickness'
            elif kind=='selection':r['source_selection']['salinity_threshold_source_value']=35
            elif kind=='area':r['source_reported_total_area']['unit']='km2'
            elif kind=='period':r['source_cruise_window']['start_date']='2022-11-27'
            elif kind=='datum':r['vertical_datum']='local_sea_surface_positive_down'
            else:r['source_facts_pointer']='/reported_average_freshwater_depth_Hf_m'
            with self.subTest(kind=kind),self.assertRaises(ValueError):self.assembled(a)
    def test_source_custody_and_transcribed_units_cannot_change(self):
        for kind in ['custody','volume','precision','window']:
            facts=copy.deepcopy(self.facts);custody=json.loads((p.ROOT/facts['acquisition_file']).read_bytes())
            if kind=='custody':custody['primary_PDF_retained']=False
            elif kind=='volume':facts['reported_total_water_volume']['unit']='Sv'
            elif kind=='precision':facts['reported_table_precision_decimal_places']=2
            else:facts['source_cruise_window']['end_date']='1989-12-31'
            with tempfile.TemporaryDirectory() as directory:
                root=Path(directory)
                for f,v in [(self.op['source_facts_file'],facts),(facts['acquisition_file'],custody)]:path=root/f;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(v))
                with self.subTest(kind=kind),self.assertRaises(ValueError):audit_and_derive(root,self.op)
    def test_exact_report_and_facts_pointers_and_hashes(self):
        r=self.addendum['evidence'][0];self.assertEqual(r['source_pointer'],'/reported_value_m');self.assertEqual(r['source_file'],p.REPORT);self.assertEqual(r['source_sha256'],hashlib.sha256(self.pieces[p.REPORT]).hexdigest());self.assertEqual(r['source_facts_sha256'],hashlib.sha256((p.ROOT/self.op['source_facts_file']).read_bytes()).hexdigest())
        a=copy.deepcopy(self.addendum);a['evidence'][0]['source_sha256']='wrong'
        with self.assertRaises(ValueError):self.assembled(a)
    def test_exactly_one_statistic_no_duplicate_or_empty_admission(self):
        for rows in [[],self.addendum['evidence']*2]:
            a=copy.deepcopy(self.addendum);a['evidence']=rows
            with self.assertRaises(ValueError):self.assembled(a)
    def test_report_and_json_csv_piece_hashes_cannot_change(self):
        for piece in [self.addendum['derived_source_report'],self.inventory['addenda'][-1]['json'],self.inventory['addenda'][-1]['csv']]:
            with self.subTest(file=piece['file']),self.assertRaises(ValueError):loader.load_inventory(self.inventory,lambda f:self.reader(f)+b' ' if f==piece['file'] else self.reader(f))
    def test_all_old_csv_cells_and_typed_reported_value_preserved(self):
        old=list(csv.DictReader(io.StringIO(prior.combined_csv_bytes(self.previous,lambda f:(p.ROOT/f).read_bytes()).decode())));new=list(csv.DictReader(io.StringIO(loader.combined_csv_bytes(self.inventory,self.reader).decode())));self.assertEqual(len(new),736)
        for a,b in zip(old,new):self.assertEqual(a,{k:b[k] for k in a})
        self.assertEqual(new[-1]['approximate_value_m'],'22');self.assertEqual(new[-1]['metric'],'reported_salinity_selected_area_mean_water_depth');self.assertEqual(new[-1]['thickness_m'],'');self.assertEqual(new[-1]['volume_eligible'],'False')
    def test_counts_input_pins_and_fixed_publication_caps(self):
        self.assertEqual(self.view['counts']['depth_references'],736);self.assertEqual(self.view['counts']['identities_with_scoped_depth_reference'],101);self.assertEqual(self.view['counts']['whole_route_depth_profiles'],0);self.assertEqual(self.view['counts']['volume_estimates'],0);self.assertEqual(self.view['metric_counts']['reported_salinity_selected_area_mean_water_depth'],1)
        for f,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256((p.ROOT/f).read_bytes()).hexdigest(),pin,f)
        self.assertTrue(all(len(raw)<2500000 for raw in self.pieces.values()));self.assertLess(sum(map(len,self.pieces.values())),3000000)


if __name__=='__main__':unittest.main()
