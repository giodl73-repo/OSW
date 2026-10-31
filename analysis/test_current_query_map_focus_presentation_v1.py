import copy
import json
import unittest
import current_query_map_focus_presentation_v1 as presentation


class FocusPresentationTests(unittest.TestCase):
    def test_only_three_presentation_hashes_change_and_engine_namespaces_are_preserved(self):
        raw=(presentation.ROOT/'research/current-utf8-validation-delivery-run-v1/engine-manifest.json').read_bytes()
        old=json.loads(raw);pins={p:'a'*64 for p in presentation.PATHS}
        new=presentation.overlay(raw,pins)
        self.assertEqual({k:v for k,v in new.items() if k not in ['sha256',presentation.KEY]},
                         {k:v for k,v in old.items() if k!='sha256'})
        self.assertEqual({p:v for p,v in new['sha256'].items() if p not in presentation.PATHS},
                         {p:v for p,v in old['sha256'].items() if p not in presentation.PATHS})
        self.assertEqual(new['sha256']['almanac/query-engine.wasm'],presentation.BINARY)
        self.assertFalse(new[presentation.KEY]['compiled_inputs_changed'])

    def test_other_engine_missing_asset_or_unrelated_asset_binding_refused(self):
        raw=(presentation.ROOT/'research/current-utf8-validation-delivery-run-v1/engine-manifest.json').read_bytes()
        pins={p:'a'*64 for p in presentation.PATHS}
        for bad in [dict(pins,**{'almanac/query-worker.js':'b'*64}),{p:v for p,v in pins.items() if p!='almanac/query.js'},dict(pins,**{'almanac/query.js':'bad'})]:
            with self.assertRaises(ValueError):presentation.overlay(raw,bad)
        changed=copy.deepcopy(json.loads(raw));changed['sha256']['almanac/query-engine.wasm']='c'*64
        with self.assertRaises(ValueError):presentation.overlay(json.dumps(changed).encode(),pins)


if __name__=='__main__':unittest.main()
