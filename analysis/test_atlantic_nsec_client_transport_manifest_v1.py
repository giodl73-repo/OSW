import unittest
from pathlib import Path
import atlantic_nsec_client_transport_manifest_v1 as scope


class ManifestTests(unittest.TestCase):
    def test_only_reviewed_client_pins_change_and_verified_binary_is_preserved(self):
        raw=Path('research/atlantic-nsec-reference-delivery-run-v1/engine-manifest.json').read_bytes()
        parent=scope.json.loads(raw);result=scope.overlay(raw,{p:'a'*64 for p in scope.PATHS})
        self.assertEqual({k:v for k,v in result.items() if k not in ['sha256',scope.KEY]},
            {k:v for k,v in parent.items() if k!='sha256'})
        self.assertEqual({k:v for k,v in result['sha256'].items() if k not in scope.PATHS},
            {k:v for k,v in parent['sha256'].items() if k not in scope.PATHS})
        self.assertEqual(result[scope.KEY]['matching_binary_sha256'],parent['sha256']['almanac/query-engine.wasm'])

    def test_changed_parent_unrelated_pin_or_unbound_binary_refused(self):
        raw=Path('research/atlantic-nsec-reference-delivery-run-v1/engine-manifest.json').read_bytes()
        for source,pins in [(raw+b' ',{'almanac/query-packet.js':'a'*64}),
            (raw,{'almanac/query-engine.wasm':'b'*64}),(raw,{'almanac/query-packet.js':'invalid'})]:
            with self.assertRaises(ValueError):scope.overlay(source,pins)


if __name__=='__main__':unittest.main()
