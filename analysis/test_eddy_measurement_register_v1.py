import csv
import io
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
        self.assertEqual(len(d['evidence']),321)
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
            own=[e for e in d['evidence'] if e['entity_id']==r['entity_id']]
            self.assertEqual(sum(e['metric']=='source_dated_event_stage_interval' for e in own),1)
            self.assertEqual(sum(e.get('source_map_estimate') is not None for e in own),2 if name=='ursa-2021' else 0)
            self.assertTrue(all(e['metric']=='source_dated_event_stage_interval' or e['evidence_role']=='map_read_editorial_candidate_reference' for e in own))
        for r in d['records']:
            self.assertFalse(r['candidate_crosswalk_is_verified']);self.assertIsNone(r['whole_lifetime_days'])
            if r['source_collection']=='horizon_loop_current' and r['entity_id'].endswith('-secondary') and r['entity_id']!='eddy:horizon:loop-66-secondary':self.assertFalse(r['evidence_ids'])
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
        self.assertEqual(len(rows),321)
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
        self.assertEqual(d['counts']['registry_entries_with_own_references'],80)
        self.assertEqual(d['counts']['identities_with_measurements'],120)
        self.assertEqual(d['counts']['linked_primary_context_entries'],14)
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
                self.assertEqual(len(r['evidence_ids']),2 if r['entity_id']=='eddy:horizon:loop-66-secondary' else 0);self.assertIsNone(r['registry_context'])
                self.assertTrue(r['linked_primary_context']['evidence_ids'])
        for r in d['evidence']:
            if r['entity_id'].startswith('eddy:horizon:'):
                self.assertTrue(r['entity_id'].endswith('-primary') or r.get('independent_named_case'))
                self.assertFalse(r['rights_screened_release_eligible'])
                self.assertIn(r['evidence_role'],['registry_source_reference','qualified_published_named_case_reference','qualified_indexed_reference','graph_digitized_named_case_reference','map_read_named_case_reference','map_read_circulation_arrow_reference'])
                if r['category']=='duration' and r['evidence_role']=='registry_source_reference':self.assertIsNone(r['value']);self.assertEqual(r['calendar_support']['end_precision'],'month')


    def test_published_area_cases_preserve_units_dates_and_unverified_association(self):
        d=register.build();batch=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v5.json').read_bytes())
        prior=hashlib.sha256(json.dumps(d['evidence'][:214],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
        self.assertEqual(prior,batch['baseline_evidence_sha256'])
        rows=d['evidence'][214:241];self.assertEqual(len(rows),27)
        self.assertEqual([r['value'] for r in rows],[24271,43199,37442,19964,24998,21530,35065,57751,92026,45049,44392,22137,48786,21318,22511,67989,23563,12421,18682,49672,12369,31304,7596,25036,52058,70659,15451])
        self.assertEqual(d['counts']['size_owners'],73);self.assertEqual(d['counts']['size_records'],113)
        for r in rows:
            a=r['named_case_association'];self.assertFalse(a['physical_crosswalk_verified'])
            self.assertEqual((r['category'],r['unit']),('size','km2'))
            self.assertIsNone(r['geometry']);self.assertIsNone(r['uncertainty'])
            self.assertFalse(r['rights_screened_release_eligible']);self.assertFalse(r['whole_lifetime_inferred'])
            self.assertIn('0.17 m',r['definition']);self.assertIn('inter-event spacing',r['qualification'])
            self.assertEqual(r['period_start'],r['period_end'])
        alias=rows[10]['named_case_association']
        self.assertEqual((alias['source_name'],alias['registry_name']),('Millenium','Millennium'))
        self.assertFalse(alias['dates_equal']);self.assertEqual(alias['registry_initial_separation'],'2001-04-22')
        self.assertEqual(rows[15]['named_case_association']['dates_equal'],True)
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:csvrows=list(csv.DictReader(stream))[214:241]
        self.assertEqual([json.loads(r['named_case_association_json']) for r in csvrows],[r['named_case_association'] for r in rows])


    def test_regional_models_speed_ranges_and_different_depth_diagnostics(self):
        d=register.build();batch=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v6.json').read_bytes())
        prior=hashlib.sha256(json.dumps(d['evidence'][:241],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
        self.assertEqual(prior,batch['baseline_evidence_sha256'])
        rows={r['id']:r for r in d['evidence'][241:248]};self.assertEqual(len(rows),7)
        self.assertEqual(rows['batumi-menna-2014-typical-diameter']['value'],100)
        for name,value in [('sevastopol',70),('kaliakra',60)]:
            r=rows[f'{name}-besiktepe-2001-model-diameter'];self.assertEqual(r['value'],value)
            self.assertEqual(r['evidence_role'],'published_model_case_reference')
            self.assertIn('summer 1992 model case',r['case_label'])
        peddy=rows['peddies-morvan-2020-model-salinity-radius'];self.assertEqual(peddy['value'],10)
        self.assertEqual(peddy['evidence_role'],'qualified_indexed_model_case_reference')
        self.assertIn('salinity anomaly',peddy['definition']);self.assertIn('other instability cases',peddy['qualification'])
        speed=rows['sevastopol-menna-2014-spring-speed-range'];self.assertIsNone(speed['value'])
        self.assertEqual((speed['unit'],speed['range_value']),('cm/s',[15,20]))
        deep=rows['lilian-guerra-2018-mid-atlantic-depth'];shallow=rows['lilian-guerra-2018-brazil-depth']
        self.assertEqual((deep['value'],shallow['value']),(1200,400));self.assertNotEqual(deep['metric'],shallow['metric'])
        for r in [deep,shallow]:
            self.assertEqual((r['category'],r['unit']),('structure','m'));self.assertNotIn('range_value',r)
            self.assertIn('not form a thickness range',r['qualification'])
            self.assertIsNone(r['period_start']);self.assertIsNone(r['geometry'])
        self.assertEqual(d['counts']['structure_owners'],10)


    def test_named_orbits_contours_and_independent_secondary_sampling(self):
        d=register.build();batch=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v7.json').read_bytes())
        prior=hashlib.sha256(json.dumps(d['evidence'][:248],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
        self.assertEqual(prior,batch['baseline_evidence_sha256'])
        rows={r['id']:r for r in d['evidence'][248:263]};self.assertEqual(len(rows),15)
        self.assertEqual(rows['triton-biggs-1996-first-orbit-west-east-major']['value'],350)
        self.assertEqual(rows['triton-biggs-1996-first-orbit-north-south-minor']['value'],200)
        self.assertEqual(rows['triton-biggs-1996-march-orbital-radii']['range_value'],[40,60])
        bound=rows['triton-biggs-1996-april-orbital-radius-bound'];self.assertIsNone(bound['value'])
        self.assertEqual(bound['upper_bound'],20);self.assertTrue(bound['upper_bound_exclusive'])
        for level,diameter,area,june in [(0.7,300,67000,290),(0.6,350,87000,310)]:
            self.assertEqual(rows[f'poseidon-meunier-2018-{level}-major-axis-diameter']['value'],diameter)
            a=rows[f'poseidon-meunier-2018-{level}-area'];self.assertEqual((a['value'],a['unit']),(area,'km2'))
            self.assertEqual(rows[f'poseidon-meunier-2018-{level}-june-diameter']['value'],june)
            self.assertIn(str(level)+' m',a['definition']);self.assertIn('2015-11-26',a['qualification'])
        sample=rows['quantum-ii-dwde-2020-rafOS-span']
        self.assertEqual(sample['value'],304);self.assertEqual(sample['entity_id'],'eddy:horizon:loop-66-secondary')
        self.assertFalse(sample['independent_named_case']['primary_values_inherited'])
        self.assertFalse(sample['independent_named_case']['association_is_verified'])
        self.assertEqual(rows['poseidon-meunier-2018-glider-span']['value'],102)
        self.assertEqual(d['counts']['secondary_entries_with_own_references'],1)
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:csvrows=list(csv.DictReader(stream))
        exported=next(r for r in csvrows if r['id']==sample['id'])
        self.assertEqual(json.loads(exported['independent_named_case_json']),sample['independent_named_case'])
        for r in rows.values():
            self.assertFalse(r['whole_lifetime_inferred']);self.assertIsNone(r['geometry'])


    def test_graph_estimates_keep_child_scope_native_radius_and_reading_precision(self):
        d=register.build();batch=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v8.json').read_bytes())
        prior=hashlib.sha256(json.dumps(d['evidence'][:263],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
        self.assertEqual(prior,batch['baseline_evidence_sha256'])
        rows=d['evidence'][263:270];self.assertEqual(len(rows),7)
        self.assertEqual([r['range_value'] for r in rows],[[40,80],[30,70],[30,130],[40,130],[50,80],[40,100],[100,220]])
        self.assertEqual(len({r['entity_id'] for r in rows}),4)
        self.assertEqual([r['source_plot_estimate']['trace_color'] for r in rows],['blue','red','green','blue','red','black','black'])
        for r in rows:
            self.assertEqual(r['unit'],'km');self.assertIsNone(r['value']);self.assertIsNone(r['uncertainty'])
            self.assertIn('not an area-equivalent',r['definition']);self.assertIn('not a seasonal envelope',r['qualification'])
            self.assertFalse(r['seasonal_playback_eligible']);self.assertFalse(r['rank_eligible']);self.assertIsNone(r['geometry'])
            plot=r['source_plot_estimate'];self.assertEqual((plot['source_raster']['width'],plot['source_raster']['height']),(1430,657))
            self.assertEqual(len(plot['source_raster']['sha256']),64)
        self.assertIn('remerged child',rows[2]['case_label']);self.assertIn('not pooled',rows[2]['qualification'])
        self.assertEqual(rows[5]['entity_id'],'eddy:horizon:loop-66-secondary')
        self.assertFalse(rows[5]['independent_named_case']['primary_values_inherited'])
        self.assertIn('sampling endpoint',rows[5]['qualification'])
        self.assertLess(rows[6]['source_plot_estimate']['approximate_plot_day_support'][1]+2,51)
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:exports=list(csv.DictReader(stream))[263:270]
        self.assertEqual([json.loads(r['source_plot_estimate_json']) for r in exports],[r['source_plot_estimate'] for r in rows])


    def test_black_sea_model_table_keeps_depth_velocity_and_event_scopes(self):
        d=register.build();batch=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v9.json').read_bytes())
        prior=hashlib.sha256(json.dumps(d['evidence'][:270],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
        self.assertEqual(prior,batch['baseline_evidence_sha256'])
        rows=d['evidence'][270:285];self.assertEqual(len(rows),15)
        depths=[r for r in rows if r['category']=='structure'];speeds=[r for r in rows if r['category']=='kinematics']
        self.assertEqual([r['value'] for r in depths],[400,130,200,350,100,400])
        self.assertEqual([r['range_value'] for r in speeds],[[.1,.2],[.1,.25],[.15,.35],[.1,.4],[.1,.15],[.1,.18]])
        for r in rows:
            self.assertEqual(r['evidence_role'],'published_model_case_reference')
            self.assertFalse(r['whole_lifetime_inferred']);self.assertIsNone(r['geometry']);self.assertIsNone(r['uncertainty'])
        for r in depths:
            self.assertEqual((r['unit'],r['period_start'],r['period_end']),('m','2000-06-10','2000-06-10'))
            self.assertIn('not lens thickness',r['qualification'])
            self.assertEqual(r['model_context']['penetration_day_as_reported'],40)
        for r in speeds:
            self.assertEqual(r['unit'],'m/s');self.assertIsNone(r['value']);self.assertIsNone(r['period_start'])
            self.assertFalse(r['model_context']['surface_map_depth_is_velocity_column_depth'])
        events=[r for r in rows if r['category']=='duration']
        self.assertEqual([r['value'] for r in events],[6,3,17]);self.assertEqual(len({r['case_label'] for r in events}),3)
        self.assertTrue(all(r['period_start'] is None and r['unit']=='day' for r in events))
        self.assertIn('open return-flow',depths[-1]['qualification'])
        self.assertEqual([r['source_name'] for r in batch['unmapped_named_source_rows']],['Sakarya','Sinop','Kizilirmak'])
        self.assertTrue(all(not r['measurement_assigned_to_another_name'] for r in batch['unmapped_named_source_rows']))
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:exports=list(csv.DictReader(stream))[270:285]
        self.assertEqual([json.loads(r['model_context_json']) for r in exports],[r['model_context'] for r in rows])
        self.assertEqual(d['counts']['duration_owners'],99);self.assertEqual(d['counts']['kinematics_owners'],70)


    def test_latakia_opposite_rotation_cases_keep_distinct_map_support(self):
        d=register.build();batch=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v10.json').read_bytes())
        prior=hashlib.sha256(json.dumps(d['evidence'][:285],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
        self.assertEqual(prior,batch['baseline_evidence_sha256'])
        rows=d['evidence'][285:289];self.assertEqual(len(rows),4)
        self.assertEqual([r['value'] for r in rows],[50,None,100,None])
        self.assertEqual(rows[1]['lower_bound'],30);self.assertTrue(rows[1]['lower_bound_exclusive'])
        self.assertEqual(rows[3]['range_value'],[15,30]);self.assertIsNone(rows[3]['lower_bound'])
        self.assertTrue(all('spring 2010 cyclonic' in r['case_label'] and (r['period_start'],r['period_end'])==('2010-05-13','2010-06-09') for r in rows[:2]))
        self.assertTrue(all('summer 2010 anticyclonic' in r['case_label'] and (r['period_start'],r['period_end'])==('2010-07-08','2010-08-04') for r in rows[2:]))
        for r in rows:
            self.assertEqual(r['entity_id'],'eddy:geography:latakia-eddy-region')
            self.assertEqual(r['evidence_role'],'qualified_indexed_reference')
            self.assertIn('not a seasonal envelope',r['qualification'])
            self.assertFalse(r['whole_lifetime_inferred']);self.assertFalse(r['seasonal_playback_eligible']);self.assertIsNone(r['geometry'])
            self.assertIsNone(r['uncertainty']);self.assertIn('HTTP 403',r['source_access'])
        entry=next(r for r in d['records'] if r['entity_id']==rows[0]['entity_id'])
        self.assertFalse(entry['size_gap']);self.assertIsNone(entry['whole_lifetime_days'])
        self.assertEqual(sum(r['size_gap'] for r in d['records']),63)


    def test_loop_narrative_diameters_do_not_become_child_or_seasonal_sizes(self):
        d=register.build();batch=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v11.json').read_bytes())
        prior=hashlib.sha256(json.dumps(d['evidence'][:289],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
        self.assertEqual(prior,batch['baseline_evidence_sha256'])
        rows=d['evidence'][289:292];self.assertEqual(len(rows),3)
        self.assertEqual([r['value'] for r in rows],[400,247,175])
        self.assertEqual([r['entity_id'] for r in rows],['eddy:horizon:loop-59-primary','eddy:horizon:loop-59-primary','eddy:horizon:loop-58-primary'])
        for r in rows:
            self.assertEqual(r['unit'],'km');self.assertIsNone(r['period_start']);self.assertIsNone(r.get('range_value'))
            self.assertIsNone(r['uncertainty']);self.assertIsNone(r['geometry']);self.assertFalse(r['seasonal_playback_eligible'])
            self.assertFalse(r['rights_screened_release_eligible']);self.assertFalse(r['whole_lifetime_inferred'])
            self.assertIn('does not specify',r['definition']);self.assertIn('physical identity crosswalk',r['qualification'])
        self.assertIn('before split',rows[0]['case_label']);self.assertIn('August 2012',rows[1]['case_label'])
        self.assertTrue(all('No value assigned to Jumbo Jr.' in r['qualification'] for r in rows[:2]))
        self.assertIn('sampling date unspecified',rows[2]['period_label'])
        self.assertIn('not independently verified',rows[2]['qualification'])


    def test_black_sea_bathymetry_cases_preserve_origin_and_model_phases(self):
        d=register.build();batch=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v12.json').read_bytes())
        prior=hashlib.sha256(json.dumps(d['evidence'][:292],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
        self.assertEqual(prior,batch['baseline_evidence_sha256'])
        rows=d['evidence'][292:299];self.assertEqual(len(rows),7)
        self.assertEqual([r['value'] for r in rows],[100,300,None,None,60,400,None])
        self.assertEqual([r['range_value'] for r in rows if r['category']=='kinematics'],[[30,35],[15,20],[15,20]])
        for r in rows:
            self.assertEqual(r['evidence_role'],'published_model_case_reference')
            self.assertIsNone(r['period_start']);self.assertIsNone(r['period_end']);self.assertIsNone(r['uncertainty'])
            c=r['model_context'];self.assertEqual((c['experiment'],c['horizontal_grid_km'],c['vertical_levels']),(2,1.6,27))
            self.assertFalse(c['model_year_is_dated_observation']);self.assertFalse(c['physical_crosswalk_verified'])
            self.assertIn('absent from experiment 1',r['qualification']);self.assertIn('not thickness',r['qualification'])
            self.assertFalse(r['physical_state_join_eligible']);self.assertFalse(r['seasonal_playback_eligible']);self.assertIsNone(r['geometry'])
        for r in rows[4:]:
            self.assertEqual(r['entity_id'],'eddy:geography:kerch-eddy-region')
            self.assertIn('regional-origin case candidate',r['qualification']);self.assertIn('Cape Sarych',r['qualification'])
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:exports=list(csv.DictReader(stream))[292:299]
        self.assertEqual([json.loads(r['model_context_json']) for r in exports],[r['model_context'] for r in rows])


    def test_qualitative_classes_preserve_source_rows_without_closing_numeric_gaps(self):
        d=register.build();batch=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v13.json').read_bytes())
        self.assertEqual(hashlib.sha256(json.dumps(d['evidence'][:299],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),batch['baseline_evidence_sha256'])
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:
            reader=csv.DictReader(stream);fields=[k for k in reader.fieldnames if k not in ['detection_context_json','source_map_estimate_json']];prior_rows=list(reader)[:299]
        prior_csv=io.StringIO(newline='');writer=csv.DictWriter(prior_csv,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(prior_rows)
        self.assertEqual(hashlib.sha256(prior_csv.getvalue().encode()).hexdigest(),batch['baseline_measurement_csv_sha256'])
        self.assertEqual(len(d['evidence']),321)
        self.assertEqual(d['size_classification_counts'],{'records':15,'owners':15,'owners_with_numeric_size_gap':9,'labels':{'Huge':6,'Medium':2,'Small':7}})
        self.assertEqual((d['counts']['size_owners'],d['counts']['identities_with_measurements'],d['counts']['identities_without_measurements']),(73,120,16))
        self.assertEqual(sum(r['size_gap'] for r in d['records']),63)
        classes=d['size_classifications'];self.assertEqual(len(classes),15)
        self.assertEqual([(r['source_name'],r['label']) for r in classes],[('Titantic','Huge'),('Sargassum','Huge'),('Rebel','Small'),('QE-2','Small'),('Quick','Huge'),('Pelagic','Huge'),('Odessa','Medium'),('Nansen','Medium'),('Millenium','Huge'),('Lazy','Small'),('Kinetic','Small'),('Juggernaut','Huge'),('Indigo','Small'),('Haskell','Small'),('Gyre','Small')])
        for r in classes:
            source=json.loads((register.ROOT/r['source_file']).read_bytes())
            self.assertEqual(register.pointer(source,r['source_pointer']),r['raw_record'])
            self.assertEqual(hashlib.sha256((register.ROOT/r['source_file']).read_bytes()).hexdigest(),r['source_sha256'])
            self.assertTrue(all(r[k] is None for k in ['numeric_thresholds','value','unit']))
            self.assertTrue(all(r[k] is False for k in ['association_is_verified','source_year_is_separation_year','rank_eligible','seasonal_playback_eligible','physical_state_join_eligible','rights_screened_release_eligible']))
        qe=next(r for r in d['records'] if r['entity_id']=='eddy:horizon:loop-40-secondary')
        self.assertFalse(qe['evidence_ids']);self.assertTrue(qe['size_gap']);self.assertEqual(qe['size_classification_ids'],[classes[3]['id']])
        self.assertEqual((classes[3]['registry_primary_name'],classes[3]['registry_name']),('Quick','QE-2'));self.assertEqual(classes[3]['label'],'Small');self.assertEqual(classes[4]['label'],'Huge')
        self.assertEqual(classes[0]['registry_name'],'Titanic');self.assertEqual(classes[8]['registry_name'],'Millennium')
        self.assertEqual(classes[-1]['source_year'],1999);self.assertEqual(classes[-1]['registry_primary_initial_separation'],'1998-05-11')
        with (register.ROOT/'research/eddy-size-classifications-v1.csv').open(encoding='utf8',newline='') as stream:exports=list(csv.DictReader(stream))
        self.assertEqual(len(exports),15);self.assertEqual([r['label'] for r in exports],[r['label'] for r in classes])
        self.assertTrue(all(r['value']==r['unit']==r['numeric_thresholds']=='' for r in exports))


    def test_kenai_detection_area_levels_signed_component_and_calendar_track_support(self):
        d=register.build();batch=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v14.json').read_bytes())
        self.assertEqual(hashlib.sha256(json.dumps(d['evidence'][:299],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),batch['baseline_evidence_sha256'])
        rows=d['evidence'][299:305];self.assertEqual(len(rows),6)
        self.assertEqual([r['value'] for r in rows[:3]],[15000,10000,6000])
        self.assertTrue(all(r['unit']=='km2' and r['category']=='size' for r in rows[:3]))
        self.assertEqual(rows[3]['value'],1.8);self.assertEqual(rows[4]['range_value'],[-.8,5.0])
        self.assertIn('negative eastward',rows[4]['definition']);self.assertIn('Not swirl speed',rows[3]['definition'])
        self.assertEqual(rows[5]['range_value'],[1278,1338]);self.assertEqual(rows[5]['calendar_support']['start_precision'],'month')
        self.assertIn('post-split main branch',rows[5]['period_label'])
        for r in rows:
            self.assertEqual(r['entity_id'],'eddy:geography:kenai-eddy-region')
            self.assertIsNone(r['period_start']);self.assertIsNone(r['period_end']);self.assertIsNone(r['uncertainty'])
            self.assertEqual(r['detection_context']['okubo_weiss_threshold_s_minus2'],-2e-12)
            self.assertEqual(r['detection_context']['cadence_days'],7)
            self.assertFalse(r['whole_lifetime_inferred']);self.assertFalse(r['physical_state_join_eligible']);self.assertFalse(r['seasonal_playback_eligible'])
            self.assertIn('no child values inherited',r['qualification'])
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:exports=list(csv.DictReader(stream))[299:305]
        self.assertEqual([json.loads(r['detection_context_json']) for r in exports],[r['detection_context'] for r in rows])
        self.assertEqual(json.loads(exports[4]['range_value_json']),[-.8,5.0])

    def test_negative_intervals_require_explicit_motion_component_contract(self):
        import copy
        row={'metric':'source_reported_signed_westward_translation_component_range','range_kind':'source_reported_signed_westward_translation_component_interval','category':'kinematics','unit':'km/day','value':None,'range_value':[-.8,5.0],'detection_context':{'translation_component_positive_direction':'westward'}}
        register.validate_numeric_interval(row)
        for key,value in [('category','size'),('unit','km2'),('value',1.8),('metric','radius'),('range_value',[float('nan'),5]),('range_value',[-.8,float('inf')]),('range_value',[5,-.8])]:
            wrong=copy.deepcopy(row);wrong[key]=value
            with self.assertRaises(AssertionError):register.validate_numeric_interval(wrong)
        wrong=copy.deepcopy(row);wrong['detection_context']['translation_component_positive_direction']='eastward'
        with self.assertRaises(AssertionError):register.validate_numeric_interval(wrong)
        ordinary={'metric':'reported_diameter','category':'size','unit':'km','value':None,'range_value':[-.8,5]}
        with self.assertRaises(AssertionError):register.validate_numeric_interval(ordinary)


    def test_map_spans_are_snapshot_reading_estimates_with_source_pixel_verification(self):
        import eddy_map_spans_v1 as maps
        d=register.build();batch=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v15.json').read_bytes())
        self.assertEqual(hashlib.sha256(json.dumps(d['evidence'][:305],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),batch['baseline_evidence_sha256'])
        rows=d['evidence'][305:309];self.assertEqual(len(rows),4)
        self.assertEqual([r['range_value'] for r in rows],[[300,475],[400,550],[325,500],[325,500]])
        self.assertEqual([r['entity_id'] for r in rows],['eddy:horizon:loop-68-primary']*2+['eddy:horizon:loop-69-primary']*2)
        for r in rows:
            m=r['source_map_estimate'];maps.validate_map_case(m['case'])
            self.assertEqual(r['range_value'],maps.span_interval(m['case'],m['component'])['range_km'])
            self.assertEqual(r['period_start'],r['period_end']);self.assertEqual(r['period_start'],m['case']['date'])
            self.assertEqual(r['evidence_role'],'map_read_named_case_reference');self.assertEqual(r['unit'],'km')
            self.assertIn('Not eddy diameter',r['definition']);self.assertIn('not instrument error',r['qualification'])
            self.assertFalse(r['rights_screened_release_eligible']);self.assertIsNone(r['uncertainty']);self.assertIsNone(r['geometry'])
            self.assertFalse(r['physical_state_join_eligible']);self.assertFalse(r['seasonal_playback_eligible'])
        proof=json.loads((register.ROOT/'research/eddy-map-span-source-verification-v1.json').read_bytes())
        self.assertEqual(proof['status'],'PASS');self.assertTrue(proof['source_pixels_verified']);self.assertTrue(proof['duplicate_figure_images_verified'])
        self.assertEqual(proof['verifier_sha256'],hashlib.sha256((register.ROOT/'analysis/eddy_map_spans_v1.py').read_bytes()).hexdigest())
        self.assertEqual(d['method_implementation_sha256']['analysis/eddy_map_spans_v1.py'],proof['verifier_sha256'])
        self.assertEqual(proof['batch_sha256'],hashlib.sha256((register.ROOT/'research/eddy-measurement-register-additions-v15.json').read_bytes()).hexdigest())
        self.assertEqual([r['selected_pixels'] for r in proof['records']],[722,551])
        self.assertEqual(batch['excluded_duplicate_figure_images']['figures'],[9,10])
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:
            reader=csv.DictReader(stream);fields=[k for k in reader.fieldnames if k!='source_map_estimate_json'];exports=list(reader)
        old_csv=io.StringIO(newline='');writer=csv.DictWriter(old_csv,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(exports[:305])
        self.assertEqual(hashlib.sha256(old_csv.getvalue().encode()).hexdigest(),batch['baseline_measurement_csv_sha256'])
        self.assertEqual([json.loads(r['source_map_estimate_json']) for r in exports[305:309]],[r['source_map_estimate'] for r in rows])

    def test_map_outline_reader_rejects_open_or_clipped_curves(self):
        from eddy_map_spans_v1 import outline_readout
        samples=bytearray([10,20,30]*10000)
        for x,y in {(x,y) for x in range(10,91) for y in [10,90]}|{(x,y) for x in [10,90] for y in range(10,91)}:
            p=(y*100+x)*3;samples[p:p+3]=bytes([255,255,255])
        valid=outline_readout(bytes(samples),100,100,[0,0,99,99]);self.assertEqual(valid['bbox_xyxy'],[10,10,90,90])
        with self.assertRaises(AssertionError):outline_readout(bytes(samples),100,100,[10,0,99,99])
        p=(10*100+50)*3;samples[p:p+3]=bytes([10,20,30])
        with self.assertRaises(AssertionError):outline_readout(bytes(samples),100,100,[0,0,99,99])


    def test_caucasian_named_model_core_is_not_outer_diameter_or_lifetime(self):
        d=register.build();batch=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v16.json').read_bytes())
        self.assertEqual(hashlib.sha256(json.dumps(d['evidence'][:309],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),batch['baseline_evidence_sha256'])
        rows=d['evidence'][309:312];self.assertEqual([r['value'] for r in rows],[30,12,2.3])
        self.assertEqual([r['category'] for r in rows],['size','kinematics','kinematics'])
        self.assertEqual([r['unit'] for r in rows],['km','day','km/day'])
        for r in rows:
            self.assertEqual(r['entity_id'],'eddy:geography:caucasus-eddy-region')
            self.assertEqual(r['evidence_role'],'published_model_case_reference')
            self.assertFalse(r['model_context']['physical_crosswalk_verified'])
            self.assertIn('not outer radius or diameter',r['qualification'])
            self.assertIn('HTTP 429',r['source_access'])
            self.assertIsNone(r['period_start']);self.assertIsNone(r['period_end'])
            self.assertIsNone(r['uncertainty']);self.assertIsNone(r['geometry'])
            self.assertFalse(r['whole_lifetime_inferred']);self.assertFalse(r['seasonal_playback_eligible'])
            self.assertFalse(r['physical_state_join_eligible']);self.assertFalse(r['rank_eligible'])
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:
            reader=csv.DictReader(stream);fields=reader.fieldnames;exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields);writer.writeheader();writer.writerows(exports[:309])
        self.assertEqual(hashlib.sha256(prior.getvalue().encode()).hexdigest(),batch['baseline_measurement_csv_sha256'])
        entry=next(r for r in d['records'] if r['entity_id']==rows[0]['entity_id'])
        self.assertFalse(entry['size_gap']);self.assertIsNone(entry['whole_lifetime_days'])

    def test_crimean_image_diameter_keeps_date_and_merger_qualification(self):
        d=register.build();batch=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v17.json').read_bytes())
        self.assertEqual(hashlib.sha256(json.dumps(d['evidence'][:312],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),batch['baseline_evidence_sha256'])
        rows=d['evidence'][312:313];self.assertEqual(len(rows),1);r=rows[0]
        self.assertEqual((r['value'],r['unit'],r['category']),(100,'km','size'))
        self.assertEqual(r['entity_id'],'eddy:geography:crimea-eddy-region')
        self.assertEqual((r['period_start'],r['period_end']),('1997-10-30','1997-10-30'))
        self.assertEqual(r['evidence_role'],'qualified_indexed_reference')
        self.assertIn('source hypothesis',r['qualification']);self.assertIn('HTTP 403',r['source_access'])
        self.assertIsNone(r['uncertainty']);self.assertIsNone(r['geometry'])
        self.assertFalse(r['physical_state_join_eligible']);self.assertFalse(r['seasonal_playback_eligible']);self.assertFalse(r['whole_lifetime_inferred'])
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:
            reader=csv.DictReader(stream);fields=reader.fieldnames;exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields);writer.writeheader();writer.writerows(exports[:312])
        self.assertEqual(hashlib.sha256(prior.getvalue().encode()).hexdigest(),batch['baseline_measurement_csv_sha256'])
        entry=next(e for e in d['records'] if e['entity_id']==r['entity_id'])
        self.assertFalse(entry['size_gap']);self.assertIsNone(entry['whole_lifetime_days'])

    def test_ursa_editorial_spans_preserve_source_paths_and_no_physical_admission(self):
        from eddy_audit_spans_v1 import AUDIT,validate_case,spans
        d=register.build();batch=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v18.json').read_bytes())
        self.assertEqual(hashlib.sha256(json.dumps(d['evidence'][:313],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),batch['baseline_evidence_sha256'])
        rows=d['evidence'][313:315];self.assertEqual(len(rows),2)
        self.assertEqual([r['range_value'] for r in rows],[[300,375],[250,325]])
        audit=json.loads((register.ROOT/AUDIT).read_bytes());case=batch['audit_span_cases'][0]
        validate_case(case,audit,hashlib.sha256((register.ROOT/AUDIT).read_bytes()).hexdigest())
        report=json.loads((register.ROOT/batch['source_pixel_report']).read_bytes())
        self.assertEqual(report['status'],'PASS');self.assertTrue(report['source_pixels_verified'])
        self.assertEqual(len(report['source_paths_reproduced']),6)
        self.assertEqual(sum(p['admitted_to_span'] for p in report['source_paths_reproduced']),4)
        self.assertFalse(report['physical_boundary_admitted'])
        self.assertEqual(report['verifier_sha256'],d['method_implementation_sha256']['analysis/eddy_audit_spans_v1.py'])
        for r in rows:
            self.assertEqual(r['entity_id'],'eddy:published:ursa-2021');self.assertEqual(r['category'],'size')
            self.assertEqual(r['period_start'],r['period_end']);self.assertEqual(r['period_start'],'2021-03-07')
            m=r['source_map_estimate'];self.assertEqual(m['calculation'],spans(case,m['component']))
            self.assertEqual(m['calculation']['accepted_scenarios'],68)
            self.assertIn('unresolved unit',r['qualification']);self.assertIn('attribution remains pending',r['scope'])
            self.assertIsNone(r['geometry']);self.assertIsNone(r['uncertainty'])
            self.assertFalse(r['physical_state_join_eligible']);self.assertFalse(r['seasonal_playback_eligible']);self.assertFalse(r['whole_lifetime_inferred']);self.assertFalse(r['rank_eligible'])
            self.assertFalse(r['rights_screened_release_eligible'])
        primary=next(r for r in d['records'] if r['entity_id']=='eddy:horizon:loop-70-primary')
        self.assertTrue(primary['size_gap'])
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:
            reader=csv.DictReader(stream);fields=reader.fieldnames;exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields);writer.writeheader();writer.writerows(exports[:313])
        self.assertEqual(hashlib.sha256(prior.getvalue().encode()).hexdigest(),batch['baseline_measurement_csv_sha256'])
        self.assertEqual([json.loads(e['source_map_estimate_json']) for e in exports[313:315]],[r['source_map_estimate'] for r in rows])

    def test_ursa_span_case_rejects_promotions_changed_owners_and_reading_rules(self):
        import copy
        from eddy_audit_spans_v1 import AUDIT,validate_case,spans
        raw=(register.ROOT/AUDIT).read_bytes();audit=json.loads(raw);pin=hashlib.sha256(raw).hexdigest()
        batch=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v18.json').read_bytes());case=batch['audit_span_cases'][0]
        for key,value in [('association_is_verified',True),('physical_state_join_eligible',True),('date','2021-03-12'),('owner_id','eddy:horizon:loop-70-primary'),('reading_allowance_pixels',0),('round_outward_km',1)]:
            wrong=copy.deepcopy(case);wrong[key]=value
            with self.assertRaises(AssertionError):validate_case(wrong,audit,pin)
        for key,value in [('physical_boundary_admitted',True),('closed_pixel_loop_verified',False),('observation_date','2021-03-12')]:
            wrong=copy.deepcopy(audit);wrong[key]=value
            with self.assertRaises(AssertionError):validate_case(case,wrong,pin)
        with self.assertRaises(AssertionError):spans(case,'diameter')
        wrong=copy.deepcopy(case);wrong['outline_cases'][0]['bbox_xyxy'][0]=wrong['roi_xyxy'][0]
        with self.assertRaises(AssertionError):spans(wrong,'east_west')

    def test_lilian_source_colour_patch_keeps_unresolved_level_unit_and_source_custody(self):
        from eddy_colour_spans_v1 import validate_case,spans
        d=register.build();batch=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v19.json').read_bytes())
        self.assertEqual(hashlib.sha256(json.dumps(d['evidence'][:315],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),batch['baseline_evidence_sha256'])
        case=batch['colour_span_cases'][0];validate_case(case)
        report=json.loads((register.ROOT/batch['source_pixel_report']).read_bytes())
        self.assertEqual(report['status'],'PASS');self.assertTrue(report['source_pixels_verified']);self.assertTrue(report['source_palette_verified'])
        self.assertEqual(report['batch_sha256'],hashlib.sha256((register.ROOT/'research/eddy-measurement-register-additions-v19.json').read_bytes()).hexdigest())
        self.assertEqual(report['verifier_sha256'],d['method_implementation_sha256']['analysis/eddy_colour_spans_v1.py'])
        self.assertEqual(report['span_math_sha256'],d['method_implementation_sha256']['analysis/eddy_map_spans_v1.py'])
        self.assertEqual(case['source_level'],10);self.assertIsNone(case['source_level_unit']);self.assertIsNone(case['physical_level_m'])
        self.assertFalse(case['full_ring_boundary_admitted']);self.assertEqual(len(case['palette']),31)
        self.assertEqual(report['patches'],case['patch_cases'])
        rows=d['evidence'][315:317];self.assertEqual(len(rows),2)
        self.assertEqual([r['range_value'] for r in rows],[[100,225],[75,150]])
        for r in rows:
            self.assertEqual(r['entity_id'],'eddy:geography:lilian-2006');self.assertEqual(r['source_file'],'research/eddy-measurement-register-additions-v19.json')
            self.assertEqual((r['period_start'],r['period_end']),('2006-07-05','2006-07-05'))
            self.assertIn('OSW diagnostic choice',r['qualification']);self.assertIn('not the authors ring-edge',r['scope'])
            self.assertEqual(r['source_map_estimate']['calculation'],spans(case,r['source_map_estimate']['component']))
            self.assertIsNone(r['geometry']);self.assertIsNone(r['uncertainty']);self.assertFalse(r['rank_eligible'])
            self.assertFalse(r['physical_state_join_eligible']);self.assertFalse(r['seasonal_playback_eligible']);self.assertFalse(r['whole_lifetime_inferred']);self.assertFalse(r['rights_screened_release_eligible'])
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:
            reader=csv.DictReader(stream);fields=reader.fieldnames;exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields);writer.writeheader();writer.writerows(exports[:315])
        self.assertEqual(hashlib.sha256(prior.getvalue().encode()).hexdigest(),batch['baseline_measurement_csv_sha256'])
        self.assertEqual([json.loads(r['source_map_estimate_json']) for r in exports[315:317]],[r['source_map_estimate'] for r in rows])

    def test_colour_patch_reader_rejects_clipping_and_ambiguous_components_without_hole_repair(self):
        from eddy_colour_spans_v1 import patch_readout,validate_case
        import copy
        palette=[{'level_lower_edge':0,'rgb_median':[255,255,255]},{'level_lower_edge':10,'rgb_median':[220,20,40]}]
        def raster(rectangles,hole=False):
            raw=bytearray([255,255,255]*10000)
            for x0,y0,x1,y1 in rectangles:
                for y in range(y0,y1):
                    for x in range(x0,x1):raw[(y*100+x)*3:(y*100+x)*3+3]=bytes([220,20,40])
            if hole:
                for y in [30,31]:
                    for x in [30,31]:raw[(y*100+x)*3:(y*100+x)*3+3]=bytes([255,255,255])
            return bytes(raw)
        result=patch_readout(raster([(20,20,60,60)],True),100,100,[0,0,99,99],palette,10)
        self.assertEqual(result['selected_pixels'],1596);self.assertEqual(result['bbox_xyxy'],[20,20,59,59])
        with self.assertRaises(AssertionError):patch_readout(raster([(0,20,40,60)]),100,100,[0,0,99,99],palette,10)
        with self.assertRaises(AssertionError):patch_readout(raster([(10,20,32,70),(60,20,82,70)]),100,100,[0,0,99,99],palette,10)
        batch=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v19.json').read_bytes());case=batch['colour_span_cases'][0]
        for key,value in [('source_level_unit','cm'),('physical_level_m',0.1),('full_ring_boundary_admitted',True),('date','2006-06-07'),('source_level',9),('physical_state_join_eligible',True)]:
            wrong=copy.deepcopy(case);wrong[key]=value
            with self.assertRaises(AssertionError):validate_case(wrong)

    def test_arrow_spans_keep_visible_extrema_and_excluded_chart_status(self):
        from eddy_arrow_spans_v1 import validate_case
        d=register.build();batch=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v20.json').read_bytes())
        self.assertEqual(hashlib.sha256(json.dumps(d['evidence'][:317],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),batch['baseline_evidence_sha256'])
        report=json.loads((register.ROOT/batch['source_pixel_report']).read_bytes())
        self.assertEqual(report['status'],'PASS');self.assertTrue(report['source_pixels_verified']);self.assertTrue(report['no_gap_repair'])
        self.assertFalse(report['physical_footprint_admitted'])
        self.assertEqual(report['batch_sha256'],hashlib.sha256((register.ROOT/'research/eddy-measurement-register-additions-v20.json').read_bytes()).hexdigest())
        self.assertEqual(report['verifier_sha256'],d['method_implementation_sha256']['analysis/eddy_arrow_spans_v1.py'])
        self.assertEqual(report['span_math_sha256'],d['method_implementation_sha256']['analysis/eddy_map_spans_v1.py'])
        self.assertTrue(all(p['closed_outline_gate_rejected'] for p in report['records']))
        for case in batch['arrow_span_cases']:
            validate_case(case);self.assertEqual(case['axis_reference_raster']['y_offset_pixels'],527)
            self.assertFalse(case['closed_contour_extraction_admitted']);self.assertFalse(case['footprint_admitted'])
            self.assertTrue(case['chart_contains_confidential_stamp']);self.assertIsNone(case['source_contour_level'])
        rows=d['evidence'][317:];self.assertEqual(len(rows),4)
        self.assertEqual([r['range_value'] for r in rows],[[125,200],[175,225],[375,425],[300,350]])
        self.assertEqual([r['entity_id'] for r in rows],['eddy:horizon:loop-61-primary']*2+['eddy:horizon:loop-62-primary']*2)
        for r in rows:
            self.assertEqual(r['source_file'],'research/eddy-measurement-register-additions-v20.json')
            self.assertEqual((r['period_start'],r['period_end']),('2015-01-22','2015-01-22'))
            self.assertIn('no gap closing',r['qualification']);self.assertIn('not an extracted closed contour',r['scope'])
            self.assertFalse(r['rights_screened_release_eligible']);self.assertFalse(r['physical_state_join_eligible']);self.assertFalse(r['seasonal_playback_eligible']);self.assertFalse(r['rank_eligible'])
            self.assertIsNone(r['geometry']);self.assertIsNone(r['uncertainty'])
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:
            reader=csv.DictReader(stream);fields=reader.fieldnames;exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields);writer.writeheader();writer.writerows(exports[:317])
        self.assertEqual(hashlib.sha256(prior.getvalue().encode()).hexdigest(),batch['baseline_measurement_csv_sha256'])
        self.assertEqual([json.loads(r['source_map_estimate_json']) for r in exports[317:]],[r['source_map_estimate'] for r in rows])
        self.assertEqual(len(batch['rejected_source_leads']),2)

    def test_ink_extremum_reader_rejects_empty_or_directionally_clipped_windows(self):
        from eddy_arrow_spans_v1 import read_extremum,validate_case
        import copy
        raw=bytearray([255,255,255]*10000)
        for y in range(20,50):raw[(y*100+30)*3:(y*100+30)*3+3]=bytes([0,0,0])
        found=read_extremum(bytes(raw),100,100,[10,10,60,60],'west')
        self.assertEqual(found['axis_coordinate_pixel'],30);self.assertEqual(found['selected_ink_pixels'],30)
        with self.assertRaises(AssertionError):read_extremum(bytes(raw),100,100,[30,10,60,60],'west')
        with self.assertRaises(AssertionError):read_extremum(bytes(raw),100,100,[40,10,60,60],'west')
        batch=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v20.json').read_bytes());case=batch['arrow_span_cases'][0]
        for key,value in [('closed_contour_extraction_admitted',True),('footprint_admitted',True),('physical_state_join_eligible',True),('rights_screened_release_eligible',True),('source_contour_level',0.17),('association_is_verified',True)]:
            wrong=copy.deepcopy(case);wrong[key]=value
            with self.assertRaises(AssertionError):validate_case(wrong)

if __name__=='__main__':unittest.main()
