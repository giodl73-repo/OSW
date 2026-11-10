"""One bounded original Alaska Coastal Current article capture; no field retrieval."""
import hashlib,json,re,urllib.error,urllib.request
from html.parser import HTMLParser
from pathlib import Path
from acquire_ncc_skagseth_table1_v1 import NoRedirect

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/alaska-jarosz2017-primary-html-acquisition-operator-v1.json'
URL='https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2016JC012102'
MAX_BYTES=1500000


class Text(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.parts=[]
    def handle_data(self,s):self.parts.append(s)


def validate_body(raw):
    html=raw.decode('utf8');p=Text();p.feed(html);text=re.sub(r'\s+',' ',' '.join(p.parts))
    markers=['Flow variability within the Alaska Coastal Current in winter','2016JC012102','Mooring Summary','62.9','65.8','96.9','73.2','throughout the water column','Winter Currents','40 h']
    if '<html' not in html.lower() or any(v.lower() not in text.lower() for v in markers):raise ValueError('Complete original article,station table and focal winter results required')


def acquire(op,out,opener=None):
    if op['url']!=URL or op['maximum_response_body_bytes']!=MAX_BYTES or op['timeout_seconds']!=25 or op['maximum_attempts']!=1 or op['follow_redirects'] is not False or op['automatic_retry'] is not False or any(op['eligibility'].values()):raise ValueError('Exact primary abstract and fixed one-attempt bounds required')
    out=Path(out);out.mkdir(exist_ok=True);report_file=out/'acquisition.json'
    if report_file.exists():raise ValueError('Do not replay a previous custody attempt')
    report={'schema':'osw.alaska-jarosz2017-primary-html-acquisition.v1','source_url':URL,'attempts':1,'status':'PENDING','body_bytes':0,'body_sha256':None,'full_article_obtained':False,'source_figures_visually_reviewed':False,'original_pdf_obtained':False,'new_references_admitted':0,'new_ocean_field_requests':0,'redirects_followed':0,'automatic_retries':0,'wire_hash_claimed':False,'full_goal_complete':False}
    save=lambda:report_file.write_bytes((json.dumps(report,indent=2)+'\n').encode());save();response=None
    try:
        request=urllib.request.Request(URL,headers={'User-Agent':'OSW-primary-source-custody/1.0','Accept-Encoding':'identity'})
        try:response=(opener or urllib.request.build_opener(NoRedirect())).open(request,timeout=25)
        except urllib.error.HTTPError as error:response=error
        report['http_status']=response.code;raw=response.read(MAX_BYTES+1)
        if len(raw)>MAX_BYTES:raise ValueError('Fixed body limit exceeded')
        report.update(body_bytes=len(raw),body_sha256=hashlib.sha256(raw).hexdigest());(out/'article.html').write_bytes(raw)
        if response.code!=200:raise ValueError('Institutional source HTTP status not200')
        validate_body(raw);report['status']='PRIMARY_FULL_HTML_RETAINED_PENDING_REVIEW';report['full_article_obtained']=True
    except (ValueError,UnicodeError,urllib.error.URLError,TimeoutError,OSError) as error:report.update(status='FAILED_NOT_RETRIED',error_type=type(error).__name__)
    finally:
        if response is not None:response.close()
    save();return report


if __name__=='__main__':
    op=json.loads((ROOT/OPERATOR).read_bytes())
    for file,pin in op['input_sha256'].items():
        if hashlib.sha256((ROOT/file).read_bytes()).hexdigest()!=pin:raise ValueError('Pinned custody input changed: '+file)
    out=Path('alaska-jarosz2017-primary-html-v1');report=acquire(op,out);report.update(operator_file=OPERATOR,operator_sha256=hashlib.sha256((ROOT/OPERATOR).read_bytes()).hexdigest(),input_sha256=op['input_sha256']);(out/'acquisition.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print(json.dumps(report),flush=True)
