"""Check complete two-sided archive coverage and unchanged source metadata."""
import json

from redsox_provider_station_support import ROOT, REPORT, LADCP, CTD, encoded


def test_every_provider_profile_and_original_join_preserved():
    raw = (ROOT / REPORT).read_bytes()
    assert raw == encoded()
    report = json.loads(raw)
    velocity = json.loads((ROOT / LADCP).read_bytes())
    hydrography = json.loads((ROOT / CTD).read_bytes())
    assert len(report['profiles']) == len(velocity['profiles']) == 445
    assert [r['velocity_metadata'] for r in report['profiles']] == velocity['profiles']
    lookup = {r['id']: r for r in hydrography['profiles']}
    seen = set()
    joins = []
    for row in report['profiles']:
        other = row['ctd_metadata']
        if other is not None:
            assert other == lookup[other['id']]
            assert other['id'] not in seen
            seen.add(other['id']); joins.append(row['assessment']['original_filename_join'])
            original_offset = row['assessment']['original_filename_join']['ctd_start_minus_ladcp_header_time_seconds']
            new_offset = row['assessment']['ladcp_minus_ctd_start_seconds']
            assert new_offset == (None if original_offset is None else -original_offset)
        assert not row['assessment']['physical_cast_identity_verified']
        assert not row['assessment']['sample_level_synchronization_verified']
        assert not row['measurement_processing_exclusions_cleared']
        assert not row['physical_width_admitted']
    assert joins == hydrography['filename_joins']
    unmatched = report['ctd_records_without_ladcp']
    assert {r['id'] for r in unmatched} == set(lookup) - seen
    assert all(r == lookup[r['id']] for r in unmatched)
    assert len(seen) + len(unmatched) == len(lookup) == 461
    assert [r['id'] for r in report['profiles'] if r['ctd_metadata'] is None] == hydrography['unmatched_ladcp_ids']
    assert not report['new_width_record_admitted']
