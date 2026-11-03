"""Bounded exact HTTP single/multipart byte ranges with shared request custody."""
import hashlib,re,urllib.request


def validate_plan(ranges,maximum_ranges=128):
    if not ranges or len(ranges)>maximum_ranges:raise ValueError('Bounded nonempty range list required')
    ordered=sorted(ranges)
    for i,row in enumerate(ordered):
        if len(row)!=2 or any(type(x) is not int for x in row) or row[0]<0 or row[1]<=0:raise ValueError('Nonnegative start and positive byte length required')
        if i and ordered[i-1][0]+ordered[i-1][1]>row[0]:raise ValueError('Duplicate or overlapping ranges forbidden')
    return ordered


def parse_multipart(body,content_type,requested,total_length):
    requested=set(validate_plan(requested));m=re.fullmatch(r'multipart/byteranges\s*;\s*boundary=(?:"([A-Za-z0-9._-]{1,70})"|([A-Za-z0-9._-]{1,70}))',content_type,re.I)
    if not m:raise ValueError('Strict multipart byte-range boundary required')
    delimiter=b'--'+(m.group(1) or m.group(2)).encode();position=0;result={}
    if body.startswith(b'\r\n'):position=2
    while True:
        if body[position:position+len(delimiter)]!=delimiter:raise ValueError('Missing exact multipart delimiter')
        position+=len(delimiter)
        if body[position:position+2]==b'--':
            position+=2
            if body[position:] not in [b'',b'\r\n'] or set(result)!=requested:raise ValueError('Missing/extra ranges or trailing body')
            return result
        if body[position:position+2]!=b'\r\n':raise ValueError('Malformed multipart line ending')
        position+=2;end=body.find(b'\r\n\r\n',position,position+8192)
        if end<0:raise ValueError('Bounded part headers required')
        headers={}
        for line in body[position:end].split(b'\r\n'):
            name,sep,value=line.partition(b':');name=name.decode('ascii').lower()
            if not sep or name in headers:raise ValueError('Malformed/duplicate part header')
            headers[name]=value.strip().decode('ascii')
        cr=re.fullmatch(r'bytes (\d+)-(\d+)/(\d+)',headers.get('content-range',''))
        if not cr:raise ValueError('Exact part Content-Range required')
        start,last,total=map(int,cr.groups());key=(start,last-start+1)
        if total!=total_length or key not in requested or key in result or headers.get('content-transfer-encoding') not in [None,'binary']:raise ValueError('Unrequested,coalesced,duplicate or changed source range')
        position=end+4;data=body[position:position+key[1]]
        if len(data)!=key[1]:raise ValueError('Truncated range payload')
        result[key]=data;position+=key[1]
        if body[position:position+2]!=b'\r\n':raise ValueError('Exact part length/delimiter mismatch')
        position+=2


class BoundedHttpRanges:
    def __init__(self,url,length,modified,allowed_ranges,maximum_requests,maximum_requested_bytes,maximum_response_body_bytes,maximum_total_response_body_bytes):
        if not url.startswith('https://data.hycom.org/datasets/GLBv0.08/expt_53.X/meanstd/netcdf/') or not url.endswith('_uv3z.nc'):raise ValueError('Declared provider velocity mean object required')
        self.url=url;self.length=length;self.modified=modified;self.allowed=set(validate_plan(allowed_ranges,1000000));self.maximum_requests=maximum_requests;self.maximum_requested_bytes=maximum_requested_bytes;self.maximum_response_body_bytes=maximum_response_body_bytes;self.maximum_total_response_body_bytes=maximum_total_response_body_bytes
        if not (0<maximum_requests<=1000 and 0<maximum_requested_bytes<=1000000 and 0<maximum_response_body_bytes<=1000000 and maximum_response_body_bytes<=maximum_total_response_body_bytes<=7000000):raise ValueError('Fixed transport ceilings exceeded')
        if any(start+n>length for start,n in self.allowed) or sum(n for _,n in self.allowed)>maximum_requested_bytes:raise ValueError('All declared ranges must fit original object/budget')
        self.attempted=set();self.completed=set();self.requested_bytes=0;self.body_bytes=0;self.rows=[]
    def read(self,ranges):
        plan=validate_plan(ranges);keys=set(plan);future=self.allowed-self.attempted-keys
        future_calls=(len(future)+127)//128
        if not keys<=self.allowed or keys&self.attempted or len(self.rows)+1+future_calls>self.maximum_requests or self.requested_bytes+sum(n for _,n in plan)+sum(n for _,n in future)>self.maximum_requested_bytes or self.body_bytes+self.maximum_response_body_bytes*(1+future_calls)>self.maximum_total_response_body_bytes:raise ValueError('Unplanned/replayed request or shared future budget exceeded')
        self.attempted.update(keys);self.requested_bytes+=sum(n for _,n in plan);row={'ranges':[list(x) for x in plan],'status':'reserved'};self.rows.append(row)
        req=urllib.request.Request(self.url,headers={'Range':'bytes='+','.join(str(s)+'-'+str(s+n-1) for s,n in plan),'If-Range':self.modified,'Accept-Encoding':'identity','User-Agent':'OSW-bounded-ranges-cloud-v1'})
        try:
            with urllib.request.urlopen(req,timeout=25) as response:
                if response.status!=206 or response.url!=self.url or response.headers.get('Last-Modified')!=self.modified or response.headers.get('Content-Encoding') not in [None,'identity']:raise ValueError('Refuse full body,changed source or encoding before read')
                size=response.headers.get('Content-Length')
                if size is None or not size.isdigit() or int(size)>self.maximum_response_body_bytes:raise ValueError('Bounded declared response length required')
                if len(plan)==1:
                    start,n=plan[0]
                    if response.headers.get('Content-Range')!='bytes '+str(start)+'-'+str(start+n-1)+'/'+str(self.length) or int(size)!=n:raise ValueError('Refuse unexpected single range before read')
                elif not response.headers.get('Content-Type','').lower().startswith('multipart/byteranges'):raise ValueError('Refuse merged/full multipart response before read')
                body=response.read(int(size)+1);self.body_bytes+=len(body);row.update(response_body_bytes=len(body),response_body_sha256=hashlib.sha256(body).hexdigest(),content_type=response.headers.get('Content-Type'),content_range=response.headers.get('Content-Range'))
                if len(body)!=int(size) or self.body_bytes>self.maximum_total_response_body_bytes:raise ValueError('Exact declared response body/budget required')
                parts={plan[0]:body} if len(plan)==1 else parse_multipart(body,response.headers['Content-Type'],plan,self.length)
            self.completed.update(keys);row.update(status='success',parts=[{'start':s,'length':n,'sha256':hashlib.sha256(parts[s,n]).hexdigest()} for s,n in plan]);return parts
        except Exception:
            row['status']='failed_no_replay';raise
    def receipt(self):
        return {'schema':'osw.bounded-hycom-http-ranges.v1','source_url':self.url,'source_bytes':self.length,'source_last_modified':self.modified,
                'maximum_requests':self.maximum_requests,'maximum_requested_bytes':self.maximum_requested_bytes,'maximum_response_body_bytes':self.maximum_response_body_bytes,'maximum_total_response_body_bytes':self.maximum_total_response_body_bytes,
                'attempted_requested_bytes':self.requested_bytes,'response_body_bytes':self.body_bytes,'allowed_ranges':len(self.allowed),'completed_ranges':len(self.completed),'requests':self.rows,'automatic_retries':0}
