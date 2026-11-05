import copy,json,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
import discover_act2010_instrument_metadata_v1 as source

class FakeFTP:
    def __init__(self,fail=False):self.fail=fail;self.commands=[];self.closed=False
    def connect(self,*a,**k):
        if self.fail:raise OSError('Synthetic connection failure')
    def login(self,user,password):assert user=='anonymous' and password=='anonymous@'
    def close(self):self.closed=True
    def retrbinary(self,command,callback,blocksize):
        self.commands.append(command)
        if command.startswith('RETR '):callback(b'Metadata only: data access and processing documentation.');return
        if command.endswith('/data/'):
            callback(b'-rw-r--r-- 1 owner group 100 Jan 1 2020 ACT_A_01.nc\n-rw-r--r-- 1 owner group 100 Jan 1 2020 README.txt\n')
        else:callback(b'drwxr-xr-x 1 owner group 4096 Jan 1 2020 data\n')

class MetadataOnly(unittest.TestCase):
    def test_anonymous_listing_and_document_only_never_nc_field(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(source.signal,'setitimer'):
            client=FakeFTP();report,journal,failed=source.collect(Path(temp)/'source',client,time.monotonic()+210)
            self.assertFalse(failed);self.assertEqual(len(report['instrument_file_candidates']),1)
            self.assertFalse(report['native_field_acquisition_eligible']);self.assertEqual(journal['ocean_field_requests'],0)
            self.assertTrue(all(not c.endswith('.nc') for c in client.commands));self.assertTrue(client.closed)
            self.assertTrue(journal['producer_finalized_before_artifact_upload']);self.assertEqual(len(journal['operations']),4)
            self.assertEqual(journal['unused_independent_case_remote_operations'],14)

    def test_one_failed_connection_is_durable_no_reconnect(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(source.signal,'setitimer'):
            folder=Path(temp)/'source';client=FakeFTP(True);report,journal,failed=source.collect(folder,client,time.monotonic()+210)
            self.assertTrue(failed);self.assertEqual(len(journal['operations']),1);self.assertEqual(journal['operations'][0]['attempts'],1)
            self.assertEqual(json.loads((folder/'journal.json').read_bytes())['operations'],journal['operations'])
            self.assertEqual(client.commands,[]);self.assertTrue(client.closed)

    def test_traversal_and_unsupported_listing_rejected(self):
        for raw in [b'-rw-r--r-- 1 x x 10 Jan 1 2020 ../../ocean.nc\n',b'nonsensical listing']:
            with self.assertRaises(ValueError):source.observed_entries(raw,source.PREFIX)
        with self.assertRaises(ValueError):source.observed_entries(b'', '/unrelated/')

    def test_only_observed_readme_license_text_is_downloadable(self):
        for name in ['ocean.nc','velocities.txt','README.nc','README.pdf']:
            self.assertFalse(source.is_document({'kind':'file','name':name}))
        self.assertTrue(source.is_document({'kind':'file','name':'README.txt'}))
        self.assertTrue(source.is_document({'kind':'file','name':'license_ACT.txt'}))

    def test_duplicate_remote_target_and_global_reserve_cannot_reset(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp);j={'operations':[],'total_body_bytes':0}
            source.reserve(j,folder,'one','LIST',source.PREFIX,128000)
            with self.assertRaises(ValueError):source.reserve(j,folder,'two','LIST',source.PREFIX,128000)
            j['total_body_bytes']=source.BODY_CAP-127999
            with self.assertRaises(ValueError):source.reserve(j,folder,'two','LIST',source.PREFIX+'data/',128000)

    def test_raw_partial_is_saved_before_error_and_never_retried(self):
        class Broken(FakeFTP):
            def retrbinary(self,command,callback,blocksize):callback(b'partial raw source');raise OSError('Synthetic transfer failure')
        with tempfile.TemporaryDirectory() as temp,patch.object(source.signal,'setitimer'):
            folder=Path(temp);j={'operations':[],'total_body_bytes':0}
            self.assertIsNone(source.operation(Broken(),folder,j,'list-01','LIST',source.PREFIX,128000,time.monotonic()+210))
            self.assertEqual((folder/'list-01.raw').read_bytes(),b'partial raw source')
            self.assertEqual(j['operations'][0]['status'],'failed_or_interrupted_no_retry')
            with self.assertRaises(ValueError):source.operation(Broken(),folder,j,'list-02','LIST',source.PREFIX,128000,time.monotonic()+210)

if __name__=='__main__':unittest.main()
