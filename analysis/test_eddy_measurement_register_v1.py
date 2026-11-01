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
        self.assertEqual(len(d['evidence']),407)
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
            analysis_rows=[e for e in own if e['metric']=='source_reported_assimilative_analysis_parent_zonal_extent']
            self.assertEqual(len(analysis_rows),1 if name=='thor-2020' else 0)
            for e in analysis_rows:register.validate_profile_context(e)
            self.assertTrue(all(e['metric']=='source_dated_event_stage_interval' or e['evidence_role']=='map_read_editorial_candidate_reference' or (name=='thor-2020' and e in analysis_rows and e['evidence_role']=='published_model_case_reference') for e in own))
        for r in d['records']:
            self.assertFalse(r['candidate_crosswalk_is_verified']);self.assertIsNone(r['whole_lifetime_days'])
            if r['source_collection']=='horizon_loop_current' and r['entity_id'].endswith('-secondary') and r['entity_id'] not in ['eddy:horizon:loop-66-secondary','eddy:horizon:loop-63-secondary']:self.assertFalse(r['evidence_ids'])
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
        self.assertEqual(len(rows),407)
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
        self.assertFalse(any(r['category']=='size' and r['entity_id']=='eddy:geography:laura-1999' for r in d['evidence'][:48]))
        self.assertEqual([r['evidence_role'] for r in d['evidence'] if r['category']=='size' and r['entity_id']=='eddy:geography:laura-1999'],['source_illustration_extent_reference']*2)

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
        self.assertEqual(d['counts']['registry_entries_with_own_references'],82)
        self.assertEqual(d['counts']['identities_with_measurements'],122)
        self.assertEqual(d['counts']['linked_primary_context_entries'],13)
        self.assertEqual(d['counts']['entries_without_numeric_or_primary_context'],1)
        self.assertEqual(sum(r['metric']=='registry_reported_maximum_surface_current' for r in d['evidence']),60)
        self.assertEqual(sum(r['metric']=='registry_separation_to_dissipation_calendar_span' for r in d['evidence']),77)
        kathleen=rows['eddy:horizon:loop-08-primary-registry-calendar-span']
        self.assertEqual(kathleen['range_value'],[214,273]);self.assertEqual(kathleen['calendar_support']['start_precision'],'month')
        rebel=rows['eddy:horizon:loop-41-primary-registry-calendar-span']
        self.assertEqual(rebel['range_value'],[0,2]);self.assertEqual(rebel['calendar_support']['unconditioned_elapsed_day_range'],[-27,2])
        self.assertTrue(rebel['calendar_support']['chronology_conditioned']);self.assertIsNone(rebel['value'])
        for r in d['records']:
            if r['entity_id']=='eddy:horizon:loop-81-primary':
                self.assertFalse(r['evidence_ids']);self.assertFalse(r['registry_context']['active_label_is_current_status'])
            if r['entity_id'].endswith('-secondary'):
                self.assertEqual(len(r['evidence_ids']),2 if r['entity_id']=='eddy:horizon:loop-66-secondary' else 1 if r['entity_id']=='eddy:horizon:loop-63-secondary' else 0);self.assertIsNone(r['registry_context'])
                self.assertTrue(r['linked_primary_context']['evidence_ids'])
        for r in d['evidence']:
            if r['entity_id'].startswith('eddy:horizon:'):
                self.assertTrue(r['entity_id'].endswith('-primary') or r.get('independent_named_case'))
                self.assertFalse(r['rights_screened_release_eligible'])
                self.assertIn(r['evidence_role'],['registry_source_reference','qualified_published_named_case_reference','qualified_indexed_reference','graph_digitized_named_case_reference','map_read_named_case_reference','map_read_circulation_arrow_reference','map_read_native_frontal_line_reference','qualified_osw_gridded_source_case_reference','qualified_indexed_model_case_reference','qualified_author_image_patch_reference'])
                if r['category']=='duration' and r['evidence_role']=='registry_source_reference':self.assertIsNone(r['value']);self.assertEqual(r['calendar_support']['end_precision'],'month')


    def test_published_area_cases_preserve_units_dates_and_unverified_association(self):
        d=register.build();batch=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v5.json').read_bytes())
        prior=hashlib.sha256(json.dumps(d['evidence'][:214],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
        self.assertEqual(prior,batch['baseline_evidence_sha256'])
        rows=d['evidence'][214:241];self.assertEqual(len(rows),27)
        self.assertEqual([r['value'] for r in rows],[24271,43199,37442,19964,24998,21530,35065,57751,92026,45049,44392,22137,48786,21318,22511,67989,23563,12421,18682,49672,12369,31304,7596,25036,52058,70659,15451])
        self.assertEqual(d['counts']['size_owners'],89);self.assertEqual(d['counts']['size_records'],166)
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
        self.assertEqual(d['counts']['structure_owners'],15)


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
        self.assertEqual(d['counts']['secondary_entries_with_own_references'],2)
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
        self.assertEqual(d['counts']['duration_owners'],101);self.assertEqual(d['counts']['kinematics_owners'],73)


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
        self.assertEqual(sum(r['size_gap'] for r in d['records']),47)


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
            reader=csv.DictReader(stream);fields=[k for k in reader.fieldnames if k not in ['detection_context_json','source_map_estimate_json','profile_context_json']];prior_rows=list(reader)[:299]
        prior_csv=io.StringIO(newline='');writer=csv.DictWriter(prior_csv,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(prior_rows)
        self.assertEqual(hashlib.sha256(prior_csv.getvalue().encode()).hexdigest(),batch['baseline_measurement_csv_sha256'])
        self.assertEqual(len(d['evidence']),407)
        self.assertEqual(d['size_classification_counts'],{'records':15,'owners':15,'owners_with_numeric_size_gap':9,'labels':{'Huge':6,'Medium':2,'Small':7}})
        self.assertEqual((d['counts']['size_owners'],d['counts']['identities_with_measurements'],d['counts']['identities_without_measurements']),(89,122,14))
        self.assertEqual(sum(r['size_gap'] for r in d['records']),47)
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
            reader=csv.DictReader(stream);fields=[k for k in reader.fieldnames if k not in ['source_map_estimate_json','profile_context_json']];exports=list(reader)
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
            reader=csv.DictReader(stream);fields=[k for k in reader.fieldnames if k!='profile_context_json'];exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(exports[:309])
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
            reader=csv.DictReader(stream);fields=[k for k in reader.fieldnames if k!='profile_context_json'];exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(exports[:312])
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
            reader=csv.DictReader(stream);fields=[k for k in reader.fieldnames if k!='profile_context_json'];exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(exports[:313])
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
            reader=csv.DictReader(stream);fields=[k for k in reader.fieldnames if k!='profile_context_json'];exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(exports[:315])
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
        rows=d['evidence'][317:321];self.assertEqual(len(rows),4)
        self.assertEqual([r['range_value'] for r in rows],[[125,200],[175,225],[375,425],[300,350]])
        self.assertEqual([r['entity_id'] for r in rows],['eddy:horizon:loop-61-primary']*2+['eddy:horizon:loop-62-primary']*2)
        for r in rows:
            self.assertEqual(r['source_file'],'research/eddy-measurement-register-additions-v20.json')
            self.assertEqual((r['period_start'],r['period_end']),('2015-01-22','2015-01-22'))
            self.assertIn('no gap closing',r['qualification']);self.assertIn('not an extracted closed contour',r['scope'])
            self.assertFalse(r['rights_screened_release_eligible']);self.assertFalse(r['physical_state_join_eligible']);self.assertFalse(r['seasonal_playback_eligible']);self.assertFalse(r['rank_eligible'])
            self.assertIsNone(r['geometry']);self.assertIsNone(r['uncertainty'])
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:
            reader=csv.DictReader(stream);fields=[k for k in reader.fieldnames if k!='profile_context_json'];exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(exports[:317])
        self.assertEqual(hashlib.sha256(prior.getvalue().encode()).hexdigest(),batch['baseline_measurement_csv_sha256'])
        self.assertEqual([json.loads(r['source_map_estimate_json']) for r in exports[317:321]],[r['source_map_estimate'] for r in rows])
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

    def test_lazarus_glider_diagnostics_preserve_phases_units_and_prior_evidence(self):
        d=register.build();batch=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v21.json').read_bytes())
        self.assertEqual(hashlib.sha256(json.dumps(d['evidence'][:321],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),batch['baseline_evidence_sha256'])
        rows=d['evidence'][321:325];self.assertEqual(len(rows),4)
        self.assertEqual([r['category'] for r in rows],['structure','structure','kinematics','structure'])
        self.assertEqual([r['unit'] for r in rows],['m','kJ/cm2','m/s','kJ/cm2'])
        self.assertEqual(rows[0]['value'],30);self.assertEqual(rows[1]['range_value'],[20,30])
        self.assertEqual(rows[2]['value'],1);self.assertEqual(rows[3]['lower_bound'],100);self.assertTrue(rows[3]['lower_bound_exclusive'])
        self.assertEqual(rows[2]['profile_context']['vertical_averaging_interval_m'],[0,1000])
        for r in rows:
            register.validate_profile_context(r)
            self.assertEqual(r['profile_context'],r['raw_record']['profile_context'])
            self.assertFalse(r['rank_eligible']);self.assertFalse(r['physical_state_join_eligible']);self.assertFalse(r['seasonal_playback_eligible']);self.assertFalse(r['whole_lifetime_inferred'])
            self.assertFalse(r['rights_screened_release_eligible']);self.assertIsNone(r['geometry']);self.assertIsNone(r['uncertainty'])
        for r in rows[2:]:self.assertIsNone(r['period_start']);self.assertIsNone(r['period_end'])
        self.assertFalse(batch['excluded_context'][0]['assigned_to_lazarus'])
        self.assertEqual(d['counts']['size_owners'],89);self.assertEqual(d['counts']['structure_owners'],15)
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:
            reader=csv.DictReader(stream);fields=[k for k in reader.fieldnames if k!='profile_context_json'];exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(exports[:321])
        self.assertEqual(hashlib.sha256(prior.getvalue().encode()).hexdigest(),batch['baseline_measurement_csv_sha256'])
        self.assertEqual([json.loads(r['profile_context_json']) for r in exports[321:325]],[r['profile_context'] for r in rows])
        self.assertTrue(all(json.loads(r['profile_context_json']) is None for r in exports[:321]))

    def test_glider_diagnostics_reject_depth_speed_unit_and_date_promotions(self):
        import copy
        rows=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v21.json').read_bytes())['records']
        for index,key,value in [(0,'unit','km'),(1,'unit','kJ'),(2,'metric','registry_reported_maximum_surface_current'),(2,'period_start','2014-10-18'),(3,'lower_bound_exclusive',False)]:
            wrong=copy.deepcopy(rows[index]);wrong[key]=value
            with self.assertRaises(AssertionError):register.validate_profile_context(wrong)
        for index,key,value in [(0,'is_eddy_vertical_extent',True),(1,'eddy_total_heat_inferred',True),(2,'averaging_axis','time'),(2,'vertical_averaging_interval_m',[0,500]),(3,'window_dates_samples',True)]:
            wrong=copy.deepcopy(rows[index]);wrong['profile_context'][key]=value
            with self.assertRaises(AssertionError):register.validate_profile_context(wrong)

    def test_eddy_w_station_separation_preserves_original_coordinates_and_profile_scope(self):
        d=register.build();path='research/eddy-measurement-register-additions-v22.json';batch=json.loads((register.ROOT/path).read_bytes())
        self.assertEqual(hashlib.sha256(json.dumps(d['evidence'][:325],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),batch['baseline_evidence_sha256'])
        rows=d['evidence'][325:327];self.assertEqual(len(rows),2);distance,depth=rows
        register.validate_station_distance(distance)
        self.assertEqual(distance['range_value'],[150,225]);self.assertEqual(distance['calculation']['unrounded_nominal_km'],190.056275)
        self.assertEqual(distance['period_precision'],'month');self.assertIsNone(distance['period_start']);self.assertIsNone(distance['period_end'])
        self.assertEqual((depth['value'],depth['unit']),(60,'m'));self.assertEqual((depth['period_start'],depth['period_end']),('2000-02-22','2000-02-22'))
        self.assertIn('not whole-eddy depth',depth['qualification']);self.assertIn('threshold unspecified',depth['definition'])
        source=batch['sources']['loncaric-2006'];self.assertEqual(source['original']['sha256'],'54da7a54790e5048c4775c5a3761b41513d3541f656a95181486067b9e58eedc')
        self.assertEqual(source['original']['bytes'],1796678);self.assertEqual(source['original']['pages'],10)
        self.assertEqual(set(source['reviewed_page_png_sha256']),{'2','4'});self.assertFalse(source['source_assets_republished'])
        for r in rows:
            self.assertEqual(r['entity_id'],'eddy:geography:agulhas-eddy-w-2000');self.assertEqual(r['source_file'],path)
            self.assertFalse(r['rank_eligible']);self.assertFalse(r['physical_state_join_eligible']);self.assertFalse(r['seasonal_playback_eligible']);self.assertFalse(r['whole_lifetime_inferred']);self.assertFalse(r['rights_screened_release_eligible'])
            self.assertIsNone(r['geometry']);self.assertIsNone(r['uncertainty'])
        self.assertEqual(d['counts']['size_owners'],89);self.assertEqual(sum(r['size_gap'] for r in d['records']),47)
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:
            reader=csv.DictReader(stream);fields=reader.fieldnames;exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields);writer.writeheader();writer.writerows(exports[:325])
        self.assertEqual(hashlib.sha256(prior.getvalue().encode()).hexdigest(),batch['baseline_measurement_csv_sha256'])
        self.assertEqual(json.loads(exports[325]['calculation_json']),distance['calculation'])

    def test_station_distance_sensitivity_covers_rounded_coordinate_cases_and_rejects_promotions(self):
        import copy,itertools,math
        row=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v22.json').read_bytes())['records'][0]
        c=row['calculation'];lo,hi=register.station_distance_interval(c)
        # Independent spherical cosine law checks the display-precision corner scenarios.
        for da,db,dc,dd in itertools.product([-.05,0,.05],repeat=4):
            p,q=map(math.radians,[-29.2+da,-28.8+dc]);dl=math.radians((6.3+dd)-(8.2+db))
            distance=6371*math.acos(math.sin(p)*math.sin(q)+math.cos(p)*math.cos(q)*math.cos(dl))
            self.assertLessEqual(lo,distance);self.assertLessEqual(distance,hi)
        for key,value in [('earth_radius_km',1),('coordinate_allowance_degrees',0),('coordinate_allowance_assumed',False),('round_outward_km',1),('simultaneity_verified',True),('diameter_inferred',True),('whole_eddy_radius_inferred',True),('closed_footprint_inferred',True),('source_accuracy_quantified',True)]:
            wrong=copy.deepcopy(row);wrong['calculation'][key]=value
            with self.assertRaises(AssertionError):register.validate_station_distance(wrong)
        for key,value in [('entity_id','eddy:geography:laura-1999'),('unit','degree'),('metric','author_reported_diameter'),('period_start','2000-02-22')]:
            wrong=copy.deepcopy(row);wrong[key]=value
            with self.assertRaises(AssertionError):register.validate_station_distance(wrong)
        wrong=copy.deepcopy(row);wrong['calculation']['center_station']['latitude']=29.2
        with self.assertRaises(AssertionError):register.validate_station_distance(wrong)

    def test_berek_native_pdf_line_spans_preserve_layer_dates_and_source_custody(self):
        from eddy_pdf_line_spans_v1 import validate_case
        from eddy_map_spans_v1 import span_interval
        d=register.build();path='research/eddy-measurement-register-additions-v23.json';batch=json.loads((register.ROOT/path).read_bytes())
        self.assertEqual(hashlib.sha256(json.dumps(d['evidence'][:327],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),batch['baseline_evidence_sha256'])
        case=batch['pdf_line_cases'][0];validate_case(case);proof=json.loads((register.ROOT/batch['source_native_report']).read_bytes())
        self.assertEqual(proof['status'],'PASS');self.assertTrue(proof['source_native_path_verified']);self.assertTrue(proof['source_axis_labels_verified']);self.assertTrue(proof['explicit_endpoint_closure_verified'])
        self.assertEqual(proof['batch_sha256'],hashlib.sha256((register.ROOT/path).read_bytes()).hexdigest())
        self.assertEqual(proof['verifier_sha256'],d['method_implementation_sha256']['analysis/eddy_pdf_line_spans_v1.py'])
        self.assertEqual(proof['span_math_sha256'],d['method_implementation_sha256']['analysis/eddy_map_spans_v1.py'])
        self.assertFalse(proof['missing_segments_reconstructed']);self.assertFalse(proof['original_assets_republished']);self.assertFalse(proof['physical_footprint_admitted'])
        self.assertEqual(case['background_ssh_date'],'2023-12-21');self.assertIsNone(case['contour_observation_date'])
        self.assertEqual(case['native_path']['segments'],3500);self.assertEqual(case['native_path']['chain_breaks'],0)
        self.assertFalse(case['native_path']['pdf_close_path_flag']);self.assertEqual(len(case['axis_label_boxes']),10)
        rows=d['evidence'][327:329];self.assertEqual(len(rows),2);self.assertEqual([r['range_value'] for r in rows],[[350,400],[300,350]])
        for r in rows:
            self.assertEqual(r['entity_id'],'eddy:horizon:loop-77-primary');self.assertEqual(r['source_file'],path)
            self.assertIsNone(r['period_start']);self.assertIsNone(r['period_end']);self.assertIsNone(r['geometry']);self.assertIsNone(r['uncertainty'])
            self.assertEqual(r['source_map_estimate']['calculation'],span_interval(case,r['source_map_estimate']['component']))
            self.assertFalse(r['rank_eligible']);self.assertFalse(r['physical_state_join_eligible']);self.assertFalse(r['seasonal_playback_eligible']);self.assertFalse(r['whole_lifetime_inferred']);self.assertFalse(r['rights_screened_release_eligible'])
        child=next(r for r in d['records'] if r['entity_id']=='eddy:horizon:loop-77-secondary');self.assertTrue(child['size_gap'])
        self.assertEqual(d['counts']['size_owners'],89);self.assertEqual(sum(r['size_gap'] for r in d['records']),47)
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:
            reader=csv.DictReader(stream);fields=reader.fieldnames;exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields);writer.writeheader();writer.writerows(exports[:327])
        self.assertEqual(hashlib.sha256(prior.getvalue().encode()).hexdigest(),batch['baseline_measurement_csv_sha256'])
        self.assertEqual([json.loads(r['source_map_estimate_json']) for r in exports[327:329]],[r['source_map_estimate'] for r in rows])

    def test_native_pdf_line_case_rejects_date_geometry_identity_and_source_changes(self):
        import copy
        from eddy_pdf_line_spans_v1 import validate_case
        c=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v23.json').read_bytes())['pdf_line_cases'][0]
        for key,value in [('contour_observation_date','2023-12-21'),('background_date_is_contour_date',True),('physical_footprint_admitted',True),('missing_segments_reconstructed',True),('association_is_verified',True),('rights_screened_release_eligible',True),('owner_id','eddy:horizon:loop-77-secondary'),('source_legend_speed_knots',.17),('reading_allowance_pdf_points',0)]:
            wrong=copy.deepcopy(c);wrong[key]=value
            with self.assertRaises(AssertionError):validate_case(wrong)
        for key,value in [('segments',3499),('chain_breaks',1),('explicit_endpoint_closure_verified',False),('points_sha256','0'*64),('stroke_width_pdf_points',4),('drawing_index',216)]:
            wrong=copy.deepcopy(c);wrong['native_path'][key]=value
            with self.assertRaises(AssertionError):validate_case(wrong)
        wrong=copy.deepcopy(c);wrong['outline']['bbox_xyxy'][0]+=1
        with self.assertRaises(AssertionError):validate_case(wrong)
        wrong=copy.deepcopy(c);wrong['axis_label_boxes'][0]['bbox'][0]+=1
        with self.assertRaises(AssertionError):validate_case(wrong)

    def test_fast_field_methods_and_haskell_thermal_maximum_preserve_prior_records(self):
        d=register.build();path='research/eddy-measurement-register-additions-v24.json';batch=json.loads((register.ROOT/path).read_bytes())
        self.assertEqual(hashlib.sha256(json.dumps(d['evidence'][:329],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),batch['baseline_evidence_sha256'])
        rows=d['evidence'][329:336];self.assertEqual(len(rows),7);fast=rows[:6];haskell=rows[6]
        self.assertEqual([r['value'] for r in fast],[280,4.6,130,40,None,None])
        self.assertEqual([r['lower_bound'] for r in fast],[None,None,None,None,180,200])
        self.assertEqual([r['unit'] for r in fast],['km','km/day','km','km','km','km'])
        self.assertEqual([r['category'] for r in fast],['travel','kinematics','size','size','size','size'])
        for r in fast:
            register.validate_fast_alias_reference(r);self.assertEqual(r['case_alias_association'],batch['case_alias_association'])
            self.assertEqual(r['entity_id'],'eddy:horizon:loop-03-primary');self.assertIn('early July 1985',r['scope']);self.assertIn('31 May 1985',r['scope'])
        self.assertIsNone(fast[2]['period_start']);self.assertIsNone(fast[3]['period_start']);self.assertIsNone(fast[3]['period_end'])
        self.assertEqual((fast[4]['period_start'],fast[4]['period_end']),('1985-10-22','1985-10-24'))
        self.assertEqual((fast[5]['period_start'],fast[5]['period_end']),('1985-11-13','1985-11-19'))
        self.assertFalse(fast[4]['lower_bound_exclusive']);self.assertFalse(fast[5]['lower_bound_exclusive'])
        source=batch['sources']['saic-1988'];self.assertEqual(source['original']['sha256'],'a9a225ca12a668ecfdf193a20a74afc36fa37180ddd819cf8977d17626eb2850')
        self.assertEqual(source['original']['bytes'],10631825);self.assertEqual(set(source['reviewed_page_png_sha256']),{'74','114','176'})
        register.validate_profile_context(haskell)
        self.assertEqual((haskell['value'],haskell['unit']),(200,'m'));self.assertEqual(haskell['profile_context']['thermal_reference_celsius'],20)
        self.assertEqual(haskell['profile_context']['aggregation'],'maximum_sampled_isotherm_depth');self.assertEqual(haskell['period_start'],haskell['period_end']);self.assertEqual(haskell['period_start'],'1999-08-03')
        self.assertFalse(batch['sources']['noaa-1999']['source_figure_pixels_reviewed']);self.assertIn('HTTP 403',haskell['source_access'])
        for r in rows:
            self.assertIsNone(r['geometry']);self.assertIsNone(r['uncertainty']);self.assertFalse(r['rank_eligible']);self.assertFalse(r['physical_state_join_eligible']);self.assertFalse(r['seasonal_playback_eligible']);self.assertFalse(r['whole_lifetime_inferred']);self.assertFalse(r['rights_screened_release_eligible'])
        self.assertEqual(d['counts']['size_owners'],89);self.assertEqual(d['counts']['structure_owners'],15);self.assertEqual(sum(r['size_gap'] for r in d['records']),47)
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:
            reader=csv.DictReader(stream);fields=reader.fieldnames;exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields);writer.writeheader();writer.writerows(exports[:329])
        self.assertEqual(hashlib.sha256(prior.getvalue().encode()).hexdigest(),batch['baseline_measurement_csv_sha256'])
        self.assertEqual([r['lower_bound_exclusive'] for r in exports[333:335]],['False','False'])
        self.assertEqual(json.loads(exports[335]['profile_context_json']),haskell['profile_context'])

    def test_fast_alias_and_airborne_temperature_diagnostics_reject_promotions(self):
        import copy
        rows=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v24.json').read_bytes())['records']
        for key,value in [('physical_crosswalk_verified',True),('separation_conventions_reconciled',True),('other_eddy_values_inherited',True),('registry_initial_separation','1985-07-01'),('source_label','Eddy A')]:
            wrong=copy.deepcopy(rows[0]);wrong['case_alias_association'][key]=value
            with self.assertRaises(AssertionError):register.validate_fast_alias_reference(wrong)
        for index,key,value in [(0,'entity_id','eddy:horizon:loop-01-primary'),(1,'unit','m/s'),(2,'metric','whole_eddy_diameter'),(4,'lower_bound_exclusive',True),(5,'rights_screened_release_eligible',True)]:
            wrong=copy.deepcopy(rows[index]);wrong[key]=value
            with self.assertRaises(AssertionError):register.validate_fast_alias_reference(wrong)
        for key,value in [('thermal_reference_celsius',26),('aggregation','whole_eddy_depth'),('is_eddy_vertical_extent',True),('raw_profiles_acquired',True)]:
            wrong=copy.deepcopy(rows[6]);wrong['profile_context'][key]=value
            with self.assertRaises(AssertionError):register.validate_profile_context(wrong)
        for key,value in [('value',260),('entity_id','eddy:horizon:loop-30-primary'),('period_start','1999-08-04')]:
            wrong=copy.deepcopy(rows[6]);wrong[key]=value
            with self.assertRaises(AssertionError):register.validate_profile_context(wrong)

    def test_murphy_profile_source_custody_and_quantities(self):
        import hashlib,csv,io
        d=register.build();batch=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v25.json').read_bytes())
        self.assertEqual(hashlib.sha256(json.dumps(d['evidence'][:336],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),batch['baseline_evidence_sha256'])
        rows=d['evidence'][336:338];self.assertEqual(len(rows),2)
        self.assertEqual([(r['category'],r['unit'],r['range_value']) for r in rows],[('size','km',[175,225]),('structure','m',[.6,.7])])
        report=json.loads((register.ROOT/batch['source_profile_report']).read_bytes());self.assertEqual(report['status'],'PASS')
        self.assertEqual(report['batch_sha256'],hashlib.sha256((register.ROOT/'research/eddy-measurement-register-additions-v25.json').read_bytes()).hexdigest())
        self.assertEqual(report['verifier_sha256'],hashlib.sha256((register.ROOT/'analysis/eddy_height_profiles_v1.py').read_bytes()).hexdigest())
        self.assertEqual(report['original_pdf_sha256'],batch['sources']['calman-1989']['original']['sha256'])
        self.assertEqual((report['crossing_windows_verified'],report['tick_windows_verified'],report['peak_windows_verified']),(12,9,2))
        exports=list(csv.DictReader(io.StringIO((register.ROOT/'research/eddy-measurement-register-v1.csv').read_text(encoding='utf8'))))
        self.assertEqual([json.loads(r['source_plot_estimate_json']) for r in exports[336:338]],[r['source_plot_estimate'] for r in rows])
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=list(exports[0]));writer.writeheader();writer.writerows(exports[:336])
        self.assertEqual(hashlib.sha256(prior.getvalue().encode()).hexdigest(),batch['baseline_measurement_csv_sha256'])
        for r in rows:
            self.assertFalse(r['rights_screened_release_eligible']);self.assertEqual(r['period_start'],'1988-06-20')
            self.assertFalse(r['source_plot_estimate']['case']['diameter_inferred'])

    def test_murphy_profile_rejects_physical_boundary_and_wrong_case(self):
        import copy
        from eddy_height_profiles_v1 import validate_case,span,peak,ink
        c=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v25.json').read_bytes())['height_profile_cases'][0]
        self.assertEqual(span(c)['total_scenarios'],384);self.assertEqual(peak(c)['total_scenarios'],8)
        for key,value in [('date','2015-01-01'),('owner_id','eddy:horizon:loop-11-primary'),('dynamic_topography_unit','cm'),('diameter_inferred',True),('author_eddy_boundary',True),('axbt_trace_combined',True),('diagnostic_level_m',.5),('rights_screened_release_eligible',True)]:
            wrong=copy.deepcopy(c);wrong[key]=value
            with self.assertRaises(AssertionError):validate_case(wrong)
        wrong=copy.deepcopy(c);wrong['crossings'][0]['crossings']['north']['distinct_columns']=[]
        with self.assertRaises(AssertionError):validate_case(wrong)
        with self.assertRaises(AssertionError):ink(bytes(300),10,10,[0,0,10,5],100)

    def test_named_mooring_speeds_preserve_source_units_and_prior_records(self):
        d=register.build();batch=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v26.json').read_bytes())
        self.assertEqual(hashlib.sha256(json.dumps(d['evidence'][:338],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),batch['baseline_evidence_sha256'])
        rows=d['evidence'][338:343];self.assertEqual(len(rows),5)
        self.assertEqual([r['depth_m'] for r in rows],[100,100,300,725,100]);self.assertEqual(rows[0]['value'],75)
        self.assertEqual([r['range_value'] for r in rows[1:]],[[80,90],[30,40],[10,20],[70,80]])
        self.assertEqual([r['profile_context']['direction_as_reported'] for r in rows],['southward','northeastward','northeastward','northeastward','eastward'])
        for r in rows:
            register.validate_profile_context(r);self.assertEqual(r['unit'],'cm/s');self.assertEqual(r['category'],'kinematics')
            self.assertIsNone(r['period_start']);self.assertIsNone(r['period_end']);self.assertIsNone(r['uncertainty']);self.assertFalse(r['rank_eligible']);self.assertFalse(r['seasonal_playback_eligible']);self.assertFalse(r['physical_state_join_eligible'])
        source=batch['sources']['nowlin-2001'];self.assertEqual(source['original']['sha256'],'2a41f8e02736876c5dbbd9388ddc6da789f4324e3d188c73b7fe863c4b8af192')
        self.assertEqual((source['original']['bytes'],source['original']['pages']),(47392646,537));self.assertEqual(set(source['reviewed_page_png_sha256']),{'192','196'})
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:
            reader=csv.DictReader(stream);fields=reader.fieldnames;exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields);writer.writeheader();writer.writerows(exports[:338])
        self.assertEqual(hashlib.sha256(prior.getvalue().encode()).hexdigest(),batch['baseline_measurement_csv_sha256'])
        self.assertEqual([json.loads(r['profile_context_json']) for r in exports[338:343]],[r['profile_context'] for r in rows])
        self.assertEqual(d['counts']['size_owners'],89);self.assertEqual(sum(r['size_gap'] for r in d['records']),47)

    def test_mooring_diagnostics_reject_inherited_depth_and_pooled_statistics(self):
        import copy
        rows=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v26.json').read_bytes())['records']
        for index,key,value in [(0,'value',120.8),(0,'unit','m/s'),(1,'entity_id','eddy:horizon:loop-08-primary'),(2,'depth_m',100),(3,'range_value',[30,40]),(4,'period_start','1988-10-01')]:
            wrong=copy.deepcopy(rows[index]);wrong[key]=value
            with self.assertRaises(AssertionError):register.validate_profile_context(wrong)
        for key,value in [('station','SAIC FF'),('is_eddy_vertical_extent',True),('whole_eddy_maximum_inferred',True),('simultaneous_vertical_profile_inferred',True),('statistic_mean_or_maximum_specified',True),('raw_time_series_acquired',True)]:
            wrong=copy.deepcopy(rows[1]);wrong['profile_context'][key]=value
            with self.assertRaises(AssertionError):register.validate_profile_context(wrong)
        wrong=copy.deepcopy(rows[0]);wrong['profile_context']['source_small_anticyclone_coalescence_context']=False
        with self.assertRaises(AssertionError):register.validate_profile_context(wrong)

    def test_year5_named_size_references_preserve_operators_and_prefix(self):
        d=register.build();batch=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v27.json').read_bytes())
        self.assertEqual(hashlib.sha256(json.dumps(d['evidence'][:343],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),batch['baseline_evidence_sha256'])
        rows=d['evidence'][343:348];self.assertEqual(len(rows),5);self.assertEqual(rows[0]['range_value'],[50,170]);self.assertEqual([r['value'] for r in rows[1:]],[244,148,180,300])
        self.assertEqual([r['case_alias_association']['source_label'] for r in rows],['Eddy E']+['Eddy F']*4)
        source=batch['sources']['saic-1989'];self.assertEqual(source['original']['sha256'],'04ba07ca114b8d1ed52921d4d935fff5c1c18c319210bd3813959e70de91a882')
        self.assertEqual((source['original']['bytes'],source['original']['pages']),(14824003,364));self.assertEqual(set(source['reviewed_page_png_sha256']),{'141','154','205','273'})
        self.assertIn('not assign each endpoint separately',rows[0]['qualification']);self.assertIn('need not be at the eddy front',rows[1]['qualification']);self.assertIn('does not specify',rows[4]['qualification'])
        for r in rows:
            register.validate_year5_alias_reference(r);self.assertIsNone(r['period_start']);self.assertIsNone(r['period_end']);self.assertIsNone(r['uncertainty']);self.assertFalse(r['rank_eligible']);self.assertFalse(r['physical_state_join_eligible']);self.assertFalse(r['seasonal_playback_eligible'])
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:
            reader=csv.DictReader(stream);fields=reader.fieldnames;exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields);writer.writeheader();writer.writerows(exports[:343])
        self.assertEqual(hashlib.sha256(prior.getvalue().encode()).hexdigest(),batch['baseline_measurement_csv_sha256'])
        self.assertEqual(d['counts']['size_owners'],89);self.assertEqual(sum(r['size_gap'] for r in d['records']),47)

    def test_year5_rejects_letter_mismatch_radius_conversion_and_seasonal_promotion(self):
        import copy
        rows=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v27.json').read_bytes())['records']
        for index,key,value in [(0,'metric','annual_eddy_diameter_range'),(0,'range_kind','seasonal_envelope'),(1,'value',488),(2,'unit','km2'),(3,'metric','whole_eddy_radius'),(4,'period_start','1988-04-01')]:
            wrong=copy.deepcopy(rows[index]);wrong[key]=value
            with self.assertRaises(AssertionError):register.validate_year5_alias_reference(wrong)
        for key,value in [('source_label','Eddy E'),('registry_name','Kathleen'),('physical_crosswalk_verified',True),('separation_conventions_reconciled',True),('other_eddy_values_inherited',True)]:
            wrong=copy.deepcopy(rows[1]);wrong['case_alias_association'][key]=value
            with self.assertRaises(AssertionError):register.validate_year5_alias_reference(wrong)

    def test_cls_chart_scale_references_and_local_maxima_preserve_prefix(self):
        d=register.build();batch=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v28.json').read_bytes())
        self.assertEqual(hashlib.sha256(json.dumps(d['evidence'][:348],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),batch['baseline_evidence_sha256'])
        rows=d['evidence'][348:352];self.assertEqual(len(rows),4)
        self.assertEqual([r['range_value'] for r in rows[:2]],[[125,225],[100,200]])
        self.assertEqual([(r['value'],r['unit']) for r in rows[2:]],[(3.5,'knots'),(4.25,'knots')])
        report=json.loads((register.ROOT/batch['source_scale_bar_report']).read_bytes());self.assertTrue(report['source_pixels_verified'])
        self.assertEqual(report['batch_sha256'],hashlib.sha256((register.ROOT/'research/eddy-measurement-register-additions-v28.json').read_bytes()).hexdigest())
        self.assertEqual(report['verifier_sha256'],hashlib.sha256((register.ROOT/'analysis/eddy_scale_bar_spans_v1.py').read_bytes()).hexdigest())
        self.assertEqual(report['original_chart_sha256'],batch['sources']['cls-2021']['chart']['sha256'])
        for r in rows[2:]:register.validate_profile_context(r);self.assertIsNone(r['period_start']);self.assertIsNone(r['profile_context']['sample_depth_m'])
        for r in rows:
            self.assertFalse(r['rights_screened_release_eligible']);self.assertFalse(r['physical_state_join_eligible']);self.assertFalse(r['seasonal_playback_eligible']);self.assertIsNone(r['geometry'])
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:
            reader=csv.DictReader(stream);fields=reader.fieldnames;exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields);writer.writeheader();writer.writerows(exports[:348])
        self.assertEqual(hashlib.sha256(prior.getvalue().encode()).hexdigest(),batch['baseline_measurement_csv_sha256'])
        self.assertEqual([json.loads(r['source_map_estimate_json']) for r in exports[348:350]],[r['source_map_estimate'] for r in rows[:2]])
        self.assertEqual(d['counts']['size_owners'],89);self.assertEqual(d['counts']['kinematics_owners'],73)

    def test_cls_scale_bar_and_adcp_reject_geographic_and_sampling_promotion(self):
        import copy
        from eddy_scale_bar_spans_v1 import validate_case,spans,ink
        b=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v28.json').read_bytes());c=b['scale_bar_cases'][0]
        self.assertEqual(spans(c,'horizontal')['total_scenarios'],8)
        for key,value in [('owner_id','eddy:horizon:loop-72-primary'),('date','2021-11-15'),('scale_bar_km',200),('projection_known',True),('geodesic_distance_inferred',True),('contour_threshold_known',True),('physical_footprint_admitted',True)]:
            wrong=copy.deepcopy(c);wrong[key]=value
            with self.assertRaises(AssertionError):validate_case(wrong)
        wrong=copy.deepcopy(c);wrong['readings'][0]['ticks'][1]['coordinate_x']+=10
        with self.assertRaises(AssertionError):validate_case(wrong)
        with self.assertRaises(AssertionError):ink(bytes(300),10,10,[0,0,10,5],75)
        for key,value in [('sample_depth_m',550),('whole_eddy_maximum_inferred',True),('raw_profiles_acquired',True),('physical_crosswalk_verified',True)]:
            wrong=copy.deepcopy(b['records'][2]);wrong['profile_context'][key]=value
            with self.assertRaises(AssertionError):register.validate_profile_context(wrong)
        for key,value in [('value',4.25),('unit','m/s'),('period_start','2021-09-01')]:
            wrong=copy.deepcopy(b['records'][2]);wrong[key]=value
            with self.assertRaises(AssertionError):register.validate_profile_context(wrong)

    def test_quantum_visible_model_front_and_multisensor_values_preserve_prefix(self):
        d=register.build();batch=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v29.json').read_bytes())
        self.assertEqual(hashlib.sha256(json.dumps(d['evidence'][:352],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),batch['baseline_evidence_sha256'])
        rows=d['evidence'][352:357];self.assertEqual(len(rows),5);self.assertEqual(rows[0]['range_value'],[225,275])
        self.assertEqual([r['value'] for r in rows[1:]],[.8,1.1,.6,1.2]);self.assertEqual([r.get('depth_m') for r in rows[1:]],[5,None,5,None])
        for r in rows[1:]:register.validate_profile_context(r)
        report=json.loads((register.ROOT/batch['source_visible_front_report']).read_bytes());self.assertTrue(report['source_pixels_verified']);self.assertTrue(report['east_side_clipped'])
        self.assertEqual(report['batch_sha256'],hashlib.sha256((register.ROOT/'research/eddy-measurement-register-additions-v29.json').read_bytes()).hexdigest())
        for key,module in [('verifier_sha256','eddy_visible_model_front_v1.py'),('axis_math_sha256','eddy_map_spans_v1.py'),('ink_reader_sha256','eddy_scale_bar_spans_v1.py')]:self.assertEqual(report[key],hashlib.sha256((register.ROOT/'analysis'/module).read_bytes()).hexdigest())
        self.assertEqual(report['meridional_span']['total_scenarios'],512);self.assertFalse(report['full_front_extent_inferred'])
        for r in rows:
            self.assertEqual(r['component_label'],'Northern post-split Quantum I source case');self.assertFalse(r['rights_screened_release_eligible']);self.assertFalse(r['physical_state_join_eligible']);self.assertFalse(r['seasonal_playback_eligible']);self.assertIsNone(r['geometry'])
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:
            reader=csv.DictReader(stream);fields=reader.fieldnames;exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields);writer.writeheader();writer.writerows(exports[:352])
        self.assertEqual(hashlib.sha256(prior.getvalue().encode()).hexdigest(),batch['baseline_measurement_csv_sha256'])
        self.assertEqual([json.loads(r['profile_context_json']) for r in exports[353:357]],[r['profile_context'] for r in rows[1:]])
        self.assertEqual(d['counts']['size_owners'],89);self.assertEqual(d['counts']['kinematics_owners'],73)

    def test_quantum_front_and_comparison_reject_reconstruction_and_depth_inheritance(self):
        import copy
        from eddy_visible_model_front_v1 import validate_case,span
        b=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v29.json').read_bytes());c=b['visible_model_front_cases'][0]
        for key,value in [('owner_id','eddy:horizon:loop-66-secondary'),('east_side_clipped',False),('east_west_span_admitted',True),('full_front_extent_inferred',True),('observed_front_inferred',True),('missing_geometry_reconstructed',True),('quantum_ii_values_inherited',True),('front_threshold_known',True)]:
            wrong=copy.deepcopy(c);wrong[key]=value
            with self.assertRaises(AssertionError):validate_case(wrong)
        wrong=copy.deepcopy(c);wrong['readings'][0]['extrema']['south']['coordinate_y']=885
        with self.assertRaises(AssertionError):validate_case(wrong)
        for index,key,value in [(1,'value',1.1),(1,'depth_m',9),(2,'depth_m',5),(2,'period_start','2018-03-25')]:
            wrong=copy.deepcopy(b['records'][index]);wrong[key]=value
            with self.assertRaises(AssertionError):register.validate_profile_context(wrong)
        for key,value in [('shared_source_approximation',False),('sample_depth_m',5),('simultaneous_vertical_section_inferred',True),('vertical_shear_computed',True),('raw_profiles_acquired',True)]:
            wrong=copy.deepcopy(b['records'][2]);wrong['profile_context'][key]=value
            with self.assertRaises(AssertionError):register.validate_profile_context(wrong)


    def test_kraken_gridded_source_case_keeps_prefix_and_sensitivity_scope(self):
        d=register.build();b=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v30.json').read_bytes())
        self.assertEqual(hashlib.sha256(json.dumps(d['evidence'][:357],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),b['baseline_evidence_sha256'])
        rows=d['evidence'][357:361];self.assertEqual(len(rows),4)
        self.assertEqual([r['range_value'] for r in rows],[[60000,70000],[275,300],[300,325],[325,375]])
        self.assertEqual([r['unit'] for r in rows],['km2','km','km','km'])
        for r in rows:
            register.validate_gridded_case(r)
            self.assertEqual(r['entity_id'],'eddy:horizon:loop-60-primary');self.assertEqual(r['period_start'],'2013-03-31')
            self.assertFalse(r['rights_screened_release_eligible']);self.assertFalse(r['physical_state_join_eligible']);self.assertFalse(r['seasonal_playback_eligible']);self.assertIsNone(r['geometry'])
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:
            reader=csv.DictReader(stream);fields=reader.fieldnames;exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields);writer.writeheader();writer.writerows(exports[:357])
        self.assertEqual(hashlib.sha256(prior.getvalue().encode()).hexdigest(),b['baseline_measurement_csv_sha256'])
        self.assertEqual([json.loads(r['calculation_json']) for r in exports[357:361]],[r['calculation'] for r in rows])
        self.assertEqual((d['counts']['size_owners'],d['counts']['size_records']),(89,166))

    def test_kraken_gridded_case_rejects_wrong_date_inheritance_and_ambiguous_matches(self):
        import copy
        from eddy_gridded_case_summary_v1 import summarize
        b=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v30.json').read_bytes())
        r=b['records'][0];report=json.loads((register.ROOT/r['calculation']['report_file']).read_bytes())
        for key,value in [('entity_id','eddy:published:kraken-2013'),('period_start','2013-04-08'),('rights_screened_release_eligible',True),('range_value',[50000,70000]),('value',64440)]:
            wrong=copy.deepcopy(r);wrong[key]=value
            with self.assertRaises(AssertionError):register.validate_gridded_case(wrong)
        for key,value in [('physical_crosswalk_verified',True),('other_kraken_values_inherited',True),('source_map_pixels_reviewed',False),('date','2013-03-24')]:
            wrong=copy.deepcopy(report);wrong['case'][key]=value
            with self.assertRaises(AssertionError):summarize(wrong,'area')
        for duplicate in [False,True]:
            wrong=copy.deepcopy(report);day=next(d for d in wrong['cloud_review']['result']['days'] if d['date']=='2013-03-31')
            if duplicate:day['scenarios'][0]['candidates'].append(copy.deepcopy(day['scenarios'][0]['candidates'][0]))
            else:day['scenarios'][0]['candidates'][0]['review_control_point_hits'][wrong['case']['control_key']][0]=False
            with self.assertRaises(AssertionError):summarize(wrong,'area')


    def test_provider_operational_chart_spans_keep_native_dates_and_baseline(self):
        d=register.build();b=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v31.json').read_bytes())
        self.assertEqual(hashlib.sha256(json.dumps(d['evidence'][:361],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),b['baseline_evidence_sha256'])
        rows=d['evidence'][361:365];self.assertEqual(len(rows),4)
        self.assertEqual([r['range_value'] for r in rows],[[100,300],[100,325],[400,625],[400,625]])
        self.assertEqual([r['period_start'] for r in rows],['2011-06-21','2011-06-21','2011-08-01','2011-08-01'])
        from eddy_operational_chart_spans_v1 import spans,validate_case
        for r in rows:
            m=r['source_map_estimate'];validate_case(m['case']);self.assertEqual(m['calculation'],spans(m['case'],m['component']))
            self.assertEqual(m['calculation']['total_scenarios'],128);self.assertFalse(m['case']['missing_ink_reconstructed']);self.assertFalse(m['case']['front_threshold_known'])
            self.assertFalse(r['physical_state_join_eligible']);self.assertFalse(r['rights_screened_release_eligible']);self.assertFalse(r['seasonal_playback_eligible']);self.assertIsNone(r['geometry'])
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:
            reader=csv.DictReader(stream);fields=reader.fieldnames;exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields);writer.writeheader();writer.writerows(exports[:361])
        self.assertEqual(hashlib.sha256(prior.getvalue().encode()).hexdigest(),b['baseline_measurement_csv_sha256'])
        self.assertEqual([json.loads(r['source_map_estimate_json']) for r in exports[361:365]],[r['source_map_estimate'] for r in rows])
        excluded=json.loads((register.ROOT/b['excluded_gridded_comparison']['file']).read_bytes())
        self.assertEqual(excluded['measurements_admitted'],0)
        self.assertEqual((d['counts']['size_owners'],d['counts']['size_records']),(89,166))

    def test_operational_chart_cases_reject_date_promotion_secondary_inheritance_and_axis_changes(self):
        import copy
        from eddy_operational_chart_spans_v1 import validate_case,spans
        b=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v31.json').read_bytes())
        for c in b['operational_chart_cases']:
            for key,value in [('date','2011-07-30'),('owner_id','eddy:horizon:loop-57-secondary'),('front_threshold_known',True),('missing_ink_reconstructed',True),('whole_eddy_dimensions_inferred',True),('association_is_verified',True),('reading_allowance_pixels',2)]:
                wrong=copy.deepcopy(c);wrong[key]=value
                with self.assertRaises(AssertionError):validate_case(wrong)
            wrong=copy.deepcopy(c);wrong['axes']['latitude'][1][0]=104
            with self.assertRaises(AssertionError):spans(wrong,'north_south')

    def test_operational_chart_ink_reader_isolates_neutral_line_from_colour_and_type(self):
        from eddy_operational_chart_spans_v1 import read_pixels,CONFIG
        width,height=303,240;raw=bytearray([255,255,255]*width*height)
        points={(x,y) for x in range(88,120) for y in [74,106]}|{(x,y) for x in [88,119] for y in range(74,107)}
        for x,y in points:raw[(y*width+x)*3:(y*width+x)*3+3]=bytes([140,140,140])
        for x in range(82,87):raw[(100*width+x)*3:(100*width+x)*3+3]=bytes([0,0,130])
        for x in range(100,105):raw[(90*width+x)*3:(90*width+x)*3+3]=bytes([0,0,0])
        rows=read_pixels(raw,width,height,CONFIG['Galileo']['windows'])
        for row in rows:
            self.assertEqual([row['extrema'][s]['coordinate'] for s in ['west','north','east','south']],[88,74,119,106])
            self.assertEqual(row['extrema']['west']['selected_pixels'],len(points))


    def test_edison_preprint_model_event_contrasts_preserve_prefix_and_do_not_close_size(self):
        d=register.build();b=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v32.json').read_bytes())
        self.assertEqual(hashlib.sha256(json.dumps(d['evidence'][:365],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),b['baseline_evidence_sha256'])
        rows=d['evidence'][365:368];self.assertEqual([r['value'] for r in rows],[6,1,1])
        self.assertEqual([r['model_context']['experiment'] for r in rows],['No-Hurricane','No-Helene','No-Milton'])
        for r in rows:
            register.validate_model_event_contrast(r);self.assertFalse(r['whole_lifetime_inferred']);self.assertFalse(r['rank_eligible']);self.assertIsNone(r['geometry'])
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:
            reader=csv.DictReader(stream);fields=reader.fieldnames;exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields);writer.writeheader();writer.writerows(exports[:365])
        self.assertEqual(hashlib.sha256(prior.getvalue().encode()).hexdigest(),b['baseline_measurement_csv_sha256'])
        self.assertEqual([json.loads(r['model_context_json']) for r in exports[365:368]],[r['model_context'] for r in rows])
        edison=next(r for r in d['records'] if r['entity_id']=='eddy:horizon:loop-80-primary')
        self.assertEqual(len(edison['evidence_ids']),3);self.assertTrue(edison['size_gap']);self.assertIsNone(edison['whole_lifetime_days']);self.assertFalse(edison['registry_context']['active_label_is_current_status'])
        self.assertEqual((d['counts']['identities_with_measurements'],d['counts']['identities_without_measurements'],d['counts']['size_owners']),(122,14,89))

    def test_edison_model_event_contrasts_reject_observed_life_and_experiment_swaps(self):
        import copy
        b=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v32.json').read_bytes())
        for row in b['records']:
            for key,value in [('entity_id','eddy:horizon:loop-81-primary'),('value',7),('category','size'),('period_start','2024-10-09'),('rights_screened_release_eligible',True)]:
                wrong=copy.deepcopy(row);wrong[key]=value
                with self.assertRaises(AssertionError):register.validate_model_event_contrast(wrong)
            for key,value in [('observed_lifetime_inferred',True),('observed_causal_effect_inferred',True),('physical_crosswalk_verified',True),('contrasts_are_additive',True),('preprint_not_peer_reviewed',False),('raw_model_fields_acquired',True),('source_figure_pixels_reviewed',True),('comparison_is_between_simulated_worlds',False),('removed_hurricanes','both'),('counterfactual_event_date','2024-10-12')]:
                wrong=copy.deepcopy(row);wrong['model_context'][key]=value
                with self.assertRaises(AssertionError):register.validate_model_event_contrast(wrong)


    def test_fast_thermal_table_preserves_prefix_csv_and_missing_zero_cells(self):
        d=register.build();b=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v33.json').read_bytes())
        self.assertEqual(hashlib.sha256(json.dumps(d['evidence'][:368],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),b['baseline_evidence_sha256'])
        rows=d['evidence'][368:385];self.assertEqual(len(rows),17)
        self.assertEqual([r['value'] for r in rows],[1300,9000,26000,50000,97000,2700,26000,48000,85000,2600,7800,17000,50000,300,2400,8100,24000])
        for r in rows:
            register.validate_profile_context(r);register.validate_fast_alias_reference(r)
            self.assertFalse(r['rank_eligible']);self.assertIsNone(r['geometry']);self.assertIsNone(r.get('depth_m'))
        self.assertFalse(any(r['id'].endswith('1985-11-750m') or r['id'].endswith('1986-01-550m') or r['id'].endswith('1986-04-550m') for r in rows))
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:
            reader=csv.DictReader(stream);fields=reader.fieldnames;exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields);writer.writeheader();writer.writerows(exports[:368])
        self.assertEqual(hashlib.sha256(prior.getvalue().encode()).hexdigest(),b['baseline_measurement_csv_sha256'])
        self.assertEqual([json.loads(r['profile_context_json']) for r in exports[368:385]],[r['profile_context'] for r in rows])
        self.assertEqual((d['counts']['size_owners'],d['counts']['size_records']),(89,166))

    def test_fast_thermal_table_rejects_level_unit_date_and_boundary_changes(self):
        import copy
        b=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v33.json').read_bytes())
        row=b['records'][0]
        for key,value in [('entity_id','eddy:horizon:loop-05-primary'),('value',1300000),('unit','km'),('depth_m',750),('period_start','1985-10-01'),('rights_screened_release_eligible',True)]:
            wrong=copy.deepcopy(row);wrong[key]=value
            with self.assertRaises(AssertionError):register.validate_profile_context(wrong)
        for key,value in [('thermal_reference_celsius',15),('temperature_surface_depth_contour_m',700),('source_table_value',9),('conversion_factor_to_km2',1),('outer_boundary_inferred',True),('annual_extrema_inferred',True),('is_eddy_vertical_extent',True),('sample_depth_inferred',True),('physical_crosswalk_verified',True)]:
            wrong=copy.deepcopy(row);wrong['profile_context'][key]=value
            with self.assertRaises(AssertionError):register.validate_profile_context(wrong)


    def test_yazoo_named_radius_and_current_close_primary_size_gap_only(self):
        d=register.build();b=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v34.json').read_bytes())
        self.assertEqual(hashlib.sha256(json.dumps(d['evidence'][:385],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),b['baseline_evidence_sha256'])
        rows=d['evidence'][385:387];self.assertEqual([r['value'] for r in rows],[150,2.5]);self.assertEqual([r['unit'] for r in rows],['km','knots'])
        for r in rows:register.validate_profile_context(r);self.assertFalse(r['rank_eligible']);self.assertIsNone(r['geometry'])
        owner=next(v for v in d['records'] if v['entity_id']=='eddy:horizon:loop-74-primary');self.assertFalse(owner['size_gap'])
        self.assertEqual(d['counts']['size_owners'],89)
        self.assertTrue(all(r['entity_id']=='eddy:horizon:loop-74-primary' for r in rows))
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:
            reader=csv.DictReader(stream);fields=reader.fieldnames;exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields);writer.writeheader();writer.writerows(exports[:385])
        self.assertEqual(hashlib.sha256(prior.getvalue().encode()).hexdigest(),b['baseline_measurement_csv_sha256'])
        self.assertEqual([json.loads(r['profile_context_json']) for r in exports[385:387]],[r['profile_context'] for r in rows])

    def test_yazoo_references_reject_diameter_depth_secondary_and_date_promotions(self):
        import copy
        b=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v34.json').read_bytes())
        for row in b['records']:
            for key,value in [('entity_id','eddy:horizon:loop-74-secondary'),('value',300),('depth_m',11),('period_start','2022-06-20'),('rights_screened_release_eligible',True)]:
                wrong=copy.deepcopy(row);wrong[key]=value
                with self.assertRaises(AssertionError):register.validate_profile_context(wrong)
            for key,value in [('physical_crosswalk_verified',True),('secondary_case_values_inherited',True),('annual_extrema_inferred',True),('geometry_inferred',True),('sample_depth_m',11),('whole_eddy_maximum_inferred',True)]:
                wrong=copy.deepcopy(row);wrong['profile_context'][key]=value
                with self.assertRaises(AssertionError):register.validate_profile_context(wrong)


    def test_zodiac_isoline_spans_preserve_prefix_and_do_not_create_geometry(self):
        from eddy_source_bold_isoline_spans_v1 import validate_case,spans
        d=register.build();b=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v35.json').read_bytes())
        self.assertEqual(hashlib.sha256(json.dumps(d['evidence'][:387],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),b['baseline_evidence_sha256'])
        rows=d['evidence'][387:391];self.assertEqual([r['range_value'] for r in rows],[[350,400],[450,525],[325,375],[250,325]])
        for r in rows:
            m=r['source_map_estimate'];validate_case(m['case']);self.assertEqual(m['calculation'],spans(m['case'],m['component']))
            self.assertEqual(m['calculation']['total_scenarios'],128);self.assertIsNone(r['value']);self.assertIsNone(r['geometry']);self.assertFalse(r['rank_eligible'])
        self.assertFalse(next(r for r in d['records'] if r['entity_id']=='eddy:horizon:loop-75-primary')['size_gap'])
        self.assertEqual((d['counts']['size_owners'],d['counts']['size_records']),(89,166))
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:
            reader=csv.DictReader(stream);fields=reader.fieldnames;exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields);writer.writeheader();writer.writerows(exports[:387])
        self.assertEqual(hashlib.sha256(prior.getvalue().encode()).hexdigest(),b['baseline_measurement_csv_sha256'])
        self.assertEqual([json.loads(r['source_map_estimate_json']) for r in exports[387:391]],[r['source_map_estimate'] for r in rows])

    def test_zodiac_isolines_reject_threshold_axes_identity_and_footprint_promotions(self):
        import copy
        from eddy_source_bold_isoline_spans_v1 import validate_case
        c=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v35.json').read_bytes())['isoline_cases'][0]
        for key,value in [('source_ssh_contour_cm',19),('source_ssh_reference','OSW daily regional mean'),('owner_id','eddy:horizon:loop-74-primary'),('reading_allowance_pixels',0),('axis_sensitivity_pixels',0),('missing_ink_reconstructed',True),('physical_footprint_admitted',True),('association_is_verified',True),('annual_extrema_inferred',True),('source_operator_equated_to_osw',True)]:
            wrong=copy.deepcopy(c);wrong[key]=value
            with self.assertRaises(AssertionError):validate_case(wrong)
        wrong=copy.deepcopy(c);wrong['axes']['latitude'][1][0]+=5
        with self.assertRaises(AssertionError):validate_case(wrong)
        wrong=copy.deepcopy(c);wrong['readings'][0]['enclosed_background_pixels']=0
        with self.assertRaises(AssertionError):validate_case(wrong)

    def test_source_isoline_reader_rejects_open_and_clipped_strokes(self):
        from eddy_source_bold_isoline_spans_v1 import read_outline
        pixels=bytearray([255]*(100*100*3))
        for y in range(10,81):
            for x in range(10,91):
                if x<13 or x>87 or y<13 or y>77:pixels[(y*100+x)*3:(y*100+x)*3+3]=b'\x00\x00\x00'
        closed=read_outline(pixels,100,100,[2,2,97,97],150);self.assertEqual(closed['bbox_xyxy'],[10,10,90,80])
        self.assertGreater(closed['enclosed_background_pixels'],300)
        with self.assertRaises(AssertionError):read_outline(pixels,100,100,[10,2,97,97],150)
        for y in range(9,14):
            for x in range(45,51):pixels[(y*100+x)*3:(y*100+x)*3+3]=b'\xff\xff\xff'
        with self.assertRaises(AssertionError):read_outline(pixels,100,100,[2,2,97,97],150)


    def test_thor_parent_analysis_extent_preserves_prefix_and_published_case(self):
        d=register.build();b=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v36.json').read_bytes())
        self.assertEqual(hashlib.sha256(json.dumps(d['evidence'][:391],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),b['baseline_evidence_sha256'])
        rows=d['evidence'][391:392];self.assertEqual(len(rows),1);r=rows[0];register.validate_profile_context(r)
        self.assertEqual(r['value'],550);self.assertEqual(r['entity_id'],'eddy:published:thor-2020');self.assertFalse(r['rank_eligible']);self.assertIsNone(r['geometry'])
        self.assertFalse(next(v for v in d['records'] if v['entity_id']==r['entity_id'])['size_gap'])
        self.assertEqual((d['counts']['size_owners'],d['counts']['size_records']),(89,166))
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:
            reader=csv.DictReader(stream);fields=reader.fieldnames;exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields);writer.writeheader();writer.writerows(exports[:391])
        self.assertEqual(hashlib.sha256(prior.getvalue().encode()).hexdigest(),b['baseline_measurement_csv_sha256'])
        self.assertEqual(json.loads(exports[391]['profile_context_json']),r['profile_context'])

    def test_thor_parent_analysis_rejects_cyclones_observations_and_child_inheritance(self):
        import copy
        row=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v36.json').read_bytes())['records'][0]
        for key,value in [('value',120),('value',150),('entity_id','eddy:horizon:loop-69-primary'),('period_start','2020-03-23'),('depth_m',1500),('rights_screened_release_eligible',True)]:
            wrong=copy.deepcopy(row);wrong[key]=value
            with self.assertRaises(AssertionError):register.validate_profile_context(wrong)
        for key,value in [('analysis_is_direct_observation',True),('forecast_member_value',True),('principal_width_inferred',True),('diameter_inferred',True),('child_values_inherited',True),('registry_values_inherited',True),('annual_extrema_inferred',True),('source_boundary_threshold','0.17 m OSW contour'),('phase','post_split_child')]:
            wrong=copy.deepcopy(row);wrong['profile_context'][key]=value
            with self.assertRaises(AssertionError):register.validate_profile_context(wrong)


    def test_kinetic_interaction_currents_preserve_prefix_and_do_not_close_size(self):
        d=register.build();b=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v37.json').read_bytes())
        self.assertEqual(hashlib.sha256(json.dumps(d['evidence'][:392],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),b['baseline_evidence_sha256'])
        rows=d['evidence'][392:394];self.assertEqual([r['value'] for r in rows],[50,30])
        self.assertEqual([r.get('depth_m') for r in rows],[None,755])
        for r in rows:register.validate_profile_context(r);self.assertFalse(r['rank_eligible']);self.assertIsNone(r['geometry'])
        self.assertTrue(next(r for r in d['records'] if r['entity_id']=='eddy:horizon:loop-34-primary')['size_gap'])
        self.assertEqual((d['counts']['size_owners'],sum(r['size_gap'] for r in d['records'])),(89,47))
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:
            reader=csv.DictReader(stream);fields=reader.fieldnames;exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields);writer.writeheader();writer.writerows(exports[:392])
        self.assertEqual(hashlib.sha256(prior.getvalue().encode()).hexdigest(),b['baseline_measurement_csv_sha256'])
        self.assertEqual([json.loads(r['profile_context_json']) for r in exports[392:394]],[r['profile_context'] for r in rows])

    def test_kinetic_currents_reject_time_depth_statistic_and_identity_promotions(self):
        import copy
        b=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v37.json').read_bytes())
        for row in b['records']:
            for key,value in [('entity_id','eddy:horizon:loop-33-primary'),('value',60),('period_start','2000-11-03'),('depth_m',600),('rights_screened_release_eligible',True)]:
                wrong=copy.deepcopy(row);wrong[key]=value
                with self.assertRaises(AssertionError):register.validate_profile_context(wrong)
            for key,value in [('physical_crosswalk_verified',True),('cross_report_case_association_verified',True),('simultaneous_vertical_profile_inferred',True),('vertical_shear_computed',True),('whole_eddy_maximum_inferred',True),('map_date_is_sample_time',True),('is_eddy_vertical_extent',True),('interaction_context','isolated_eddy'),('source_phase','january_2001'),('statistic','whole_eddy_maximum')]:
                wrong=copy.deepcopy(row);wrong['profile_context'][key]=value
                with self.assertRaises(AssertionError):register.validate_profile_context(wrong)


    def test_quiet_sst_axes_preserve_prefix_and_close_only_named_size_gap(self):
        d=register.build();b=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v38.json').read_bytes())
        self.assertEqual(hashlib.sha256(json.dumps(d['evidence'][:394],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),b['baseline_evidence_sha256'])
        rows=d['evidence'][394:396];self.assertEqual(len(rows),2)
        self.assertEqual((rows[0]['value'],rows[1]['range_value']),(400,[250,300]))
        for r in rows:register.validate_profile_context(r);self.assertFalse(r['rank_eligible']);self.assertIsNone(r['geometry']);self.assertIsNone(r['period_start']);self.assertIsNone(r['period_end'])
        owner=next(r for r in d['records'] if r['entity_id']=='eddy:horizon:loop-14-primary');self.assertFalse(owner['size_gap'])
        self.assertEqual((d['counts']['size_owners'],d['counts']['size_records'],sum(r['size_gap'] for r in d['records'])),(89,166,47))
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:
            reader=csv.DictReader(stream);fields=reader.fieldnames;exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields);writer.writeheader();writer.writerows(exports[:394])
        self.assertEqual(hashlib.sha256(prior.getvalue().encode()).hexdigest(),b['baseline_measurement_csv_sha256'])
        self.assertEqual([json.loads(r['profile_context_json']) for r in exports[394:396]],[r['profile_context'] for r in rows])

    def test_quiet_axes_reject_strict_bound_dates_area_and_identity_promotions(self):
        import copy
        b=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v38.json').read_bytes())
        for row in b['records']:
            for key,value in [('entity_id','eddy:horizon:loop-13-primary'),('value',350),('period_start','1990-08-12'),('depth_m',200),('upper_bound',400),('rights_screened_release_eligible',True)]:
                wrong=copy.deepcopy(row);wrong[key]=value
                with self.assertRaises(AssertionError):register.validate_profile_context(wrong)
            for key,value in [('strict_bound_inferred',True),('per_image_axis_values_known',True),('continuous_observation_interval_inferred',True),('ellipse_area_derived',True),('mathematical_ellipse_fit_verified',True),('outer_boundary_operator_known',True),('physical_crosswalk_verified',True),('annual_extrema_inferred',True),('orientation_as_reported','principal_geodesic_axis'),('approximation_as_reported','exact'),('image_dates',['1990-09-14'])]:
                wrong=copy.deepcopy(row);wrong['profile_context'][key]=value
                with self.assertRaises(AssertionError):register.validate_profile_context(wrong)


    def test_nelson_local_current_phases_preserve_prefix_and_size_gap(self):
        d=register.build();b=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v39.json').read_bytes())
        self.assertEqual(hashlib.sha256(json.dumps(d['evidence'][:396],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),b['baseline_evidence_sha256'])
        rows=d['evidence'][396:401];self.assertEqual(len(rows),5)
        self.assertEqual([r.get('depth_m') for r in rows],[45,45,None,None,None])
        self.assertEqual((rows[0]['upper_bound'],rows[0]['upper_bound_exclusive'],rows[1]['value'],rows[2]['range_value'],rows[3]['value'],rows[4]['value']),(0.4,True,1.4,[2.2,2.7],3.6,2.6))
        for r in rows:register.validate_profile_context(r);self.assertFalse(r['rank_eligible']);self.assertIsNone(r['geometry'])
        owner=next(r for r in d['records'] if r['entity_id']=='eddy:horizon:loop-11-primary');self.assertTrue(owner['size_gap'])
        self.assertEqual((d['counts']['size_owners'],d['counts']['size_records'],sum(r['size_gap'] for r in d['records'])),(89,166,47))
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:
            reader=csv.DictReader(stream);fields=reader.fieldnames;exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields);writer.writeheader();writer.writerows(exports[:396])
        self.assertEqual(hashlib.sha256(prior.getvalue().encode()).hexdigest(),b['baseline_measurement_csv_sha256'])
        self.assertEqual([json.loads(r['profile_context_json']) for r in exports[396:401]],[r['profile_context'] for r in rows])

    def test_nelson_currents_reject_bathymetry_depth_phase_bound_and_identity_promotions(self):
        import copy
        b=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v39.json').read_bytes())
        for row in b['records']:
            for key,value in [('entity_id','eddy:horizon:loop-10-primary'),('value',99),('period_start','1989-10-01'),('depth_m',500),('rights_screened_release_eligible',True)]:
                wrong=copy.deepcopy(row);wrong[key]=value
                with self.assertRaises(AssertionError):register.validate_profile_context(wrong)
            for key,value in [('bathymetry_is_sampling_depth',True),('whole_eddy_maximum_inferred',True),('simultaneous_vertical_profile_inferred',True),('vertical_shear_computed',True),('is_eddy_vertical_extent',True),('annual_extrema_inferred',True),('physical_crosswalk_verified',True),('phase','annual_envelope'),('sample_depth_m',1000),('statistic','eddy_wide_maximum')]:
                wrong=copy.deepcopy(row);wrong['profile_context'][key]=value
                with self.assertRaises(AssertionError):register.validate_profile_context(wrong)
        wrong=copy.deepcopy(b['records'][0]);wrong['upper_bound_exclusive']=False
        with self.assertRaises(AssertionError):register.validate_profile_context(wrong)

    def test_atwater_image_patch_preserves_prior_data_and_qualified_scope(self):
        from eddy_author_animation_patch_v1 import validate_record,spans
        d=register.build();b=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v40.json').read_bytes())
        self.assertEqual(hashlib.sha256(json.dumps(d['evidence'][:401],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),b['baseline_evidence_sha256'])
        rows=d['evidence'][401:403];case=b['author_animation_patch_cases'][0]
        self.assertEqual([r['range_value'] for r in rows],[[300,425],[100,225]])
        self.assertEqual((d['counts']['size_owners'],d['counts']['size_records'],sum(r['size_gap'] for r in d['records'])),(89,166,47))
        for raw,r in zip(b['records'],rows):
            validate_record(case,raw)
            self.assertEqual(spans(case,raw['map_span_component'])['total_scenarios'],384)
            self.assertFalse(r['rank_eligible']);self.assertIsNone(r['geometry']);self.assertFalse(r['physical_state_join_eligible']);self.assertFalse(r['seasonal_playback_eligible'])
        report=json.loads((register.ROOT/'research/eddy-author-animation-patch-source-verification-v1.json').read_bytes())
        self.assertEqual(report['verifier_sha256'],d['method_implementation_sha256']['analysis/eddy_author_animation_patch_v1.py'])
        self.assertEqual(report['patches'],case['patch_cases'])
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:
            reader=csv.DictReader(stream);fields=reader.fieldnames;exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields);writer.writeheader();writer.writerows(exports[:401])
        self.assertEqual(hashlib.sha256(prior.getvalue().encode()).hexdigest(),b['baseline_measurement_csv_sha256'])
        self.assertEqual([json.loads(r['source_map_estimate_json']) for r in exports[401:403]],[r['source_map_estimate'] for r in rows])

    def test_atwater_operator_rejects_boundary_identity_and_field_promotions(self):
        import copy
        from eddy_author_animation_patch_v1 import validate_case,validate_record,patch_readouts
        b=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v40.json').read_bytes());case=b['author_animation_patch_cases'][0]
        for key,value in [('owner_id','eddy:horizon:loop-77-primary'),('date','2023-08-02'),('frame_index_zero_based',117),('source_level_m',0.17),('legend_label','absolute ADT (m)'),('field_datum','absolute'),('source_original_pdf_acquired',True)]+[(k,True) for k in ['physical_crosswalk_verified','full_ring_boundary_admitted','physical_state_join_eligible','observational_measurement_admitted','exact_field_product_verified','seasonal_range_inferred']]:
            wrong=copy.deepcopy(case);wrong[key]=value
            with self.assertRaises(AssertionError):validate_case(wrong)
        for key,value in [('entity_id','eddy:horizon:loop-77-primary'),('metric','eddy_diameter'),('range_value',[1,2]),('period_start','2023-08-02'),('rights_screened_release_eligible',True)]:
            wrong=copy.deepcopy(b['records'][0]);wrong[key]=value
            with self.assertRaises(AssertionError):validate_record(case,wrong)
        # A large source-colour field touching the ROI must be rejected, not cropped into a size.
        rgb=bytes(case['palette'][-1]['rgb']);high=max(case['palette'],key=lambda p:p['level_m']);rgb=bytes(high['rgb'])
        with self.assertRaises(AssertionError):patch_readouts(rgb*80*80,80,80,[10,10,69,69],case['palette'])
        # No matching legend colour must not produce a component.
        with self.assertRaises(AssertionError):patch_readouts(bytes([0,255,0])*80*80,80,80,[10,10,69,69],case['palette'])

    def test_laura_cartographic_spans_and_ssh_keep_earlier_records_and_operators_separate(self):
        from eddy_cartographic_circle_spans_v1 import validate_record,spans
        d=register.build();b=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v41.json').read_bytes())
        self.assertEqual(hashlib.sha256(json.dumps(d['evidence'][:403],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),b['baseline_evidence_sha256'])
        rows=d['evidence'][403:406];case=b['cartographic_circle_cases'][0]
        self.assertEqual([r.get('range_value') for r in rows[:2]],[[125,200],[100,150]])
        self.assertEqual((rows[2]['value'],rows[2]['unit']),(40,'cm'));register.validate_profile_context(rows[2])
        for raw,r in zip(b['records'][:2],rows[:2]):
            validate_record(case,raw);self.assertEqual(spans(case,raw['map_span_component'])['total_scenarios'],512)
            self.assertFalse(r['rank_eligible']);self.assertIsNone(r['geometry']);self.assertIsNone(r['period_start']);self.assertIsNone(r['period_end'])
        self.assertEqual((d['counts']['size_owners'],d['counts']['size_records'],d['counts']['structure_owners'],sum(r['size_gap'] for r in d['records'])),(89,166,15,47))
        owner=next(r for r in d['records'] if r['entity_id']==case['owner_id']);self.assertFalse(owner['size_gap'])
        report=json.loads((register.ROOT/'research/eddy-cartographic-circle-source-verification-v1.json').read_bytes())
        self.assertEqual(report['verifier_sha256'],d['method_implementation_sha256']['analysis/eddy_cartographic_circle_spans_v1.py'])
        self.assertFalse(report['physical_boundary_admitted'])
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:
            reader=csv.DictReader(stream);fields=reader.fieldnames;exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields);writer.writeheader();writer.writerows(exports[:403])
        self.assertEqual(hashlib.sha256(prior.getvalue().encode()).hexdigest(),b['baseline_measurement_csv_sha256'])
        self.assertEqual([json.loads(r['source_map_estimate_json']) for r in exports[403:405]],[r['source_map_estimate'] for r in rows[:2]])
        self.assertEqual(json.loads(exports[405]['profile_context_json']),rows[2]['profile_context'])

    def test_laura_cartographic_circle_and_ssh_reject_physical_and_temporal_promotions(self):
        import copy
        from eddy_cartographic_circle_spans_v1 import validate_case,validate_record,validate_ssh_record,read_extremum
        b=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v41.json').read_bytes());case=b['cartographic_circle_cases'][0]
        for key,value in [('owner_id','eddy:geography:astrid-2000'),('date','2000-03-01'),('source_month_label','Jan 00'),('boundary_operator','0.17 m ADT')]+[(k,True) for k in ['circle_is_physical_boundary','geodesic_circle_assumed','circle_fit_performed','physical_crosswalk_verified','physical_state_join_eligible','area_derived','diameter_inferred','exact_survey_instant_known','annual_extrema_inferred']]:
            wrong=copy.deepcopy(case);wrong[key]=value
            with self.assertRaises(AssertionError):validate_case(wrong)
        for key,value in [('metric','eddy_diameter'),('period_start','2000-03-01'),('range_value',[1,2]),('rights_screened_release_eligible',True)]:
            wrong=copy.deepcopy(b['records'][0]);wrong[key]=value
            with self.assertRaises(AssertionError):validate_record(case,wrong)
        for key,value in [('unit','m'),('value',400),('depth_m',40),('entity_id','eddy:geography:astrid-2000'),('period_start','2000-03-01')]:
            wrong=copy.deepcopy(b['records'][2]);wrong[key]=value
            with self.assertRaises(AssertionError):validate_ssh_record(wrong)
        for key,value in [('is_eddy_vertical_extent',True),('hydrographic_and_ssh_centers_assumed_equal',True),('full_lifetime_maximum_inferred',True),('annual_extrema_inferred',True),('anomaly_reference','absolute ADT')]:
            wrong=copy.deepcopy(b['records'][2]);wrong['profile_context'][key]=value
            with self.assertRaises(AssertionError):validate_ssh_record(wrong)
        for gray in [0,255]:
            with self.assertRaises(AssertionError):read_extremum(bytes([gray])*794*600,794,600,'west',150)

    def test_nautilus_ii_own_calendar_narrative_preserves_parent_and_prior_data(self):
        d=register.build();b=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v42.json').read_bytes())
        self.assertEqual(hashlib.sha256(json.dumps(d['evidence'][:406],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),b['baseline_evidence_sha256'])
        r=d['evidence'][406];register.validate_nautilus_calendar_reference(r)
        self.assertEqual(r['range_value'],[184,275]);self.assertIsNone(r['period_start']);self.assertIsNone(r['period_end']);self.assertFalse(r['whole_lifetime_inferred']);self.assertIsNone(r['geometry']);self.assertFalse(r['seasonal_playback_eligible'])
        child=next(v for v in d['records'] if v['entity_id']=='eddy:horizon:loop-63-secondary')
        self.assertEqual(child['evidence_ids'],[r['id']]);self.assertTrue(child['size_gap']);self.assertFalse(child['duration_gap']);self.assertIsNone(child['whole_lifetime_days'])
        self.assertEqual(child['linked_primary_context']['entity_id'],'eddy:horizon:loop-63-primary')
        self.assertFalse(r['independent_named_case']['primary_values_inherited'])
        self.assertEqual((d['counts']['identities_with_measurements'],d['counts']['identities_without_measurements'],d['counts']['secondary_entries_with_own_references'],d['counts']['duration_owners']),(122,14,2,101))
        self.assertEqual((d['counts']['size_owners'],sum(v['size_gap'] for v in d['records'])),(89,47))
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:
            reader=csv.DictReader(stream);fields=reader.fieldnames;exports=list(reader)
        prior=io.StringIO(newline='');writer=csv.DictWriter(prior,fieldnames=fields);writer.writeheader();writer.writerows(exports[:406])
        self.assertEqual(hashlib.sha256(prior.getvalue().encode()).hexdigest(),b['baseline_measurement_csv_sha256'])
        self.assertEqual(json.loads(exports[406]['calendar_support_json']),r['calendar_support'])
        self.assertEqual(json.loads(exports[406]['independent_named_case_json']),r['independent_named_case'])

    def test_nautilus_ii_calendar_reference_rejects_parent_dates_exact_life_and_false_precision(self):
        import copy
        b=json.loads((register.ROOT/'research/eddy-measurement-register-additions-v42.json').read_bytes());raw=b['records'][0]
        for key,value in [('entity_id','eddy:horizon:loop-63-primary'),('metric','measured_lifespan'),('range_value',[180,270]),('period_start','2015-05-01'),('period_end','2015-11-30'),('value',230),('unit','month'),('rights_screened_release_eligible',True)]:
            wrong=copy.deepcopy(raw);wrong[key]=value
            with self.assertRaises(AssertionError):register.validate_nautilus_calendar_reference(wrong)
        for key,value in [('start_date_max','2015-05-01'),('end_month_min','2015-11'),('end_date_min','2015-11-01'),('end_date_max','2016-01-01'),('start_precision','day'),('chronology_conditioned',True),('unconditioned_elapsed_day_range',[184,274])]:
            wrong=copy.deepcopy(raw);wrong['calendar_support'][key]=value
            with self.assertRaises(AssertionError):register.validate_nautilus_calendar_reference(wrong)
        for key in ['association_is_verified','primary_values_inherited','exact_split_event_identified','continuous_identity_across_reconnections_verified','whole_physical_lifetime_verified','shared_figure_contour_is_child_boundary','parent_registry_dates_used']:
            wrong=copy.deepcopy(raw);wrong['independent_named_case'][key]=True
            with self.assertRaises(AssertionError):register.validate_nautilus_calendar_reference(wrong)

if __name__=='__main__':unittest.main()
