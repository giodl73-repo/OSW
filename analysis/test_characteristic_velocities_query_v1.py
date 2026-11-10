import copy,unittest
from unittest.mock import patch
import characteristic_velocities_query_v1 as query

class AdmissionTests(unittest.TestCase):
    def fixture(self):
        doc=query.build_contract();rows={n:[] for n in doc['parent_collection_counts']};rows['sources']=copy.deepcopy(doc['prior_source_inventory'])
        for prior in doc['prior_owners'].values():
            for name in ('objects','entities','widths'):rows[name].extend(copy.deepcopy(prior[name]))
        rows['current_speed_statistics']=[{'id':'pooled-speed','mean':.83}];rows['current_core_velocity_estimates']=[{'id':'seasonal-core','velocity':.2}]
        doc['parent_collection_counts']={n:len(v) for n,v in rows.items()};return doc,rows
    def test_ten_rows_and_all_older_measurement_operators_preserved(self):
        doc,rows=self.fixture();before=copy.deepcopy(rows);after,manifest=query.apply_verified(rows,{'input_sha256':{}},doc,parent_logical_sha256=query.PARENT,contract_sha256=query.digest(doc))
        self.assertEqual(rows,before);self.assertEqual(len(after[query.COLLECTION]),10)
        for name in rows:
            if name not in ('objects','sources'):self.assertEqual(after[name],rows[name])
        for family in query.FAMILIES:self.assertEqual([r for r in after['objects'] if r['id']==family],[r for r in rows['objects'] if r['id']==family])
        self.assertEqual(sum(r['capabilities'].get('characteristic_velocity',0) for r in after['objects']),10)
    def test_parent_owner_or_new_id_corruption_refused(self):
        for case in range(3):
            doc,rows=self.fixture();parent=query.PARENT
            if case==0:parent='0'*64
            elif case==1:rows['objects'][0]['fingerprint']='changed'
            else:rows['claims'].append({'id':doc['records'][0]['id']});doc['parent_collection_counts']['claims']=1
            with self.assertRaises(ValueError):query.apply_verified(rows,{},doc,parent_logical_sha256=parent,contract_sha256=query.digest(doc))
    def test_false_time_series_or_physical_geometry_in_preparation_refused(self):
        original=query.read
        for field,value in [('monthly_speed_playback_eligible',True),('annual_speed_extrema',[.3,.4]),('geometry',{'type':'Point','coordinates':[0,0]})]:
            def altered(path):
                data=original(path)
                if path==query.PREPARED:data['new_records'][0][field]=value
                return data
            with patch.object(query,'read',side_effect=altered),self.assertRaises(ValueError):query.build_contract()
    def test_frozen_contract(self):self.assertEqual((query.ROOT/query.FILE).read_bytes(),query.encoded(query.build_contract()))

if __name__=='__main__':unittest.main()
