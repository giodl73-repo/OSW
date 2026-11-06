"""Cloud-only, exact-range NetCDF classic header inspection; no variable data."""
import base64,hashlib,json,math,struct,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/pacific-neuc-mean-header-inspection-operator-v1.json'
TYPES={1:('b',1),2:('c',1),3:('h',2),4:('i',4),5:('f',4),6:('d',8)}


class HeaderReader:
    def __init__(self,fetch,maximum_bytes=200000):
        self.fetch=fetch;self.maximum_bytes=maximum_bytes;self.position=0;self.raw=bytearray();self.first_data=None
    def take(self,n):
        if type(n) is not int or n<0 or self.position+n>self.maximum_bytes or (self.first_data is not None and self.position+n>self.first_data):raise ValueError('Header byte bound or first data offset exceeded')
        if not n:return b''
        raw=self.fetch(self.position,n)
        if len(raw)!=n:raise ValueError('Exact header bytes required')
        self.raw.extend(raw);self.position+=n;return raw
    def uint(self):return struct.unpack('>I',self.take(4))[0]
    def name(self):
        n=self.uint()
        if not 1<=n<=1024:raise ValueError('Bounded nonempty metadata name required')
        raw=self.take((n+3)//4*4)
        if any(raw[n:]):raise ValueError('Nonzero header padding')
        name=raw[:n].decode('utf8')
        if '/' in name or '\x00' in name:raise ValueError('Invalid metadata name')
        return name
    def count(self,tag,maximum):
        actual,n=struct.unpack('>II',self.take(8))
        if (actual,n)==(0,0):return 0
        if actual!=tag or n>maximum:raise ValueError('Unexpected or excessive header list')
        return n
    def attributes(self):
        result={}
        for _ in range(self.count(12,128)):
            name=self.name();kind,n=struct.unpack('>II',self.take(8))
            if name in result or kind not in TYPES or n>50000:raise ValueError('Duplicate/unknown/oversized attribute')
            code,size=TYPES[kind];length=n*size;raw=self.take((length+3)//4*4)
            if any(raw[length:]):raise ValueError('Nonzero attribute padding')
            value=raw[:length].decode('utf8',errors='replace') if kind==2 else [x if math.isfinite(x) else str(x) for x in struct.unpack('>'+str(n)+code,raw[:length])]
            result[name]={'nc_type':kind,'values':value,'raw_value_base64':base64.b64encode(raw[:length]).decode()}
        return result


def inspect(fetch,maximum_bytes=200000):
    r=HeaderReader(fetch,maximum_bytes);magic=r.take(4)
    if magic not in [b'CDF\x01',b'CDF\x02']:raise ValueError('Only classic CDF1/CDF2 header grammar supported')
    records=r.uint()
    if records==0xffffffff:raise ValueError('Streaming record count unsupported')
    dimensions=[]
    for _ in range(r.count(10,32)):
        name=r.name();length=r.uint()
        if name in [d['name'] for d in dimensions]:raise ValueError('Duplicate dimension')
        dimensions.append({'name':name,'declared_length':length})
    if sum(d['declared_length']==0 for d in dimensions)>1:raise ValueError('Multiple record dimensions unsupported')
    attributes=r.attributes();variables=[]
    for _ in range(r.count(11,128)):
        name=r.name();rank=r.uint()
        if rank>8 or name in [v['name'] for v in variables]:raise ValueError('Excessive rank or duplicate variable')
        ids=list(struct.unpack('>'+str(rank)+'I',r.take(4*rank)))
        if any(i>=len(dimensions) for i in ids) or any(dimensions[i]['declared_length']==0 for i in ids[1:]):raise ValueError('Invalid dimension IDs/record position')
        attrs=r.attributes();kind,vsize=struct.unpack('>II',r.take(8));begin=struct.unpack('>I' if magic[-1]==1 else '>Q',r.take(4 if magic[-1]==1 else 8))[0]
        if kind not in TYPES or begin>=2**63 or begin%4 or begin<r.position:raise ValueError('Invalid variable type/data offset')
        r.first_data=begin if r.first_data is None else min(r.first_data,begin)
        variables.append({'name':name,'dimension_ids':ids,'dimension_names':[dimensions[i]['name'] for i in ids],
                          'is_record_variable':bool(ids and dimensions[ids[0]]['declared_length']==0),'nc_type':kind,
                          'external_element_bytes':TYPES[kind][1],'vsize':vsize,'begin':begin,'attributes':attrs})
    if r.first_data is not None and r.position>r.first_data:raise ValueError('Header overlaps variable data')
    return {'format':'CDF'+str(magic[-1]),'record_count':records,'dimensions':dimensions,'global_attributes':attributes,'variables':variables,
            'header_bytes':r.position,'header_sha256':hashlib.sha256(r.raw).hexdigest(),'header_base64':base64.b64encode(r.raw).decode(),
            'variable_data_read':False,'axis_values_read':False,'ocean_velocity_values_read':False}


class HttpHeaderRanges:
    def __init__(self,url,maximum_requests=1024,maximum_bytes=200000):
        if not url.startswith('https://data.hycom.org/datasets/GLBv0.08/expt_53.X/meanstd/netcdf/') or not url.endswith('_uv3z.nc'):raise ValueError('Declared provider mean object required')
        self.url=url;self.maximum_requests=maximum_requests;self.maximum_bytes=maximum_bytes;self.rows=[];self.total=0;self.end=0
        with urllib.request.urlopen(urllib.request.Request(url,method='HEAD',headers={'User-Agent':'OSW-header-only-cloud-inspection'}),timeout=25) as response:
            if response.status!=200 or response.url!=url or response.headers.get('Accept-Ranges')!='bytes':raise ValueError('Stable ranged provider object required')
            self.length=int(response.headers['Content-Length']);self.modified=response.headers.get('Last-Modified')
            if not self.modified:raise ValueError('Last-Modified identity required')
    def read(self,start,n):
        if type(start) is not int or type(n) is not int or n<=0 or start!=self.end or start+n>self.length or self.total+n>self.maximum_bytes or len(self.rows)>=self.maximum_requests:raise ValueError('Sequential header request budget exceeded')
        expected='bytes '+str(start)+'-'+str(start+n-1)+'/'+str(self.length)
        request=urllib.request.Request(self.url,headers={'User-Agent':'OSW-header-only-cloud-inspection','Range':'bytes='+str(start)+'-'+str(start+n-1),'If-Range':self.modified,'Accept-Encoding':'identity'})
        with urllib.request.urlopen(request,timeout=25) as response:
            if response.status!=206 or response.url!=self.url or response.headers.get('Content-Range')!=expected or response.headers.get('Content-Length')!=str(n) or response.headers.get('Last-Modified')!=self.modified or response.headers.get('Content-Encoding') not in [None,'identity']:raise ValueError('Refuse full body,changed object,encoding or mismatched byte range')
            raw=response.read(n+1)
            if len(raw)!=n:raise ValueError('Exact bounded response required')
        self.rows.append({'start':start,'length':n,'sha256':hashlib.sha256(raw).hexdigest()});self.total+=n;self.end=start+n
        return raw


def main():
    op=json.loads((ROOT/OPERATOR).read_bytes())
    for f,pin in op['input_sha256'].items():
        if hashlib.sha256((ROOT/f).read_bytes()).hexdigest()!=pin:raise ValueError('Inspection input changed: '+f)
    source=HttpHeaderRanges(op['source_object_url'],op['maximum_header_requests'],op['maximum_header_bytes'])
    if source.length!=op['expected_content_length'] or source.modified!=op['expected_last_modified']:raise ValueError('Provider object differs from predeclared HEAD identity')
    result=inspect(source.read,op['maximum_header_bytes'])
    result.update(schema='osw.hycom-precomputed-mean-header-inspection.v1',operator_file=OPERATOR,operator_sha256=hashlib.sha256((ROOT/OPERATOR).read_bytes()).hexdigest(),input_sha256=op['input_sha256'],source_object_url=source.url,source_content_length=source.length,source_last_modified=source.modified,
                  range_requests=source.rows,requested_metadata_bytes=source.total,new_depth_measurements=0,current_identity_validated=False,averaging_semantics_validated=False,regional_field_subset_acquired=False,runtime_changed=False,full_goal_complete=False)
    out=Path('pacific-neuc-mean-header-inspection-v1');out.mkdir(exist_ok=True);(out/'header-inspection.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'format':result['format'],'header_bytes':result['header_bytes'],'requests':len(source.rows),'dimensions':result['dimensions'],'variables':[v['name'] for v in result['variables']],'ocean_velocity_values_read':False}))


if __name__=='__main__':main()
