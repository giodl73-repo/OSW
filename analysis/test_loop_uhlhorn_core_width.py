"""Source admission and PDF edition checks for the pre-Lili core observation."""
import copy
import io
import json
import re
from pathlib import Path

import pytest
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, NumberObject
import check_loop_uhlhorn_core_width as widths
import uhlhorn_thesis_source as thesis


@pytest.mark.parametrize('filename,expected', [
    ('journal-article.pdf', 'local original verified'),
    ('repository-current.pdf', 'unchanged176-page thesis graph verified'),
])
def test_acquisition_cli_reports_original_and_verified_cover_without_local_manifest(filename, expected, monkeypatch, capsys):
    import acquire_local_paper_fixtures as acquisition
    data = (thesis.DIRECTORY / filename).read_bytes()
    monkeypatch.setattr(acquisition, 'PAPERS', ('uhlhorn-loop-2008',))
    monkeypatch.setattr(acquisition, 'acquire', lambda name, directory: data)
    acquisition.main()
    assert expected in capsys.readouterr().out


def test_original_section_has_declared_cutoff_width_dates_and_reference():
    reader = PdfReader(thesis.resolve_source())
    text = reader.pages[64].extract_text()
    for value in ['100', '0.4', '0.75', '750', '300', '19-23 Sept.']:
        assert value in text
    row = widths.record()
    widths.validate_row(row)
    assert row['approximate_width_km'] == 100 and row['width_range_km'] is None
    assert row['observed_period'] == {'start':'2002-09-19', 'end':'2002-09-23'}
    assert row['original_regional_context']['source_speed_threshold_m_s'] == .4
    assert row['fixed_layer_bounds_m'] is None and row['section_geometry'] is None
    assert row['uncertainty_km'] is None and row['annual_width_range_km'] is None


def test_source_efolding_wording_cannot_redefine_fixed_threshold():
    import math
    context = widths.record()['original_regional_context']
    assert context['source_threshold_to_prose_peak_ratio'] == .4/.75
    assert not math.isclose(.4/.75, math.exp(-1), rel_tol=.1)
    assert context['source_e_folding_wording_is_adopted_threshold'] is False
    assert context['reference_depth_is_width_layer'] is False


@pytest.mark.parametrize('key,value', [
    ('approximate_width_km',200), ('width_range_km',[100,200]),
    ('current_id','gulf-stream-system'), ('current_id','yucatan'),
    ('fixed_layer_bounds_m',[0,300]), ('uncertainty_km',20),
    ('calendar_months',[9]), ('seasonal_playback_eligible',True),
    ('annual_width_range_km',[100,200]), ('whole_current_representative',True),
    ('width_rank_eligible',True), ('observed_period',{'start':'2002-10-04','end':'2002-10-04'}),
])
def test_rejects_reassignment_layer_and_seasonal_promotion(key,value):
    row = widths.record(); row[key] = value
    with pytest.raises(ValueError): widths.validate_row(row)


def test_missing_duplicate_and_erased_support_are_rejected():
    inventory=json.loads((widths.ROOT/'research/ocean-current-width-inventory.json').read_bytes())
    widths.validate_inventory(inventory)
    for mode in ['missing','duplicate','erased']:
        bad=copy.deepcopy(inventory); row=next(r for r in bad['measurements'] if r['id']==widths.ID)
        if mode=='missing':bad['measurements'].remove(row)
        if mode=='duplicate':bad['measurements'].append(copy.deepcopy(row))
        if mode=='erased':row.pop('original_regional_context')
        with pytest.raises(ValueError):widths.validate_inventory(bad)


@pytest.mark.parametrize('mode',['content','page_order','page_size'])
def test_rejects_changed_scientific_pdf_pages(mode):
    data=thesis.resolve_source().read_bytes(); reader=PdfReader(io.BytesIO(data))
    writer=PdfWriter();writer.clone_document_from_reader(reader)
    if mode=='content':
        page=writer.pages[64]; stream=page.get_contents()
        stream.set_data(stream.get_data()+b'\n0 0 m 100 100 l S\n')
        page[NameObject('/Contents')]=stream
    elif mode=='page_order':
        kids=writer._pages.get_object()['/Kids']
        kids[64],kids[65]=kids[65],kids[64]
    else:writer.pages[64].mediabox.upper_right=(500,500)
    output=io.BytesIO();writer.write(output)
    manifest=json.loads((thesis.DIRECTORY/'acquisition.json').read_bytes())
    with pytest.raises(ValueError):thesis.verify_rendition(output.getvalue(),manifest)


def test_container_producer_does_not_change_original_page_graph():
    data=thesis.resolve_source().read_bytes()
    changed,count=re.subn(rb'/Producer \(pypdf\)',b'/Producer (qypdf)',data)
    assert count > 0 and changed != data
    manifest=json.loads((thesis.DIRECTORY/'acquisition.json').read_bytes())
    assert thesis.verify_rendition(changed,manifest)['thesis_graph_sha256'] == thesis.describe(data)['thesis_graph_sha256']
