"""Small exact-owner fixtures; complete packet validation remains a cloud gate."""
import copy
import json

import pytest
import baffin_bound_admission as a
import baffin_bound_owner_projection as p


def fixture():
    doc = json.loads(a.read(a.FILE))
    old = p.parent()['owner']
    return doc, {
        'entities': [copy.deepcopy(doc['accepted_entity'])],
        'objects': [copy.deepcopy(old), {'id':'current:other','fingerprint':'keep'}],
        'length_assessments': [copy.deepcopy(doc['prior_length_assessment'])],
        'measurements': [],
        'claims': [{'id':'prior:claim:'+str(i),'subject_id':a.ENTITY,
                    'source_id':old['source_ids'][0],'review_status':'not_individually_reviewed'}
                   for i in range(old['recorded_claims'])],
        'sources': [{'id':identity} for identity in old['source_ids']],
        'widths': [{'id':identity,'current_id':'baffin','source_id':old['source_ids'][0]}
                   for identity in old['width_ids']],
        'geometries': [{'id':'prior:geometry','entity_id':a.ENTITY}],
    }


def test_exact_owner_preparation_preserves_physics_and_prior_rows():
    doc, collections = fixture()
    before = copy.deepcopy(collections)
    staged, receipt = p.prepare(collections, doc)
    assert collections == before
    old = before['objects'][0]
    new = staged['objects'][0]
    for key in old:
        if key not in p.METADATA_FIELDS:
            assert new[key] == old[key], key
    assert new['measurement_ids'] == [a.MEASUREMENT]
    assert new['capabilities']['reported_length'] == 0
    assert new['capabilities']['scoped_width'] == 2
    assert new['linked_source_count'] == len(new['source_ids']) == old['linked_source_count'] + 2
    assert new['recorded_claims'] == old['recorded_claims'] + 1
    assert staged['objects'][1] == before['objects'][1]
    assert receipt['owner_projection_verified'] is True
    assert receipt['working_delivery_verified'] is False
    for key in ['routes_geometry','time_evidence','identity','media']:
        assert new['section_fingerprints'][key] == old['section_fingerprints'][key]
    for key in ['measurements','sources','claims']:
        assert new['section_fingerprints'][key] != old['section_fingerprints'][key]
    assert staged['widths'] == before['widths']


@pytest.mark.parametrize('change', ['geometry','capability','date','width-ids','claim-count','duplicate-owner'])
def test_changed_parent_owner_rejects_atomically(change):
    doc, collections = fixture()
    owner = collections['objects'][0]
    if change == 'geometry': owner['map_features'][0]['geometry']['coordinates'] = [0,0]
    if change == 'capability': owner['capabilities']['geometry'] = 1
    if change == 'date': owner['latest_observation_date'] = '2026-10-24'
    if change == 'width-ids': owner['width_ids'].pop()
    if change == 'claim-count': owner['recorded_claims'] += 1
    if change == 'duplicate-owner': collections['objects'].append(copy.deepcopy(owner))
    before = copy.deepcopy(collections)
    with pytest.raises(ValueError, match='verified parent Baffin owner'):
        p.prepare(collections, doc)
    assert collections == before


@pytest.mark.parametrize('change', ['missing-claim','changed-review','missing-width','new-measurement','unregistered-source','unexpected-source'])
def test_incoherent_evidence_inventory_rejects_atomically(change):
    doc, collections = fixture()
    if change == 'missing-claim': collections['claims'].pop()
    if change == 'changed-review': collections['claims'][0]['review_status'] = 'reviewed'
    if change == 'missing-width': collections['widths'].pop()
    if change == 'new-measurement': collections['measurements'].append({'id':'other:measurement','entity_id':a.ENTITY})
    if change == 'unregistered-source': collections['sources'].pop()
    if change == 'unexpected-source':
        collections['sources'].append({'id':'source:unexpected'})
        collections['claims'][0]['source_id'] = 'source:unexpected'
    before = copy.deepcopy(collections)
    with pytest.raises(ValueError): p.prepare(collections, doc)
    assert collections == before


def test_transition_stays_prepared_and_binds_the_verified_parent():
    document = json.loads(a.read(p.FILE))
    assert a.encoded(document) == a.encoded(p.build_transition())
    assert document['parent_owner_sha256'] == p.PARENT_SHA
    assert document['working_delivery_verified'] is False
    assert document['owner']['evidence_transition']['scientific_source_inputs_recomputed'] is False
