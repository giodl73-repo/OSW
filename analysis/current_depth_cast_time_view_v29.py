"""Correct cast temporal semantics in a new view; immutable v28 stays intact."""
import copy,hashlib,json,os,signal,socket,time
from pathlib import Path
import load_current_depth_reference_inventory_v28 as prior
ROOT=Path(__file__).resolve().parents[1]
OP='research/current-depth-cast-time-view-operator-v29.json'
PREVIOUS='research/current-depth-reference-inventory-v28.json'
INVENTORY='research/current-depth-reference-inventory-v29.json'
CORRECTION='research/a20-cast-temporal-semantics-correction-v1.json'
SOURCE_LEDGER='research/a20-local-depth-reference-admission-ledger-v1.json'
FACTS=prior.FACTS
ADDENDUM='research/current-depth-reference-addenda/a20-local-fixed-direction-depths-v1.json'
REMOVE='metric_frame_is_instantaneous_sample_not_climatology'


def numbers(v):
    if isinstance(v,dict):return sum(numbers(a) for a in v.values())
    if isinstance(v,list):return sum(numbers(a) for a in v)
    return int(type(v) in (int,float))


def corrections():
    return {'schema':'osw.a20-cast-temporal-semantics-correction.v1','metric':prior.METRIC,
        'reference_ids':['gulf-stream-a20-2021-cast-'+s+'-local-frame-'+str(t)+'cms' for s in ['014','015','016'] for t in [5,10,20]],
        'remove_field':REMOVE,'set_fields':{'metric_frame_is_cast_specific_not_climatology':True,
            'source_frame_is_mathematical_instant':False,'source_actual_cast_duration_resolved':False,
            'source_cast_timestamp_role':'provider_nominal_profile_datetime_not_per_depth_measurement_time'},
        'temporal_scope_template':'Processed LADCP cast {datetime}; finite cast duration may combine downcast/upcast measurements. No climatological mean,seasonal phase or annual range.',
        'scientific_depth_values_changed':False,'runtime_changed':False,'full_goal_complete':False}


def corrected(view,correction):
    if correction!=corrections():raise ValueError('Only the exact cast-time terminology correction is permitted')
    out=copy.deepcopy(view);seen=set()
    for row in out['evidence']:
        if row['id'] not in correction['reference_ids']:continue
        if row['metric']!=prior.METRIC or row.get(REMOVE) is not True:raise ValueError('Exact previous local-proxy field required')
        seen.add(row['id']);del row[REMOVE]
        row.update(copy.deepcopy(correction['set_fields']))
        row['temporal_scope']=correction['temporal_scope_template'].format(datetime=row['source_cast_datetime_utc'])
    if seen!=set(correction['reference_ids']):raise ValueError('Exactly nine existing references, no additions/removals')
    if out['counts']!=view['counts']:raise ValueError('No reference-count changes')
    return out


def load_inventory(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v29':raise ValueError('Inventoryv29 required')
    previous=json.loads(prior.checked_piece(manifest['previous_inventory'],reader))
    view=prior.load_inventory(previous,reader)
    correction=json.loads(prior.checked_piece(manifest['temporal_semantics_correction'],reader))
    out=corrected(view,correction)
    for k in ['counts','metric_counts','coordinate_unit_counts']:
        if out[k]!=manifest[k]:raise ValueError('Every prior catalog count must remain unchanged')
    if any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):
        raise ValueError('No runtime/completion promotion')
    out.update(copy.deepcopy(manifest['view_metadata']));out['temporal_semantics_correction_file']=manifest['temporal_semantics_correction']['file']
    return out


def build():
    op=json.loads((ROOT/OP).read_bytes())
    for p,h in op['input_sha256'].items():
        if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('Frozen dependency changed:'+p)
    reads={FACTS:0,ADDENDUM:0};packets={}
    def reader(p):
        raw=(ROOT/p).read_bytes()
        if p in reads:reads[p]+=1;packets[p]=raw
        return raw
    previous_raw=reader(PREVIOUS);previous=json.loads(previous_raw)
    before=prior.load_inventory(previous,reader);correction=corrections();after=corrected(before,correction)
    encode=lambda v:(json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
    piece=lambda p,raw:{'file':p,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    correction_raw=encode(correction)
    manifest={'schema':'osw.current-depth-reference-inventory.v29','status':'PINNED_REFERENCES_WITH_CAST_DURATION_TEMPORAL_SEMANTICS',
        'previous_inventory':piece(PREVIOUS,previous_raw),'temporal_semantics_correction':piece(CORRECTION,correction_raw),
        'counts':after['counts'],'metric_counts':after['metric_counts'],'coordinate_unit_counts':after['coordinate_unit_counts'],
        'view_metadata':{'schema':'osw.current-depth-reference-view.v29','status':'CAST_SPECIFIC_OBSERVATIONS_NOT_MATHEMATICAL_INSTANTS',
            'interpretation':'Same869references and values. NineA20local depth proxies use processed cast-specific96mframes; nominal cast timestamp is not a per-depth instantaneous observation. Earlier catalog snapshots remain immutable.',
            'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False},
        'runtime_changed':False,'full_goal_complete':False}
    final=load_inventory(manifest,lambda p:correction_raw if p==CORRECTION else reader(p))
    if final['evidence']!=after['evidence'] or reads!={FACTS:2,ADDENDUM:2}:raise ValueError('Exact actual correction roundtrip and two case-packet reads')
    # Count the two A20 packet reads by their already parsed source context and rows,
    # without parsing those files a third time just to compute accounting.
    thin=before['source_contexts'][prior.CONTEXT]
    prior_op=json.loads((ROOT/'research/current-depth-reference-inventory-operator-v28.json').read_bytes())
    facts_piece=piece(FACTS,packets[FACTS])
    reconstructed_addendum={'schema':prior.SCHEMA,'id':'a20-local-fixed-direction-depths-v1',
        'base_snapshot_sha256':previous['base']['json']['sha256'],'operator_file':'research/current-depth-reference-inventory-operator-v28.json',
        'operator_sha256':hashlib.sha256((ROOT/'research/current-depth-reference-inventory-operator-v28.json').read_bytes()).hexdigest(),
        'input_sha256':prior_op['input_sha256'],'reviewed_source_facts':facts_piece,'source_contexts':{prior.CONTEXT:thin},
        'evidence':[r for r in before['evidence'] if r['id'] in correction['reference_ids']],
        'runtime_changed':False,'full_goal_complete':False}
    if encode(reconstructed_addendum)!=packets[ADDENDUM]:raise ValueError('Exact in-memory addendum accounting reconstruction')
    ledger=json.loads((ROOT/SOURCE_LEDGER).read_bytes())
    decoded=2*(numbers(thin)+numbers(reconstructed_addendum))+numbers(ledger)
    meta=ledger['corrected_case_metadata_touch_bound']+decoded;scalars=ledger['corrected_case_scalar_bound']+decoded
    if meta>10000 or scalars>250000:raise ValueError('Original cumulative A20 caps unchanged')
    audit={'schema':'osw.a20-cast-time-correction-ledger.v1','status':'TEMPORAL_LABEL_CORRECTED_DEPTHS_AND_COUNTS_UNCHANGED',
        'new_decoded_metadata_numbers':decoded,'corrected_case_metadata_touch_bound':meta,'corrected_case_scalar_bound':scalars,
        'prior_case_time_charge_seconds':ledger['cumulative_case_time_charge_seconds'],'counts':after['counts'],
        'new_provider_requests':0,'new_native_ocean_values_decoded':0,'new_depth_references':0,
        'changed_temporal_labels':9,'runtime_changed':False,'full_goal_complete':False}
    return {INVENTORY:encode(manifest),CORRECTION:correction_raw},audit


def main():
    def stopped(*a):raise SystemExit('Stopped offline cast-time correction')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stopped)
    socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('No network/source requests'))
    signal.alarm(90);start=float(os.environ['OSW_A20_CAST_TIME_PHASE_START'])
    if not 0<=time.monotonic()-start<90:raise ValueError('Shared synthetic-test/producer clock')
    out=ROOT/'current-depth-reference-inventory-v29';out.mkdir(exist_ok=False)
    pieces,audit=build();audit['new_cast_time_correction_phase_seconds']=time.monotonic()-start
    audit['cumulative_case_time_charge_seconds']=audit['prior_case_time_charge_seconds']+audit['new_cast_time_correction_phase_seconds']
    if audit['cumulative_case_time_charge_seconds']>180:raise ValueError('Original time cap unchanged')
    raw=(json.dumps(audit,indent=2)+'\n').encode()
    if sum(map(len,pieces.values()))+len(raw)>2400000:raise ValueError('Fixed output cap')
    (out/'inventory.json').write_bytes(pieces[INVENTORY]);(out/'correction.json').write_bytes(pieces[CORRECTION]);(out/'correction-ledger.json').write_bytes(raw)
    print(json.dumps(audit))


if __name__=='__main__':main()
