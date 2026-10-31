"""Source integrity and independent statistical checks for ASCA sections."""
import json
import shutil
import statistics as independent

import numpy as np
import pytest

import build_asca_100m_sections as sections
import check_asca_100m_source as source


@pytest.fixture(scope='module')
def packets():
    return sections.build()


def test_missing_and_singleton_spread_are_not_zero_or_error_bars():
    values = np.array([[np.nan, 2, 1], [np.nan, np.nan, 3]], dtype='float32')
    result = sections.statistics(values)
    assert result['valid_count'] == [0, 1, 2]
    assert result['mean'] == [None, 2, 2]
    assert result['sample_sd'][:2] == [None, None]
    assert result['sample_sd'][2] == pytest.approx(2 ** .5)


def test_paired_population_is_distinct_from_component_population():
    v = np.array([[1, 4], [9, 6]], dtype='float32')
    u = np.array([[2, np.nan], [np.nan, 8]], dtype='float32')
    paired = np.isfinite(v) & np.isfinite(u)
    assert sections.statistics(v)['mean'] == [5, 5]
    assert sections.statistics(v, paired)['mean'] == [1, 6]
    assert sections.statistics(u, paired)['valid_count'] == [1, 1]
    assert sections.statistics(v, paired)['sample_sd'] == [None, None]


def test_original_float_bits_null_masks_and_timestamps_round_trip(packets):
    raw, monthly = packets
    _, coords, arrays = source.load()
    assert len(raw['profiles']) == 931
    for field in source.FIELDS:
        restored = np.array([[np.nan if x is None else x for x in p['fields'][field]]
                             for p in raw['profiles']], dtype='>f4')
        mask = np.isfinite(arrays[field])
        assert np.array_equal(np.isfinite(restored), mask)
        assert np.array_equal(restored.view('>u4')[mask], arrays[field].view('>u4')[mask])
    assert [p['source_epoch_seconds'] for p in raw['profiles']] == coords['time'].tolist()
    assert [p['observed_at'] for p in raw['profiles']] == [sections.iso(t) for t in coords['time']]
    assert len({p['id'] for p in raw['profiles']}) == 931
    assert sum(f['sample_count'] for f in monthly['frames']) == 931


def test_calendar_years_partial_bins_and_quantization_are_explicit(packets):
    raw, monthly = packets
    frames = monthly['frames']
    assert len(frames) == 27
    assert [(f['year'], f['month']) for f in frames] == sorted((f['year'], f['month']) for f in frames)
    partial = [f for f in frames if not f['complete_calendar_time_support']]
    assert [(f['year'], f['month'], f['sample_count']) for f in partial] == [(2016, 4, 15), (2018, 6, 3)]
    assert all('partial month' in f['label'] for f in partial)
    assert all(f['calendar_time_coverage_clock_tolerance_seconds'] == 64 for f in frames)
    assert all(not f['climatology'] and not f['width_rank_eligible'] for f in frames)
    assert not monthly['seasonal_cycle_playback_eligible']
    assert not monthly['interpolated_frame_playback_eligible']
    assert all(chr(194) not in f['label'] for f in frames)
    assert all(f['whole_current_width_km'] is None and f['geographic_edges'] is None for f in frames)


def test_every_month_cell_agrees_with_independent_statistics(packets):
    _, monthly = packets
    _, _, arrays = source.load()
    for frame in monthly['frames']:
        selected = {k: arrays[k][frame['source_time_indices']] for k in source.FIELDS}
        for field, data in selected.items():
            actual = frame['field_statistics'][field]
            for cell in range(601):
                vals = [float(v) for v in data[:, cell] if np.isfinite(v)]
                assert actual['valid_count'][cell] == len(vals)
                assert actual['mean'][cell] == (pytest.approx(independent.mean(vals), abs=1e-14) if vals else None)
                assert actual['sample_sd'][cell] == (pytest.approx(independent.stdev(vals), abs=1e-14) if len(vals)>1 else None)
        paired = np.isfinite(selected['v']) & np.isfinite(selected['U'])
        for field in ['v', 'U']:
            actual = frame['paired_vector_statistics'][field]
            assert actual['valid_count'] == paired.sum(axis=0).tolist()
            for cell in range(601):
                vals = [float(v) for v in selected[field][:, cell][paired[:, cell]]]
                assert actual['mean'][cell] == (pytest.approx(independent.mean(vals), abs=1e-14) if vals else None)
                assert actual['sample_sd'][cell] == (pytest.approx(independent.stdev(vals), abs=1e-14) if len(vals)>1 else None)


@pytest.mark.parametrize('relative', ['header-and-coordinates.bin', 'raw-ranges/group-00.bin', 'provider-record.json', 'acquisition.json'])
def test_source_corruption_rejected_without_provider_fallback(tmp_path, relative):
    directory = tmp_path / 'source'
    shutil.copytree(source.DIRECTORY, directory)
    path = directory / relative
    original = path.read_bytes()
    changed = bytearray(original)
    changed[len(changed)//2] ^= 1
    path.write_bytes(changed)
    with pytest.raises(ValueError, match='Changed'):
        source.load(directory)


def test_generated_packets_match_frozen_contract_and_builder(packets):
    contract = json.loads((source.ROOT / sections.CONTRACT).read_bytes())
    for file_key, hash_key in [('raw_profile_file','raw_profile_sha256'), ('monthly_section_file','monthly_section_sha256'),
                               ('source_acquisition_file','source_acquisition_sha256'), ('protocol_file','protocol_sha256'),
                               ('builder_file','builder_sha256')]:
        assert sections.digest(contract[file_key]) == contract[hash_key]
    raw, monthly = packets
    for path, generated in [(sections.RAW, raw), (sections.MONTHLY, monthly)]:
        stored = json.loads((source.ROOT / path).read_bytes())
        if path == sections.MONTHLY:
            generated = {**generated, 'raw_profile_file':sections.RAW,
                         'raw_profile_sha256':sections.digest(sections.RAW)}
        assert stored == generated
    assert contract['width_measurement_admitted'] is False
