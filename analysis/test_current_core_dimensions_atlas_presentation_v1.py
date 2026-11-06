import unittest
import current_core_dimensions_atlas_presentation_v1 as presentation

class PresentationTests(unittest.TestCase):
    def test_binary_catalog_packet_and_compiler_receipts_unchanged(self):
        original=(presentation.ROOT/'research/current-core-dimensions-delivery-run-v1/engine-manifest.json').read_bytes()
        prior=presentation.json.loads(original);updates={p:presentation.hashlib.sha256((presentation.ROOT/p).read_bytes()).hexdigest() for p in presentation.PATHS}
        actual=presentation.overlay(original,updates)
        self.assertEqual({p:v for p,v in actual['sha256'].items() if p not in presentation.PATHS},{p:v for p,v in prior['sha256'].items() if p not in presentation.PATHS})
        self.assertEqual(actual['published_current_core_dimensions_engine_v1'],prior['published_current_core_dimensions_engine_v1'])
        for changed in [{**updates,'almanac/query-engine.wasm':'0'*64},{next(iter(updates)):'0'*64}]:
            with self.assertRaises(ValueError):presentation.overlay(original,changed)
        with self.assertRaises(ValueError):presentation.overlay(original+b' ',updates)

if __name__=='__main__':unittest.main()
