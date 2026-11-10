"""Cloud-only multipart header probe and contiguous coordinate block custody."""
import base64,hashlib,json,math,struct
from pathlib import Path
from bounded_hycom_http_ranges_v1 import BoundedHttpRanges

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/pacific-neuc-mean-coordinate-access-operator-v1.json'


def coordinate_layout(header):
    if header['format']!='CDF2' or header['record_count']!=1:raise ValueError('Verified single-record CDF2 mean object required')
    variables={v['name']:v for v in header['variables']};names=['depth','lat','lon','time'];parts=[]
    for name in names:
        v=variables[name]
        if v['nc_type']!=6 or v['external_element_bytes']!=8 or v['dimension_names']!=[name] or v['vsize']%8:raise ValueError('Simple one-dimensional double coordinate required')
        parts.append((v['begin'],v['vsize'],name))
    parts.sort();start=parts[0][0];end=start
    for begin,n,name in parts:
        if begin!=end:raise ValueError('Coordinate block must have no gaps or overlap')
        end+=n
    if start!=header['header_bytes'] or end!=min(variables[k]['begin'] for k in ['water_u','water_v']):raise ValueError('Coordinate block must end before velocity bytes')
    return start,end-start,parts


def decode_coordinates(raw,start,parts,dimensions,records):
    sizes={d['name']:d['declared_length'] for d in dimensions};sizes['time']=records;arrays={}
    for begin,n,name in parts:
        if begin<start or begin-start+n>len(raw) or n!=8*sizes[name]:raise ValueError('Exact declared coordinate shape required')
        values=list(struct.unpack('>'+str(sizes[name])+'d',raw[begin-start:begin-start+n]))
        if not all(math.isfinite(v) for v in values):raise ValueError('Finite coordinate values required')
        if name!='time' and any(b<=a for a,b in zip(values,values[1:])):raise ValueError('Strictly increasing native coordinate axis required')
        arrays[name]=values
    return arrays


def main():
    op=json.loads((ROOT/OPERATOR).read_bytes())
    for f,pin in op['input_sha256'].items():
        if hashlib.sha256((ROOT/f).read_bytes()).hexdigest()!=pin:raise ValueError('Coordinate access input changed: '+f)
    header=json.loads((ROOT/op['header_inspection_file']).read_bytes());original=base64.b64decode(header['header_base64'],validate=True)
    if hashlib.sha256(original).hexdigest()!=header['header_sha256'] or len(original)!=header['header_bytes']:raise ValueError('Verified header custody changed')
    start,n,parts=coordinate_layout(header);probe=[tuple(x) for x in op['header_probe_ranges']]
    if [start,n]!=op['expected_coordinate_block'] or any(s+k>len(original) for s,k in probe):raise ValueError('Declared metadata ranges changed')
    reader=BoundedHttpRanges(header['source_object_url'],header['source_content_length'],header['source_last_modified'],probe+[(start,n)],op['maximum_requests'],op['maximum_requested_bytes'],op['maximum_response_body_bytes'],op['maximum_total_response_body_bytes'])
    out=Path('pacific-neuc-mean-coordinate-access-v1');out.mkdir(exist_ok=True)
    try:
        fragments=reader.read(probe)
        for key,value in fragments.items():
            if value!=original[key[0]:key[0]+key[1]]:raise ValueError('Multipart returned bytes differ from verified header')
        raw=reader.read([(start,n)])[start,n];arrays=decode_coordinates(raw,start,parts,header['dimensions'],header['record_count'])
        if len(arrays['depth'])!=40 or arrays['depth'][0]!=0 or arrays['depth'][-1]!=5000:raise ValueError('Expected unchanged40level depth axis')
        result={'schema':'osw.pacific-neuc-mean-coordinate-access.v1','operator_file':OPERATOR,'operator_sha256':hashlib.sha256((ROOT/OPERATOR).read_bytes()).hexdigest(),'input_sha256':op['input_sha256'],
                'header_inspection_file':op['header_inspection_file'],'header_inspection_sha256':hashlib.sha256((ROOT/op['header_inspection_file']).read_bytes()).hexdigest(),
                'source_object_url':header['source_object_url'],'source_content_length':header['source_content_length'],'source_last_modified':header['source_last_modified'],
                'header_probe_fragments':[{'start':s,'length':k,'raw_base64':base64.b64encode(fragments[s,k]).decode()} for s,k in probe],
                'coordinate_block_start':start,'coordinate_block_bytes':n,'coordinate_block_sha256':hashlib.sha256(raw).hexdigest(),'coordinate_block_base64':base64.b64encode(raw).decode(),
                'coordinate_variable_spans':[{'name':name,'begin':begin,'bytes':length} for begin,length,name in parts],'coordinate_arrays':arrays,
                'time_coordinate_is_averaging_interval':False,'coordinate_values_read':True,'ocean_velocity_values_read':False,'regional_velocity_subset_acquired':False,
                'new_depth_measurements':0,'current_identity_validated':False,'averaging_semantics_validated':False,'runtime_changed':False,'full_goal_complete':False}
        (out/'coordinates.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
        print(json.dumps({'multipart_header_probe_passed':True,'coordinate_lengths':{k:len(v) for k,v in arrays.items()},'coordinate_block_bytes':n,'ocean_velocity_values_read':False}))
    finally:
        (out/'transport-ledger.json').write_text(json.dumps(reader.receipt(),indent=2,allow_nan=False)+'\n')


if __name__=='__main__':main()
