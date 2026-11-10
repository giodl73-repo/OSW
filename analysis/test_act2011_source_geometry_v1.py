import copy,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
import qualify_act2011_source_geometry_v1 as source

CONTEXT={'latitude_limits_degrees_north':[-34.9,-33.5],'longitude_limits_degrees_east':[27.4,28.4]}
def points(lat=-32.3464):return {'instrument_observations':[[{'requested_time_utc':'2011-06-'+str(day)+'T12:00:00Z','source_coordinate':[27.6579,lat]} for day in [14,15,16]] for k in range(2)]}
def prior():return {'operations':[{'target_id':'old'+str(i),'command':'LIST','path':'/old/'+str(i)} for i in range(10)],'total_body_bytes':1742987}

class Client:
    def __init__(self,data):self.data=data;self.commands=[];self.closed=False
    def connect(self,*a,**k):pass
    def login(self,*a):assert a==('anonymous','anonymous@')
    def close(self):self.closed=True
    def retrbinary(self,command,callback,blocksize):self.commands.append(command);callback(self.data)

class GeometryQualification(unittest.TestCase):
    def test_actual_conflict_and_no_provider_coordinate_mutation(self):
        p=points();before=copy.deepcopy(p);r=source.compare(p,CONTEXT)
        self.assertEqual(r['points_outside_catalogue_extent'],6);self.assertEqual(r['status'],'SOURCE_CATALOGUE_EXTENT_CONFLICT')
        self.assertEqual(p,before);self.assertFalse(r['provider_coordinates_modified']);self.assertIsNone(r['corrected_nominal_position'])
        self.assertFalse(r['geographic_assignment_eligible']);self.assertFalse(r['physical_state_join_eligible'])

    def test_inside_extent_is_not_location_or_axis_validation(self):
        r=source.compare(points(-34),CONTEXT)
        self.assertEqual(r['points_outside_catalogue_extent'],0);self.assertFalse(r['geographic_assignment_eligible'])
        self.assertFalse(r['catalogue_extent_membership_is_location_validation'])

    def test_missing_coordinates_and_fitted_extent_not_silently_accepted(self):
        p=points();p['instrument_observations'][0][0]['source_coordinate']=None
        r=source.compare(p,CONTEXT);self.assertFalse(r['point_outcomes'][0]['coordinate_valid_numeric_degrees'])
        with self.assertRaises(ValueError):source.compare(p,CONTEXT|{'latitude_limits_degrees_north':[-35,-32]})

    def test_three_new_ops_preserve_original_ten_and_do_not_read_native_fields(self):
        data=b'Original public source metadata.';targets=[{'target_id':k,'path':source.BASE+p,'provider_size_bytes':len(data),'provider_asserted_sha256':source.sha(data)} for k,p in zip(['archive-lonlat','archive-journal'],source.PATHS)]
        p=prior();before=copy.deepcopy(p['operations']);c=Client(data)
        audit={'conservative_case_scalar_bound_including_prior_metadata':85175,'case_time_charge_after_audit':54.31767040399999}
        with tempfile.TemporaryDirectory() as temp,patch.object(source.signal,'setitimer'):
            r,j,failed=source.collect(Path(temp)/'out',c,p,audit,targets,points(),CONTEXT,time.monotonic()+155)
            self.assertFalse(failed);self.assertEqual(j['operations'][:10],before);self.assertEqual(len(j['operations']),13)
            self.assertEqual(j['unused_independent_case_remote_operations'],5);self.assertEqual(len(c.commands),2)
            self.assertFalse(r['native_files_downloaded_again']);self.assertEqual(r['new_native_ocean_values_decoded'],0)
            self.assertTrue(j['producer_finalized_before_artifact_upload']);self.assertTrue(c.closed)

    def test_source_hash_mismatch_retains_exact_bytes_and_never_retries(self):
        data=b'Original bytes';t={'target_id':'archive-lonlat','path':source.BASE+source.PATHS[0],'provider_size_bytes':len(data),'provider_asserted_sha256':'0'*64}
        j=prior();j['qualification_body_bytes']=0;c=Client(data)
        with tempfile.TemporaryDirectory() as temp,patch.object(source.signal,'setitimer'):
            folder=Path(temp)
            with self.assertRaises(ValueError):source.acquire(c,folder,j,t,time.monotonic()+155)
            self.assertEqual((folder/'archive-lonlat.raw').read_bytes(),data)
            with self.assertRaises(ValueError):source.acquire(c,folder,j,t,time.monotonic()+155)
            self.assertEqual(len(c.commands),1)

    def test_closed_phase_budget_is_not_renewed_or_reset(self):
        j=prior();j['qualification_body_bytes']=0
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)
            for i in range(3):source.reserve(j,folder,'new'+str(i),'RETR','/new/'+str(i),0)
            with self.assertRaises(ValueError):source.reserve(j,folder,'new3','RETR','/new/3',0)
            self.assertEqual(len(j['operations']),13)

if __name__=='__main__':unittest.main()
