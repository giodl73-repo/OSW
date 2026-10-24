"""Small fixtures only; never load the complete atlas on the user's computer."""
import copy

import pytest

import check_current_gap_parent_rehearsal as a


def test_replay_accepts_only_baseline_or_the_verified_installed_cohort():
    current = {'schema':'osw.query-packet.v1','logical_sha256':a.PARENT_SHA}
    a.verify_current_packet(current, {})
    current['logical_sha256'] = 'installed-candidate'
    proof = {'status':'verified_cloud_delivery','cohort_version':'indian-coastal-brazil-t24-v1',
             'parent_logical_sha256':a.PARENT_SHA,'packet_logical_sha256':'installed-candidate',
             'native_verified':True,'browser_verified':True}
    a.verify_current_packet(current, proof)
    for field, value in [('cohort_version','future-cohort'), ('packet_logical_sha256','different'),
                         ('parent_logical_sha256','other-parent'), ('browser_verified',False),
                         ('native_verified',False), ('status','prepared')]:
        bad = {**proof,field:value}
        with pytest.raises(ValueError): a.verify_current_packet(current,bad)
    with pytest.raises(ValueError): a.verify_current_packet(current,{})


def test_parent_transport_snapshot_is_pinned_without_loading_any_parts():
    import hashlib
    import json
    raw = (a.ROOT / a.PARENT_PACKET).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == a.PARENT_PACKET_SHA
    packet = json.loads(raw)
    assert packet['logical_sha256'] == a.PARENT_SHA
    assert packet['logical_byte_length'] == 187116909
    assert len(packet['parts']) == 12


def test_original_row_content_and_order_are_verified():
    old = {'objects': [{'id': 'current:x', 'published_length_km': 10, 'capabilities': {'scoped_width': 1}}],
           'measurements': [{'id': 'one', 'value': 1}, {'id': 'two', 'value': 2}]}
    pins = a.capture_prior(old)
    old_objects = a.capture_objects(old['objects'])
    candidate = copy.deepcopy(old)
    candidate['measurements'].append({'id': 'three', 'value': 3})
    candidate['objects'][0].update(source_ids=['source:new'], linked_source_count=1)
    assert a.verify_preservation(pins, old_objects, candidate)['all_prior_nonobject_rows_exact']
    for mutation in ('value', 'order', 'erase'):
        bad = copy.deepcopy(candidate)
        if mutation == 'value': bad['measurements'][0]['value'] = 2
        elif mutation == 'order': bad['measurements'][:2] = list(reversed(bad['measurements'][:2]))
        else: bad['measurements'].clear()
        with pytest.raises(ValueError): a.verify_preservation(pins, old_objects, bad)


@pytest.mark.parametrize('field,value', [('published_length_km', 20), ('map_features', [{'new': 'geometry'}]), ('capabilities', {'scoped_width': 2})])
def test_old_physical_object_fields_and_capabilities_cannot_change(field, value):
    old = [{'id': 'current:x', 'published_length_km': 10, 'map_features': [], 'capabilities': {'scoped_width': 1}}]
    row = {**copy.deepcopy(old[0]), field: value}
    with pytest.raises(ValueError): a.verify_preservation({}, a.capture_objects(old), {'objects': [row]})


@pytest.mark.parametrize('disk,memory', [(0, 8*1024**3), (2*1024**3, None), (2*1024**3, 1024**3)])
def test_insufficient_resources_block_before_packet_loading(disk, memory):
    with pytest.raises(ValueError, match='no packet loaded'): a.resources(disk, memory)


def test_resource_preflight_accepts_declared_minimums():
    a.resources(2*1024**3, 3*1024**3)


def test_unchanged_record_cannot_be_spuriously_marked_updated():
    old = [{'id': 'current:x', 'published_length_km': 10, 'capabilities': {},
            'fingerprint': 'original', 'section_fingerprints': {'sources': 'unchanged'}}]
    snapshot = a.capture_objects(old)
    changed = copy.deepcopy(old)
    changed[0]['fingerprint'] = 'unnecessary-new-fingerprint'
    with pytest.raises(ValueError, match='spuriously'):
        a.verify_preservation({}, snapshot, {'objects': changed})
