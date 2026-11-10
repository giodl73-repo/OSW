"""Refresh one checked dashboard projection without changing physical evidence."""
import copy
import hashlib
import json
from collections import Counter
from south_java_layer_query_v1 import TARGET, OWNER_FIELDS, fingerprint

DASHBOARD='research/ocean-motion-dashboard.json'
FIELDS={'model_analysis_layer_ids','model_depth_context_ids','capabilities','evidence_links',
        'source_ids','linked_source_count','section_fingerprints','fingerprint'}


def includes(actual,source):
    if isinstance(source,dict):
        return isinstance(actual,dict) and all(includes(actual.get(key),value) for key,value in source.items())
    return fingerprint(actual)==fingerprint(source)


def projects(object_row,entry):
    for key,value in entry.items():
        if key=='map_features':
            actual=object_row.get(key)
            if not isinstance(actual,list) or any(not any(includes(item,feature) for item in actual) for feature in value):
                return False
        elif not includes(object_row.get(key),value):return False
    return True


def refresh(manifest,prior_objects,updated_objects):
    receipt=manifest.get('dashboard_receipt',{})
    raw=receipt.get('source_json')
    if not isinstance(raw,str):raise ValueError('Missing dashboard source receipt')
    prior_sha=hashlib.sha256(raw.encode()).hexdigest()
    if (receipt.get('source_file')!=DASHBOARD or receipt.get('source_sha256')!=prior_sha
            or manifest.get('input_sha256',{}).get(DASHBOARD)!=prior_sha):
        raise ValueError('Changed parent dashboard receipt')
    doc=json.loads(raw)
    if doc.get('schema')!='osw.motion-dashboard.v1' or doc.get('fingerprint_version')!=2:
        raise ValueError('Unsupported dashboard projection')
    def indexed(rows):
        if not isinstance(rows,list) or any(not isinstance(row,dict) or not isinstance(row.get('id'),str) for row in rows):
            raise ValueError('Invalid dashboard/object rows')
        result={row['id']:row for row in rows}
        if len(result)!=len(rows):raise ValueError('Duplicate dashboard/object IDs')
        return result
    old,new,entries=indexed(prior_objects),indexed(updated_objects),indexed(doc.get('entries'))
    if set(old)!=set(new) or set(old)!=set(entries) or TARGET not in old:
        raise ValueError('Dashboard identity coverage changed')
    if doc.get('counts')!=dict(Counter(row['type'] for row in prior_objects)):
        raise ValueError('Dashboard source counts changed')
    for key,row in old.items():
        if not projects(row,entries[key]):raise ValueError('Parent dashboard does not project its objects')
        if key!=TARGET and fingerprint(row)!=fingerprint(new[key]):raise ValueError('Unrelated dashboard object changed')
    before,after=old[TARGET],new[TARGET]
    changed={key for key in set(before)|set(after) if fingerprint(before.get(key))!=fingerprint(after.get(key))}
    if changed-FIELDS:raise ValueError('Physical owner fields changed')
    caps={cap for _,cap in OWNER_FIELDS.values()}
    if set(after['capabilities'])-set(before['capabilities'])-caps:
        raise ValueError('Undeclared owner capability added')
    for key,value in before['capabilities'].items():
        if key not in caps and fingerprint(after['capabilities'].get(key))!=fingerprint(value):
            raise ValueError('Physical owner capability changed')
    for key,value in before['section_fingerprints'].items():
        if key!='model_layer_context' and after['section_fingerprints'].get(key)!=value:
            raise ValueError('Prior scientific fingerprint changed')
    if set(after['section_fingerprints'])-set(before['section_fingerprints'])-{'model_layer_context'}:
        raise ValueError('Undeclared scientific fingerprint added')
    doc=copy.deepcopy(doc)
    replacement=copy.deepcopy(entries[TARGET])
    for key in sorted(changed):replacement[key]=copy.deepcopy(after[key])
    doc['entries']=[replacement if row['id']==TARGET else row for row in doc['entries']]
    if not projects(after,replacement):raise ValueError('Updated dashboard does not project its owner')
    doc['snapshot_fingerprint']=fingerprint(doc['entries'])
    doc['model_context_projection']={'version':'south-java-iskandar-2006-v1','parent_source_sha256':prior_sha,
        'changed_owner_ids':[TARGET],'physical_dimension_admission':False}
    updated_raw=(json.dumps(doc,ensure_ascii=False,indent=2)+'\n').encode()
    updated_sha=hashlib.sha256(updated_raw).hexdigest()
    result=copy.deepcopy(manifest)
    result['dashboard_receipt']={'source_file':DASHBOARD,'source_sha256':updated_sha,'source_json':updated_raw.decode()}
    result['input_sha256'][DASHBOARD]=updated_sha
    proof={'parent_dashboard_sha256':prior_sha,'candidate_dashboard_sha256':updated_sha,
        'changed_dashboard_entry_ids':[TARGET],'changed_owner_fields':sorted(changed),
        'unchanged_dashboard_entries':len(old)-1,'dashboard_counts_preserved':True,
        'physical_fields_and_capabilities_preserved':True}
    return result,proof
