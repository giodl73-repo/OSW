"""HTTP ASCII Float64 coordinate reader using unchanged paired-coordinate checks."""
import base64,json,math,re,subprocess,sys,urllib.error,urllib.parse,urllib.request
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
import probe_hycom_native_client_coordinates_v1 as frozen

ROOT=frozen.ROOT
OPERATOR='research/hycom-http-coordinate-probe-operator-v1.json'
OUT=Path('hycom-http-coordinate-probe-v1')
CONTROLS=['research/source-data/ncc-north-joint-sections-v1/2022-03-15-section-61p5n.json','research/source-data/ncc-north-joint-sections-v1/2022-12-15-section-62p25n.json']


def coordinate_url(url,axis):return url+'.ascii?'+axis+urllib.parse.quote('[0:1:'+str(frozen.SHAPES[axis]-1)+']',safe=':')
URLS={url+suffix:20000 for url in frozen.SOURCES.values() for suffix in ['.dds','.das']}
URLS.update({coordinate_url(url,axis):32*size+4096 for url in frozen.SOURCES.values() for axis,size in frozen.SHAPES.items()})


def dds_shapes(raw):
    text=raw.decode('utf8').split('Grid {',1)[0];result={}
    if not text.lstrip().startswith('Dataset {'):raise ValueError('Original DDS metadata response required')
    for axis,size in frozen.SHAPES.items():
        matches=re.findall(r'\bFloat64\s+'+axis+r'\['+axis+r'\s*=\s*(\d+)\]',text)
        if matches!=[str(size)]:raise ValueError('Exactly one expected Float64 coordinate declaration required')
        result[axis]=(size,)
    return result


def das_strings(raw):
    text=raw.decode('utf8');result={}
    if not text.lstrip().startswith('Attributes {'):raise ValueError('Original DAS metadata required')
    for name in [*frozen.SHAPES,'NC_GLOBAL']:
        block=re.search(r'(?ms)^ {4}'+name+r'\s*\{\s*\n(.*?)^ {4}\}',text)
        if not block:raise ValueError('Original top-level coordinate/global DAS block required')
        pairs=re.findall(r'String\s+(\w+)\s+("(?:\\.|[^"\\])*")\s*;',block.group(1));attributes={}
        for key,value in pairs:
            if key in attributes:raise ValueError('Unique source string attributes required')
            attributes[key]=json.loads(value)
        result[name]=attributes
    return result


def ascii_values(raw,axis):
    if axis not in frozen.SHAPES:raise ValueError('Only coordinate ASCII data permitted')
    size=frozen.SHAPES[axis];text=raw.decode('utf8');parts=text.split('---------------------------------------------')
    if len(parts)!=2 or not parts[0].lstrip().startswith('Dataset {') or re.findall(r'\bFloat64\s+'+axis+r'\['+axis+r'\s*=\s*(\d+)\]',parts[0])!=[str(size)]:raise ValueError('Exact original Float64 coordinate response header required')
    lines=parts[1].strip().splitlines()
    if not lines or lines[0].strip()!=f'{axis}[{size}]':raise ValueError('Exact full native coordinate label required')
    tokens='\n'.join(lines[1:]).split(',')
    number=r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?'
    if len(tokens)!=size or any(not re.fullmatch(number,token.strip()) for token in tokens):raise ValueError('All-and-only expected Float64 coordinate tokens required')
    values=[float(token) for token in tokens]
    if not all(math.isfinite(v) for v in values):raise ValueError('Finite native coordinates required')
    return values


class NoRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):raise ValueError('No redirects or extra HTTP attempts permitted')


class HTTP:
    def __init__(self,out,opener=None):
        self.out=Path(out);self.opener=opener or urllib.request.build_opener(NoRedirects());self.seen=set();self.report={'schema':'osw.hycom-coordinate-http-ledger.v1','requests':[],'new_velocity_or_salinity_field_requests':0,'retries':0,'redirects_followed':0,'wire_hash_claimed':False};self.save()
    def save(self):frozen.write_json(self.out/'http-ledger.json',self.report)
    def get(self,url):
        if url not in URLS or url in self.seen:raise ValueError('Only fixed metadata/full-coordinate URLs once;no model fields or replays')
        self.seen.add(url);row={'url':url,'status':'HTTP_REQUEST_PENDING','attempts':1,'network_operation_timeout_seconds':15,'maximum_response_body_bytes':URLS[url]};self.report['requests'].append(row);self.save();raw=b'';status=None;error=None
        try:
            request=urllib.request.Request(url,headers={'User-Agent':'OSW-full-native-coordinate-probe','Accept-Encoding':'identity'})
            with self.opener.open(request,timeout=15) as response:status=response.status;raw=response.read(URLS[url]+1)
        except urllib.error.HTTPError as failure:
            status=failure.code;error=type(failure).__name__
            try:raw=failure.read(URLS[url]+1)
            except (TimeoutError,OSError) as read_error:error+=':'+type(read_error).__name__
            finally:failure.close()
        except (urllib.error.URLError,TimeoutError,OSError,ValueError) as failure:error=type(failure).__name__
        truncated=len(raw)>URLS[url];body=raw[:URLS[url]];payload={'schema':'osw.hycom-coordinate-http-response.v1','url':url,'http_status':status,'error_type':error,'retained_response_body_base64':base64.b64encode(body).decode(),'retained_response_body_sha256':frozen.digest(body),'retained_response_body_bytes':len(body),'response_body_truncated':truncated,'wire_hash_claimed':False};name='http-response-'+str(len(self.report['requests']))+'.json';encoded=frozen.encode(payload);frozen.write_json(self.out/name,payload);row.update(status='HTTP_RESPONSE_RETAINED' if error is None and status==200 and not truncated else 'HTTP_REQUEST_FAILED_OR_OVERSIZE',http_status=status,error_type=error,response={'file':name,'bytes':len(encoded),'sha256':frozen.digest(encoded)});self.save()
        if row['status']!='HTTP_RESPONSE_RETAINED':raise ValueError('Coordinate HTTP request failed;see durable response receipt')
        return body


class Values:
    def __init__(self,values):self.values=values
    def tolist(self):return list(self.values)


class Variable:
    def __init__(self,ds,axis):self.ds=ds;self.axis=axis;self.shape=ds.shapes[axis];self.dimensions=(axis,)
    def __getattr__(self,name):
        if name not in self.ds.attributes[self.axis]:raise AttributeError(name)
        return self.ds.attributes[self.axis][name]
    def __getitem__(self,key):
        if key!=slice(None):raise ValueError('Only the exact complete native coordinate slice permitted')
        return Values(ascii_values(self.ds.http.get(coordinate_url(self.ds.url,self.axis)),self.axis))


class Dataset:
    def __init__(self,url,http):
        if url not in frozen.SOURCES.values():raise ValueError('Original fixed2022sources only')
        self.url=url;self.http=http;self.shapes=dds_shapes(http.get(url+'.dds'));self.attributes=das_strings(http.get(url+'.das'))
    def __getitem__(self,axis):
        if axis not in frozen.SHAPES:raise ValueError('No velocity/salinity/model-variable access permitted')
        return Variable(self,axis)
    def ncattrs(self):return list(self.attributes['NC_GLOBAL'])
    def getncattr(self,key):return self.attributes['NC_GLOBAL'][key]
    def close(self):pass


@contextmanager
def configured():
    old=frozen.OPERATOR;frozen.OPERATOR=OPERATOR
    try:yield
    finally:frozen.OPERATOR=old


def validate_controls(root,out,report):
    arrays={}
    for record in report['records']:
        arrays.setdefault(record['dataset'],{})[record['axis']]=json.loads((out/record['piece']['file']).read_bytes())['values']
    controls=[]
    for file in CONTROLS:
        case=json.loads((root/file).read_bytes());lat=case['native_latitude_index'];it=case['source_time_index'];stamp=datetime.strptime(case['snapshot_time_utc'],'%Y-%m-%dT%H:%M:%SZ');hours=(stamp-datetime(2000,1,1)).total_seconds()/3600
        for product in frozen.SOURCES:
            a=arrays[product];context=report['time_context'][product]
            if context!={'units':'hours since 2000-01-01 00:00:00','calendar':'gregorian'} or a['depth']!=case['depth_levels_m'] or a['lat'][lat]!=case['native_latitude_degrees_north'] or a['time'][it]!=hours or any(a['lon'][c['global_longitude_index']]!=c['native_source_longitude_degrees_east'] for c in case['columns']):raise ValueError('Exact retained original native coordinates/depths/date-index controls must match')
        controls.append({'file':file,'status':'EXACT_RETAINED_COORDINATE_CONTROL_MATCH'})
    return controls


def worker(root=ROOT,out=OUT,opener=None):
    out=Path(out);out.mkdir(exist_ok=True);http=HTTP(out,opener)
    with configured():report=frozen.worker(root=root,out=out,factory=lambda url:Dataset(url,http))
    try:report['retained_coordinate_controls']=validate_controls(root,out,report)
    except Exception as error:
        report.update(status='HTTP_COORDINATE_CONTROLS_FAILED',failure_stage={'operation':'RETAINED_COORDINATE_CONTROLS'},error_type=type(error).__name__);frozen.write_json(out/'worker-report.json',report);raise
    report['coordinate_transport_backend']='bounded_HTTP_ASCII_Float64';report['retained_controls_establish_current_depth']=False;frozen.write_json(out/'worker-report.json',report)
    if len(http.report['requests'])!=12 or any(row['status']!='HTTP_RESPONSE_RETAINED' for row in http.report['requests']):raise ValueError('Exactly12successful fixed coordinate/metadata requests required')
    return report


def probe(root=ROOT,out=OUT,runner=subprocess.run):
    def wrapper_runner(command,**kwargs):
        command=list(command);command[1]=str(Path(__file__).resolve());return runner(command,**kwargs)
    with configured():frozen.probe(root=root,out=out,runner=wrapper_runner)


if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--worker':worker(out=Path(sys.argv[2]))
    elif len(sys.argv)==1:probe()
    else:raise ValueError('Only bounded HTTP coordinate parent/worker calls supported')
