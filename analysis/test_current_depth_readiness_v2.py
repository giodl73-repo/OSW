import copy,unittest
from build_current_depth_readiness_v2 import join,months_from_cases

def priority(owner,kind):
    return {'entity_id':owner,'identity_level':'family' if owner.endswith('family') else 'current',
        'priority_kind':kind,'collection_priority_rank':1,'cases':[],
        'supported_regional_case_count':0,'unresolved_regional_case_count':0,'supported_mean_cross_section_count':0,
        'regional_supported_adjacent_segment_occurrences':0,'regional_gap_segment_occurrences':0,
        'next_collection_action':'scoped collection required','source_depth_reference_count':1}

def fixture():
    view={'records':[{'entity_id':'current:family','name':'Family'},{'entity_id':'current:leaf','name':'Leaf'}],
        'evidence':[{'id':'ref','entity_id':'current:leaf','metric':'core_depth','unit':'m','source_cast_profile_id':'one-cast'}]}
    old={'records':[priority('current:family','declared_member_discovery_not_parent_scalar'),priority('current:leaf','no_own_supported_regional_case')]}
    return view,old

class ReadinessSemantics(unittest.TestCase):
    def test_member_parent_does_not_become_a_missing_individual_measurement(self):
        view,old=fixture();report=join(view,old,[])
        self.assertEqual(report['direct_current_regional_priority_gaps'],['current:leaf'])
        self.assertFalse(report['records'][0]['parent_requires_single_depth'])
        self.assertEqual(report['records'][0]['canonical_reference_count'],0)
        self.assertEqual(report['records'][1]['canonical_reference_count'],1)

    def test_snapshot_labels_are_not_a_seasonal_range(self):
        cases=[{'case_scope':{'snapshot_time_utc':'2022-03-15T00:00:00Z'}},{'case_scope':{'snapshot_time_utc':None}},
            {'case_scope':{'snapshot_time_utc':'2022-09-15T00:00:00Z'}}]
        self.assertEqual(months_from_cases(cases),(['2022-03-15','2022-09-15'],[3,9],[]))
        view,old=fixture();old['records'][1]['cases']=cases;r=join(view,old,[])['records'][1]
        self.assertFalse(r['snapshot_month_labels_establish_seasonal_climatology'])
        self.assertIsNone(r['physical_annual_depth_range_m'])

    def test_reviewed_phase_product_is_not_independent_observation_or_volume(self):
        view,old=fixture();product={'id':'cycle','entity_id':'current:leaf','kind':'fitted_phase_cycle'}
        before=copy.deepcopy((view,old,product));report=join(view,old,[product]);row=report['records'][1]
        self.assertEqual(row['reviewed_temporal_products'],[product])
        self.assertFalse(row['regional_cases_are_independent_observations'])
        self.assertIsNone(row['volume_km3']);self.assertEqual((view,old,product),before)

    def test_absent_from_explicit_registry_does_not_assert_absent_project_data(self):
        view,old=fixture();r=join(view,old,[])['records'][1]
        self.assertIn('other_project_data_not_excluded',r['temporal_index_status'])

    def test_nominal_mean_period_is_not_given_an_invented_calendar_month(self):
        self.assertEqual(months_from_cases([{'case_scope':{'snapshot_time_utc':'provider-mean-period'}}]),([],[],['provider-mean-period']))

    def test_duplicate_product_or_identity_mismatch_rejected(self):
        view,old=fixture();p={'id':'cycle','entity_id':'current:leaf'}
        with self.assertRaises(ValueError):join(view,old,[p,p])
        with self.assertRaises(ValueError):join(view,{'records':old['records'][:1]},[])



class CompiledV40Semantics(unittest.TestCase):
    def setUp(self):
        import json,csv,io,hashlib
        import compiled_depth_catalog_view_v3 as c
        self.c=c;self.files={};self.reads=[]
        def piece(path,raw):
            self.files[path]=raw;return {'file':path,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
        self.piece=piece;self.encode=lambda x:(json.dumps(x,separators=(',',':'))+'\n').encode()
        def table(rows):
            fields=sorted({k for r in rows for k in r});out=io.StringIO(newline='');w=csv.DictWriter(out,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows({k:c.cell(r.get(k)) for k in fields} for r in rows);return out.getvalue().encode()
        self.table=table
        def reader(path):self.reads.append(path);return self.files[path]
        self.reader=reader
        self.base={'records':[{'entity_id':'current:leaf','name':'Leaf','status':'scoped_depth_reference'},{'entity_id':'current:family','name':'Family','status':'not_yet_assessed'}],'evidence':[{'id':'old','entity_id':'current:leaf','metric':'core_depth','unit':'m','approximate_value_m':100,'physical_current_bottom_established':False}],'source_contexts':{}}
        c.refresh(self.base);self.meta={'schema':'synthetic','status':'admitted','interpretation':'typed references only','runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}
        bp=self.piece('research/base.json',self.encode(self.base));bc=self.piece('research/base.csv',self.table(self.base['evidence']))
        self.manifest={'schema':'osw.current-depth-reference-inventory.v28','base':{'json':bp,'csv':bc},'addenda':[],'counts':copy.deepcopy(self.base['counts']),'metric_counts':copy.deepcopy(self.base['metric_counts']),'coordinate_unit_counts':copy.deepcopy(self.base['coordinate_unit_counts']),'view_metadata':copy.deepcopy(self.meta)}
        self.row={'id':'new','entity_id':'current:leaf','metric':'reported_censored_flow_pressure_reach','unit':'dbar','approximate_value_m':None,'source_bound_kind':'strict_lower_support_not_current_bottom','physical_current_bottom_established':False}
        self.addendum={'id':'synthetic-admitted','evidence':[self.row],'source_contexts':{'new-context':{'definition':'preserve exact qualifier'}},'source_result':{'file':'research/source-data/NEVER-READ-NATIVE','sha256':'x'},'runtime_changed':False,'full_goal_complete':False}
    def part(self,addendum=None):
        a=self.addendum if addendum is None else addendum
        return {'id':a['id'],'json':self.piece('research/add.json',self.encode(a)),'csv':self.piece('research/add.csv',self.table(a['evidence']))}
    def test_compiled_append_keeps_qualifiers_units_and_never_reads_source_provenance(self):
        before=copy.deepcopy(self.base);part=self.part();self.c.append(self.base,part,self.reader);self.assertEqual(self.base['evidence'][-1],self.row);self.assertEqual(self.base['evidence'][0],before['evidence'][0]);self.assertEqual(self.base['coordinate_unit_counts'],{'dbar':1,'m':1});self.assertIsNone(self.base['evidence'][-1]['approximate_value_m']);self.assertTrue(all('source-data/' not in p for p in self.reads))
    def test_supported_v34_manifest_reads_only_typed_admitted_pieces(self):
        prev=self.piece('research/previous.json',self.encode(self.manifest));part=self.part();expected=copy.deepcopy(self.base);self.c.append(expected,part,self.reader)
        manifest={'schema':'osw.current-depth-reference-inventory.v34','previous_inventory':prev,'reference_addendum':part,'counts':expected['counts'],'metric_counts':expected['metric_counts'],'coordinate_unit_counts':expected['coordinate_unit_counts'],'view_metadata':copy.deepcopy(self.meta)}
        out=self.c.load_inventory(manifest,self.reader);self.assertEqual(out['evidence'],expected['evidence']);self.assertEqual(out['source_contexts'],expected['source_contexts']);self.assertTrue(all('source-data/' not in p for p in self.reads))
    def test_duplicate_reference_owner_and_context_overwrites_rejected(self):
        for change in ['duplicate','unknown','context','promote']:
            a=copy.deepcopy(self.addendum);view=copy.deepcopy(self.base)
            if change=='duplicate':a['evidence'][0]['id']='old'
            elif change=='unknown':a['evidence'][0]['entity_id']='current:unknown'
            elif change=='context':view['source_contexts']['new-context']={}
            else:a['full_goal_complete']=True
            with self.assertRaises(ValueError):self.c.append(view,self.part(a),self.reader)
    def test_csv_mismatch_and_shadowed_data_or_runtime_promotion_rejected(self):
        part=self.part();part['csv']=self.piece('research/add.csv',b'id\nwrong\n')
        with self.assertRaises(ValueError):self.c.append(copy.deepcopy(self.base),part,self.reader)
        for key,value in [('evidence',[]),('runtime_changed',True),('full_goal_complete',0)]:
            m=copy.deepcopy(self.manifest);m['view_metadata'][key]=value
            with self.assertRaises(ValueError):self.c.load_inventory(m,self.reader)
    def calendar(self):
        view=copy.deepcopy(self.base);view['records'].append({'entity_id':'current:leeuwin','name':'Leeuwin','status':'scoped_depth_reference'});rows=[]
        for month in range(1,13):
            censor=month in [3,8,11];ref='support-'+str(month) if censor else 'boundary-'+str(month)
            e={'id':ref,'entity_id':'current:leeuwin','metric':'derived_censored_mean_flow_reach' if censor else 'derived_mean_velocity_zero_crossing_depth','unit':'m','approximate_value_m':None if censor else 120,'computed_zero_crossing_depth_m':None if censor else 120};view['evidence'].append(e)
            rows.append({'month':month,'boundary_reference_id':None if censor else ref,'support_reference_id':ref if censor else None,'display_boundary_depth_m':None if censor else 120,'computed_zero_crossing_depth_m':None if censor else 120,'support_lower_bound_m':475 if censor else None,'sampling_limit_is_boundary':False,'physical_uncertainty_m':None})
        series={'schema':'osw.leeuwin-monthly-depth-support-series.v2','entity_id':'current:leeuwin','site_id':'WATR50','months':rows,'counts':{'calendar_months':12,'finite_boundary_descriptors':9,'censored_support_months':3,'unknown_boundary_months':3},'annual_depth_range_m':None,'seasonal_interpolation_performed':False,'physical_current_bottom_established':False,'physical_thickness_m':None,'volume_m3':None}
        return view,series
    def test_nine_boundaries_and_three_censored_support_months_keep_null_depths(self):
        view,series=self.calendar();before=copy.deepcopy(series);self.c.verify_calendar(view,series,self.table(series['months']));self.assertEqual(series,before)
        for month in [3,8,11]:self.assertIsNone(series['months'][month-1]['display_boundary_depth_m']);self.assertEqual(series['months'][month-1]['support_lower_bound_m'],475)
    def test_calendar_support_not_finite_boundary_uncertainty_or_annual_range(self):
        for change in ['boundary','sample','annual','owner','duplicate','uncertainty']:
            view,series=self.calendar()
            if change=='boundary':series['months'][2]['display_boundary_depth_m']=475
            elif change=='sample':series['months'][2]['sampling_limit_is_boundary']=True
            elif change=='annual':series['annual_depth_range_m']=[120,475]
            elif change=='owner':series['entity_id']='current:leaf'
            elif change=='duplicate':series['months'][1]['boundary_reference_id']=series['months'][0]['boundary_reference_id']
            else:series['months'][2]['physical_uncertainty_m']=5
            with self.assertRaises(ValueError):self.c.verify_calendar(view,series,self.table(series['months']))
    def test_cast_specific_terminology_correction_preserves_scientific_values(self):
        correction=self.c.corrections();rows=[]
        for ref in correction['reference_ids']:rows.append({'id':ref,'entity_id':'current:leaf','metric':self.c.METRIC,self.c.REMOVE:True,'source_cast_datetime_utc':'2021-05-01T00:00:00Z','approximate_value_m':123.456})
        view={'evidence':rows,'counts':{'depth_references':9}};saved=copy.deepcopy(view);out=self.c.corrected(view,correction);self.assertEqual(view,saved);self.assertEqual(out['counts'],saved['counts'])
        for a,b in zip(saved['evidence'],out['evidence']):self.assertEqual(a['approximate_value_m'],b['approximate_value_m']);self.assertFalse(b['source_frame_is_mathematical_instant']);self.assertTrue(b['metric_frame_is_cast_specific_not_climatology'])
    def test_readiness_calendar_join_keeps_other_data_index_nonexhaustive(self):
        from build_current_depth_readiness_v2 import join
        view,old=fixture();v,s=self.calendar();s['entity_id']='current:leaf';view['calendar_depth_series']=[s];report=join(view,old,[]);row=next(r for r in report['records'] if r['entity_id']=='current:leaf');self.assertEqual(row['canonical_calendar_depth_series'],[s]);self.assertIsNone(row['physical_annual_depth_range_m']);self.assertIn('not_exhaustive',row['canonical_calendar_index_scope']);self.assertEqual(report['counts']['canonical_censored_calendar_months'],3)

if __name__=='__main__':unittest.main()
