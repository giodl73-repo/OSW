import csv
from datetime import date
import hashlib
import json
import unittest
import build_eddy_measurement_register_v1 as register


class EddyRegister(unittest.TestCase):
    def test_identity_inventory_and_source_custody(self):
        d=register.build()
        self.assertEqual(len(d['records']),136)
        self.assertEqual(len({r['entity_id'] for r in d['records']}),136)
        self.assertEqual(len(d['evidence']),48)
        for path,pin in d['input_sha256'].items():self.assertEqual(hashlib.sha256((register.ROOT/path).read_bytes()).hexdigest(),pin)
        for r in d['evidence']:
            source=json.loads((register.ROOT/r['source_file']).read_bytes())
            self.assertEqual(register.pointer(source,r['source_pointer']),r['raw_record'])
            self.assertTrue(r['source_url']);self.assertTrue(r['source_locator'])
        self.assertFalse(d['full_goal_complete']);self.assertFalse(d['runtime_changed'])

    def test_size_conflicts_and_population_statistics_keep_their_meaning(self):
        d=register.build();rows={r['id']:r for r in d['evidence']}
        conflict=rows['eliza-2007-feb-2009-radius']
        self.assertIsNone(conflict['value']);self.assertTrue(conflict['value_conflict'])
        self.assertEqual({c['value_km'] for c in conflict['source_claims']},{88,93})
        january=rows['eliza-2007-january-section-radius']
        self.assertTrue(january['date_conflict']);self.assertIsNone(january['raw_record']['period_month'])
        self.assertEqual(rows['astrid-2000-maximum-speed-radius']['value'],120)
        self.assertEqual(rows['astrid-2000-integration-radius']['value'],140)
        population=[r for r in d['evidence'] if r['metric'].startswith('population_mean')]
        self.assertEqual([(r['value'],r['standard_deviation'],r['sample_count']) for r in population],[(64,6,2),(71,13,5),(80,16,18),(81,12,42),(79,9,63),(73,10,73),(77,16,74)])
        self.assertTrue(all(r['entity_id']=='eddy:geography:agulhas-rings-family' and r['uncertainty'] is None for r in population))
        self.assertTrue(all(r['geometry'] is None and not r['rank_eligible'] and not r['seasonal_playback_eligible'] for r in d['evidence']))

    def test_date_windows_units_and_candidate_identities_are_not_lifetimes(self):
        d=register.build();rows={r['entity_id']:r for r in d['records']}
        for name in ['thor-2020','ursa-2021']:
            r=rows['eddy:published:'+name]
            self.assertIsNotNone(r['paper_window_context']);self.assertFalse(r['evidence_ids'])
        for r in d['records']:
            self.assertFalse(r['candidate_crosswalk_is_verified']);self.assertIsNone(r['whole_lifetime_days'])
            if r['source_collection']=='horizon_loop_current':self.assertFalse(r['evidence_ids'])
        for r in d['evidence']:
            if r['metric'] in ['source_track_elapsed_span','coherent_core_analysis_interval']:
                self.assertEqual(r['value'],(date.fromisoformat(r['period_end'])-date.fromisoformat(r['period_start'])).days)
            self.assertFalse(r['whole_lifetime_inferred'])
        lilian=next(r for r in d['evidence'] if r['metric']=='author_reported_approximate_lifetime')
        self.assertEqual((lilian['value'],lilian['unit']),(3.5,'year'))
        travel=next(r for r in d['evidence'] if r['category']=='travel')
        self.assertIsNone(travel['value']);self.assertEqual(travel['lower_bound'],5500);self.assertTrue(travel['lower_bound_exclusive'])
        self.assertEqual(sum(r['unit']=='month' for r in d['evidence']),3)

    def test_csv_does_not_drop_conflicts_or_rewrite_units(self):
        d=register.build();evidence={r['id']:r for r in d['evidence']}
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:rows=list(csv.DictReader(stream))
        self.assertEqual(len(rows),48)
        for r in rows:
            original=evidence[r['id']]
            self.assertEqual(r['unit'],original['unit']);self.assertEqual(r['source_pointer'],original['source_pointer'])
            self.assertEqual(r['value'],str(original['value']) if original['value'] is not None else '')
            self.assertEqual(json.loads(r['source_claims_json']),original['source_claims'])

    def test_second_batch_preserves_first_batch_and_new_scopes(self):
        d=register.build();rows={r['id']:r for r in d['evidence']}
        pin=hashlib.sha256(json.dumps(d['evidence'][:40],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
        self.assertEqual(pin,d['first_batch_evidence_sha256'])
        self.assertEqual(d['counts']['identities_with_measurements'],23)
        kenai=rows['kenai-2007-rovegno-censored-track-span']
        self.assertEqual(kenai['value'],378);self.assertTrue(kenai['right_censored'])
        ulla=rows['meddy-ulla-paillet-tracked-duration']
        self.assertEqual((ulla['value'],ulla['unit']),(18,'month'));self.assertIsNone(ulla['period_start'])
        self.assertIn('abstract',ulla['source_access'])
        for member in ['a','b']:
            r=rows[f'haida-1998{member}-crawford-component-radius']
            self.assertEqual(r['component_label'],'Haida-1998'+member)
            self.assertIn('before the June 1998 merger',r['scope'])
        laura=rows['laura-1999-van-aken-maximum-drift-speed']
        self.assertEqual((laura['value'],laura['unit']),(8.6,'km/day'))
        self.assertFalse(any(r['category']=='size' and r['entity_id']=='eddy:geography:laura-1999' for r in d['evidence']))


if __name__=='__main__':unittest.main()
