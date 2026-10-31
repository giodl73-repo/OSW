import csv
import hashlib
import json
import unittest
import build_current_width_register_v1 as register


class WidthRegister(unittest.TestCase):
    def test_complete_inventory_and_exact_source_custody(self):
        document=register.build();rows=document['records'];evidence=document['evidence']
        self.assertEqual(len(rows),111);self.assertEqual(len({r['entity_id'] for r in rows}),111)
        self.assertEqual(len(evidence),191);self.assertEqual(len({r['id'] for r in evidence}),191)
        self.assertEqual(document['counts']['identities_with_retained_scoped_evidence'],93)
        self.assertEqual(document['counts']['identities_with_direct_width_reference'],94)
        self.assertFalse(document['full_goal_complete'])
        for path,pin in document['input_sha256'].items():
            self.assertEqual(hashlib.sha256((register.ROOT/path).read_bytes()).hexdigest(),pin)
        for row in evidence:
            source=json.loads((register.ROOT/row['source_file']).read_bytes())
            self.assertEqual(register.pointer(source,row['source_pointer']),row['raw_record'])
            self.assertTrue(row['source_url']);self.assertTrue(row['source_locator'])

    def test_bounds_ranges_and_confinement_are_not_fabricated_point_widths(self):
        evidence={r['id']:r for r in register.build()['evidence']}
        lower=evidence['eacc-dekeyzer-2012-bell-cited-width-lower-bound']
        self.assertEqual(lower['lower_bound_km'],160);self.assertTrue(lower['lower_bound_exclusive']);self.assertIsNone(lower['point_km'])
        constraint=evidence['ngcu-zenk-1999-vitiaz-width-constraint']
        self.assertIsNone(constraint['upper_bound_km']);self.assertIsNone(constraint['point_km'])
        self.assertEqual(constraint['constraint']['reference_scale_km'],20)
        source_zero=evidence['neuc-glider-2015-northern-jet-range']
        self.assertEqual(source_zero['range_km'],[0,200]);self.assertTrue(source_zero['zero_range_endpoint_as_reported']);self.assertIsNone(source_zero['point_km'])
        sjc=evidence['south-java-sprintall-2010-ombai-thermal-front-confinement-reference']
        self.assertIsNone(sjc['point_km']);self.assertIsNone(sjc['range_km'])
        self.assertEqual(sjc['constraint']['reference_range_km'],[10,15])
        self.assertEqual(sjc['evidence_role'],'new_qualified_reference')
        for r in evidence.values():
            if r['raw_record'].get('approximate_width_km') is None and r['raw_record'].get('width_range_km'):
                self.assertIsNone(r['point_km'])

    def test_family_and_regional_records_do_not_create_whole_current_widths(self):
        document=register.build();by_id={r['entity_id']:r for r in document['records']}
        families=[r for r in document['records'] if r['identity_level']=='family']
        self.assertEqual(len(families),8)
        self.assertTrue(all(r['member_references'] and not r['evidence_ids'] for r in families))
        self.assertFalse(by_id['current:gulf-stream-system']['evidence_ids'])
        for r in document['records']:
            self.assertIsNone(r['whole_current_representative_width_km'])
            self.assertIsNone(r['annual_width_range_km'])
            self.assertFalse(r['physical_area_from_length_times_width_eligible'])
        krug=next(r for r in document['evidence'] if r['id']=='agulhas-krug-2012-altimetry-gaussian-core-mean-width')
        self.assertEqual(krug['point_km'],64)
        self.assertTrue(krug['quality_note']['source_operator_ambiguity'])

    def test_generated_csv_keeps_values_and_record_provenance(self):
        records={r['id']:r for r in register.build()['evidence']}
        with (register.ROOT/register.CSV_PATH).open(encoding='utf8',newline='') as stream:
            exported=list(csv.DictReader(stream))
        self.assertEqual(len(exported),191)
        for row in exported:
            source=records[row['id']]
            self.assertEqual(row['point_km'],str(source['point_km']) if source['point_km'] is not None else '')
            self.assertEqual(row['source_file'],source['source_file']);self.assertEqual(row['source_pointer'],source['source_pointer'])
            self.assertEqual(row['constraint_json'],json.dumps(source['constraint'],ensure_ascii=False) if source['constraint'] else '')


if __name__=='__main__':unittest.main()
