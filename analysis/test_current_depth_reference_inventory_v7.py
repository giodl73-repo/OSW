import copy,csv,hashlib,io,json,unittest,xml.etree.ElementTree as ET
import build_current_depth_reference_inventory_v7 as p
import load_current_depth_reference_inventory_v6 as prior
import load_current_depth_reference_inventory_v7 as loader
from derive_nwasc_selected_noncore_depths_v1 import extract_paragraph


class SelectedNoncoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes());cls.inventory,cls.addendum,cls.report,cls.pieces,cls.view=p.build();read=lambda f:json.loads((p.ROOT/f).read_bytes());cls.previous=read(cls.op['previous_inventory_file']);cls.before=prior.load_inventory(cls.previous,lambda f:(p.ROOT/f).read_bytes());cls.parts=prior.read_parts(cls.previous,lambda f:(p.ROOT/f).read_bytes());cls.context=read(cls.op['source_context_file']);tree=ET.fromstring((p.ROOT/cls.context['source_xml_file']).read_bytes());cls.paragraph=next(' '.join(''.join(el.itertext()).split()) for el in tree.iter() if el.tag.split('}')[-1]=='p' and 'core is wedge-shaped' in ''.join(el.itertext()))
    def reader(self,f):return self.pieces[f] if f in self.pieces else (p.ROOT/f).read_bytes()
    def assembled(self,a=None,report=None):return loader.assemble(*self.parts,[(a or self.addendum,report or self.report)])
    def test_all736_prior_refs_contexts_and_record_fields_preserved(self):
        self.assertEqual(self.view['evidence'][:736],self.before['evidence']);self.assertEqual(self.inventory['base'],self.previous['base']);self.assertEqual(self.inventory['addenda'][:-1],self.previous['addenda'])
        for k,v in self.before['source_contexts'].items():self.assertEqual(self.view['source_contexts'][k],v)
        for old in self.before['records']:
            new=next(r for r in self.view['records'] if r['entity_id']==old['entity_id']);self.assertEqual(new['depth_reference_ids'][:len(old['depth_reference_ids'])],old['depth_reference_ids']);self.assertEqual({k:v for k,v in old.items() if k!='depth_reference_ids'},{k:v for k,v in new.items() if k!='depth_reference_ids'})
    def test_xml_explicit_noncore_values_roles_and_gates(self):
        rows=extract_paragraph(self.paragraph);self.assertEqual([(r['section_id'],r['reported_noncore_lower_extent_m'],r['source_core_lower_extent_m'],r['shoreward_isobath_gate_m']) for r in rows],[('svinoy',530,460,1500),('gimsoy',630,530,2500)])
        self.assertEqual([r['source_section_id'] for r in self.addendum['evidence']],['svinoy','gimsoy']);self.assertEqual([r['approximate_value_m'] for r in self.addendum['evidence']],[530,630])
    def test_missing_duplicate_or_unreported_noncore_statements_rejected(self):
        for text in ['',self.paragraph.replace('non-core area','other area'),self.paragraph+self.paragraph,self.paragraph.replace('630 m','unknown m')]:
            with self.assertRaises(ValueError):extract_paragraph(text)
    def test_existing_core_refs_preserved_and_cross_checked(self):
        for r in self.addendum['evidence']:
            old=next(x for x in self.before['evidence'] if x['id']==r['source_existing_core_reference_id']);self.assertEqual(old['metric'],'core_lower_boundary_depth');self.assertEqual(old['approximate_value_m'],r['source_core_lower_extent_m']);self.assertEqual(old,next(x for x in self.view['evidence'] if x['id']==old['id']))
    def test_static_source_selection_not_dynamic_dates_or_full_layer(self):
        for r in self.addendum['evidence']:
            self.assertEqual(r['source_mean_definition_years'],[1993,2022]);self.assertEqual(r['source_selection']['upper_selection_depth_m'],50);self.assertEqual(r['source_selection']['absolute_salinity_minimum_g_kg'],35.16);self.assertEqual(r['source_selection']['core_transport_fraction'],.5);self.assertIsNone(r['observed_period']);self.assertIsNone(r['calendar_months']);self.assertIsNone(r['upper_boundary_m']);self.assertIsNone(r['thickness_m'])
    def test_no_broad_norwegian_coastal_or_frontal_inheritance(self):
        for entity in ['current:norwegian','current:norwegian-coastal','current:norwegian-atlantic-front']:
            a=copy.deepcopy(self.addendum);a['evidence'][0]['entity_id']=entity
            with self.subTest(entity=entity),self.assertRaises(ValueError):self.assembled(a)
    def test_source_extent_cannot_become_core_bathymetry_or_uncertainty(self):
        for kind in ['core','gate','role','selection','years','section','core_id','paragraph']:
            a=copy.deepcopy(self.addendum);r=a['evidence'][0]
            if kind=='core':r['approximate_value_m']=460
            elif kind=='gate':r['approximate_value_m']=1500
            elif kind=='role':r['source_population_role']='core'
            elif kind=='selection':r['source_selection']['upper_selection_depth_m']=0
            elif kind=='years':r['source_mean_definition_years']=[2022,2022]
            elif kind=='section':r['source_section_id']='bjornoya'
            elif kind=='core_id':r['source_existing_core_reference_id']='wrong'
            else:r['source_xml_paragraph_index']=999
            with self.subTest(kind=kind),self.assertRaises(ValueError):self.assembled(a)
    def test_no_bottom_span_error_annual_geometry_or_volume_promotion(self):
        for key,value in [('lower_boundary_m',530),('thickness_m',480),('uncertainty_m',70),('range_m',[460,530]),('annual_range_m',[460,630]),('source_sampled_lon_lat',[5,63]),('same_source_width_reference_id','wrong-width'),('physical_current_bottom_established',True),('source_core_comparison_is_error_bar',True),('volume_eligible',True),('reference_route_projection_eligible',True)]:
            a=copy.deepcopy(self.addendum);a['evidence'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.assembled(a)
    def test_exact_xml_paragraph_and_report_provenance(self):
        digest=hashlib.sha256(self.paragraph.encode()).hexdigest()
        for r in self.addendum['evidence']:self.assertEqual(r['source_xml_normalized_paragraph_sha256'],digest);self.assertEqual(r['source_file'],p.REPORT);self.assertEqual(r['source_sha256'],hashlib.sha256(self.pieces[p.REPORT]).hexdigest())
        a=copy.deepcopy(self.addendum);a['evidence'][0]['source_pointer']='/records/-1'
        with self.assertRaises(ValueError):self.assembled(a)
    def test_report_and_json_csv_piece_hashes_cannot_change(self):
        for piece in [self.addendum['derived_source_report'],self.inventory['addenda'][-1]['json'],self.inventory['addenda'][-1]['csv']]:
            with self.subTest(file=piece['file']),self.assertRaises(ValueError):loader.load_inventory(self.inventory,lambda f:self.reader(f)+b' ' if f==piece['file'] else self.reader(f))
    def test_all_old_csv_cells_preserved_and_noncore_fields_typed(self):
        old=list(csv.DictReader(io.StringIO(prior.combined_csv_bytes(self.previous,lambda f:(p.ROOT/f).read_bytes()).decode())));new=list(csv.DictReader(io.StringIO(loader.combined_csv_bytes(self.inventory,self.reader).decode())));self.assertEqual(len(new),738)
        for a,b in zip(old,new):self.assertEqual(a,{k:b[k] for k in a})
        for r in new[736:]:self.assertEqual(r['metric'],'reported_selected_noncore_water_mass_lower_extent');self.assertEqual(r['source_population_role'],'non_core_selected_Atlantic_Water');self.assertEqual(r['thickness_m'],'');self.assertEqual(r['volume_eligible'],'False')
    def test_counts_input_pins_and_fixed_publication_caps(self):
        self.assertEqual(self.view['counts']['depth_references'],738);self.assertEqual(self.view['counts']['identities_with_scoped_depth_reference'],101);self.assertEqual(self.view['counts']['whole_route_depth_profiles'],0);self.assertEqual(self.view['counts']['volume_estimates'],0);self.assertEqual(self.view['metric_counts']['reported_selected_noncore_water_mass_lower_extent'],2)
        for f,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256((p.ROOT/f).read_bytes()).hexdigest(),pin,f)
        self.assertTrue(all(len(raw)<2500000 for raw in self.pieces.values()));self.assertLess(sum(map(len,self.pieces.values())),3000000)


if __name__=='__main__':unittest.main()
