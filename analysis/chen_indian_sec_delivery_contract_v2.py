"""Preserve the pinned historical source contract while projecting live records."""
import copy
import hashlib
import json
from pathlib import Path
from chen_indian_sec_delivery_contract_v1 import (
    OWNER, CONTRACT, CONTRACT_SHA, transform_rows, full_scene, expected_query,
    dashboard_document, verify_object, verify_inventory, engine_manifest,
)

ROOT=Path(__file__).resolve().parents[1]
BASIN_FILE='research/equatorial-basin-identity-query-contract-v3.json'
BASIN_SHA='1486ee54bfa7b7b17bdc08ebdc788d63c93a058e4f632b23b39d79f1c74a591d'


def historical_contract():
    raw=(ROOT/BASIN_FILE).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=BASIN_SHA:
        raise ValueError('Changed historical basin source contract')
    return json.loads(raw)


def expected_snapshot(name, old, c, logical_sha):
    if name not in ('atlas','seasons','dashboard') or old.get('ok') is not True:
        raise ValueError('Complete parent snapshot required')
    # This root field is the source document itself, not a live collection.
    # Require its exact independently pinned contents; omit no subfields.
    historical=old.get('basin_identity_contract')
    if name!='dashboard' and historical!=historical_contract():
        raise ValueError('Parent historical basin contract differs')
    projected={k:v for k,v in old.items() if k!='basin_identity_contract'}
    result=transform_rows(projected,c)
    if 'basin_identity_contract' in old:
        result['basin_identity_contract']=copy.deepcopy(historical)
    result['bundle_sha256']=logical_sha
    if name=='dashboard':
        result['snapshot_json']=dashboard_document(json.loads(old['snapshot_json']),c)
    else:
        result['regional_model_length_scenes']={'indian-south-equatorial':full_scene(c)}
        if name=='atlas':
            path='research/ocean-motion-dashboard.json'
            result['sources_json'][path]=dashboard_document(json.loads(old['sources_json'][path]),c)
    return result


def normalized_snapshot(name, value):
    result=copy.deepcopy(value)
    if name=='dashboard':result['snapshot_json']=json.loads(value['snapshot_json'])
    elif name=='atlas':
        path='research/ocean-motion-dashboard.json'
        result['sources_json'][path]=json.loads(value['sources_json'][path])
    return result


def verify_snapshot(name, old, new, c):
    if new.get('ok') is not True:raise ValueError('Complete candidate snapshot required')
    expected=expected_snapshot(name,old,c,new['bundle_sha256'])
    if expected!=normalized_snapshot(name,new):
        raise ValueError('Complete '+name+' changed outside declared regional evidence')
