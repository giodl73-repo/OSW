import copy,hashlib,json,unittest
from unittest.mock import patch
import numpy as np
import derive_ngcc_direction_depth_sources_v1 as p


class NgccReusedDirectionSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read=staticmethod(lambda f:(p.ROOT/f).read_bytes())
        cls.op=json.loads(cls.read(p.OPERATOR))
        with patch('netCDF4.Dataset',side_effect=AssertionError('No field retrieval allowed')):cls.manifest,cls.pieces=p.build()
        cls.entry=cls.manifest['sections'][0];cls.record=json.loads(cls.pieces[cls.entry['file']]);cls.native_file=cls.entry['native_field_file'];cls.raw=json.loads(cls.read(cls.native_file))

    def test_all16_sources32_contexts_and_zero_new_requests(self):
        self.assertEqual(len(self.manifest['sections']),16);self.assertEqual(self.manifest['counts']['direction_context_diagnoses'],32)
        self.assertEqual(self.manifest['counts']['new_velocity_field_requests'],0)
        for entry in self.manifest['sections']:
            record=json.loads(self.pieces[entry['file']]);self.assertEqual(set(record['direction_contexts']),{'southeastward','northwestward'})
            self.assertEqual(record['entity_id'],p.TARGET);self.assertEqual(record['native_acquisition_owner_entity_id'],p.NATIVE_OWNER);self.assertNotEqual(p.TARGET,p.NATIVE_OWNER)

    def test_declared_opposite_frames_upper_window_and_dates(self):
        for key,bearing in [('southeastward',110),('northwestward',290)]:
            cfg=p.direction_config(self.op,key);self.assertEqual(cfg['component_bearing_degrees_true'],bearing);self.assertEqual(cfg['selection_depth_interval_m'],[0,100]);self.assertEqual(cfg['primary_threshold_m_s'],.1)
        self.assertEqual(self.op['snapshot_times_utc'],['2022-03-15T00:00:00Z','2022-06-15T00:00:00Z','2022-09-15T00:00:00Z','2022-12-15T00:00:00Z'])

    def test_signed_profiles_are_opposite_and_resolve_original_native_positions(self):
        a=self.record['direction_contexts']['southeastward']['profiles'];b=self.record['direction_contexts']['northwestward']['profiles']
        for i,(se,nw) in enumerate(zip(a,b)):
            self.assertEqual(se['source_native_profile_ref'],self.native_file+'#/columns/'+str(i));self.assertEqual(nw['sampled_lon_lat'],self.raw['columns'][i]['sampled_lon_lat'])
            for x,y in zip(se['signed_reference_component_m_s'],nw['signed_reference_component_m_s']):
                if x is None:self.assertIsNone(y)
                else:self.assertAlmostEqual(x,-y,places=12)

    def test_native_arrays_and_undercurrent_depths_are_not_modified_or_inherited(self):
        original=copy.deepcopy(self.raw)
        first=p.derive_direction(self.raw,self.native_file,self.entry['native_field_sha256'],self.op,'southeastward')
        changed=copy.deepcopy(self.raw);changed['diagnosis']={'invented_undercurrent_bottom_m':999999}
        second=p.derive_direction(changed,self.native_file,self.entry['native_field_sha256'],self.op,'southeastward')
        self.assertEqual(first,second);self.assertEqual(self.raw,original)
        self.assertFalse(first['undercurrent_depth_values_inherited']);self.assertFalse(first['surface_undercurrent_separation_performed'])

    def test_missing_native_component_propagates_unknown_without_bridging(self):
        raw=copy.deepcopy(self.raw);raw['columns'][1]['eastward_velocity_m_s'][0]=None
        for key in ['southeastward','northwestward']:
            result=p.derive_direction(raw,self.native_file,self.entry['native_field_sha256'],self.op,key)
            self.assertIsNone(result['profiles'][1]['signed_reference_component_m_s'][0])

    def test_strong_deep_undercurrent_cannot_fill_weak_surface_selection(self):
        raw=copy.deepcopy(self.raw);z=raw['depth_levels_m'];theta=np.deg2rad(290)
        for c in raw['columns']:
            speed=[.07 if depth<=100 else .8 if depth<=300 else 0.0 for depth in z]
            c['eastward_velocity_m_s']=[float(s*np.sin(theta)) for s in speed];c['northward_velocity_m_s']=[float(s*np.cos(theta)) for s in speed]
        for key in ['southeastward','northwestward']:
            result=p.derive_direction(raw,self.native_file,self.entry['native_field_sha256'],self.op,key)
            self.assertIsNone(result['diagnosis']['selected_column_index']);self.assertEqual(result['diagnosis']['selected_column_threshold_layers'],[])

    def test_component_diagnosis_and_native_pointer_mutations_are_rejected(self):
        derived=self.record['direction_contexts']['northwestward'];p.validate_direction(self.raw,derived,self.op)
        for kind in ['signed','diagnosis','pointer','owner','additive']:
            bad=copy.deepcopy(derived)
            if kind=='signed':bad['profiles'][1]['signed_reference_component_m_s'][0]=999
            if kind=='diagnosis':bad['diagnosis']['selected_column_index']=9999
            if kind=='pointer':bad['profiles'][1]['source_native_profile_ref']='invented#/columns/1'
            if kind=='owner':bad['entity_id']=p.NATIVE_OWNER
            if kind=='additive':bad['direction_contexts_are_additive']=True
            with self.subTest(kind=kind),self.assertRaises(ValueError):p.validate_direction(self.raw,bad,self.op)

    def test_frame_window_and_cutoff_retuning_rejected(self):
        for field,value in [('component_bearing_degrees_true',315),('selection_depth_interval_m',[0,200]),('primary_threshold_m_s',.05)]:
            op=copy.deepcopy(self.op);op['direction_contexts']['northwestward'][field]=value
            with self.assertRaises(ValueError):p.direction_config(op,'northwestward')

    def test_every_derived_file_and_native_pin_matches(self):
        for entry in self.manifest['sections']:
            self.assertEqual(hashlib.sha256(self.pieces[entry['file']]).hexdigest(),entry['sha256']);self.assertEqual(len(self.pieces[entry['file']]),entry['bytes'])
            self.assertEqual(hashlib.sha256(self.read(entry['native_field_file'])).hexdigest(),entry['native_field_sha256'])
        for file,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256(self.read(file)).hexdigest(),pin)

    def test_no_physical_annual_independent_observation_or_volume_promotion(self):
        for entry in self.manifest['sections']:
            record=json.loads(self.pieces[entry['file']]);self.assertFalse(any(record['eligibility'].values()))
            self.assertFalse(record['direction_contexts_are_additive']);self.assertFalse(record['contexts_are_independent_observations']);self.assertFalse(record['water_mass_classification_performed'])
            self.assertEqual(record['new_independent_observations'],0);self.assertFalse(record['full_goal_complete'])
        self.assertTrue(all(len(raw)<2500000 for raw in self.pieces.values()))


if __name__=='__main__':unittest.main()
