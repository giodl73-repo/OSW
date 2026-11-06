"""Bounded native-layer catalogue discovery; zero ocean-field reads."""
import hashlib
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPERATOR = 'research/norkyst-native-metadata-operator-v1.json'
CATALOG = 'https://thredds.met.no/thredds/catalog/romshindcast/norkyst_v3/catalog.xml'
PREFIX = '/thredds/catalog/romshindcast/norkyst_v3/'


def localname(tag): return tag.rsplit('}', 1)[-1]


def catalogue(raw, url):
    tree = ET.fromstring(raw); refs = []; datasets = []; services = []
    for node in tree.iter():
        name = localname(node.tag)
        if name == 'catalogRef':
            href = node.attrib.get('{http://www.w3.org/1999/xlink}href')
            if not href: raise ValueError('Observed catalogue reference needs href')
            target = urllib.parse.urljoin(url, href)
            parsed = urllib.parse.urlparse(target)
            if parsed.scheme == 'https' and parsed.hostname == 'thredds.met.no' and parsed.path.startswith(PREFIX):
                refs.append({'name':node.attrib.get('name',''), 'url':target})
        elif name == 'dataset' and node.attrib.get('urlPath'):
            datasets.append({'name':node.attrib.get('name',''), 'urlPath':node.attrib['urlPath'],
                             'serviceName':node.attrib.get('serviceName')})
        elif name == 'service' and node.attrib.get('serviceType','').upper() in ['OPENDAP','DODS']:
            base = urllib.parse.urljoin(url, node.attrib.get('base',''))
            if urllib.parse.urlparse(base).scheme == 'https' and urllib.parse.urlparse(base).hostname == 'thredds.met.no':
                services.append({'name':node.attrib.get('name'), 'base':base})
    return {'references':refs, 'datasets':datasets, 'opendap_services':services}


def priority(ref, level):
    text = (ref['name'] + ' ' + ref['url']).lower()
    if 'zdepth' in text or any(word in text for word in ['daymean','dailymean','monthlymean']): return None
    years = re.findall(r'(?:/|\b)(20\d\d)(?:/|\b)', text)
    if years and '2024' not in years: return None
    month = re.search(r'/2024/(\d{2})/', text)
    if month and month[1] != '03': return None
    if ref['name'].strip().isdigit() and len(ref['name'].strip()) == 2 and ref['name'].strip() != '03': return None
    short = (ref['name'] + ' ' + urllib.parse.urlparse(ref['url']).path.removeprefix(PREFIX)).lower()
    native = next((score for word,score in [('native',100),('sigma',90),('sdepth',80),('s_depth',80),('s-coord',80),('s-level',80),('original',70),('3d',60),('hourly',50),('roms',40)] if word in short), 0)
    if level == 0 and not native: return None
    return native + (20 if '2024' in text else 0) + (10 if month else 0)


def read_metadata(url, receipt, opener):
    p = urllib.parse.urlparse(url)
    if p.scheme != 'https' or p.hostname != 'thredds.met.no' or not (p.path.endswith('catalog.xml') or p.path.endswith('.dds') or p.path.endswith('.das')) or p.query:
        raise ValueError('Only observed THREDDS catalogue/DDS/DAS metadata, never field endpoints')
    receipt.update(url=url, attempts=1, status='reserved', bytes_received=0)
    request = urllib.request.Request(url,headers={'Accept-Encoding':'identity','User-Agent':'OSW-native-layer-metadata-v1'})
    try:
        with opener(request,timeout=25) as response:
            if response.status != 200 or response.url != url or response.headers.get('Content-Encoding') not in [None,'identity']:
                raise ValueError('Exact uncompressed metadata200 response required')
            declared = response.headers.get('Content-Length')
            if declared is not None and (not declared.isdigit() or int(declared)>250000): raise ValueError('Metadata response cap exceeded')
            raw = response.read(250001); receipt['bytes_received'] = len(raw)
            if len(raw)>250000: raise ValueError('Metadata body cap exceeded')
        receipt.update(status='success',sha256=hashlib.sha256(raw).hexdigest())
        return raw
    except Exception as error:
        receipt.update(status='failed_no_retry',error_type=type(error).__name__,error_summary=str(error)[:200])
        raise


def main():
    op = json.loads((ROOT/OPERATOR).read_bytes())
    for file,pin in op['input_sha256'].items():
        if hashlib.sha256((ROOT/file).read_bytes()).hexdigest()!=pin: raise ValueError('Frozen input changed:'+file)
    out = ROOT/'norkyst-native-metadata-v1'; out.mkdir(exist_ok=True)
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*args,**kwargs): return None
    opener = urllib.request.build_opener(NoRedirect()).open
    report = {'schema':'osw.norkyst-native-metadata-discovery.v1','target_date':'2024-03-15',
              'transport_receipts':[], 'catalogues':[], 'candidate_dataset_paths':[],
              'selected_dataset':None,'ocean_field_requests':0,'decoded_ocean_values':0,
              'previous_fixed_z_responses_retrieved_again':False,'runtime_changed':False,'full_goal_complete':False}
    queue = [(CATALOG,0)]; visited = set(); services = set(); failed = False
    try:
        while queue and len(visited)<4:
            url,level = queue.pop(0)
            if url in visited: continue
            visited.add(url); receipt = {}; report['transport_receipts'].append(receipt)
            raw = read_metadata(url,receipt,opener)
            filename = 'catalogue-'+str(len(visited)).zfill(2)+'.xml'; (out/filename).write_bytes(raw)
            receipt['file'] = filename
            parsed = catalogue(raw,url)
            services.update(s['base'] for s in parsed['opendap_services'])
            report['catalogues'].append({'url':url,'file':filename,'references':parsed['references'],
                                          'dataset_count':len(parsed['datasets']), 'dataset_examples':parsed['datasets'][:30]})
            for dataset in parsed['datasets']:
                path = dataset['urlPath']
                if '20240315' in path and 'zdepth' not in path.lower() and path.endswith('.nc'):
                    if dataset not in report['candidate_dataset_paths']: report['candidate_dataset_paths'].append(dataset)
            if report['candidate_dataset_paths']: break
            refs = [(priority(ref,level),ref['url']) for ref in parsed['references']]
            refs = sorted(((-score,target) for score,target in refs if score is not None))
            queue = [(target,level+1) for _,target in refs] + queue
        candidates = report['candidate_dataset_paths']
        if len(candidates)==1 and len(services)==1:
            dataset = candidates[0]; base = next(iter(services))
            url = base.rstrip('/') + '/' + urllib.parse.quote(dataset['urlPath'].lstrip('/'),safe='/')
            report['selected_dataset'] = {**dataset,'opendap_url':url}
            for kind in ['dds','das']:
                receipt = {}; report['transport_receipts'].append(receipt)
                raw = read_metadata(url+'.'+kind,receipt,opener)
                filename='native-20240315.'+kind; (out/filename).write_bytes(raw); receipt['file']=filename
            report['status']='representative_dataset_metadata_captured_pending_vertical_convention_review'
        else:
            report['status']='catalogue_evidence_requires_review_no_dataset_guessed'
    except Exception as error:
        failed=True; report['status']='metadata_transport_or_parse_failed_no_retry'
        report['error_type']=type(error).__name__; report['error_summary']=str(error)[:200]
    finally:
        report['requests_attempted']=len(report['transport_receipts'])
        raw=(json.dumps(report,indent=2)+'\n').encode()
        if len(raw)>500000 or sum(p.stat().st_size for p in out.iterdir())+len(raw)>2400000:
            raise ValueError('Metadata artifact budget exceeded')
        (out/'discovery.json').write_bytes(raw)
        print(json.dumps(report))
    if failed: raise SystemExit(1)


if __name__=='__main__': main()
