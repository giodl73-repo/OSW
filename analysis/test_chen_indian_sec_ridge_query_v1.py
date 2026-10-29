import copy
import unittest
import chen_indian_sec_ridge_query_v1 as subject


class QueryAdmissionGuards(unittest.TestCase):
    def fixture(self,contract):
        selected=contract['prior_records'];owned={}
        for owner in [subject.FAMILY,subject.ENTITY]:
            data=selected['identities'][owner]
            for name,key in [('objects','object'),('entities','entity')]:owned.setdefault(name,[]).append(copy.deepcopy(data[key]))
            for name,rows in data['linked_records'].items():owned.setdefault(name,[]).extend(copy.deepcopy(rows))
            owned.setdefault('sources',[]).extend(copy.deepcopy(data['owner_sources']))
        required=set(owned)|{'objects','entities','sources','length_assessments','current_length_series','current_length_readings','widths','reference_routes'}
        collections={}
        for name in required:
            unique={}
            for row in owned.get(name,[]):unique.setdefault(row['id'],row)
            rows=list(unique.values())
            count=contract['parent_collection_counts'][name]
            for index in range(count-len(rows)):
                row={'id':'fixture:'+name+':'+str(index)}
                if name=='length_assessments':row['entity_id']='fixture:other:'+str(index)
                rows.append(row)
            collections[name]=rows
        return collections,{'input_sha256':{},'fixture_untouched':{'value':1}}

    def test_all_values_failures_and_sensitivities_are_first_class(self):
        c=subject.build_contract()
        self.assertEqual(len(c['reading_records']),75)
        self.assertEqual(sum(r['length_km'] is not None for r in c['reading_records']),8)
        self.assertEqual(sum(r['geometry'] is None for r in c['reading_records']),67)
        self.assertEqual(len(c['sensitivity_records']),120)
        ids={r['id'] for r in c['reading_records'] if r['length_km'] is not None}
        self.assertTrue(all(r['reading_id'] in ids for r in c['sensitivity_records']))

    def test_append_changes_only_declared_rows_and_preserves_physical_gaps(self):
        c=subject.build_contract();before,manifest=self.fixture(c)
        snapshot=copy.deepcopy(before)
        after,updated=subject.prepare(before,manifest,c,parent_logical_sha256=subject.PARENT)
        self.assertEqual(before,snapshot)
        self.assertEqual(len(after[subject.READINGS]),1687)
        self.assertEqual(len(after[subject.SERIES]),2)
        self.assertEqual(len(after['sources']),222)
        self.assertEqual(len(after[subject.SENSITIVITIES]),120)
        self.assertEqual(next(r for r in after['objects'] if r['id']==subject.FAMILY),c['prior_records']['identities'][subject.FAMILY]['object'])
        owner=next(r for r in after['objects'] if r['id']==subject.ENTITY)
        self.assertIsNone(owner['published_length_km'])
        self.assertEqual(owner['capabilities']['reported_length'],0)
        self.assertEqual(owner['capabilities']['reference_route'],0)
        for name in before:
            if name not in ['objects','sources','length_assessments',subject.SERIES,subject.READINGS]:self.assertIs(after[name],before[name])
        self.assertEqual(updated['fixture_untouched'],manifest['fixture_untouched'])

    def test_deleted_withheld_case_or_changed_ownership_rejected(self):
        c=subject.build_contract();data,manifest=self.fixture(c)
        for kind in ['delete','owner']:
            altered=copy.deepcopy(c)
            if kind=='delete':altered['reading_records'].pop(0)
            else:altered['reading_records'][0]['entity_id']=subject.FAMILY
            with self.assertRaises(ValueError):subject.prepare(data,manifest,altered,parent_logical_sha256=subject.PARENT)

    def test_false_whole_current_claim_or_uncertainty_rejected(self):
        c=subject.build_contract();data,manifest=self.fixture(c)
        altered=copy.deepcopy(c);altered['series_record']['whole_current_length_km']=4700
        with self.assertRaises(ValueError):subject.prepare(data,manifest,altered,parent_logical_sha256=subject.PARENT)
        altered=copy.deepcopy(c);altered['sensitivity_records'][0]['is_physical_uncertainty']=True
        with self.assertRaises(ValueError):subject.prepare(data,manifest,altered,parent_logical_sha256=subject.PARENT)

    def test_new_source_id_collision_refused(self):
        c=subject.build_contract();data,manifest=self.fixture(c)
        filler=next(r for r in data['sources'] if r['id'].startswith('fixture:'))
        filler['id']=subject.SOURCE_IDS[0]
        with self.assertRaises(ValueError):subject.prepare(data,manifest,c,parent_logical_sha256=subject.PARENT)

    def test_parent_owner_or_source_change_refused(self):
        c=subject.build_contract()
        for kind in ['owner','source']:
            data,manifest=self.fixture(c)
            if kind=='owner':next(r for r in data['objects'] if r['id']==subject.ENTITY)['published_length_km']=100
            else:
                old=c['prior_records']['identities'][subject.ENTITY]['owner_sources'][0]['id']
                next(r for r in data['sources'] if r['id']==old)['label']='changed'
            with self.assertRaises(ValueError):subject.prepare(data,manifest,c,parent_logical_sha256=subject.PARENT)

    def test_reapplication_or_wrong_logical_parent_refused(self):
        c=subject.build_contract();data,manifest=self.fixture(c)
        after,updated=subject.prepare(data,manifest,c,parent_logical_sha256=subject.PARENT)
        with self.assertRaises(ValueError):subject.prepare(after,updated,c,parent_logical_sha256=subject.PARENT)
        with self.assertRaises(ValueError):subject.prepare(data,manifest,c,parent_logical_sha256='wrong')

    def test_display_interpolation_preserves_gates_and_ten_km_limit(self):
        points=[[105,-11],[104,-12]];g=subject.display_geometry(points)
        self.assertEqual(g['coordinates'][0],points[0]);self.assertEqual(g['coordinates'][-1],points[-1])
        self.assertTrue(all(subject.science.GEOD.inv(*a,*b)[2]<=10000.00001 for a,b in zip(g['coordinates'],g['coordinates'][1:])))


if __name__=='__main__':unittest.main()
