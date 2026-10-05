"""Validate source-supported conceptual connections; no length or width inference."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'research/indonesian-throughflow-network-input.json'

def require(condition):
    if not condition:raise ValueError("Invalid flow network source or measurement scope")

def validate(doc):
    require(doc['schema']=='osw.flow-network.v1' and doc['rank_eligible'] is False)
    for key in ['length_km','width_km','annual_length_range_km','annual_width_range_km']:require(doc[key] is None)
    nodes=doc['nodes'];ids={n['id'] for n in nodes};require(len(ids)==len(nodes))
    require(len({e['id'] for e in doc['edges']})==len(doc['edges']))
    for node in nodes:require(node['coordinates_lon_lat'] is None and len(node['schematic_xy'])==2)
    for edge in doc['edges']:
        require(edge['from_id'] in ids and edge['to_id'] in ids and edge['from_id']!=edge['to_id'])
        require(edge['length_km'] is None and edge['width_km'] is None and edge['geometry'] is None and edge['rank_eligible'] is False)
    require(abs(sum(s['value'] for s in doc['passage_samples'])-doc['reported_exit_total_Sv'])<1e-9)
    for sample in doc['passage_samples']:
        require(sample['node_id'] in ids and sample['unit']=='Sv' and sample['quantity']=='section_volume_transport')
        require(sample['sampling_period']=={'from_year':2004,'to_year':2006,'precision':'year'})
        require(not sample['integration_width_is_physical_current_width'] and not sample['rank_eligible'])
        for mooring in sample['moorings']:
            ld,lm,bd,bm=mooring['source_degrees_minutes']
            require(mooring['coordinates_lon_lat']==[round(ld+lm/60,8),round(-(bd+bm/60),8)])
            require(mooring['deployment_start']<mooring['deployment_end'])
    return doc

def build():
    raw=INPUT.read_bytes();document=validate(json.loads(raw));base={'entity_id':document['entity_id'],'current_id':document['current_id'],'network_id':document['id'],'source_url':document['source_url'],'source_file':INPUT.relative_to(ROOT).as_posix(),'source_file_sha256':hashlib.sha256(raw).hexdigest(),'rank_eligible':False}
    network={**base,'id':document['id'],'label':document['label'],'status':document['status'],'scope':document['scope'],'document':document,'source_json':raw.decode('utf-8')}
    records={'flow_networks':[network],'flow_network_nodes':[],'flow_network_edges':[],'passage_samples':[]}
    for key,collection in [('nodes','flow_network_nodes'),('edges','flow_network_edges'),('passage_samples','passage_samples')]:
        for source in document[key]:
            record={**base,**source,'source_record':source}
            if collection=='passage_samples':
                record['map_features']=[{'geometry':{'type':'Point','coordinates':m['coordinates_lon_lat']},'role':'published_mooring_locator_not_axis_edge_or_whole_current_footprint','mooring_label':m['label'],'source_url':document['source_url'],'source_locator':'Table 2, first-deployment coordinates','source_file_sha256':base['source_file_sha256'],'deployment_start':m['deployment_start'],'deployment_end':m['deployment_end'],'position_time_support':'First-deployment coordinates only; deployment period does not establish position persistence or exact redeployment coordinates.','note':'INSTANT mooring location; first-deployment coordinates, differing deployment periods retained in card. Decimal conversion does not increase source accuracy.'} for m in source['moorings']]
            records[collection].append(record)
    return records
