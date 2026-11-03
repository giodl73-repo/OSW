"""Single bounded cloud attempt to retain the primary NCC ADCP supporting table."""
import hashlib,json,urllib.error,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/ncc-skagseth-table1-acquisition-operator-v1.json'
URL='https://agupubs.onlinelibrary.wiley.com/action/downloadSupplement?doi=10.1029%2F2011JC006996&file=jgrc12064-sup-0001-t01.txt'
MAX_BODY_BYTES=65536


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):return None


def acquire(op,out,opener=None):
    if op['url']!=URL or op['maximum_http_attempts']!=1 or op['maximum_response_body_bytes']!=MAX_BODY_BYTES or op['timeout_seconds']!=25 or op['follow_redirects'] is not False or op['automatic_retry'] is not False:raise ValueError('Frozen primary table URL and single-attempt bounds required')
    if any(op['eligibility'].values()):raise ValueError('Acquisition establishes no physical depth or new measurement')
    out.mkdir(exist_ok=True)
    ledger={'schema':'osw.ncc-skagseth-table1-acquisition-report.v1','source_url':URL,'attempts':1,'redirects_followed':0,'automatic_retries':0,'maximum_response_body_bytes':MAX_BODY_BYTES,'status':None,'http_status':None,'content_type':None,'retained_body_bytes':0,'body_sha256':None,'source_table_retained':False,'numeric_table_parsing_performed':False,'new_current_measurements_admitted':0,'new_ocean_field_requests':0,'runtime_changed':False,'full_goal_complete':False}
    request=urllib.request.Request(URL,headers={'User-Agent':'OSW-primary-source-custody/1.0','Accept':'text/plain','Accept-Encoding':'identity'})
    transport=opener or urllib.request.build_opener(NoRedirect())
    response=None
    try:
        try:response=transport.open(request,timeout=25)
        except urllib.error.HTTPError as error:response=error
        ledger['http_status']=response.code;ledger['content_type']=response.headers.get('Content-Type','');raw=response.read(MAX_BODY_BYTES+1)
        if len(raw)>MAX_BODY_BYTES:
            ledger.update(status='RESPONSE_BODY_LIMIT_EXCEEDED',retained_body_bytes=0,body_limit_exceeded=True)
        else:
            ledger.update(retained_body_bytes=len(raw),body_sha256=hashlib.sha256(raw).hexdigest());(out/'response-body.bin').write_bytes(raw)
            if response.code!=200:ledger['status']='HTTP_RESPONSE_NOT_SOURCE_SUCCESS'
            elif not raw or b'<html' in raw[:2048].lower() or b'<!doctype html' in raw[:2048].lower():ledger['status']='NON_TABLE_OR_EMPTY_RESPONSE'
            else:
                try:raw.decode('utf8')
                except UnicodeDecodeError:ledger['status']='NON_UTF8_TABLE_RESPONSE'
                else:ledger.update(status='PRIMARY_TABLE_BYTES_RETAINED_PENDING_CONTENT_REVIEW',source_table_retained=True)
    except (urllib.error.URLError,TimeoutError,OSError) as error:
        ledger.update(status='TRANSPORT_FAILURE',error_type=type(error).__name__)
    finally:
        if response is not None:response.close()
    return ledger


def main():
    op=json.loads((ROOT/OPERATOR).read_bytes())
    for f,pin in op['input_sha256'].items():
        if hashlib.sha256((ROOT/f).read_bytes()).hexdigest()!=pin:raise ValueError('Pinned acquisition input changed: '+f)
    out=Path('ncc-skagseth-table1-acquisition-v1');report=acquire(op,out);report.update(operator_file=OPERATOR,operator_sha256=hashlib.sha256((ROOT/OPERATOR).read_bytes()).hexdigest(),input_sha256=op['input_sha256'])
    (out/'acquisition.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print(json.dumps(report))


if __name__=='__main__':main()
