"""One bounded cloud request for an East Greenland Coastal original definition paper."""
import hashlib,json,urllib.error,urllib.request
from pathlib import Path
from acquire_ncc_skagseth_table1_v1 import NoRedirect

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/egcc-sutherland-primary-paper-acquisition-operator-v1.json'
URL='https://rpickart.whoi.edu/wp-content/uploads/sites/53/2016/02/ProginOcean2008_Sutherland.pdf'
MAX_BODY_BYTES=7000000


def acquire(op,out,transport=None):
    if op['url']!=URL or op['maximum_http_attempts']!=1 or op['maximum_response_body_bytes']!=MAX_BODY_BYTES or op['timeout_seconds']!=25 or op['follow_redirects'] is not False or op['automatic_retry'] is not False:raise ValueError('Exact primary URL and frozen single-attempt bounds required')
    if any(op['eligibility'].values()):raise ValueError('Paper acquisition does not admit a measurement')
    out.mkdir(exist_ok=True);report={'schema':'osw.egcc-sutherland-primary-paper-acquisition.v1','source_url':URL,'attempts':1,'http_status':None,'status':None,'redirects_followed':0,'automatic_retries':0,'body_bytes':0,'body_sha256':None,'primary_PDF_retained':False,'new_measurements_admitted':0,'new_ocean_field_requests':0,'runtime_changed':False,'full_goal_complete':False};response=None
    try:
        request=urllib.request.Request(URL,headers={'User-Agent':'OSW-primary-source-custody/1.0','Accept':'application/pdf','Accept-Encoding':'identity'})
        try:response=(transport or urllib.request.build_opener(NoRedirect())).open(request,timeout=25)
        except urllib.error.HTTPError as error:response=error
        report['http_status']=response.code;report['content_type']=response.headers.get('Content-Type','');raw=response.read(MAX_BODY_BYTES+1)
        if len(raw)>MAX_BODY_BYTES:report['status']='RESPONSE_BODY_LIMIT_EXCEEDED'
        else:
            report.update(body_bytes=len(raw),body_sha256=hashlib.sha256(raw).hexdigest())
            if response.code==200 and raw.startswith(b'%PDF-'):
                (out/'journal-article.pdf').write_bytes(raw);report.update(status='PRIMARY_PDF_RETAINED_PENDING_VISUAL_REVIEW',primary_PDF_retained=True)
            else:
                (out/'error-response.bin').write_bytes(raw);report['status']='HTTP_OR_CONTENT_NOT_PRIMARY_PDF'
    except (urllib.error.URLError,TimeoutError,OSError) as error:report.update(status='TRANSPORT_FAILURE',error_type=type(error).__name__)
    finally:
        if response is not None:response.close()
    return report


def main():
    op=json.loads((ROOT/OPERATOR).read_bytes())
    for f,pin in op['input_sha256'].items():
        if hashlib.sha256((ROOT/f).read_bytes()).hexdigest()!=pin:raise ValueError('Pinned source acquisition input changed: '+f)
    out=Path('egcc-sutherland-primary-paper-v1');report=acquire(op,out);report.update(operator_file=OPERATOR,operator_sha256=hashlib.sha256((ROOT/OPERATOR).read_bytes()).hexdigest(),input_sha256=op['input_sha256']);(out/'acquisition.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print(json.dumps(report))


if __name__=='__main__':main()
