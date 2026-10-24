"""Independent small-source coverage expectations; no packet, engine or browser."""
import copy
import json
from pathlib import Path

import pytest
from browser_current_catalogue_fixture import expected_reference_route_ids

ROOT=Path(__file__).resolve().parents[1]


def test_all_78_declared_route_ids_include_separate_source_anchor_card():
    ids=expected_reference_route_ids(ROOT)
    base=json.loads((ROOT/'research/ocean-current-working-reference-routes.json').read_bytes())
    assert len(ids)==len(set(ids))==78
    assert set(row['id'] for row in base['candidates']) < set(ids)
    assert set(ids)-{row['id'] for row in base['candidates']}=={'norwegian-atlantic-slope-asar-regional-reference-route'}


@pytest.mark.parametrize('change',['missing','duplicate','count','owner','identity','scope','collision'])
def test_inconsistent_source_inventory_rejects(tmp_path,change):
    base=json.loads((ROOT/'research/ocean-current-working-reference-routes.json').read_bytes())
    addition=json.loads((ROOT/'research/nwasc-source-anchor-reference-route.json').read_bytes())
    if change=='missing':base['candidates'].pop()
    if change=='duplicate':base['candidates'][1]=copy.deepcopy(base['candidates'][0])
    if change=='count':base['counts']['route_candidates']=78
    if change=='owner':addition['current_id']='other'
    if change=='identity':addition['route_record']['id']='other'
    if change=='scope':addition['route_record']['comparison_group']='whole_current_lengths'
    if change=='collision':base['candidates'][0]['id']=addition['route_record']['id']
    folder=tmp_path/'research';folder.mkdir()
    (folder/'ocean-current-working-reference-routes.json').write_text(json.dumps(base),encoding='utf8')
    (folder/'nwasc-source-anchor-reference-route.json').write_text(json.dumps(addition),encoding='utf8')
    with pytest.raises(ValueError,match='route inventory'):expected_reference_route_ids(tmp_path)
