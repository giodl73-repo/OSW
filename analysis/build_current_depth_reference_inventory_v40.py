"""Offline admission and twelve-month join of already-reviewed Leeuwin descriptors."""
import hashlib,json,os,signal,socket,time
from pathlib import Path
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery
import load_current_depth_reference_inventory_v40 as loader
ROOT=Path(__file__).resolve().parents[1]
OP='research/current-depth-reference-inventory-operator-v40.json'
PREVIOUS='research/current-depth-reference-inventory-v39.json'
INVENTORY='research/current-depth-reference-inventory-v40.json'
ADDENDUM='research/current-depth-reference-addenda/leeuwin-watr50-reviewed-monthly-censor-support-v1.json'
CSV='research/current-depth-reference-addenda/leeuwin-watr50-reviewed-monthly-censor-support-v1.csv'
SERIES='research/leeuwin-monthly-depth-support-series-v2.json'
SERIES_CSV='research/leeuwin-monthly-depth-support-series-v2.csv'
def encode(v):return (json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
def main():
    start=float(os.environ['OSW_LEEUWIN_CENSOR_START'])
    def stopped(*a):raise TimeoutError('Bounded descriptor admission deadline')
    signal.signal(signal.SIGALRM,stopped);signal.signal(signal.SIGTERM,stopped)
    elapsed=time.monotonic()-start
    if not 0<=elapsed<30:raise ValueError('Shared synthetic/producer clock')
    signal.alarm(max(1,int(60-elapsed)));socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline descriptors only; native sources remain closed'))
    out=ROOT/'current-depth-reference-inventory-v40';out.mkdir(exist_ok=False)
    def save(v):
        tmp=out/'query-ledger.tmp';tmp.write_bytes(encode(v));os.replace(tmp,out/'catalog-query-ledger.json')
    query=DescriptorQuery(save,prior_numeric=0,prior_bytes=0);reader=query.reader(lambda p:(ROOT/p).read_bytes())
    piece=lambda p,raw:{'file':p,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
    try:
        with query.decoding():
            op=json.loads(reader(OP))
            for p,h in op['input_sha256'].items():
                if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('Frozen admission input changed:'+p)
            raw_source=reader(loader.SOURCE);raw_review=reader(loader.REVIEW);raw_method=reader(loader.METHOD)
            for raw,pin in [(raw_source,loader.SOURCE_SHA),(raw_review,loader.REVIEW_SHA),(raw_method,loader.METHOD_SHA)]:
                if hashlib.sha256(raw).hexdigest()!=pin:raise ValueError('Exact retained reviewed descriptor bytes required')
            source,review,method=map(json.loads,[raw_source,raw_review,raw_method]);prior_raw=reader(PREVIOUS);before=loader.previous.load_inventory(json.loads(prior_raw),reader)
            if before['counts']['depth_references']!=905:raise ValueError('Exact canonical predecessor')
            a={'schema':loader.SCHEMA,'id':loader.ADDENDUM_ID,'source_result':piece(loader.SOURCE,raw_source),'support_review':piece(loader.REVIEW,raw_review),'mean_operator':piece(loader.METHOD,raw_method),
                'source_contexts':{loader.CONTEXT:loader.context(method)},'evidence':loader.references(source,review,method,before),'runtime_changed':False,'full_goal_complete':False}
            after=loader.assemble(before,a,source,review,method)
            if after['evidence'][:-3]!=before['evidence'] or any(after['source_contexts'][k]!=v for k,v in before['source_contexts'].items()):raise ValueError('All905 prior references/contexts preserved')
            for old,new in zip(before['records'],after['records']):
                if {k:v for k,v in old.items() if k!='depth_reference_ids'}!={k:v for k,v in new.items() if k!='depth_reference_ids'}:raise ValueError('Non-reference owner field changed')
            if after['counts']!={'identities':111,'depth_references':908,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0} or after['coordinate_unit_counts']!={'dbar':2,'m':906}:raise ValueError('Only three processed-mean support references admitted')
            series=loader.calendar_series(after,source,review,method);ar=encode(a);table=loader.reference_csv_bytes(a['evidence']);sr=encode(series);st=loader.reference_csv_bytes(series['months'])
            manifest={'schema':'osw.current-depth-reference-inventory.v40','status':'PINNED_REFERENCES_WITH_LEEUWIN_REVIEWED_MONTHLY_CENSOR_SUPPORT','previous_inventory':piece(PREVIOUS,prior_raw),
                'reference_addendum':{'id':a['id'],'json':piece(ADDENDUM,ar),'csv':piece(CSV,table)},'calendar_series':{'json':piece(SERIES,sr),'csv':piece(SERIES_CSV,st)},
                'counts':after['counts'],'metric_counts':after['metric_counts'],'coordinate_unit_counts':after['coordinate_unit_counts'],
                'view_metadata':{'schema':'osw.current-depth-reference-view.v40','status':'NINE_MONTHLY_MEAN_BOUNDARIES_PLUS_THREE_CENSORED_SUPPORT_MONTHS',
                    'interpretation':'Local Leeuwin processed mean-profile series: nine existing calculated reversals and three475m sampled-sign support bounds. Three boundary depths remain unknown. Mixed observed/extrapolated/SOM product, not physical depth or annual extrema.',
                    'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False},'runtime_changed':False,'full_goal_complete':False}
            pieces={INVENTORY:encode(manifest),ADDENDUM:ar,CSV:table,SERIES:sr,SERIES_CSV:st}
            final_reader=lambda p:pieces[p] if p in pieces else reader(p)
            final=loader.load_inventory(json.loads(pieces[INVENTORY]),final_reader)
            if any(final[k]!=after[k] for k in ['evidence','records','source_contexts']) or final['calendar_depth_series']!=before.get('calendar_depth_series',[])+[series]:raise ValueError('Actual complete catalog/series/CSV roundtrip')
            result={'schema':'osw.leeuwin-monthly-censor-admission-ledger.v1','status':'THREE_REVIEWED_CENSOR_SUPPORTS_AND_TWELVE_MONTH_SERIES_ADMITTED','counts':after['counts'],'prior_references_preserved':905,'new_references':3,
                'monthly_series_counts':series['counts'],'new_provider_requests':0,'new_native_values_decoded':0,'new_depth_values_computed':0,'new_independent_observations':0,'native_budget_renewed':False,
                'historical_native_budget_compliance_reestablished':False,'query_numeric_tokens':query.ledger['reserved_numeric_tokens'],'query_json_bytes':query.ledger['unique_json_bytes'],
                'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}
        rr=encode(result)
        if sum(map(len,pieces.values()))+len(rr)+(out/'catalog-query-ledger.json').stat().st_size>2400000:raise ValueError('Whole output cap')
        for p,n in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv'),(SERIES,'monthly-series.json'),(SERIES_CSV,'monthly-series.csv')]:(out/n).write_bytes(pieces[p])
        (out/'admission-ledger.json').write_bytes(rr);print(json.dumps(result),flush=True)
    finally:signal.alarm(0)
if __name__=='__main__':main()
