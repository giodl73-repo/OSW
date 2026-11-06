"""Cloud-only inventory of retained ACT manifest bytes, with zero provider calls."""
import hashlib,json,re,socket,urllib.request,xml.etree.ElementTree as ET
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parents[1]
OP='research/act2010-retained-manifest-operator-v1.json'
SOURCE='research/source-data/act2010-version-metadata-v2/phase2-provider-xml.raw'
BASE='/nodc/archive/arc0085/0140939/1.1/'


def inventory(raw):
    if len(raw)>128000 or b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():raise ValueError('Bounded retained manifest without entities required')
    tree=ET.fromstring(raw)
    if tree.tag!='accession' or tree.attrib!={'manifest_version':'2'}:raise ValueError('Original NCEI accession manifest schema required')
    head=tree.find('head')
    if head is None or head.findtext('id')!='0140939' or head.findtext('version')!='1.1' or head.findtext('directory')!=BASE:raise ValueError('Exact observed accession/version/base required')
    entries=tree.findall('body/files/file')
    if not 1<=len(entries)<=2000:raise ValueError('Global metadata entry bound required')
    declared_count=int(head.findtext('file_count'));declared_bytes=int(head.findtext('byte_count'))
    rows=[];seen=set()
    for i,node in enumerate(entries):
        path=node.findtext('path','');pure=PurePosixPath(path)
        if not path or pure.is_absolute() or '\\' in path or any(p in ['', '.', '..'] for p in path.split('/')) or any(not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_. -]{0,180}',p) for p in path.split('/')):raise ValueError('Safe actual relative archive path required')
        if path in seen:raise ValueError('Duplicate manifest path rejected')
        seen.add(path);category=node.findtext('type_category');kind=node.findtext('type');size=int(node.findtext('size'))
        if category not in ['regular','irregular'] or size<0 or size>100000000:raise ValueError('Supported bounded metadata file kind/size required')
        digests=[n.text for n in node.findall('digest') if n.attrib.get('algorithm')=='sha256']
        if len(digests)!=1 or not re.fullmatch('[0-9a-f]{64}',digests[0] or ''):raise ValueError('One provider-asserted SHA256 per observed entry required')
        regular=category=='regular'
        rows.append({'manifest_path':path,'ftp_url':'ftp://ftp-oceans.ncei.noaa.gov'+BASE+path,
          'provider_entry_kind':kind,'provider_type_category':category,'provider_size_bytes':size,'provider_asserted_sha256':digests[0],
          'source_manifest_xpath':'/accession/body/files/file['+str(i+1)+']',
          'regular_file':regular,'candidate_netCDF':regular and path.lower().endswith('.nc'),
          'documentation_candidate':regular and (path.startswith('about/') or bool(re.search(r'readme|read_me|license|licence',path,re.I))),
          'fits_2p4MB_single_response_before_other_case_output':size<2400000,
          'native_file_downloaded':False,'native_file_hash_independently_verified':False,
          'native_schema_or_QC_verified':False,'field_acquisition_eligible':False})
    regular=[r for r in rows if r['regular_file']]
    count_scope='all_entries' if declared_count==len(rows) else 'regular_files' if declared_count==len(regular) else 'unresolved'
    all_bytes=sum(r['provider_size_bytes'] for r in rows);regular_bytes=sum(r['provider_size_bytes'] for r in regular)
    byte_scope='all_entries' if declared_bytes==all_bytes else 'regular_files' if declared_bytes==regular_bytes else 'unresolved'
    return {'schema':'osw.act2010-retained-manifest-inventory.v1','source_accession':'0140939','source_version':'1.1',
      'status':'RETAINED_MANIFEST_INDEXED_NO_NATIVE_FIELDS_OR_REUSE_PERMISSION_INFERRED',
      'manifest_file':SOURCE,'manifest_sha256':hashlib.sha256(raw).hexdigest(),
      'declared_entry_or_file_count':declared_count,'declared_total_bytes':declared_bytes,
      'entry_count_scope_reconciled':count_scope,'byte_count_scope_reconciled':byte_scope,
      'indexed_entry_count':len(rows),'indexed_regular_file_count':len(regular),
      'indexed_regular_file_bytes':regular_bytes,'indexed_all_entry_bytes':all_bytes,
      'candidate_netCDF_count':sum(r['candidate_netCDF'] for r in rows),
      'single_response_size_fit_candidate_count':sum(r['candidate_netCDF'] and r['fits_2p4MB_single_response_before_other_case_output'] for r in rows),
      'entries':rows,'source_XML_is_checksum_manifest_not_rights_document':True,
      'manifest_metadata_is_scientific_depth_evidence':False,'provider_requests':0,'new_native_ocean_values_decoded':0,
      'case_remote_operations_used_unchanged':6,'case_remote_operations_cap_unchanged':18,
      'metadata_stage_remote_operations_used_unchanged':6,'metadata_stage_remote_operations_cap_unchanged':6,
      'case_native_profile_or_scalar_reserves_reset':False,'native_field_acquisition_eligible':False,
      'access_label_conflict_resolved':False,'new_current_depth_references':0,'runtime_changed':False,'full_goal_complete':False}


def no_network(*a,**k):raise RuntimeError('Retained manifest indexing forbids every provider request')


def main():
    urllib.request.urlopen=no_network;urllib.request.build_opener=no_network;socket.create_connection=no_network
    op=json.loads((ROOT/OP).read_bytes())
    for f,h in op['input_sha256'].items():
        if hashlib.sha256((ROOT/f).read_bytes()).hexdigest()!=h:raise ValueError('Pinned retained metadata input changed:'+f)
    result=inventory((ROOT/SOURCE).read_bytes())
    result['input_sha256']=op['input_sha256'];result['operator_sha256']=hashlib.sha256((ROOT/OP).read_bytes()).hexdigest()
    raw=(json.dumps(result,indent=2,allow_nan=False)+'\n').encode()
    if len(raw)>=2400000:raise ValueError('Metadata output cap exceeded')
    out=ROOT/'act2010-retained-manifest-v1';out.mkdir(exist_ok=False);(out/'manifest-index.json').write_bytes(raw)
    print(json.dumps({k:result[k] for k in ['status','indexed_entry_count','indexed_regular_file_count','candidate_netCDF_count','single_response_size_fit_candidate_count','declared_total_bytes','entry_count_scope_reconciled','byte_count_scope_reconciled','provider_requests','native_field_acquisition_eligible']}),flush=True)

if __name__=='__main__':main()
