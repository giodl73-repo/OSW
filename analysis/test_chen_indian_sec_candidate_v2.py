import copy
import hashlib
import json
import os
import unittest
from unittest.mock import patch
import check_chen_indian_sec_candidate_v2 as subject

class CandidatePreservation(unittest.TestCase):
    def fixture(self):
        owner='current:indian-south-equatorial'
        before={'schema':'osw.query-bundle.v1','manifest':{'input_sha256':{'prior':'a'*64},'keep':1},'collections':{
            'objects':[{'id':owner,'capabilities':{'reported_length':0}},{'id':'other','width':None}],
            'length_assessments':[{'id':'assessment','entity_id':owner}],
            'current_length_series':[], 'current_length_readings':[], 'sources':[],
            'widths':[{'id':'old-width','width_km':None}],'reference_routes':[{'id':'old-route'}]}}
        c={'parent_logical_sha256':'b'*64,'input_sha256':{'new':'c'*64},
           'final_owner':{'id':owner,'capabilities':{'reported_length':0},'new_series':1},
           'final_length_assessment':{'id':'assessment','entity_id':owner,'regional_series':1},
           'series_record':{'id':'series'},'reading_records':[{'id':'failed','length_km':None},{'id':'qualified','length_km':4700}],
           'sensitivity_records':[{'id':'choice'}],'new_sources':[{'id':'paper'}]}
        after=copy.deepcopy(before);a=after['collections']
        a['objects'][0]=c['final_owner'];a['length_assessments'][0]=c['final_length_assessment']
        a['current_length_series']=[c['series_record']];a['current_length_readings']=c['reading_records'];a['sources']=c['new_sources'];a['current_length_sensitivities']=c['sensitivity_records']
        c['expected_totals']={k:len(v) for k,v in a.items()}
        pin=hashlib.sha256((json.dumps(c,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()).hexdigest()
        after['manifest']['input_sha256'].update(c['input_sha256']);after['manifest']['input_sha256']['research/chen-indian-sec-ridge-length-query-contract-v1.json']=pin
        after['manifest']['indian_sec_model_grid_lengths_v1']={'schema':'osw.indian-sec-model-grid-length-runtime.v1','contract_file':'research/chen-indian-sec-ridge-length-query-contract-v1.json','contract_sha256':pin,'parent_logical_sha256':c['parent_logical_sha256'],'series_added':1,'readings_added':75,'sensitivities_added':120,'qualified_model_grid_lengths':8,'withheld_readings':67,'reported_lengths_added':0,'reference_routes_added':0,'widths_added':0,'physical_state_joins_added':0}
        return before,after,c

    def test_local_refusal_precedes_packet_or_compiler_access(self):
        with patch.dict(os.environ,{},clear=True),patch.object(subject,'read',side_effect=AssertionError('early read')),patch.object(subject.subprocess,'check_output',side_effect=AssertionError('early compiler')):
            with self.assertRaises(ValueError):subject.controls()

    def test_exact_extension_and_unrelated_rows_preserved(self):
        before,after,c=self.fixture();result=subject.verify_extension(before,after,c)
        self.assertEqual(result['unchanged_collections'],2)

    def test_unrelated_data_and_missing_values_cannot_change(self):
        for name in ['widths','reference_routes','objects']:
            before,after,c=self.fixture();after['collections'][name][-1]['unrequested']=0
            with self.assertRaises(ValueError):subject.verify_extension(before,after,c)

    def test_omitted_failed_case_refused(self):
        before,after,c=self.fixture();after['collections']['current_length_readings']=after['collections']['current_length_readings'][1:]
        with self.assertRaises(ValueError):subject.verify_extension(before,after,c)

    def test_historical_manifest_and_receipt_tampering_refused(self):
        for mutation in ['pin','prior','receipt','extra']:
            before,after,c=self.fixture()
            if mutation=='pin':after['manifest']['input_sha256']['prior']='d'*64
            elif mutation=='prior':after['manifest']['keep']=2
            elif mutation=='receipt':after['manifest']['indian_sec_model_grid_lengths_v1']['reported_lengths_added']=1
            else:after['manifest']['extra']=1
            with self.assertRaises(ValueError):subject.verify_extension(before,after,c)

    def test_envelope_or_collection_inventory_changes_refused(self):
        for mutation in ['envelope','collection']:
            before,after,c=self.fixture()
            if mutation=='envelope':after['schema']='other'
            else:after['collections']['unexpected']=[]
            with self.assertRaises(ValueError):subject.verify_extension(before,after,c)

if __name__=='__main__':unittest.main()
