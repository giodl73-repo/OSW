"""Coarse SVG map contact screen; never an ocean/physical-volume validation."""
import copy,hashlib,json,math,os,re,signal,socket,time,xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery
ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/north-brazil-reference-solids-v1.json'
LAND='figures/osw-province-atlas-interactive.svg'
OP='research/north-brazil-reference-land-operator-v1.json'
EPS=1e-9
NUMBER=r'-?\d+(?:\.\d+)?'
encode=lambda v:(json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
sha=lambda raw:hashlib.sha256(raw).hexdigest()

class VectorBudget:
    def __init__(self,query):self.query=query;self.nodes=0
    def reserve(self,numeric=0,nodes=0,raw=None):
        q=self.query;size=0 if raw is None else len(raw)
        if self.nodes+nodes>6000 or size>2500000 or q.ledger['reserved_numeric_tokens']+numeric>q.numeric_cap or q.ledger['unique_json_bytes']+size>q.byte_cap:raise ValueError('Prospective vector nodes/numeric/packet/byte cap before interpretation')
        self.nodes+=nodes;q.ledger['reserved_numeric_tokens']+=numeric;q.ledger['new_numeric_tokens']+=numeric
        q.ledger['unique_json_bytes']+=size;q.ledger['new_json_bytes']+=size
        q.ledger['geometry_nodes_reserved']=self.nodes
        if raw is not None:q.ledger['packets'].append({'sha256':sha(raw),'bytes':size,'reserved_numeric_tokens':0,'format':'derived_svg','status':'reserved_before_xml_string_parse'})
        if numeric:q.ledger['svg_coordinate_numeric_conversions_reserved']=q.ledger.get('svg_coordinate_numeric_conversions_reserved',0)+numeric
        q.save(q.ledger)

def read_mask(raw,budget):
    budget.reserve(raw=raw)
    root=ET.fromstring(raw);found=[]
    def walk(node,transformed=False):
        transformed=transformed or bool(node.get('transform'))
        if node.get('class')=='land-context':
            if transformed or node.tag.split('}')[-1]!='path' or node.get('fill-rule')!='evenodd':raise ValueError('Exact untransformed even-odd land path required')
            found.append(node.get('d'))
        for child in node:walk(child,transformed)
    walk(root)
    if len(found)!=1 or not found[0]:raise ValueError('One complete existing land-context path required')
    metadata=' '.join(n.text or '' for n in root.iter() if n.tag.split('}')[-1]=='metadata')
    if 'Natural Earth 1:110m land' not in metadata or '9e0729ee253ca7d7a5c4ae9395fb1902264c5377c52e224d13dd85010e2835d9' not in metadata:raise ValueError('Exact coarse source identity required')
    path=found[0]
    if re.sub(r'[MLZ]|'+NUMBER+r'|[\s,]+','',path):raise ValueError('No curve/relative/unsupported path commands')
    tokens=re.findall(r'[MLZ]|'+NUMBER,path);numbers=[t for t in tokens if t not in ['M','L','Z']]
    if len(numbers)%2:raise ValueError('Complete coordinate pairs')
    budget.reserve(numeric=len(numbers),nodes=len(numbers)//2)
    rings=[];current=None;i=0
    while i<len(tokens):
        command=tokens[i];i+=1
        if command=='Z':
            if current is None or len(current)<3:raise ValueError('Closed rings with at least three vertices')
            rings.append(current);current=None;continue
        if command not in ['M','L'] or i+1>=len(tokens) or any(tokens[j] in ['M','L','Z'] for j in [i,i+1]):raise ValueError('Exact M/L coordinate pair grammar')
        xy=[float(tokens[i]),float(tokens[i+1])];i+=2
        if not all(math.isfinite(v) for v in xy):raise ValueError('Finite display coordinates')
        if command=='M':
            if current is not None:raise ValueError('Do not implicitly close or repair a ring')
            current=[]
        elif current is None:raise ValueError('L requires open ring')
        current.append(xy)
    if current is not None or not rings:raise ValueError('All source land rings explicitly closed')
    return rings

def segment_box(a,b,rect):
    low,high=0.,1.
    for dim,(minimum,maximum) in enumerate([(rect[0],rect[2]),(rect[1],rect[3])]):
        delta=b[dim]-a[dim]
        if abs(delta)<=EPS:
            if a[dim]<minimum-EPS or a[dim]>maximum+EPS:return False
        else:
            start,end=(minimum-a[dim])/delta,(maximum-a[dim])/delta
            low=max(low,min(start,end));high=min(high,max(start,end))
            if low>high+EPS:return False
    return True

def filled(point,rings):
    inside=False;x,y=point
    for ring in rings:
        for a,b in zip(ring,ring[1:]+ring[:1]):
            if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
    return inside

def contact(rect,rings):
    xmin,ymin,xmax,ymax=rect
    if not all(math.isfinite(v) for v in rect) or not xmin<xmax or not ymin<ymax:raise ValueError('Nonempty finite rectangle')
    for ring in rings:
        if max(p[0] for p in ring)<xmin-EPS or min(p[0] for p in ring)>xmax+EPS or max(p[1] for p in ring)<ymin-EPS or min(p[1] for p in ring)>ymax+EPS:continue
        if any(segment_box(a,b,rect) for a,b in zip(ring,ring[1:]+ring[:1])):return 'coarse_land_boundary_meets_reference_cell'
    if any(filled(p,rings) for p in [[xmin,ymin],[xmin,ymax],[xmax,ymin],[xmax,ymax]]):return 'reference_cell_corner_in_coarse_land_fill'
    return 'no_contact_detected_in_coarse_display_mask'

def rectangle(lons,lats,budget):
    if len(lons)!=2 or len(lats)!=2 or not all(type(v) in (int,float) and math.isfinite(v) for v in [*lons,*lats]) or not -180<=lons[0]<lons[1]<=180 or not -90<=lats[0]<lats[1]<=90:raise ValueError('Original geographic cell bounds')
    budget.reserve(nodes=4)
    return [60+(lons[0]+180)/360*1480,90+(90-lats[1])/180*740,60+(lons[1]+180)/360*1480,90+(90-lats[0])/180*740]

def build(source,rings,budget):
    if source['schema']!='osw.north-brazil-reference-solids.v1' or source['entity_id']!='current:north-brazil' or source['physical_volume_eligible'] is not False or source['whole_current_volume_km3'] is not None or source['original_physical_volume_ineligibility_preserved'] is not True:raise ValueError('Exact unpromoted hypothetical source only')
    rows=[]
    for pi,pair in enumerate(source['section_pairs']):
        for ci,cell in enumerate(pair['cells']):
            box=rectangle(cell['longitude_cell_degrees_east'],pair['actual_native_latitude_degrees_north'],budget);status=contact(box,rings)
            rows.append({'source_section_pair_index':pi,'source_cell_index':ci,'snapshot_time_utc':pair['snapshot_time_utc'],
                'south_section_id':pair['south_section_id'],'north_section_id':pair['north_section_id'],
                'longitude_cell_degrees_east':copy.deepcopy(cell['longitude_cell_degrees_east']),
                'latitude_cell_degrees_north':copy.deepcopy(pair['actual_native_latitude_degrees_north']),
                'coarse_mask_contact_status':status,'withheld_by_coarse_land_screen':status!='no_contact_detected_in_coarse_display_mask',
                'original_reference_solid_volume_km3':cell['reference_solid_volume_km3'],
                'original_sampling_bracket_reference_volume_bounds_km3':copy.deepcopy(cell['sampling_bracket_reference_volume_bounds_km3']),
                'land_free_ocean_support_established':False,'physical_current_volume_km3':None})
    if len(rows)!=source['counts']['accepted_reference_solids']:raise ValueError('Complete source solid accounting')
    dates=[]
    for original in source['by_date']:
        own=[r for r in rows if r['snapshot_time_utc']==original['snapshot_time_utc']];clear=[r for r in own if not r['withheld_by_coarse_land_screen']]
        if len(own)!=original['accepted_reference_solid_count']:raise ValueError('Exact source date population')
        dates.append({'snapshot_time_utc':original['snapshot_time_utc'],'original_date_summary':copy.deepcopy(original),
            'coarse_contact_count':sum(r['withheld_by_coarse_land_screen'] for r in own),'no_coarse_contact_count':len(clear),
            'retained_after_coarse_screen_partial_reference_volume_km3':sum(r['original_reference_solid_volume_km3'] for r in clear) if clear else None,
            'sampling_bracket_retained_reference_volume_bounds_km3':[sum(r['original_sampling_bracket_reference_volume_bounds_km3'][k] for r in clear) for k in [0,1]] if clear else None,
            'physical_or_whole_current_volume_km3':None,'land_free_ocean_support_established':False})
    return {'schema':'osw.north-brazil-reference-land-screen.v1','source_reference_solids':SOURCE,'source_coarse_display_mask':LAND,
        'counts':{'source_reference_solids':len(rows),'coarse_land_contact':sum(r['withheld_by_coarse_land_screen'] for r in rows),'no_coarse_land_contact':sum(not r['withheld_by_coarse_land_screen'] for r in rows)},
        'by_date':dates,'cells':rows,'mask_interpretation':'Natural Earth1:110m coarse land rendered into the existing OSW SVG,equirectangular1600x1050frame,left60/top90/1480x740map,roundedto0.1displayunit,even-odd fill. Boundary touch counts as contact; no geometric repair,curve approximation or fine shoreline claim.',
        'interpretation':'Coarse display-mask diagnostic only. Apparent contacts are withheld from this screened reference sum,not deleted from the frozen source. No contact at this generalized rounded mask does not establish land-free ocean support,interior velocity,branch membership,continuous geometry,physical uncertainty or actual current volume. Different date support masks remain incomparable as seasonal volume changes. No physical/global/whole-route admission.',
        'physical_volume_eligible':False,'land_free_ocean_support_established':False,'new_observations':0,'runtime_changed':False,'full_goal_complete':False}

def main():
    start=float(os.environ['OSW_NBC_REFERENCE_LAND_START'])
    def stop(*a):raise TimeoutError('Shared60second test/producer deadline')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stop)
    if not 0<=time.monotonic()-start<30:raise ValueError('Shared test/producer clock')
    signal.alarm(max(1,int(60-(time.monotonic()-start))));socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline admitted reference and SVG only'))
    out=ROOT/'north-brazil-reference-land-v1';out.mkdir(exist_ok=False)
    def save(value):
        tmp=out/'query-ledger.tmp';tmp.write_bytes(encode(value));os.replace(tmp,out/'query-ledger.json')
    query=DescriptorQuery(save,prior_numeric=0,prior_bytes=0);reader=query.reader(lambda p:(ROOT/p).read_bytes());budget=VectorBudget(query)
    try:
        with query.decoding():
            op=json.loads(reader(OP))
            for path,pin in op['input_sha256'].items():
                if sha((ROOT/path).read_bytes())!=pin:raise ValueError('Frozen input changed:'+path)
            source=json.loads(reader(SOURCE));before=copy.deepcopy(source);mask=(ROOT/LAND).read_bytes();rings=read_mask(mask,budget)
            report=build(source,rings,budget)
            if source!=before or report['counts']['source_reference_solids']!=145:raise ValueError('All145sourcecells retained without mutation')
            report.update(source_reference_solids_sha256=sha(reader(SOURCE)),source_coarse_display_mask_sha256=sha(mask))
            raw=encode(report)
            if json.loads(raw)!=report or encode(json.loads(raw))!=raw:raise ValueError('Full actual guarded scientific JSON roundtrip')
        total=len(raw)+(out/'query-ledger.json').stat().st_size
        if total>2400000:raise ValueError('Whole artifact cap')
        (out/'land-screen.json').write_bytes(raw)
        print(json.dumps({'counts':report['counts'],'by_date':report['by_date'],'geometry_nodes_reserved':budget.nodes,'query_numeric_tokens':query.ledger['reserved_numeric_tokens'],'query_bytes_including_svg':query.ledger['unique_json_bytes'],'whole_output_bytes':total,'cumulative_active_seconds':time.monotonic()-start,'physical_volume_eligible':False,'full_goal_complete':False}))
    finally:signal.alarm(0)

if __name__=='__main__':main()
