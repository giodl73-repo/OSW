import copy,hashlib,json,struct,unittest
import pacific_neuc_mean_rectangle_v2 as p
import test_pacific_neuc_mean_sections_v1 as t


class RectangleTests(unittest.TestCase):
    def fixture(self):
        axes,h,old=t.MeanSectionTests().fixture();op=json.loads((p.ROOT/p.OPERATOR).read_bytes());return axes,h,op
    def test_rows_are_contiguous_exact_unique_and_request_plan_has_single_probe(self):
        axes,h,op=self.fixture();sections,patches,batches,counts=p.rectangle_plan(axes,h,op)
        self.assertEqual(counts['cell_pairs'],800);self.assertEqual(counts['packed_component_bytes'],3200);self.assertEqual(counts['native_longitudes_deg_e'],axes['lon']);self.assertEqual(len(batches[0]),1)
        ranges=[r for batch in batches for r in batch];self.assertEqual(len(ranges),len(set(ranges)));self.assertEqual(sum(n for _,n in ranges),3200)
        self.assertEqual(set(ranges),{r for patch in patches for r in patch['ranges']});self.assertTrue(all(len(batch)<=32 for batch in batches))
    def test_rectangle_and_patch_and_whole_plan_budgets_fail_before_network(self):
        axes,h,op=self.fixture()
        for key,value in [('maximum_total_cell_pairs',799),('maximum_total_decoded_bytes',6399),('maximum_cell_pairs_per_patch',99),('maximum_http_requests',1),('maximum_total_response_body_bytes',12000),('maximum_requested_bytes',3199)]:
            bad=copy.deepcopy(op);bad[key]=value
            with self.assertRaises(ValueError):p.rectangle_plan(axes,h,bad)
    def test_section_extraction_has_exact_global_indices_for_each_component(self):
        axes,h,op=self.fixture();sections,patches,batches,counts=p.rectangle_plan(axes,h,op);parts={}
        for patch in patches:
            for i,key in enumerate(patch['ranges']):parts[key]=struct.pack('>4h',1,2,3,4)
        for section in sections:
            for name in ['water_u','water_v']:
                raw=p.extract_section_raw(parts,section,counts,axes,name);self.assertEqual(struct.unpack('>200h',raw),(section['native_longitude_index']+1,)*200)
        key=next(iter(parts));parts[key]=b'bad'
        with self.assertRaises(ValueError):p.extract_section_raw(parts,sections[0],counts,axes,'water_u')
    def test_frozen_scientific_rules_preserved_and_no_coverage_promotion(self):
        axes,h,op=self.fixture();old=json.loads((p.ROOT/'research/pacific-neuc-mean-sections-operator-v1.json').read_bytes())
        for key in ['entity_id','nominal_provider_period','temporal_operator_class','section_longitudes_deg_e','latitude_gate_deg_n','independent_southern_jet_latitude_context_deg_n','selection_depth_interval_m','core_search_depth_interval_m','surface_component_gate_m_s','primary_threshold_m_s','thresholds_m_s','maximum_axis_distance_km','maximum_total_cell_pairs','maximum_total_decoded_bytes','maximum_http_requests','maximum_total_response_body_bytes']:
            self.assertEqual(op[key],old[key],key)
        self.assertFalse(op['regional_inventory_promotion_authorized']);self.assertEqual(op['maximum_ranges_per_request'],32)
        for f,pin in op['input_sha256'].items():self.assertEqual(hashlib.sha256((p.ROOT/f).read_bytes()).hexdigest(),pin,f)


if __name__=='__main__':unittest.main()
