"""Actual small synthetic export round-trip, with missing symbols and JSON link."""
import xml.etree.ElementTree as ET

from current_local_extent_evidence_v1 import project
from test_current_local_extent_evidence_v1 import inputs
from render_current_local_extent_evidence_v1 import render


def test_exported_nonascii_svg_is_parseable_and_retains_accessible_evidence(tmp_path):
    values=inputs.__wrapped__()
    case=next(c for c in values[0]['cases'] if c['case_id']=='m01:offset0:step5')
    metric=next(m for m in case['metrics'] if m['fraction']==.5 and m['quantity']=='core_to_positive_normal_threshold_extent')
    metric.update(status='source_scale_supported_local_extent',source_scale_gate_passed=True,
        extent_bracket_km=[10,15],maximum_native_cell_scale_km=2,minimum_span_in_native_cell_scales=5)
    bundle=project(*values);svg=tmp_path/'synthetic.svg';png=tmp_path/'synthetic.png'
    manifest=render(bundle,svg,png)
    root=ET.parse(svg).getroot()
    assert root.get('role')=='img' and root.get('aria-labelledby')=='extent-title extent-description'
    body=svg.read_text(encoding='utf-8')
    assert '×' in body and 'encoding=\'utf-8\'' in body
    assert 'No source-scale-supported extent' in body and 'No independent shoreline reference' in body
    assert any(node.tag.endswith('}a') for node in root.iter())
    assert png.read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
    assert manifest['primary_attempts_drawn']==96 and not manifest['data_values_reestimated']
    assert manifest['status_counts_by_quantity']['core_to_positive_normal_threshold_extent']['source_scale_supported']==1
