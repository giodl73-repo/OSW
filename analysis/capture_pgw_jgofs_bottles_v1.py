"""One staged source case: capture two declared bottle files, not depth claims."""
import csv,hashlib,html,io,json,os,re,signal,time,urllib.error,urllib.parse,urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OP='research/pgw-jgofs-bottle-source-case-operator-v1.json'
LANDING='https://www.bco-dmo.org/dataset/2528'
FILES={'TT043':'bottle_TT043.csv','TT049':'bottle_TT049.csv'}
CAPS={'TT043':320000,'TT049':550000}
NUMBERS=re.compile(rb'[-+]?\d+(?:\.\d*)?(?:[Ee][-+]?\d+)?')

def encode(v):return (json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
def sha(v):return hashlib.sha256(v).hexdigest()

class Anchors(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.links=[];self.text=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a':
            for k,v in attrs:
                if k=='href' and v:self.links.append(urllib.parse.urljoin(LANDING,v))
    def handle_data(self,data):self.text.append(data)

def metadata(raw):
    text=raw.decode('utf8');parser=Anchors();parser.feed(text)
    if not ('CC-BY-4.0' in text or 'creativecommons.org/licenses/by/4.0' in text):raise ValueError('Explicit primary CC-BY4.0 metadata required')
    selected={}
    for cruise,filename in FILES.items():
        hits={url for url in parser.links if urllib.parse.urlsplit(url).path.rsplit('/',1)[-1]==filename}
        if len(hits)!=1:raise ValueError('Exactly one primary observed file URL for '+filename)
        url=hits.pop();parts=urllib.parse.urlsplit(url)
        if parts.scheme!='https' or parts.netloc!='datadocs.bco-dmo.org':raise ValueError('Only declared primary HTTPS file host')
        selected[cruise]=url
    plain=re.sub(r'\s+',' ',html.unescape(' '.join(parser.text)))
    snippets=[]
    for match in re.finditer(r'IPTS|ITS.?90|pressure|salinity|temperature|unitText|unitCode',plain,re.I):
        snippets.append(plain[max(0,match.start()-100):match.end()+180])
        if len(snippets)>=24:break
    return {'schema':'osw.pgw-jgofs-primary-file-metadata.v1','dataset_url':LANDING,'selected_file_urls':selected,'license':'CC-BY-4.0','parameter_context_snippets':snippets,'source_metadata_sha256':sha(raw),'temperature_scale_qualified':False,'pressure_unit_qualified':False,'salinity_scale_qualified':False,'interpretation':'Primary literal file links and contextual metadata only. Units/scales,profile identity,geographic membership and vertical support still require explicit qualification; no current depths admitted.'}

def header(raw):
    text=raw.decode('utf-8-sig');lines=text.splitlines()
    for i,line in enumerate(lines[:32]):
        row=next(csv.reader([line]));normalized=[re.sub('[^a-z0-9]','',v.casefold()) for v in row]
        if any(v in ['lat','latitude','latn'] for v in normalized) and any(v in ['lon','long','longitude','lone'] for v in normalized):
            return {'source_header_line_1based':i+1,'columns':row,'normalized_columns':normalized,'status':'HEADER_LABELS_CAPTURED_NOT_UNIT_OR_PROFILE_QUALIFICATION','native_numeric_values_decoded':0}
    return {'source_header_line_1based':None,'columns':[],'normalized_columns':[],'status':'UNQUALIFIED_HEADER_NO_NATIVE_PARSE','native_numeric_values_decoded':0}

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):raise RuntimeError('No redirects or alternate source targets')

def main():
    start=float(os.environ['OSW_JGOFS_CAPTURE_START']);out=ROOT/'pgw-jgofs-bottle-source-capture-v1';out.mkdir(exist_ok=False)
    ledger={'schema':'osw.pgw-jgofs-original-bottle-source-case-ledger.v1','case_id':'pgw-jgofs2528-TT043-TT049-v1','phase':'raw_source_capture_before_native_profile_analysis','provider_operation_cap_total':3,'provider_operations_attempted':0,'provider_operations_remaining':3,'raw_byte_cap_total':7000000,'raw_bytes_retained':0,'numeric_scalar_cap_total':250000,'raw_lexical_numeric_reservation':0,'original_analysis_scalar_reservation':100000,'native_numeric_values_decoded':0,'native_profile_analysis_passes':0,'maximum_selected_profiles':150,'minimum_selected_profiles':3,'maximum_native_levels_per_selected_profile':40,'maximum_decoded_cells':20000,'maximum_measurement_nodes':6000,'cumulative_active_second_cap':60,'targets':[],'status':'INITIALIZED','new_current_depth_measurements':0,'full_goal_complete':False}
    def save():
        ledger['cumulative_active_seconds']=time.monotonic()-start;tmp=out/'case-ledger.tmp';tmp.write_bytes(encode(ledger));os.replace(tmp,out/'case-ledger.json')
    def stop(*a):ledger['status']='TERMINATED_AT_ORIGINAL_ABSOLUTE_DEADLINE_OR_SIGTERM';save();raise TimeoutError('Original60active-second source case deadline')
    signal.signal(signal.SIGALRM,stop);signal.signal(signal.SIGTERM,stop);elapsed=time.monotonic()-start
    if not 0<=elapsed<30:raise ValueError('One shared synthetic/capture clock')
    signal.alarm(max(1,int(60-elapsed)));save()
    def capture(url,name,cap):
        parts=urllib.parse.urlsplit(url)
        if parts.scheme!='https' or parts.netloc not in ['www.bco-dmo.org','datadocs.bco-dmo.org'] or ledger['provider_operations_remaining']<=0:raise ValueError('Original source hosts and shared case operation cap')
        target={'url':url,'file':name,'reserved_byte_cap':cap,'status':'RESERVED_BEFORE_REQUEST'};ledger['targets'].append(target);ledger['provider_operations_attempted']+=1;ledger['provider_operations_remaining']-=1;save();raw=b''
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'OSW-bounded-observational-source-preflight/1.0','Accept-Encoding':'identity'})
            try:
                with urllib.request.build_opener(NoRedirect()).open(req,timeout=min(25,max(1,60-(time.monotonic()-start)))) as response:raw=response.read(cap+1);target['http_status']=response.status
            except urllib.error.HTTPError as error:raw=error.read(cap+1);target['http_status']=error.code;raise
        except BaseException as error:target['status']='FAILED_NO_RETRY';target['error_type']=type(error).__name__;raise
        finally:
            (out/name).write_bytes(raw);ledger['raw_bytes_retained']+=len(raw);target['bytes']=len(raw);target['sha256']=sha(raw);save()
        if len(raw)>cap or ledger['raw_bytes_retained']>7000000:raise ValueError('Raw source retained before byte-cap rejection')
        tokens=len(NUMBERS.findall(raw));target['lexical_numeric_upper_bound']=tokens;ledger['raw_lexical_numeric_reservation']+=tokens
        ledger['combined_numeric_upper_bound']=ledger['raw_lexical_numeric_reservation']+ledger['original_analysis_scalar_reservation']
        if ledger['combined_numeric_upper_bound']>250000:save();raise ValueError('Shared prospective source/analysis scalar cap before source interpretation')
        target['status']='RETAINED_AND_RESERVED_BEFORE_INTERPRETATION';save();return raw
    try:
        op=json.loads((ROOT/OP).read_bytes())
        for p,h in op['input_sha256'].items():
            if sha((ROOT/p).read_bytes())!=h:raise ValueError('Frozen original case input changed:'+p)
        primary_raw=capture(LANDING,'dataset-metadata.html',500000);facts=metadata(primary_raw);files=[]
        for cruise,filename in FILES.items():
            raw=capture(facts['selected_file_urls'][cruise],filename,CAPS[cruise]);files.append({'cruise_id':cruise,'source_file':filename,'source_url':facts['selected_file_urls'][cruise],'bytes':len(raw),'sha256':sha(raw),'header':header(raw)})
        manifest={'schema':'osw.pgw-jgofs-raw-bottle-source-cohort.v1','metadata':facts,'files':files,'selected_profile_region_degrees':{'west':57,'east':60,'south':22,'north':24.5},'selected_pressure_window_if_dbar_qualified':[80,700],'proposed_pgw_core_window_if_dbar_qualified':[150,400],'proposed_core_sigma0_window_kg_m3':[25.5,27.],'proposed_maximum_adjacent_pressure_gap_dbar':125,'proposed_primary_fraction_contour':.25,'proposed_operator_context_doi':'10.1029/2023JC020668','proposed_mixture_endmembers_SA_CT':{'IODW':[34.86,1.],'PGW':[41.04,29.56],'ICW':[36.37,23.45]},'interpretation':'Two predeclared cruise source bodies retained without native numeric or profile parsing. Cruise labels/publication versions are not exact observing dates. Do not assign current identity or hydrographic boundaries until source units,temperature scale,QC,profile grouping and native support qualify. Historical mixture application would be an explicitly assumed diagnostic,not a1995measured current bottom.','native_numeric_values_decoded':0,'new_current_depth_measurements':0,'runtime_changed':False,'full_goal_complete':False}
        packet=encode(manifest)
        if len(packet)+sum(p.stat().st_size for p in out.iterdir() if p.is_file())>2400000:raise ValueError('Whole source/output cap')
        (out/'source-cohort.json').write_bytes(packet);ledger['status']='RAW_DECLARED_COHORT_RETAINED_ANALYSIS_PENDING_UNITS_AND_NATIVE_SUPPORT';save()
        print(json.dumps({'status':ledger['status'],'source_files':files,'provider_operations_attempted':ledger['provider_operations_attempted'],'provider_operations_remaining':ledger['provider_operations_remaining'],'raw_bytes_retained':ledger['raw_bytes_retained'],'combined_numeric_upper_bound':ledger['combined_numeric_upper_bound'],'native_numeric_values_decoded':0,'new_current_depth_measurements':0}),flush=True)
    except BaseException as error:
        if ledger['status']!='TERMINATED_AT_ORIGINAL_ABSOLUTE_DEADLINE_OR_SIGTERM':ledger['status']='FAILED_OR_UNQUALIFIED_SOURCE_CAPTURE_NO_RETRY';ledger['error_type']=type(error).__name__;save()
        raise
    finally:signal.alarm(0);save()

if __name__=='__main__':main()
