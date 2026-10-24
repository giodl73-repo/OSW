"""Independent small-source coverage expectations; no packet, engine or browser."""
import copy
import json
from pathlib import Path

import pytest
from browser_current_catalogue_fixture import expected_reference_route_ids, expected_current_map_ids

ROOT=Path(__file__).resolve().parents[1]


def test_declared_106_currents_keep_four_additions_unlocated():
    mapped, unlocated=expected_current_map_ids(ROOT)
    assert len(mapped)==len(set(mapped))==102
    assert set(unlocated)=={'current:west-india-coastal','current:east-india-coastal',
                            'current:east-african-coastal','current:south-java'}
    assert not set(mapped)&set(unlocated)


@pytest.mark.parametrize('change',['invented_mark','invented_geometry_capability','missing_historical_mark'])
def test_map_expectations_reject_invented_or_missing_marks(tmp_path,change):
    folder=tmp_path/'research';folder.mkdir()
    for name in ['ocean-current-effective-catalogue.json','indian-current-identity-query-contract-v1.json']:
        (folder/name).write_bytes((ROOT/'research'/name).read_bytes())
    coastal=json.loads((folder/'indian-current-identity-query-contract-v1.json').read_bytes())
    dashboard=json.loads((ROOT/'research/ocean-motion-dashboard.json').read_bytes())
    # Keep this synthetic fixture small; geometry validity is tested in native gates.
    dashboard={'entries':[{'id':row['id'],'map_features':row['map_features']}
                          for row in dashboard['entries']]}
    if change=='invented_mark':coastal['additions']['objects'][0]['map_features']=[{'geometry':{'type':'Point','coordinates':[0,0]}}]
    if change=='invented_geometry_capability':coastal['additions']['objects'][0]['capabilities']['geometry']=1
    if change=='missing_historical_mark':
        next(row for row in dashboard['entries'] if row['id']=='current:gulf-stream')['map_features']=[]
    (folder/'indian-current-identity-query-contract-v1.json').write_text(json.dumps(coastal),encoding='utf8')
    (folder/'ocean-motion-dashboard.json').write_text(json.dumps(dashboard),encoding='utf8')
    with pytest.raises(ValueError):expected_current_map_ids(tmp_path)


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
