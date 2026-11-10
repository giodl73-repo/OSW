"""Actual compact query scene preserves the complete model-context evidence."""
import json
import pytest
import south_australian_flow_context as scene


@pytest.fixture(scope='module')
def checked():return scene.verify_inputs()


def test_compact_scene_preserves_all_cases_and_source_pins(checked):
    doc,pins=checked
    raw=json.loads((scene.ROOT/scene.context.OUTPUT).read_bytes())
    assert len(doc['months'])==12 and doc['original_scalar_overlap']==55632
    assert doc['valid_paired_vectors']==1070550
    assert not doc['current_association_verified'] and not doc['width_measurement_admitted']
    assert doc['whole_current_width_km'] is None and doc['annual_width_range_km'] is None
    for saved,original in zip(doc['months'],raw['months']):
        assert saved['threshold_cases']==original['threshold_cases']
        assert saved['seed']==original['seed']
        assert saved['original_section_span_km']==original['original_section_span_km']
        assert len(saved['direction_samples'])==247
        for iy,ix,u,v,count in saved['direction_samples']:
            assert count==original['paired_counts_by_cell'][iy][ix]
            assert (u is not None and v is not None)==(count>=saved['minimum_required_pairs'])
    for path,pin in pins.items():assert scene.context.sha(scene.ROOT/path)==pin


def test_registered_source_documents_and_figures_are_available(checked):
    doc,_=checked
    registry=json.loads((scene.ROOT/'almanac/index-sources.json').read_bytes())['documents']
    assert registry.count(scene.FILE)==1 and registry.count(doc['raw_context_file'])==1
    for key in ['source_figure','context_figure']:assert (scene.ROOT/doc[key]).exists()
    record=scene.record(doc)
    assert record['id']==scene.ID and record['entity_id']=='current:south-australian'
    assert record['document']==doc and not record['rank_eligible']
