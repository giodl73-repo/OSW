import copy,unittest
from ecco_bounded_subset_plan_v1 import PRODUCT,plan_subset,prerequisite_report

def fixture():
    axes={'time':'time','level':'Z','lat':'latitude','lon':'longitude'}
    fields={n:{'kind':'Array','dtype':'Float32','dimensions':['time','Z','latitude','longitude'],'units':'m/s','fill_metadata_present':True} for n in ['EVEL','NVEL']}
    for role,name in axes.items():fields[name]={'kind':'Array','dtype':'Float64','dimensions':[name],'units':'m' if role=='level' else 'synthetic'}
    fields['Z_bnds']={'kind':'Array','dtype':'Float64','dimensions':['Z','nv'],'units':'m'}
    return {'product':PRODUCT,'protocol':'DAP2','metadata_sha256':'a'*64,'axis_names':axes,'dimensions':{'time':12,'Z':50,'latitude':360,'longitude':720,'nv':2},'fields':fields,'coordinate_fields':{**axes,'level_bounds':'Z_bnds'}}

def window():return {'time':[0,0],'level':[0,39],'lat':[0,0],'lon':[0,2]}

class SubsetPlanTests(unittest.TestCase):
    def test_every_requested_array_has_explicit_inclusive_slices(self):
        p=plan_subset(fixture(),window());self.assertEqual((p['profiles'],p['levels'],p['cells']),(3,40,120));self.assertIn('EVEL[0:1:0][0:1:39][0:1:0][0:1:2]',p['constraint_expression']);self.assertIn('Z_bnds[0:1:39][0:1:1]',p['constraint_expression']);self.assertEqual(len(p['constraint_expression'].split(',')),7)
    def test_all_times_count_against_same_profile_cap(self):
        w=window();w['time']=[0,1];w['lon']=[0,74];self.assertEqual(plan_subset(fixture(),w)['profiles'],150);w['lon']=[0,75]
        with self.assertRaises(ValueError):plan_subset(fixture(),w)
    def test_vertical_cap_is_not_bypassed_by_stride(self):
        w=window();w['level']=[0,40]
        with self.assertRaises(ValueError):plan_subset(fixture(),w)
        w['level']=[0,2,49]
        with self.assertRaises(ValueError):plan_subset(fixture(),w)
    def test_minimum_profiles_and_invalid_ranges(self):
        for role,pair in [('lon',[0,1]),('lon',[2,1]),('lat',[-1,0]),('lon',[0,720]),('level',[False,2])]:
            w=window();w[role]=pair
            with self.subTest(role=role,pair=pair),self.assertRaises(ValueError):plan_subset(fixture(),w)
    def test_missing_or_implicit_axes_rejected(self):
        w=window();del w['lat']
        with self.assertRaises(ValueError):plan_subset(fixture(),w)
        m=fixture();m['fields']['EVEL']['dimensions']=['time','Z','latitude']
        with self.assertRaises(ValueError):plan_subset(m,window())
    def test_dimension_order_comes_from_metadata(self):
        m=fixture();m['fields']['NVEL']['dimensions']=['longitude','latitude','Z','time'];p=plan_subset(m,window());self.assertIn('NVEL[0:1:2][0:1:0][0:1:39][0:1:0]',p['constraint_expression'])
    def test_grid_packing_units_and_unknown_fills_rejected(self):
        for change in [{'kind':'Grid'},{'dtype':'Int16'},{'units':'cm/s'},{'fill_metadata_present':False}]:
            m=fixture();m['fields']['EVEL'].update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):plan_subset(m,window())
    def test_vertical_interfaces_and_coordinates_required(self):
        for mode in ['missing','three','wrong_coordinate']:
            m=fixture()
            if mode=='missing':del m['coordinate_fields']['level_bounds']
            elif mode=='three':m['dimensions']['nv']=3
            else:m['fields']['latitude']['dimensions']=['longitude']
            with self.subTest(mode=mode),self.assertRaises(ValueError):plan_subset(m,window())
    def test_product_protocol_digest_and_identifier_rejected(self):
        for key,value in [('product','another_product'),('protocol','DAP4'),('metadata_sha256','not_digest')]:
            m=fixture();m[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):plan_subset(m,window())
        m=fixture();m['coordinate_fields']['level']='Z;fetch_all()'
        with self.assertRaises(ValueError):plan_subset(m,window())
    def test_inputs_immutable_and_array_byte_accounting(self):
        m=fixture();w=window();old=copy.deepcopy((m,w));p=plan_subset(m,w);self.assertEqual((m,w),old);self.assertEqual(p['numeric_values'],2*120+1+40+1+3+80);self.assertEqual(p['native_array_bytes'],2*120*4+(1+40+1+3+80)*8)
    def test_bounds_are_not_server_science_or_transport_validation(self):
        p=plan_subset(fixture(),window())
        for key in ['native_bytes_include_transport_overhead','actual_endpoint_verified','actual_transport_bound_verified','actual_field_data_acquired','current_axis_or_identity_validated','scientific_depth_operator_frozen','full_goal_complete']:self.assertIs(p[key],False)
    def test_missing_credentials_and_boolean_claims_do_not_verify_acquisition(self):
        flags=dict(earthdata_available=False,metadata_verified=False,server_subset_verified=False,transport_bound_verified=False,scientific_operator_frozen=False);p=prerequisite_report(**flags);self.assertEqual(len(p['declared_missing_prerequisites']),5);self.assertFalse(p['actual_acquisition_verified']);p=prerequisite_report(**{k:True for k in flags});self.assertTrue(p['all_declared_prerequisites_met']);self.assertFalse(p['actual_acquisition_verified']);flags['earthdata_available']='token'
        with self.assertRaises(ValueError):prerequisite_report(**flags)

if __name__=='__main__':unittest.main()
