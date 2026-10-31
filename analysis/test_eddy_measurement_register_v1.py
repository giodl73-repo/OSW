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
        self.assertEqual(len(d['evidence']),214)
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
            self.assertIsNotNone(r['paper_window_context'])
            self.assertTrue(all(e['metric']=='source_dated_event_stage_interval' for e in d['evidence'] if e['entity_id']==r['entity_id']))
        for r in d['records']:
            self.assertFalse(r['candidate_crosswalk_is_verified']);self.assertIsNone(r['whole_lifetime_days'])
            if r['source_collection']=='horizon_loop_current' and r['entity_id'].endswith('-secondary'):self.assertFalse(r['evidence_ids'])
        for r in d['evidence']:
            if r['metric'] in ['source_track_elapsed_span','coherent_core_analysis_interval','source_dated_event_stage_interval']:
                self.assertEqual(r['value'],(date.fromisoformat(r['period_end'])-date.fromisoformat(r['period_start'])).days)
            self.assertFalse(r['whole_lifetime_inferred'])
        lilian=next(r for r in d['evidence'] if r['metric']=='author_reported_approximate_lifetime')
        self.assertEqual((lilian['value'],lilian['unit']),(3.5,'year'))
        travel=next(r for r in d['evidence'] if r['category']=='travel')
        self.assertIsNone(travel['value']);self.assertEqual(travel['lower_bound'],5500);self.assertTrue(travel['lower_bound_exclusive'])
        self.assertEqual(sum(r['unit']=='month' for r in d['evidence']),4)

    def test_csv_does_not_drop_conflicts_or_rewrite_units(self):
        d=register.build();evidence={r['id']:r for r in d['evidence']}
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:rows=list(csv.DictReader(stream))
        self.assertEqual(len(rows),214)
        for r in rows:
            original=evidence[r['id']]
            self.assertEqual(r['unit'],original['unit']);self.assertEqual(r['source_pointer'],original['source_pointer'])
            self.assertEqual(r['value'],str(original['value']) if original['value'] is not None else '')
            self.assertEqual(json.loads(r['source_claims_json']),original['source_claims'])
            self.assertEqual(json.loads(r['range_value_json']),original.get('range_value'))
            self.assertEqual(json.loads(r['calculation_json']),original.get('calculation'))
            self.assertEqual(json.loads(r['calendar_support_json']),original.get('calendar_support'))

    def test_second_batch_preserves_first_batch_and_new_scopes(self):
        d=register.build();rows={r['id']:r for r in d['evidence']}
        pin=hashlib.sha256(json.dumps(d['evidence'][:40],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
        self.assertEqual(pin,d['first_batch_evidence_sha256'])
        self.assertEqual(len({r['entity_id'] for r in d['evidence'][:48]}),23)
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

    def test_regional_ranges_models_and_phase_intervals_are_not_whole_feature_measurements(self):
        d=register.build();rows={r['id']:r for r in d['evidence']}
        batch=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v3.json').read_bytes())
        prior=hashlib.sha256(json.dumps(d['evidence'][:48],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
        self.assertEqual(prior,batch['baseline_evidence_sha256'])
        self.assertEqual(d['counts']['non_registry_entries_with_references'],40)
        self.assertEqual(len({r['entity_id'] for r in d['evidence'][:77]}),40)
        diameter=rows['meddies-bower-1997-typical-diameter']
        self.assertIsNone(diameter['value']);self.assertEqual(diameter['range_value'],[20,100])
        depth=rows['peddies-font-2024-depth-band']
        self.assertEqual((depth['category'],depth['unit'],depth['range_value']),('structure','m',[200,300]))
        self.assertIsNone(depth['value'])
        bound=rows['cuban-kourafalou-2017-diameter-bound']
        self.assertIsNone(bound['value']);self.assertEqual(bound['upper_bound'],100);self.assertTrue(bound['upper_bound_exclusive'])
        for name,value in [('mindanao',126),('halmahera',260)]:
            r=rows[f'{name}-arruda-nof-2003-model-radius'];self.assertEqual(r['value'],value)
            self.assertEqual(r['metric'],'published_theoretical_model_case_radius')
        self.assertEqual(rows['danube-korotaev-2003-presence']['unit'],'percent')
        for name,elapsed in [('thor-2020',56),('ursa-2021',49)]:
            r=rows[name+'-event-stage-interval'];self.assertEqual(r['value'],elapsed)
            self.assertEqual(r['metric'],'source_dated_event_stage_interval');self.assertFalse(r['whole_lifetime_inferred'])

    def test_registry_calendar_precision_and_secondary_noninheritance(self):
        d=register.build();rows={r['id']:r for r in d['evidence']}
        batch=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v4.json').read_bytes())
        prior=hashlib.sha256(json.dumps(d['evidence'][:77],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
        self.assertEqual(prior,batch['baseline_evidence_sha256'])
        self.assertEqual(d['counts']['registry_entries_with_own_references'],79)
        self.assertEqual(d['counts']['identities_with_measurements'],119)
        self.assertEqual(d['counts']['linked_primary_context_entries'],15)
        self.assertEqual(d['counts']['entries_without_numeric_or_primary_context'],2)
        self.assertEqual(sum(r['metric']=='registry_reported_maximum_surface_current' for r in d['evidence']),60)
        self.assertEqual(sum(r['metric']=='registry_separation_to_dissipation_calendar_span' for r in d['evidence']),77)
        kathleen=rows['eddy:horizon:loop-08-primary-registry-calendar-span']
        self.assertEqual(kathleen['range_value'],[214,273]);self.assertEqual(kathleen['calendar_support']['start_precision'],'month')
        rebel=rows['eddy:horizon:loop-41-primary-registry-calendar-span']
        self.assertEqual(rebel['range_value'],[0,2]);self.assertEqual(rebel['calendar_support']['unconditioned_elapsed_day_range'],[-27,2])
        self.assertTrue(rebel['calendar_support']['chronology_conditioned']);self.assertIsNone(rebel['value'])
        for r in d['records']:
            if r['entity_id'] in ['eddy:horizon:loop-80-primary','eddy:horizon:loop-81-primary']:
                self.assertFalse(r['evidence_ids']);self.assertFalse(r['registry_context']['active_label_is_current_status'])
            if r['entity_id'].endswith('-secondary'):
                self.assertFalse(r['evidence_ids']);self.assertIsNone(r['registry_context'])
                self.assertTrue(r['linked_primary_context']['evidence_ids'])
        for r in d['evidence']:
            if r['entity_id'].startswith('eddy:horizon:'):
                self.assertTrue(r['entity_id'].endswith('-primary'))
                self.assertFalse(r['rights_screened_release_eligible'])
                self.assertEqual(r['evidence_role'],'registry_source_reference')
                if r['category']=='duration':self.assertIsNone(r['value']);self.assertEqual(r['calendar_support']['end_precision'],'month')


if __name__=='__main__':unittest.main()
