import copy,json,tempfile,unittest
from pathlib import Path
from acquire_p02w_kuroshio_native_depths_v1 import validate_operator,qualify_header,ROOT,OP,no_frame_cases
from sample_a20_gulf_stream_core_direction_depths_v2 import fixed_frame,sample_aligned
from sample_a20_gulf_stream_depth_brackets_v1 import coarse_indices
from inspect_retained_a20_gulf_stream_headers_v2 import safe_attribute
from acquire_a20_gulf_stream_cast_headers_v1 import reserve


class P02WNativeChecks(unittest.TestCase):
    def test_exact_whole_case_caps_and_targets(self):
        op=json.loads((ROOT/OP).read_bytes());validate_operator(op)
        for k,v in [('maximum_provider_operations',4),('maximum_selected_levels_per_cast',100),('maximum_native_profiles',150)]:
            bad=copy.deepcopy(op);bad[k]=v
            with self.assertRaises(ValueError):validate_operator(bad)

    def test_requests_durably_reserved_once(self):
        with tempfile.TemporaryDirectory() as n:
            p=Path(n);j={'operations':[]};t={'station':'00601','url':'https://example.invalid/00601.nc'}
            reserve(j,p,t)
            self.assertEqual(json.loads((p/'journal.json').read_bytes())['operations'][0]['status'],'reserved_before_request')
            with self.assertRaises(ValueError):reserve(j,p,t)

    def test_header_requires_documented_version_shape_and_units(self):
        h={'global_attributes':{'GEN_Software_orig':'LDEO LADCP software: Version IX_14','GEN_LADCP_station':6,'datetime':'2022-05-05T05:18:00'},
            'variables':{k:{'dimensions':['z'],'shape':[500],'attributes':{'units':u}} for k,u in [('z','Meters'),('u','m/s'),('v','m/s'),('uerr','m/s')]}}
        h['variables'].update({k:{'shape':[],'attributes':{'units':u}} for k,u in [('lat','degrees_north'),('lon','degrees_east')]})
        qualify_header({'cast_id':'00601'},h)
        bad=copy.deepcopy(h);bad['variables']['z']['attributes']['units']='dbar'
        with self.assertRaises(ValueError):qualify_header({'cast_id':'00601'},bad)
        bad=copy.deepcopy(h);bad['global_attributes']['GEN_Software_orig']='unknown'
        with self.assertRaises(ValueError):qualify_header({'cast_id':'00601'},bad)

    def test_large_source_text_omitted_and_numeric_attributes_charged(self):
        ledger={'prior_failed_numeric_attribute_values':0,'reconstruction_numeric_attribute_touches':0,'new_numeric_attribute_values_touched':0}
        r=safe_attribute('x'*12001,ledger);self.assertEqual(r['utf8_bytes'],12001)
        safe_attribute(1.,ledger);self.assertEqual(ledger['new_numeric_attribute_values_touched'],1)

    def test_reused_cutoff_kernel_handles_northward_flow_without_speed_substitution(self):
        z=[float(i*8) for i in range(801)];calls=[]
        def point(i):return {'u_m_s':0.,'v_m_s':.8-z[i]/2000,'uerr_m_s':.02}
        initial=coarse_indices(z);inherited=[{'native_index':i,'depth_m':z[i],**point(i)} for i in initial]
        frame=fixed_frame({'selected_native_samples':inherited,'coarse_native_indices':initial})
        def read(i):calls.append(i);return point(i)
        r=sample_aligned(z,inherited,read,frame['east_north_unit_vector'])
        self.assertLessEqual(r['selected_native_levels'],40);self.assertEqual(len(calls),len(set(calls)))
        for c in r['threshold_cases']:
            self.assertAlmostEqual(c['lower_depth_m'],(.8-c['threshold_m_s'])*2000)
            self.assertFalse(c['first_native_downcrossing_below_core_verified'])

    def test_unqualified_reference_does_not_fill_unknown_depths(self):
        rows=no_frame_cases();self.assertEqual(len(rows),3)
        self.assertTrue(all(r['lower_depth_m'] is None and not r['physical_current_bottom_established'] for r in rows))


if __name__=='__main__':unittest.main()
