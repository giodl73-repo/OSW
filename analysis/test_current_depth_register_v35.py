"""Verify targeted distance-datum corrections without changing measurements."""
import copy
import csv
import hashlib
import io
import json
import unittest
import build_current_depth_register_v34 as previous
import build_current_depth_register_v35 as depth


class CoreThicknessDatumNormalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prior=previous.build();cls.data=depth.build()
        cls.manifest=json.loads((depth.ROOT/depth.CORRECTIONS).read_bytes())
        cls.ids={r['entity_id'] for r in cls.data['records']};cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def test_only_three_metadata_records_change_and_all_numbers_preserved(self):
        changed=[]
        for old,new in zip(self.prior['evidence'],self.data['evidence']):
            if old!=new:
                changed.append(old['id']);restored=copy.deepcopy(new)
                restored['vertical_datum']=restored.pop('source_record_vertical_datum')
                restored.pop('normalization_file');restored.pop('normalization_rule_id')
                self.assertEqual(restored,old)
        self.assertEqual(changed,depth.IDS)
        self.assertEqual(self.data['counts'],self.prior['counts']);self.assertEqual(self.data['records'],self.prior['records'])
        self.assertFalse(self.data['previous_evidence_preserved']);self.assertTrue(self.data['previous_evidence_numerical_values_preserved'])

    def test_core_span_uses_distance_datum_with_original_label_retained(self):
        rows=[r for r in self.data['evidence'] if r['metric']=='core_vertical_thickness']
        self.assertEqual([r['approximate_value_m'] for r in rows],[57,1719,1025])
        for row in rows:
            self.assertEqual(row['vertical_datum'],'not_applicable_thickness_distance')
            self.assertEqual(row['source_record_vertical_datum'],'local_sea_surface_positive_down')
            self.assertEqual(row['normalization_file'],depth.CORRECTIONS)
            depth.validate_reference(row,self.ids,self.metrics)

    def test_correction_manifest_cannot_change_other_fields_or_rows(self):
        for key,value in [('field','approximate_value_m'),('normalized_value','local_sea_surface_positive_down'),('reference_id','unreviewed-reference'),('prior_reference_sha256','0'*64)]:
            manifest=copy.deepcopy(self.manifest);manifest['corrections'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):depth.normalize(self.prior,manifest)
        manifest=copy.deepcopy(self.manifest);manifest['corrections'].pop()
        with self.assertRaises(ValueError):depth.normalize(self.prior,manifest)

    def test_distance_rule_keeps_threshold_model_and_geometry_validation(self):
        row=next(r for r in self.data['evidence'] if r['id']==depth.IDS[0])
        for key,value in [('vertical_datum','local_sea_surface_positive_down'),('velocity_threshold_m_s',0.01),('velocity_threshold_operator','>='),('model_product','ORAS5'),('climatology_years',[2001,2015]),('thickness_m',57),('volume_eligible',True)]:
            changed=copy.deepcopy(row);changed[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):depth.validate_reference(changed,self.ids,self.metrics)

    def test_previous_files_and_manifest_hash_pins_preserved(self):
        self.assertEqual(json.loads((depth.ROOT/previous.OUTPUT).read_bytes()),self.prior)
        for path,digest in self.data['input_sha256'].items():self.assertEqual(hashlib.sha256((depth.ROOT/path).read_bytes()).hexdigest(),digest)
        self.assertEqual(self.data['new_depth_references'],0);self.assertEqual(self.data['metadata_correction_count'],3)

    def test_json_csv_keep_provenance_and_unchanged_numeric_values(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        raw=depth.csv_bytes(self.data);self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),raw)
        rows={r['id']:r for r in csv.DictReader(io.StringIO(raw.decode('utf8')))}
        for id,value in zip(depth.IDS,[57,1719,1025]):
            self.assertEqual(float(rows[id]['approximate_value_m']),value)
            self.assertEqual(rows[id]['vertical_datum'],'not_applicable_thickness_distance')
            self.assertEqual(rows[id]['source_record_vertical_datum'],'local_sea_surface_positive_down')
            self.assertEqual(rows[id]['normalization_file'],depth.CORRECTIONS)

    def test_member_lookup_refresh_adds_no_measurements(self):
        index=depth.build_member_index(self.data)
        self.assertEqual(json.loads((depth.ROOT/depth.MEMBER_OUTPUT).read_bytes()),index)
        self.assertEqual(index['depth_register_file'],depth.OUTPUT)
        self.assertEqual(index['counts']['distinct_member_depth_references'],46)
        self.assertEqual(index['counts']['new_measurements'],0)
        old=json.loads((depth.ROOT/'research/current-depth-member-index-v4.json').read_bytes())
        self.assertEqual(index['records'],old['records']);self.assertEqual(index['counts'],old['counts'])


if __name__=='__main__':unittest.main()
