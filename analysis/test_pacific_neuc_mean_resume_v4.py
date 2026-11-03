import copy,hashlib,json,unittest
import pacific_neuc_mean_resume_v4 as p
import test_pacific_neuc_mean_resume_v3 as prior_tests


class ResidualTests(unittest.TestCase):
    def fixture(self):
        h,l,seed,op=prior_tests.RecoveryTests().fixture();cp={**copy.deepcopy(seed),'request_index':3};raw=json.dumps(cp).encode()
        bundle={'schema':'osw.exact-utf8-artifact-member-bundle.v1','members':[{'file':'completed-ranges/request-003.json','content_utf8':raw.decode(),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}]}
        return seed,bundle
    def test_bundle_restores_original_utf8_bytes_without_rewriting_seed(self):
        seed,b=self.fixture();r=p.restore_checkpoint_bundle(b,seed)
        self.assertEqual(len(r['parts']),2);self.assertEqual(len(seed['parts']),1)
    def test_bundle_hash_length_source_request_and_duplicate_changes_rejected(self):
        seed,b=self.fixture()
        for kind in ['hash','length','name','duplicate','source','request']:
            bad=copy.deepcopy(b);member=bad['members'][0]
            if kind=='hash':member['sha256']='bad'
            if kind=='length':member['bytes']+=1
            if kind=='name':member['file']='../request-003.json'
            if kind=='duplicate':bad['members']*=2
            if kind in ['source','request']:
                cp=json.loads(member['content_utf8']);cp['source_url' if kind=='source' else 'request_index']='changed';raw=json.dumps(cp).encode();member.update(content_utf8=raw.decode(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
            with self.subTest(kind=kind),self.assertRaises(ValueError):p.restore_checkpoint_bundle(bad,seed)
    def test_duplicate_success_in_bundle_rejected_by_aggregate_custody(self):
        seed,b=self.fixture();cp=p.restore_checkpoint_bundle(b,seed);h,l,_,op=prior_tests.RecoveryTests().fixture()
        with self.assertRaises(ValueError):p.import_custody([l],cp,h)
    def test_actual_residual_plan_accounts_for_every_prior_attempt_and_success(self):
        op=json.loads((p.ROOT/p.OPERATOR).read_bytes())
        for f,pin in op['input_sha256'].items():self.assertEqual(hashlib.sha256((p.ROOT/f).read_bytes()).hexdigest(),pin,f)
        geometry=json.loads((p.ROOT/op['geometry_operator_file']).read_bytes());h=json.loads((p.ROOT/geometry['header_file']).read_bytes());axes=json.loads((p.ROOT/geometry['coordinates_file']).read_bytes())['coordinate_arrays']
        sections,patches,_,counts=p.rectangle_plan(axes,h,geometry);allowed=[r for patch in patches for r in patch['ranges']]
        cp=p.restore_checkpoint_bundle(json.loads((p.ROOT/op['prior_checkpoint_bundle_file']).read_bytes()),json.loads((p.ROOT/op['prior_checkpoint_file']).read_bytes()))
        parts,rows,requested,body=p.import_custody([json.loads((p.ROOT/f).read_bytes()) for f in op['prior_ledger_files']],cp,h)
        batches=p.recovery_plan(allowed,parts,rows,requested,body,op)
        self.assertEqual((len(parts),len(rows),requested,body,len(batches)),(2306,465,300160,567537,355))
        self.assertEqual(requested+sum(n for batch in batches for _,n in batch),527232);self.assertEqual(len(rows)+len(batches),820)
        missing=[r for batch in batches for r in batch];self.assertEqual(len(missing),1774);self.assertFalse(set(parts)&set(missing));self.assertEqual(set(parts)|set(missing),set(allowed))
        self.assertEqual(counts['cell_pairs'],130560)


if __name__=='__main__':unittest.main()
