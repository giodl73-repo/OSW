"""Source maps, raw series and clock blocks preserve supplied data and gaps."""
import json
import xml.etree.ElementTree as ET
import numpy as np
from build_loop_durante_source_view import ROOT,REPORT,FIGURE,GENERATOR,blocks
from acquire_loop_durante_2026 import verify,sha


def test_clock_blocks_do_not_bridge_nan_or_calendar_gaps():
    result=blocks(np.array([719529.,719530.,np.nan,719532.,719535.,719536.]))
    assert [(r['first_source_index'],r['last_source_index']) for r in result]==[(0,1),(3,3),(4,5)]
    assert sum(r['source_records'] for r in result)==5


def test_saved_view_preserves_every_selected_plot_value_and_source_time():
    _,quality,arrays=verify();doc=json.loads((ROOT/REPORT).read_bytes())
    assert doc['input_sha256'][GENERATOR]==sha(ROOT/GENERATOR)
    for phase,suffix in zip(doc['phases'],['max','min']):
        for key,prefix in [('speed_m_s','C'),('eastward_m_s','U'),('northward_m_s','V')]:
            actual=np.array(phase[key],dtype=float);expected=arrays[prefix+suffix]
            assert np.array_equal(actual,expected,equal_nan=True)
        assert np.array_equal(phase['unjoined_source_coordinate_points'],arrays[phase['coordinate_field']],equal_nan=True)
        # These are incoming coordinate means, not a complete northern Loop path.
        assert max(p[1] for p in phase['unjoined_source_coordinate_points'])<23.2
    for name,clock in doc['clocks'].items():
        assert clock['source_position_index_basis']=='zero_based_native_position'
        expected=arrays[name].reshape(-1)
        assert np.array_equal(np.array(clock['source_serial_days'],dtype=float),expected,equal_nan=True)
        actual=[i for b in clock['daily_blocks'] for i in range(b['first_source_index'],b['last_source_index']+1)]
        assert actual==np.flatnonzero(np.isfinite(expected)).tolist()
    for name,series in doc['source_scalar_series'].items():
        assert np.array_equal(np.array(series['source_values'],dtype=float),arrays[name].reshape(-1),equal_nan=True)
        assert series['time_field']=='tid' and not series['length_or_width_derived_from_area']
    assert not doc['source_axes_are_complete_loop_paths'] and not doc['source_axis_points_are_connected']
    assert not doc['current_length_admitted'] and not doc['width_measurement_admitted']


def test_figure_source_hashes_and_accessible_description():
    receipt=json.loads((ROOT/FIGURE).read_bytes())
    assert receipt['source_view_sha256']==sha(ROOT/REPORT)
    assert receipt['generator_sha256']==sha(ROOT/GENERATOR)
    for path,pin in receipt['figures'].items():
        assert sha(ROOT/path)==pin
        if path.endswith('.svg'):
            svg=ET.parse(ROOT/path).getroot();assert svg.get('role')=='img'
            for element_id in svg.get('aria-labelledby').split():assert any(n.get('id')==element_id and n.text for n in svg)
