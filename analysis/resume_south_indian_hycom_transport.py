"""Declared longer-timeout retry of unchanged frozen source requests."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.request import urlopen

from acquire_eac_100m_source import write_json
from acquire_indian_secc_hycom_2013 import pin
from acquire_south_indian_hycom_hydrography import validate_plan, validate_response, LIMIT, ROOT

TIMEOUT = 180
DECLARATION = ROOT/'research/south-indian-hycom-longer-timeout-resume.json'
PROTOCOL = 'plans/south-indian-hycom-transport-resume-v1.md'
OPERATOR = 'analysis/resume_south_indian_hycom_transport.py'


def declare(directory, declaration=DECLARATION):
    """Run only after the previous acquisition process is terminal."""
    directory, declaration = Path(directory), Path(declaration)
    if declaration.exists():
        raise ValueError('Existing declaration requires inspection, not replacement')
    plan = validate_plan(directory)
    existing, missing = {}, []
    for request in plan['requests']:
        path = directory/request['file']; receipt_path = path.with_suffix('.receipt.json')
        if path.exists() != receipt_path.exists():
            raise ValueError('Incomplete original/receipt pair requires inspection')
        if not path.exists():
            missing.append(request['file']); continue
        receipt = json.loads(receipt_path.read_bytes())
        if receipt['url'] != request['url'] or receipt['pin'] != pin(path):
            raise ValueError('Changed successful original')
        validate_response(path.read_bytes(), request, plan, directory)
        existing[path.name] = {'response': pin(path), 'receipt': pin(receipt_path)}
    if not missing:
        raise ValueError('No missing requests to resume')
    dependencies = {**plan['operators'], **plan['rules'],
                    OPERATOR: pin(ROOT/OPERATOR), PROTOCOL: pin(ROOT/PROTOCOL)}
    document = {'schema':'osw.south-indian-hycom-transport-resume.v1',
                'declared_utc':datetime.now(timezone.utc).isoformat(),
                'source_selection':pin(directory/'selection.json'),
                'dependencies':dependencies,'timeout_seconds':TIMEOUT,
                'workers':2,'response_byte_limit':LIMIT,
                'existing_successful_originals':existing,'missing_request_files':missing,
                'scope':'Transport timeout only: exact original request URLs, time indices, fields, depths, coordinates, response format and all scientific checks unchanged.',
                'physical_width_admitted':False,'current_association_verified':False}
    write_json(declaration,document)
    return document


def checked_declaration(directory, declaration=DECLARATION):
    directory, declaration = Path(directory), Path(declaration)
    plan = validate_plan(directory)
    document = json.loads(declaration.read_bytes())
    if (document['schema']!='osw.south-indian-hycom-transport-resume.v1'
            or document['source_selection']!=pin(directory/'selection.json')
            or document['timeout_seconds']!=TIMEOUT or document['workers']!=2
            or document['response_byte_limit']!=LIMIT
            or document['physical_width_admitted'] is not False
            or document['current_association_verified'] is not False):
        raise ValueError('Changed operational declaration')
    expected_dependencies={**plan['operators'],**plan['rules'],
                           OPERATOR:pin(ROOT/OPERATOR),PROTOCOL:pin(ROOT/PROTOCOL)}
    if document['dependencies']!=expected_dependencies:
        raise ValueError('Operational dependency set differs')
    for name,expected in document['dependencies'].items():
        if pin(ROOT/name)!=expected:
            raise ValueError('Changed declared operational dependency: '+name)
    all_files={r['file'] for r in plan['requests']}
    before=set(document['existing_successful_originals'])
    missing=document['missing_request_files']
    if (len(set(missing))!=len(missing) or before & set(missing)
            or before | set(missing)!=all_files):
        raise ValueError('Operational declaration changed source request coverage')
    for name,expected in document['existing_successful_originals'].items():
        path=directory/name
        if pin(path)!=expected['response'] or pin(path.with_suffix('.receipt.json'))!=expected['receipt']:
            raise ValueError('Successful original/receipt was modified')
    return plan,document


def resume(directory, declaration=DECLARATION):
    directory, declaration=Path(directory),Path(declaration)
    plan,document=checked_declaration(directory,declaration)
    def one(request):
        path=directory/request['file'];receipt_path=path.with_suffix('.receipt.json')
        if path.exists() != receipt_path.exists():
            raise ValueError('Incomplete original/receipt pair requires inspection')
        if path.exists():
            receipt=json.loads(receipt_path.read_bytes())
            if receipt['url']!=request['url'] or receipt['pin']!=pin(path):
                raise ValueError('Changed resumed original')
            validate_response(path.read_bytes(),request,plan,directory)
            print('retained',path.name,flush=True);return
        try:
            with urlopen(request['url'],timeout=TIMEOUT) as response:
                raw=response.read(LIMIT+1)
                headers,final_url=dict(response.headers),response.url
            if len(raw)>LIMIT:
                raise ValueError('Oversized source response')
            validate_response(raw,request,plan,directory)
            path.write_bytes(raw)
            write_json(receipt_path,{'url':request['url'],'final_url':final_url,
                       'pin':pin(path),'acquired_utc':datetime.now(timezone.utc).isoformat(),
                       'headers':headers,'operational_resume_declaration':{
                           'path':declaration.relative_to(ROOT).as_posix(),'pin':pin(declaration)},
                       'timeout_seconds':TIMEOUT})
            print('acquired',path.name,len(raw),flush=True)
        except Exception as error:
            with (directory/'failures.jsonl').open('a',encoding='utf8') as stream:
                stream.write(json.dumps({'file':request['file'],'url':request['url'],
                             'utc':datetime.now(timezone.utc).isoformat(),'error':repr(error),
                             'operation':'declared_longer_timeout_resume','timeout_seconds':TIMEOUT})+'\n')
            raise
    selected=[r for r in plan['requests'] if r['file'] in document['missing_request_files']]
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures=[executor.submit(one,r) for r in selected]
        failures=[]
        for future in futures:
            try:future.result()
            except Exception as error:failures.append(repr(error))
    if failures:
        raise ValueError(f'{len(failures)} failed requests; successful originals retained; first: {failures[0]}')
    checked_declaration(directory,declaration)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['declare','resume'])
    parser.add_argument('--directory',type=Path,default=ROOT/'.pytest_cache/south-indian-hycom-2013')
    args=parser.parse_args()
    if args.action=='declare':
        result=declare(args.directory)
        print(json.dumps({'existing_originals':len(result['existing_successful_originals']),
                          'missing_requests':result['missing_request_files'],'timeout_seconds':TIMEOUT}))
    else:resume(args.directory)
