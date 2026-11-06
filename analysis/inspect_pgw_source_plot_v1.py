"""Cloud-only bounded original-document and vector-plot feasibility inspection."""
import hashlib,json,math,re,urllib.request
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/pgw-source-plot-inspection-operator-v1.json'


def validate_original(raw,op):
    if len(raw)!=op['source_bytes'] or hashlib.sha256(raw).hexdigest()!=op['source_sha256'] or not raw.startswith(b'%PDF-'):raise ValueError('Exact retained original PDF required')


def read_original(op,receipt,opener=urllib.request.urlopen):
    if op['maximum_http_requests']!=1 or not 0<op['source_bytes']<=op['maximum_response_body_bytes']<=18000000 or op['request_timeout_seconds']!=25 or op['source_url']!='https://archimer.ifremer.fr/doc/00000/390/83.pdf':raise ValueError('Predeclared one-request document budget required')
    receipt.update(requests=1,response_body_bytes=0,status='reserved',automatic_retries=0)
    request=urllib.request.Request(op['source_url'],headers={'Accept-Encoding':'identity','User-Agent':'OSW-primary-document-inspection-v1'})
    try:
        with opener(request,timeout=25) as response:
            if response.status!=200 or response.url!=op['source_url'] or response.headers.get('Content-Encoding') not in [None,'identity']:raise ValueError('Exact source URL/status/encoding required')
            declared=response.headers.get('Content-Length')
            if declared is not None and (not declared.isdigit() or int(declared)!=op['source_bytes'] or int(declared)>op['maximum_response_body_bytes']):raise ValueError('Declared original document length changed')
            receipt['declared_content_length']=declared;chunks=[]
            while True:
                chunk=response.read(min(65536,op['maximum_response_body_bytes']-receipt['response_body_bytes']+1))
                if not chunk:break
                chunks.append(chunk);receipt['response_body_bytes']+=len(chunk)
                if receipt['response_body_bytes']>op['maximum_response_body_bytes']:raise ValueError('Bounded document body exceeded')
            raw=b''.join(chunks);validate_original(raw,op);receipt.update(status='success',response_body_sha256=hashlib.sha256(raw).hexdigest());return raw
    except Exception:
        receipt['status']='failed_no_retry';raise


def inspect_page(page,op):
    drawings=page.get_drawings();words=page.get_text('words')
    if len(drawings)>op['maximum_drawings'] or sum(len(p['items']) for p in drawings)>op['maximum_primitives'] or len(words)>op['maximum_words']:raise ValueError('Predeclared page-inspection complexity exceeded')
    summaries=[]
    for i,path in enumerate(drawings):
        rect=list(path['rect'])
        if len(rect)!=4 or any(not math.isfinite(x) for x in rect):raise ValueError('Finite page geometry required')
        summaries.append({'drawing_index':i,'sequence_number':path.get('seqno'),'type':path['type'],'dashes':path.get('dashes'),'width_points':path.get('width'),'stroke_color':path.get('color'),'fill_color':path.get('fill'),'rectangle_points':rect,'primitive_counts':dict(Counter(item[0] for item in path['items']))})
    labels=[]
    for word in words:
        token=word[4].strip("'\"")
        if re.fullmatch(r'[0-9]{1,4}',token) or token in ['Zsmax','Hpgw','Wpgw','Xgeom','Distance','R13']:
            labels.append({'text':token,'rectangle_points':list(word[:4])})
    return {'page_rectangle_points':list(page.rect),'drawing_count':len(drawings),'primitive_count':sum(len(p['items']) for p in drawings),'image_count':len(page.get_images()),'paths':summaries,'selected_axis_and_legend_labels':labels,'curve_vertices_exported':False,'axis_calibration_applied':False,'new_measurement_values_extracted':0}


def screen_neuc(sections):
    rows=[]
    for i,s in enumerate(sections):
        d=s['diagnostic'];primary=next((p for p in d['selected_column_threshold_layers'] if p['threshold_m_s']==.02),None)
        flags={'original_axis_maximum_interior':d['horizontal_interior_selection'],'in_independent_southern_jet_context':d['selected_node_in_independent_latitude_context'],'primary_detached_from_surface':d['primary_layer_detached_from_surface'],'primary_lower_resolved':primary is not None and primary['lower_depth_m'] is not None}
        rows.append({'section_index':i,'selected_column_index':d['selected_column_index'],'eligibility_flags':flags,'regional_axis_proxy_anchor_eligible':all(flags.values())})
    return {'source_section_screen':rows,'adjacent_eligible_anchor_pairs':sum(a['regional_axis_proxy_anchor_eligible'] and b['regional_axis_proxy_anchor_eligible'] for a,b in zip(rows,rows[1:])),'weaker_replacement_selected':False,'new_route_created':False,'new_depths_extracted':0}


def main():
    import pymupdf
    op=json.loads((ROOT/OPERATOR).read_bytes())
    for f,pin in op['input_sha256'].items():
        if hashlib.sha256((ROOT/f).read_bytes()).hexdigest()!=pin:raise ValueError('Frozen inspection input changed: '+f)
    out=Path('pgw-source-plot-inspection-v1');out.mkdir(exist_ok=True);receipt={'schema':'osw.source-document-transport-ledger.v1','source_url':op['source_url'],'maximum_http_requests':1,'maximum_response_body_bytes':op['maximum_response_body_bytes'],'ocean_field_requests':0}
    try:
        raw=read_original(op,receipt)
        with pymupdf.open(stream=raw,filetype='pdf') as document:
            if document.page_count!=op['source_pages']:raise ValueError('Original document page count changed')
            result=inspect_page(document[op['pdf_page_number']-1],op)
        result.update(schema='osw.pgw-source-plot-feasibility.v1',operator_file=OPERATOR,operator_sha256=hashlib.sha256((ROOT/OPERATOR).read_bytes()).hexdigest(),input_sha256=op['input_sha256'],source_url=op['source_url'],source_pdf_sha256=op['source_sha256'],source_pdf_bytes=len(raw),source_pdf_pages=op['source_pages'],pdf_page_number=op['pdf_page_number'],source_figure_number=5,neuc_original_axis_path_screen=screen_neuc([json.loads((ROOT/f).read_bytes()) for f in op['neuc_section_files']]),original_pdf_redistributed=False,source_figure_redistributed=False,reference_inventory_changed=False,model_inventory_changed=False,runtime_changed=False,full_goal_complete=False)
        encoded=(json.dumps(result,indent=2,allow_nan=False)+'\n').encode();
        if len(encoded)>op['maximum_report_bytes']:raise ValueError('Bounded inspection metadata required')
        (out/'inspection.json').write_bytes(encoded)
        print(json.dumps({k:result[k] for k in ['drawing_count','primitive_count','image_count','new_measurement_values_extracted','neuc_original_axis_path_screen']}))
    finally:
        (out/'transport-ledger.json').write_bytes((json.dumps(receipt,indent=2,allow_nan=False)+'\n').encode())


if __name__=='__main__':main()
