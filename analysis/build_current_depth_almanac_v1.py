"""Index admitted depth references and regional pairs; no source science rerun."""
import copy,csv,hashlib,io,json,math,os,re,signal,socket,time
from collections import Counter
from pathlib import Path
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery
from compiled_depth_catalog_view_v3 import load_inventory
ROOT=Path(__file__).resolve().parents[1]
INPUTS='research/current-depth-almanac-inputs-v1.json'
OP='research/current-depth-almanac-operator-v1.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
encode=lambda v:(json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
finite=lambda v:type(v) in (int,float) and math.isfinite(v)

class CSVQuery:
    """Reserve whole unique CSV packets and each scalar conversion prospectively."""
    def __init__(self,query):self.query=query;self.seen=set()
    def rows(self,raw):
        q=self.query;key=sha(raw)
        if key not in self.seen:
            if len(raw)>2500000 or q.ledger['unique_json_bytes']+len(raw)>q.byte_cap:raise ValueError('Prospective CSV packet/total byte cap')
            q.ledger['unique_json_bytes']+=len(raw);q.ledger['new_json_bytes']+=len(raw)
            q.ledger['packets'].append({'sha256':key,'bytes':len(raw),'reserved_numeric_tokens':0,'format':'csv','status':'reserved_before_csv_parse'})
            q.save(q.ledger);self.seen.add(key)
        rows=list(csv.DictReader(io.StringIO(raw.decode('utf8'))))
        if any(None in row or any(v is None for v in row.values()) for row in rows):raise ValueError('Rectangular complete CSV required')
        return rows
    def scalar(self,text):
        if text in ('','null','None'):return None
        q=self.query
        if q.ledger['reserved_numeric_tokens']+1>q.numeric_cap:raise ValueError('Prospective CSV numeric cap')
        q.ledger['reserved_numeric_tokens']+=1;q.ledger['new_numeric_tokens']+=1
        q.ledger['csv_scalar_conversions_reserved']=q.ledger.get('csv_scalar_conversions_reserved',0)+1;q.save(q.ledger)
        value=float(text)
        if not finite(value):raise ValueError('Finite CSV scalar required')
        return value

def scope_for(owner,paths,scopes,declared=None):
    candidates=[]
    for path in paths:
        method=scopes[path]
        config=method if method.get('entity_id')==owner else method.get('currents',{}).get(owner)
        if config is not None and (not declared or declared==path):candidates.append((path,method,config))
    if len(candidates)!=1:raise ValueError('Exactly one pinned owner scope operator required:'+owner)
    return candidates[0]

def normalize(row,dataset,index,scopes,pairing,adapter):
    owner=row['entity_id'];path,method,config=scope_for(owner,dataset['scope_operators'],scopes,row.get('source_rule_operator_file'))
    if row['snapshot_time_utc'] not in method['snapshot_times_utc']:raise ValueError('Exact original operator date required')
    frame=config['component_bearing_degrees_true'];cutoff=config['primary_threshold_m_s']
    for field,expected in [('component_bearing_degrees_true',frame),('velocity_threshold_m_s',cutoff)]:
        if row.get(field) and adapter.scalar(row[field])!=expected:raise ValueError('CSV/operator frame or cutoff mismatch')
    source=row.get('source_compiled_descriptor_file') or dataset['fallback_compiled_descriptor_file']
    source_hash=row.get('source_compiled_descriptor_sha256') or dataset['fallback_compiled_descriptor_sha256']
    if not source or not source_hash or pairing['input_sha256'].get(source)!=source_hash:raise ValueError('Exact compiled provenance binding required')
    pointer=row['source_descriptor_pointer']
    if not re.fullmatch(r'/cases/[0-9]+',pointer):raise ValueError('Original compiled case pointer required')
    anchor=json.loads(row['original_axis_proxy_depth_anchor'] or 'null')
    run=None;location=None;state='unresolved_original_axis'
    if anchor is not None:
        run=anchor['paired_component_run'];location=anchor['sampled_lon_lat']
        if len(location)!=2 or not all(finite(v) for v in location) or not -180<=location[0]<=180 or not -90<=location[1]<=90:raise ValueError('Finite original longitude/latitude required')
        if anchor.get('physical_current_depth_m') is not None or anchor.get('whole_route_interpolation_allowed') is not False:raise ValueError('No physical or whole-route promotion')
        upper,lower,thickness=[run[k] for k in ['upper_depth_m','lower_depth_m','thickness_m']]
        if any(v is not None and (not finite(v) or v<0) for v in [upper,lower,thickness]):raise ValueError('Depths are finite nonnegative or null')
        if thickness is not None:
            bounds=run['sampling_thickness_bounds_m']
            if upper is None or lower is None or thickness<=0 or not math.isclose(lower-upper,thickness,abs_tol=1e-8,rel_tol=1e-10) or not isinstance(bounds,list) or len(bounds)!=2 or not all(finite(v) for v in bounds) or not 0<=bounds[0]<=thickness<=bounds[1]:raise ValueError('Finite paired thickness and enclosing sampling bracket required')
            state='finite_component_depth_pair'
        else:
            if run.get('sampling_thickness_bounds_m') is not None:raise ValueError('Censored pair cannot have finite thickness brackets')
            state='censored_component_depth_pair'
    out={'id':'regional:'+dataset['id']+':'+str(index),'record_type':'regional_depth_estimate','entity_id':owner,
        'dataset_id':dataset['id'],'section_id':row['section_id'],'snapshot_time_utc':row['snapshot_time_utc'],
        'source_status':row['status'],'estimate_status':state,'sampled_lon_lat':location,
        'component_bearing_degrees_true':frame,'velocity_threshold_m_s':cutoff,
        'upper_depth_m':None if run is None else run['upper_depth_m'],
        'lower_depth_m':None if run is None else run['lower_depth_m'],
        'thickness_m':None if run is None else run['thickness_m'],
        'sampling_thickness_bounds_m':None if run is None else run.get('sampling_thickness_bounds_m'),
        'native_supported_minimum_component_span_m':None if run is None else run.get('native_supported_minimum_component_span_m'),
        'original_axis_proxy_depth_anchor':copy.deepcopy(anchor),
        'original_csv':dataset['csv'],'original_csv_sha256':dataset['csv_sha256'],'original_csv_data_row_index':index,
        'original_csv_row_policy':'All original cells remain unchanged in the hash-pinned CSV. Row index is zero-based after header; opaque original_primary_layer is not reinterpreted or duplicated.',
        'source_rule_operator_file':path,'source_compiled_descriptor_file':source,'source_compiled_descriptor_sha256':source_hash,'source_descriptor_pointer':pointer,
        'physical_current_depth_m':None,'whole_route_interpolation_allowed':False,'volume_km3':None,
        'sampling_bracket_is_physical_uncertainty':False,'independent_current_axis_validated':False}
    return out

def assemble(view,readiness,datasets,estimates,scopes):
    owners={r['entity_id']:r for r in view['records']}
    if len(owners)!=len(view['records']) or set(owners)!={r['entity_id'] for r in readiness['records']}:raise ValueError('Exact canonical/readiness identity join')
    if len({r['id'] for r in estimates})!=len(estimates) or any(r['entity_id'] not in owners for r in estimates):raise ValueError('Unique estimate IDs and known owners required')
    currents=[]
    for ready in readiness['records']:
        owner=ready['entity_id'];own=[r for r in estimates if r['entity_id']==owner]
        refs=[r for r in view['evidence'] if r['entity_id']==owner]
        if ready['canonical_reference_ids']!=[r['id'] for r in refs]:raise ValueError('Exact canonical current reference index required')
        currents.append({'record_type':'current','entity_id':owner,'name':owners[owner]['name'],'identity_level':ready['identity_level'],
            'canonical_reference_ids':[r['id'] for r in refs],'canonical_reference_metric_counts':dict(Counter(r['metric'] for r in refs)),
            'regional_estimate_ids':[r['id'] for r in own],'regional_estimate_status_counts':dict(Counter(r['estimate_status'] for r in own)),
            'paired_index_scope':'explicit_21_admitted_products_not_exhaustive_no_pairs_does_not_mean_no_depth_data',
            'direct_current_without_supported_regional_case':ready['direct_current_without_supported_regional_case'],
            'whole_route_physical_depth_m':None,'volume_km3':None})
    entries=currents+[{'record_type':'canonical_reference','reference':copy.deepcopy(r)} for r in view['evidence']]+estimates
    entries += [{'record_type':'canonical_source_context','id':k,'context':copy.deepcopy(v)} for k,v in view['source_contexts'].items()]
    entries += [{'record_type':'paired_dataset','dataset':copy.deepcopy(d)} for d in datasets]
    entries += [{'record_type':'scope_operator','file':p,'operator':copy.deepcopy(v)} for p,v in scopes.items()]
    entries += [{'record_type':'calendar_series','series':copy.deepcopy(s)} for s in view.get('calendar_depth_series',[])]
    return {'schema':'osw.current-depth-almanac.expanded.v1','counts':{'currents':len(currents),'canonical_references':len(view['evidence']),
        'paired_datasets':len(datasets),'regional_estimates':len(estimates),'owners_with_paired_rows':len({r['entity_id'] for r in estimates}),
        **dict(Counter(r['estimate_status'] for r in estimates))},'entries':entries,
        'canonical_inventory':'research/current-depth-reference-inventory-v40.json',
        'interpretation':'Core depths, thicknesses, pressure coordinates, finite component pairs and censor-support limits remain different quantities. Sampling brackets are not physical uncertainty. Editorial sections and selected axes are not validated physical current boundaries. Dated model cases are not independent observations or seasonal climatology. Parent/member records are not additive. No global depth ranking, route interpolation or physical volume.',
        'pending_unadmitted_work_review':'research/current-depth-partitioned-paired-depth-query-failure-review-v1.json',
        'native_sources_followed':False,'runtime_changed':False,'full_goal_complete':False}

def table(rows,fields):
    stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=fields,lineterminator='\n');writer.writeheader()
    cells=[{k:('' if r.get(k) is None else json.dumps(r[k],ensure_ascii=False,separators=(',',':')) if isinstance(r[k],(dict,list)) else str(r[k])) for k in fields} for r in rows]
    writer.writerows(cells);raw=stream.getvalue().encode()
    if list(csv.DictReader(io.StringIO(raw.decode())))!=cells:raise ValueError('Full CSV cell roundtrip')
    return raw

def compact_report(report):
    if report['schema']!='osw.current-depth-almanac.expanded.v1':raise ValueError('Full scientific v1 report required')
    out=copy.deepcopy(report);schemas=[];lookup={};strings=[];string_lookup={}
    def pack(value):
        if isinstance(value,dict):
            keys=tuple(value)
            if keys not in lookup:lookup[keys]=len(schemas);schemas.append(list(keys))
            index=lookup[keys]
            return [1,index,[pack(v) for v in value.values()]]
        if isinstance(value,list):return [0,[pack(v) for v in value]]
        if type(value)==str:
            if value not in string_lookup:string_lookup[value]=len(strings);strings.append(value)
            return [2,string_lookup[value]]
        if value is None or type(value) in (bool,int,float):return value
        raise ValueError('Only original JSON values can be packed')
    node=pack(out['entries']);out['entries']={'encoding':'ordered-object-tables.v1','object_key_schemas':schemas,'string_values':strings,'node':node};out['schema']='osw.current-depth-almanac.v1'
    return out

def expand_report(compact):
    out=copy.deepcopy(compact)
    if out['schema']!='osw.current-depth-almanac.v1':raise ValueError('Packed scientific v2 report required')
    block=out['entries']
    if not isinstance(block,dict) or set(block)!=set(['encoding','object_key_schemas','string_values','node']) or block['encoding']!='ordered-object-tables.v1':raise ValueError('Exact ordered-object encoding required')
    schemas=block['object_key_schemas']
    if not isinstance(schemas,list) or any(not isinstance(keys,list) or not all(type(k)==str for k in keys) or len(keys)!=len(set(keys)) for keys in schemas) or len(schemas)!=len({tuple(keys) for keys in schemas}):raise ValueError('Unique ordered string-key schemas required')
    strings=block['string_values']
    if not isinstance(strings,list) or not all(type(v)==str for v in strings) or len(strings)!=len(set(strings)):raise ValueError('Unique exact string table required')
    def unpack(node):
        if not isinstance(node,list):
            if node is None or type(node) in (bool,int,float):return node
            raise ValueError('Untagged original object forbidden')
        if len(node)==2 and type(node[0])==int and node[0]==0 and isinstance(node[1],list):return [unpack(v) for v in node[1]]
        if len(node)==2 and type(node[0])==int and node[0]==2 and type(node[1])==int and 0<=node[1]<len(strings):return strings[node[1]]
        if len(node)!=3 or type(node[0])!=int or node[0]!=1 or type(node[1])!=int or not 0<=node[1]<len(schemas) or not isinstance(node[2],list) or len(node[2])!=len(schemas[node[1]]):raise ValueError('Exact object tag,valid schema and full value count required')
        return {key:unpack(value) for key,value in zip(schemas[node[1]],node[2])}
    cases=unpack(block['node'])
    if not isinstance(cases,list) or any(not isinstance(row,dict) for row in cases):raise ValueError('Expanded cases must be objects in a list')
    out['entries']=cases;out['schema']='osw.current-depth-almanac.expanded.v1';return out

def main():
    start=float(os.environ['OSW_DEPTH_ALMANAC_START'])
    def stop(*a):raise TimeoutError('Shared60second deadline including tests')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stop)
    if not 0<=time.monotonic()-start<30:raise ValueError('Shared synthetic-test/producer clock')
    signal.alarm(max(1,int(60-(time.monotonic()-start))));socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline descriptors only'))
    out=ROOT/'current-depth-almanac-v1';out.mkdir(exist_ok=False)
    def save(value):
        tmp=out/'query-ledger.tmp';tmp.write_bytes(encode(value));os.replace(tmp,out/'query-ledger.json')
    query=DescriptorQuery(save,prior_numeric=0,prior_bytes=0);adapter=CSVQuery(query);reader=query.reader(lambda p:(ROOT/p).read_bytes())
    try:
        with query.decoding():
            op=json.loads(reader(OP))
            for path,pin in op['input_sha256'].items():
                if sha((ROOT/path).read_bytes())!=pin:raise ValueError('Frozen input changed:'+path)
            manifest=json.loads(reader(INPUTS));view=load_inventory(json.loads(reader(manifest['canonical_inventory'])),reader)
            readiness=json.loads(reader(manifest['readiness']));scopes={};datasets=[];estimates=[]
            for declared in manifest['datasets']:
                d=copy.deepcopy(declared);pairing=json.loads(reader(d['pairing_operator']));review=json.loads(reader(d['review']))
                if review['status']!=d['expected_review_status']:raise ValueError('Exact admitted review status')
                raw=reader(d['csv']);piece=review['outputs'][d['csv']]
                if sha(raw)!=piece['sha256'] or len(raw)!=piece['bytes']:raise ValueError('Exact reviewed CSV custody')
                d['csv_sha256']=sha(raw);d['review_sha256']=sha(reader(d['review']));d['source_review']=review
                for path in d['scope_operators']:
                    raw_scope=reader(path)
                    if sha(raw_scope)!=pairing['input_sha256'][path]:raise ValueError('Exact original scope operator')
                    if path not in scopes:scopes[path]=json.loads(raw_scope)
                rows=adapter.rows(raw)
                if len(rows)!=pairing['source_cases']:raise ValueError('Complete admitted cohort required')
                estimates.extend(normalize(row,d,i,scopes,pairing,adapter) for i,row in enumerate(rows));datasets.append(d)
            report=assemble(view,readiness,datasets,estimates,scopes)
            if report['counts']['currents']!=111 or report['counts']['canonical_references']!=908 or report['counts']['paired_datasets']!=21:raise ValueError('Complete declared almanac scope')
            packed=compact_report(report);raw=encode(packed);restored=expand_report(json.loads(raw))
            if restored!=report or encode(restored)!=encode(report):raise ValueError('Complete lossless scientific JSON roundtrip')
        models=table(estimates,['id','entity_id','dataset_id','section_id','snapshot_time_utc','estimate_status','sampled_lon_lat','component_bearing_degrees_true','velocity_threshold_m_s','upper_depth_m','lower_depth_m','thickness_m','sampling_thickness_bounds_m','native_supported_minimum_component_span_m','source_rule_operator_file','original_csv','original_csv_data_row_index'])
        currents=table([r for r in report['entries'] if r['record_type']=='current'],['entity_id','name','identity_level','canonical_reference_metric_counts','regional_estimate_status_counts','direct_current_without_supported_regional_case'])
        total=len(raw)+len(models)+len(currents)+(out/'query-ledger.json').stat().st_size
        if total>2400000:raise ValueError('Whole output artifact cap')
        for name,blob in [('almanac.json',raw),('regional-estimates.csv',models),('currents.csv',currents)]: (out/name).write_bytes(blob)
        print(json.dumps({'counts':report['counts'],'query_numeric_tokens':query.ledger['reserved_numeric_tokens'],'query_bytes':query.ledger['unique_json_bytes'],'whole_output_bytes':total,'cumulative_active_seconds':time.monotonic()-start,'runtime_changed':False,'full_goal_complete':False}))
    finally:signal.alarm(0)

if __name__=='__main__':main()
