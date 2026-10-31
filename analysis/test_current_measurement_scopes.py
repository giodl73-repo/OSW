"""Scope metadata cannot become borrowed dimensions or admitted aliases."""
from pathlib import Path
import copy,hashlib
from unittest.mock import patch
import json,unittest,xml.etree.ElementTree as ET
import build_current_measurement_scopes as scope

class MeasurementScopeTests(unittest.TestCase):
    def test_complete_worklist_reconstructs_without_numeric_admission(self):
        index=scope.verify()
        self.assertEqual(index['counts'],{'basin_family':8,'unresolved_name':2,'continuity_hypothesis':1,'passage_network':1,'compound_current_system':1})
        self.assertEqual(len(index['records']),13)
        for record in index['records']:
            doc=record['document']
            self.assertIsNone(doc['parent_width_km']);self.assertIsNone(doc['annual_width_range_km'])
            for key in ['new_width_record_admitted','member_measurements_inherited','aliases_resolved','physical_taxonomy_admitted','physical_edge_geometry_admitted','observation_date_inherited']:
                self.assertIs(doc[key],False)
            self.assertEqual(doc['prior_width_decision'],'width_not_assessed')

    def test_explicit_members_proposals_and_related_names_stay_distinct(self):
        reports,_,_,_=scope.build();by_id={r['current_id']:r for r in reports.values()}
        north=by_id['north-equatorial']['members']
        self.assertEqual([m['id'] for m in north],['atlantic-north-equatorial','pacific-north-equatorial'])
        self.assertTrue(all(m['record_status']=='proposed' and m['scoped_width_record_count'] is None for m in north))
        norwegian=by_id['norwegian']['members']
        self.assertTrue(all(m['relationship']=='related_name_not_equated' for m in norwegian))
        australian=by_id['australian-west-south-boundary-flow']
        self.assertEqual([m['id'] for m in australian['members']],['leeuwin','south-australian','zeehan'])
        self.assertGreater(sum(m['scoped_width_record_count'] for m in australian['members']),0)
        self.assertIsNone(australian['parent_width_km'])
        self.assertTrue(all(m['width_values_inherited_by_parent'] is False for m in australian['members']))

    def test_proposed_members_never_become_released_record_links(self):
        _,_,notes,_=scope.build()
        for note in notes['entries']:
            if note.get('measurement_scope_assessment'):
                self.assertFalse(set(note['related_current_ids'])&set(note['related_proposed_current_ids']))
                self.assertIsNone(note['observed_period'])

    def test_source_change_rejects_before_generating_scope(self):
        with patch.object(scope,'digest',return_value='0'*64),self.assertRaisesRegex(ValueError,'Changed object-scope input'):
            scope.build()

    def test_promoted_generated_record_is_rejected(self):
        path=scope.ROOT/scope.path_for('north-equatorial')
        original=Path.read_bytes
        changed=json.loads(original(path));changed['parent_width_km']=100
        def altered(candidate):return scope.encoded(changed) if candidate==path else original(candidate)
        with patch.object(Path,'read_bytes',altered),self.assertRaisesRegex(ValueError,'Stale object-scope artifact'):
            scope.verify()

    def test_diagrams_have_text_alternatives_without_geographic_geometry(self):
        _,figures,_,_=scope.build();self.assertEqual(len(figures),13)
        ns={'s':'http://www.w3.org/2000/svg'}
        for raw in figures.values():
            svg=ET.fromstring(raw)
            self.assertEqual(svg.attrib['role'],'img')
            self.assertIn('not a geographic map',svg.find('s:desc',ns).text)
            self.assertFalse(svg.findall('.//s:path',ns))
            self.assertIn('not inherited',raw.decode())

    def test_member_update_changes_only_the_dependent_assessment(self):
        before,_,_,_=scope.build()
        name='research/ocean-current-width-inventory.json';path=scope.ROOT/name
        original=Path.read_bytes;data=json.loads(original(path))
        row=copy.deepcopy(next(r for r in data['measurements'] if r['current_id']=='leeuwin'))
        row['id']='synthetic-new-leeuwin-evidence';data['measurements'].append(row)
        raw=scope.encoded(data)
        def altered(candidate):return raw if candidate==path else original(candidate)
        with patch.object(Path,'read_bytes',altered),patch.dict(scope.FROZEN_INPUTS,{name:hashlib.sha256(raw).hexdigest()}):
            after,_,_,_=scope.build()
        self.assertEqual([r['current_id'] for p,r in before.items() if r!=after[p]],['australian-west-south-boundary-flow'])

if __name__=='__main__':unittest.main()
