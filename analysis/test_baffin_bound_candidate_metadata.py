"""Small preservation/receipt fixtures; no full query packet is loaded."""
import copy
import json

import pytest
import baffin_bound_admission as a
import baffin_bound_candidate_metadata as m
from test_baffin_bound_owner_projection import fixture as owner_fixture


def fixture():
    doc, collections = owner_fixture()
    collections['objects'][1]['type'] = 'named_current'
    dashboard = {'schema':'osw.motion-dashboard.v1','fingerprint_version':2,
                 'entries':copy.deepcopy(collections['objects']),
                 'snapshot_fingerprint':m.fingerprint(collections['objects']),
                 'counts':{'named_current':2}, 'built_at_utc':'2026-10-24T00:00:00Z',
                 'candidate_delivery':{'version':'previous','published':False}}
    raw = m.encoded(dashboard)
    manifest = {'davidson_reported_width_version':'wallace-line67-v1',
                'input_sha256':{m.DASHBOARD:m.digest(raw)},
                'editorial_collections':['objects','current_length_bound_admissions'],
                'dashboard_receipt':{'source_file':m.DASHBOARD,'source_sha256':m.digest(raw),'source_json':raw.decode()}}
    return doc, collections, manifest, raw


def test_coherent_metadata_and_owner_preparation_do_not_change_inputs():
    doc, collections, manifest, raw = fixture()
    before = copy.deepcopy((collections,manifest))
    meta, staged, dashboard_raw, receipt = m.prepare(manifest,collections,raw,doc,prepared_at_utc='2026-10-24T01:00:00Z')
    assert (collections,manifest) == before
    dashboard = json.loads(dashboard_raw)
    assert dashboard['entries'] == staged['objects']
    assert dashboard['snapshot_fingerprint'] == m.fingerprint(staged['objects'])
    assert dashboard['counts'] == {'named_current':2}
    assert dashboard['built_at_utc'] == '2026-10-24T01:00:00Z'
    assert staged['objects'][0]['latest_observation_date'] == collections['objects'][0]['latest_observation_date']
    assert meta[a.VERSION_KEY] == '1'
    assert meta['editorial_collections'].count('current_length_bound_scenarios') == 1
    assert meta['dashboard_receipt']['source_json'] == dashboard_raw.decode()
    assert meta['input_sha256'][m.DASHBOARD] == m.digest(dashboard_raw)
    assert receipt['preservation']['all_other_prior_nonobject_rows_exact'] is True
    assert receipt['preservation']['unchanged_objects_verified'] == 1
    assert receipt['working_delivery_verified'] is False


@pytest.mark.parametrize('change', ['receipt','projection','version','replay','dependency','collections'])
def test_incoherent_parent_or_unsafe_replay_rejects_without_mutation(change):
    doc, collections, manifest, raw = fixture()
    if change == 'receipt': manifest['dashboard_receipt']['source_sha256'] = '0'*64
    if change == 'projection':
        document = json.loads(raw);document['snapshot_fingerprint'] = 'changed'
        raw = m.encoded(document)
        manifest['dashboard_receipt'].update(source_sha256=m.digest(raw),source_json=raw.decode())
        manifest['input_sha256'][m.DASHBOARD] = m.digest(raw)
    if change == 'version': manifest['davidson_reported_width_version'] = 'other'
    if change == 'replay': manifest[a.VERSION_KEY] = '1'
    if change == 'dependency': manifest['input_sha256'][next(iter(doc['input_sha256']))] = 'changed'
    if change == 'collections': manifest['editorial_collections'] = ['objects','objects']
    before = copy.deepcopy((collections,manifest))
    with pytest.raises(ValueError): m.prepare(manifest,collections,raw,doc,prepared_at_utc='2026-10-24T01:00:00Z')
    assert (collections,manifest) == before


@pytest.mark.parametrize('collection', ['claims','widths','geometries','objects','length_assessments','current_length_bound_scenarios'])
def test_postpreparation_corruption_is_not_misreported_as_preservation(collection):
    doc, collections, manifest, raw = fixture()
    _, staged, _, _ = m.prepare(manifest,collections,raw,doc,prepared_at_utc='2026-10-24T01:00:00Z')
    if collection == 'current_length_bound_scenarios': staged[collection].append(copy.deepcopy(staged[collection][0]))
    else:
        staged[collection] = copy.deepcopy(staged[collection])
        staged[collection][0]['id'] = 'corrupt'
    with pytest.raises(ValueError): m.verify_preservation(collections,staged,doc)


@pytest.mark.parametrize('collection,key,value', [
    ('measurements','value',1100), ('claims','source_id','source:other'),
    ('sources','original_sha256','0'*64),
    ('current_length_bound_admissions','rank_eligible',True),
    ('current_length_bound_scenarios','is_observation',True)])
def test_correct_append_count_cannot_hide_changed_evidence_values(collection,key,value):
    doc, collections, manifest, raw = fixture()
    _, staged, _, _ = m.prepare(manifest,collections,raw,doc,prepared_at_utc='2026-10-24T01:00:00Z')
    staged[collection] = copy.deepcopy(staged[collection])
    staged[collection][len(collections.get(collection,[]))][key] = value
    with pytest.raises(ValueError,match='unexpected append'):
        m.verify_preservation(collections,staged,doc)


def test_scenario_order_and_source_identity_cannot_change_with_same_counts():
    doc, collections, manifest, raw = fixture()
    _, staged, _, _ = m.prepare(manifest,collections,raw,doc,prepared_at_utc='2026-10-24T01:00:00Z')
    staged['current_length_bound_scenarios'] = list(reversed(staged['current_length_bound_scenarios']))
    with pytest.raises(ValueError,match='unexpected append'):
        m.verify_preservation(collections,staged,doc)


def parent_fixture():
    packet = json.loads(a.read('research/davidson-width-parent-query-packet-v1.json'))
    packet['logical_sha256'] = 'e'*64
    installed = {'schema':'osw.davidson-width-installed-delivery.v1','status':'verified_cloud_delivery',
                 'cohort_version':'davidson-wallace-line67-v1',
                 'parent_logical_sha256':m.owner.parent()['parent_logical_sha256'],
                 'packet_logical_sha256':packet['logical_sha256'],
                 'candidate':{'logical_sha256':packet['logical_sha256'],'logical_bytes':packet['logical_byte_length'],
                              'objects':246,'named_currents':106,'widths':172,'rows':108530},
                 'native_verified':True,'browser_verified':True,'working_dataset_delivery_verified':True,
                 'scientific_release_published':False,'main_merged':False}
    return packet, installed


def test_preceding_delivery_receipt_shape_and_transport_match():
    packet, installed = parent_fixture()
    m.validate_parent(packet,installed)


@pytest.mark.parametrize('key,value', [('status','prepared'),('cohort_version','other'),
    ('native_verified',False),('browser_verified',False),('working_dataset_delivery_verified',False),
    ('scientific_release_published',True),('main_merged',True),('packet_logical_sha256','a'*64)])
def test_prepared_or_unverified_parent_cannot_advance(key,value):
    packet, installed = parent_fixture()
    installed[key] = value
    with pytest.raises(ValueError): m.validate_parent(packet,installed)


def test_old_106_transport_cannot_masquerade_as_davidson_delivery():
    packet, installed = parent_fixture()
    packet['logical_sha256'] = m.owner.parent()['parent_logical_sha256']
    installed['packet_logical_sha256'] = packet['logical_sha256']
    installed['candidate']['logical_sha256'] = packet['logical_sha256']
    with pytest.raises(ValueError): m.validate_parent(packet,installed)
