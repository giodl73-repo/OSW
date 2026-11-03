"""Bounded primary HTML plus original figure custody; no ocean-field queries."""
import hashlib,json,re,subprocess,sys,urllib.error,urllib.request
from html.parser import HTMLParser
from pathlib import Path
from acquire_ncc_skagseth_table1_v1 import NoRedirect

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/nec-huang2022-primary-html-acquisition-operator-v1.json'
OUT=Path('nec-huang2022-primary-html-v1')
TARGETS=[('article.html','https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2022.979442/full',1500000),('figure2.webp','https://www.frontiersin.org/files/Articles/979442/xml-images/fmars-09-979442-g002.webp',800000)]
TITLE='Interannual variations of the North Equatorial Current/Undercurrent from mooring array observations'


def encode(v):return (json.dumps(v,separators=(',',':'),allow_nan=False)+'\n').encode()
def save(file,v):
    temp=file.with_suffix('.pending');temp.write_bytes(encode(v));temp.replace(file)


class Text(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.parts=[]
    def handle_data(self,value):self.parts.append(value)


def validate_html(raw):
    text=raw.decode('utf8');parser=Text();parser.feed(text);plain=re.sub(r'\s+',' ',' '.join(parser.parts))
    if '<html' not in text.lower() or TITLE.lower() not in plain.lower() or '979442' not in text:raise ValueError('Original full primary article identity required')
    if any(value not in plain for value in ['70 m','90 m','430 m','400 m','1-year']):raise ValueError('Complete focal results and filter methods must be present')


def validate_operator(op):
    if op['targets']!=[{'file':f,'url':u,'maximum_response_body_bytes':cap} for f,u,cap in TARGETS] or op['timeout_seconds']!=25 or op['maximum_attempts_per_url']!=1 or op['follow_redirects'] is not False or op['automatic_retry'] is not False or op['worker_timeout_seconds']!=90 or op['maximum_joint_body_bytes']!=2300000 or any(op['eligibility'].values()):raise ValueError('Exact two-document targets and unchanged bounded single-attempt custody required')


def acquire(op,out,opener=None):
    validate_operator(op);out=Path(out);out.mkdir(exist_ok=True)
    if (out/'acquisition.json').exists():raise ValueError('Never replay a prior attempted custody run')
    opener=opener or urllib.request.build_opener(NoRedirect());report={'schema':'osw.nec-huang2022-primary-html-acquisition.v1','requests':[],'new_ocean_field_requests':0,'new_references_admitted':0,'automatic_retries':0,'redirects_followed':0,'original_pdf_obtained':False,'wire_hash_claimed':False,'full_goal_complete':False};save(out/'acquisition.json',report)
    for filename,url,cap in TARGETS:
        row={'file':filename,'url':url,'attempt':1,'status':'PENDING','maximum_response_body_bytes':cap};report['requests'].append(row);save(out/'acquisition.json',report);response=None;raw=b''
        try:
            request=urllib.request.Request(url,headers={'User-Agent':'OSW-primary-source-custody/1.0','Accept-Encoding':'identity'})
            try:response=opener.open(request,timeout=25)
            except urllib.error.HTTPError as error:response=error
            row['http_status']=response.code;row['content_type']=response.headers.get('Content-Type','');raw=response.read(cap+1)
            if len(raw)>cap:raise ValueError('Fixed document body limit exceeded')
            row.update(body_bytes=len(raw),body_sha256=hashlib.sha256(raw).hexdigest());(out/filename).write_bytes(raw)
            if response.code!=200:raise ValueError('Primary document HTTP status not200')
            if filename.endswith('.html'):validate_html(raw)
            elif raw[:4]!=b'RIFF' or raw[8:12]!=b'WEBP':raise ValueError('Original WebP figure required')
            row['status']='EXACT_PRIMARY_DOCUMENT_RETAINED'
        except (ValueError,UnicodeError,urllib.error.URLError,TimeoutError,OSError) as error:
            row.update(status='FAILED_NOT_RETRIED',error_type=type(error).__name__);save(out/'acquisition.json',report);return report
        finally:
            if response is not None:response.close()
        save(out/'acquisition.json',report)
    report['status']='PRIMARY_HTML_AND_ORIGINAL_FIGURE_RETAINED_PENDING_REVIEW';save(out/'acquisition.json',report);return report


def worker(root=ROOT,out=OUT):
    op=json.loads((root/OPERATOR).read_bytes())
    for file,pin in op['input_sha256'].items():
        if hashlib.sha256((root/file).read_bytes()).hexdigest()!=pin:raise ValueError('Pinned custody input changed: '+file)
    report=acquire(op,out);report.update(operator_file=OPERATOR,operator_sha256=hashlib.sha256((root/OPERATOR).read_bytes()).hexdigest(),input_sha256=op['input_sha256']);save(Path(out)/'acquisition.json',report);print(json.dumps(report),flush=True)


if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--worker':worker(out=Path(sys.argv[2]))
    elif len(sys.argv)==1:
        OUT.mkdir(exist_ok=True)
        try:
            process=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--worker',str(OUT)],capture_output=True,timeout=90);result={'status':'WORKER_TERMINAL','returncode':process.returncode,'log':(process.stdout+process.stderr)[-16000:].decode('utf8',errors='replace')}
        except subprocess.TimeoutExpired as failure:result={'status':'WORKER_KILLED_AT_90_SECOND_BOUND','returncode':None}
        save(OUT/'process-report.json',result);print(json.dumps(result),flush=True)
    else:raise ValueError('Only fixed parent/worker invocations allowed')
