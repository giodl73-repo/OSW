import ast,copy,pathlib,unittest
from unittest.mock import patch
import build_current_depth_almanac_v2 as v2
from test_current_depth_almanac_v1 import AlmanacTests

class ContinuationTests(unittest.TestCase):
    def setUp(self):
        self.ledger={'reserved_numeric_tokens':190596,'unique_json_bytes':11025249,'packets':[{'sha256':'6e43d47b6c3a0106fe3d0606d10d6d59e8b2f216a47598f319e1d9b1b8731f71','bytes':2075007,'reserved_numeric_tokens':161481,'status':'decoded_and_cached'}]}
    def test_identical_scientific_functions_and_encoding(self):
        root=pathlib.Path(__file__).parent
        funcs=lambda name:{n.name:ast.dump(n,include_attributes=False) for n in ast.parse((root/name).read_text()).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
        a=funcs('build_current_depth_almanac_v1.py');b=funcs('build_current_depth_almanac_v2.py')
        for name in a:
            if name!='main':self.assertEqual(a[name],b[name],name)
    def test_changed_output_cannot_reuse_prior_proof(self):
        with self.assertRaises(ValueError):v2.verify_prior_roundtrip(b'changed',self.ledger)
        with self.assertRaises(ValueError):v2.verify_prior_roundtrip(b'x'*2075007,self.ledger)
    def test_pending_or_different_packet_not_prior_success(self):
        for key,value in [('status','reserved_before_decode'),('reserved_numeric_tokens',0),('bytes',10),('sha256','different')]:
            ledger=copy.deepcopy(self.ledger);ledger['packets'][-1][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):v2.verify_prior_roundtrip(b'x',ledger)
    def test_cumulative_charges_cannot_reset(self):
        for key in ['reserved_numeric_tokens','unique_json_bytes']:
            ledger=copy.deepcopy(self.ledger);ledger[key]=0
            with self.subTest(key=key),self.assertRaises(ValueError):v2.verify_prior_roundtrip(b'x',ledger)
    def test_prior_proof_is_only_byte_custody_no_json_decode(self):
        # Synthetic hash stub exercises control flow; actual cloud packet uses real SHA256.
        with patch.object(v2,'sha',return_value=self.ledger['packets'][-1]['sha256']),patch.object(v2.json,'loads',side_effect=AssertionError('No scientific decode allowed')):
            proof=v2.verify_prior_roundtrip(b'x'*2075007,self.ledger)
        self.assertFalse(proof['new_final_packet_json_decode_performed']);self.assertEqual(proof['original_numeric_charge_retained'],161481)

if __name__=='__main__':unittest.main()
