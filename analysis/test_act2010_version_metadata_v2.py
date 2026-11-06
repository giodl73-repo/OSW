import copy,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
import discover_act2010_version_metadata_v2 as source

class Client:
    def __init__(self,broken=False):self.commands=[];self.broken=broken;self.closed=False;self.connections=0
    def connect(self,*a,**k):self.connections+=1
    def login(self,*a):assert a==('anonymous','anonymous@')
    def close(self):self.closed=True
    def retrbinary(self,command,callback,blocksize):
        self.commands.append(command)
        if command.startswith('RETR '):callback(b'<root><accessConstraints>None</accessConstraints></root>' if not self.broken else b'<!DOCTYPE bad><root/>')
        elif command.endswith('/1.1/'):
            callback(b'drwxr-xr-x 1 o g 1 Jan 1 2020 data\n')
        else:callback(b'drwxr-xr-x 1 o g 1 Jan 1 2020 0-data\n')

class VersionContinuation(unittest.TestCase):
    def test_exact_prior_budget_and_observed_targets(self):
        j,r=source.prior_state();self.assertEqual(len(j['operations']),2);self.assertEqual(j['total_body_bytes'],134)
        self.assertEqual([e['name'] for e in r['observed_entries']],['0140939.1.1.xml','1.1'])

    def test_four_remaining_operations_no_root_or_field_replay(self):
        j,r=source.prior_state();before=copy.deepcopy(j['operations'])
        with tempfile.TemporaryDirectory() as temp,patch.object(source.signal,'setitimer'):
            c=Client();report,journal,failed=source.collect(Path(temp)/'new',c,j,r,time.monotonic()+160)
            self.assertFalse(failed);self.assertEqual(journal['operations'][:2],before)
            self.assertEqual(len(journal['operations']),6);self.assertEqual(journal['unused_independent_case_remote_operations'],12)
            self.assertEqual(journal['unused_metadata_stage_remote_operations'],0);self.assertEqual(c.connections,1)
            self.assertNotIn('LIST '+source.frozen.PREFIX,c.commands)
            self.assertTrue(all(not s.endswith(('.nc','.mat','.zip')) for s in c.commands))
            self.assertFalse(report['native_field_acquisition_eligible']);self.assertTrue(c.closed)
            self.assertEqual(report['unvisited_observed_directories'][0]['name'],'0-data')

    def test_source_metadata_does_not_automatically_grant_fields(self):
        m=source.legal_metadata(b'<r><accessConstraints>None</accessConstraints><useLimitation>Credit investigators</useLimitation></r>')
        self.assertFalse(m['field_permission_automatically_inferred']);self.assertEqual(len(m['provider_legal_statements']),2)

    def test_entities_and_oversized_xml_rejected(self):
        for raw in [b'<!DOCTYPE r><r/>',b'<!ENTITY x><r/>',b'x'*128001]:
            with self.assertRaises(ValueError):source.legal_metadata(raw)

    def test_parser_failure_saves_bytes_and_never_retries(self):
        j,r=source.prior_state()
        with tempfile.TemporaryDirectory() as temp,patch.object(source.signal,'setitimer'):
            c=Client(True);folder=Path(temp)/'new';report,journal,failed=source.collect(folder,c,j,r,time.monotonic()+160)
            self.assertTrue(failed);self.assertEqual(len(journal['operations']),4)
            self.assertEqual(len(c.commands),1);self.assertTrue((folder/'phase2-provider-xml.raw').exists())
            self.assertFalse(report['native_field_acquisition_eligible'])

    def test_no_guessed_data_path_if_version_listing_missing(self):
        class NoData(Client):
            def retrbinary(self,command,callback,blocksize):
                if command.startswith('LIST '):self.commands.append(command);callback(b'-rw-r--r-- 1 o g 1 Jan 1 2020 other.nc\n')
                else:super().retrbinary(command,callback,blocksize)
        j,r=source.prior_state()
        with tempfile.TemporaryDirectory() as temp,patch.object(source.signal,'setitimer'):
            c=NoData();_,journal,failed=source.collect(Path(temp)/'new',c,j,r,time.monotonic()+160)
            self.assertTrue(failed);self.assertEqual(len(journal['operations']),5);self.assertEqual(len(c.commands),2)

if __name__=='__main__':unittest.main()
