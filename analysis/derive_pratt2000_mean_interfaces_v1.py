"""Extract two explicitly reported monthly-mean interfaces from retained prose."""
import hashlib,json,os,re,signal,socket,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OP='research/pratt2000-mean-interface-operator-v1.json'
QUOTE='research/pratt2000-bab-mandab-mean-interface-quote-v1.txt'
CUSTODY='research/pratt2000-bab-mandab-mean-interface-custody-v1.json'
LEDGER='research/pratt2000-bab-mandab-primary-ledger-v1.json'
def numbers(v):
    if isinstance(v,dict):return sum(numbers(x) for x in v.values())
    if isinstance(v,list):return sum(numbers(x) for x in v)
    return int(type(v) in (int,float))
def derive(raw):
    if len(raw)>1000:raise ValueError('Exact bounded source quote')
    text=json.loads(b'"'+raw+b'"')
    match=re.fullmatch(r'ranges from (\d+) m in winter to (\d+) m in\s+summer\.',text)
    if not match or tuple(int(x) for x in match.groups())!=(35,110):raise ValueError('Exact source-reported interface endpoints')
    rows=[]
    for season,value in zip(['winter','summer'],map(int,match.groups())):
        rows.append({'id':'red-sea-pratt2000-hanish-'+season+'-mean-interface','entity_id':'current:red-sea-saline-overflow','metric':'reported_monthly_mean_velocity_zero_crossing_interface_depth','approximate_value_m':value,'unit':'m','source_season_label':season,'source_statistic':'authors_reported_endpoint_of_monthly_mean_profile_interface_depths','geographic_scope':'Hanish Sill,Bab al Mandab; local exchange-flow interface','temporal_scope':'Source monthly profiles April-November1996; authors winter/summer labels, exact endpoint occupation month unresolved; not seasonal climatology or annual extrema.','vertical_datum':'below_sea_surface_as_reported','source_boundary_definition':'Mean velocity zero crossing between inflowing Gulf of Aden water and deeper outflowing Red Sea water.','source_velocity_profile_sampling_context':'10mvertical bins from10to130m; sourceextrapolated0/140/150m separately; no raw velocity reconstruction performed.','physical_current_bottom_m':None,'thickness_m':None,'range_m':None,'annual_range_m':None,'uncertainty_m':None,'calendar_month':None,'paired_lower_boundary_m':None,'whole_current_representative':False,'physical_depth_ranking_eligible':False,'seasonal_playback_eligible':False,'reference_route_projection_eligible':False,'volume_eligible':False,'source_qualifications':['Boundary of a monthly mean velocity profile, not mean individual interface depths.','Source season labels do not provide a recurring seasonal cycle or independent monthly observations.','No bottom or thickness from subtracting a sill/bathymetric/sampling depth.','Surface summer outflow is not the dense deeper overflow.','No exact station coordinates or route geometry from a named section.']})
    return rows

def main():
    def stopped(*args):raise SystemExit('Bounded retained-prose derivation stopped; no replay')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stopped)
    socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline retained source only'))
    start=float(os.environ['OSW_PRATT_INTERFACE_START']);signal.alarm(60)
    if not 0<=time.monotonic()-start<30:raise ValueError('Shared phase clock')
    out=ROOT/'pratt2000-mean-interface-v1';out.mkdir(exist_ok=False)
    audit={'status':'RESERVED_RETAINED_PROSE_TRANSFORMATION','new_provider_operations':0,'new_native_array_values_decoded':0,'new_canonical_references':0}
    def save():(out/'derivation-ledger.json').write_bytes((json.dumps(audit,indent=2)+'\n').encode())
    save()
    try:
        read=lambda p:(ROOT/p).read_bytes()
        op=json.loads(read(OP))
        for p,h in op['input_sha256'].items():
            if hashlib.sha256(read(p)).hexdigest()!=h:raise ValueError('Frozen input changed:'+p)
        c=json.loads(read(CUSTODY));prior=json.loads(read(LEDGER));raw=read(QUOTE)
        if prior['status']!='PRIMARY_PDF_CAPTURED_PENDING_SCIENTIFIC_SCOPE_REVIEW' or prior['attempted_provider_operations']!=1 or prior['source_numeric_tokens']!=1092 or prior['native_array_values_decoded']!=0:raise ValueError('Original closed case accounting')
        if hashlib.sha256(raw).hexdigest()!=c['quote_sha256'] or len(raw)!=c['quote_bytes'] or c['raw_pdf_sha256']!=prior['body_sha256']:raise ValueError('Exact source fragment custody')
        rows=derive(raw)
        report={'schema':'osw.pratt2000-hanish-reported-mean-interfaces.v1','source_url':prior['source_url'],'citation':'Pratt,L.J.,Deese,H.E.,Murray,S.P.andJohns,W.(2000),JPO30,2515-2534,doi:10.1175/1520-0485(2000)030<2515:CDMISH>2.0.CO;2','source_pdf_sha256':prior['body_sha256'],'source_locator':c['source_locator'],'source_quote_custody':CUSTODY,'rows':rows,'new_canonical_references':0,'runtime_changed':False,'full_goal_complete':False}
        encoded=(json.dumps(report,indent=2)+'\n').encode();back=json.loads(encoded)
        if back!=report:raise ValueError('Full actual source descriptor JSON roundtrip')
        newnumbers=numbers(op)+numbers(c)+numbers(prior)+4+2*numbers(report)
        audit.update(status='TWO_SOURCE_REPORTED_MEAN_INTERFACES_VERIFIED_NOT_CANONICALLY_ADMITTED',original_source_case_ledger=prior,new_metadata_and_descriptor_numeric_charge=newnumbers,cumulative_source_case_numeric_bound=prior['source_numeric_tokens']+newnumbers,provider_operations_remaining=0,new_phase_elapsed_seconds=time.monotonic()-start)
        audit['cumulative_case_elapsed_seconds']=prior['elapsed_seconds']+audit['new_phase_elapsed_seconds']
        if audit['cumulative_source_case_numeric_bound']>250000 or audit['cumulative_case_elapsed_seconds']>60 or len(encoded)>2000000:raise ValueError('Original case limits not renewed')
        (out/'interfaces.json').write_bytes(encoded);save();print(json.dumps(audit))
    except BaseException as error:
        audit.update(status='FAILED_NO_RETRY',error_type=type(error).__name__,error=str(error));save();raise
    finally:signal.alarm(0)
if __name__=='__main__':main()
