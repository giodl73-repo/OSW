"""Publish stable response locations while retaining the original custody receipt."""
import argparse,hashlib,json
from pathlib import Path
from urllib.parse import urlsplit,urlunsplit

ROOT=Path(__file__).resolve().parents[1]
RECEIPT='research/source-data/cchdo-p14n-1993/acquisition.json'

def verify():
 doc=json.loads((ROOT/RECEIPT).read_bytes());publication=doc['receipt_publication']
 if publication['generator_file']!='analysis/prepare_p14n_ctd_receipt.py' or publication['generator_sha256']!=hashlib.sha256(Path(__file__).read_bytes()).hexdigest():raise ValueError('Changed public receipt generator')
 for row in doc['source_files']:
  data=(ROOT/row['file']).read_bytes()
  if len(data)!=row['byte_count'] or hashlib.sha256(data).hexdigest()!=row['sha256']:raise ValueError('Changed original data')
  if urlsplit(row['response_url']).query or urlsplit(row['response_url']).fragment:raise ValueError('Expiring redirect query in public receipt')
 return doc

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--prepare-public',action='store_true');args=parser.parse_args()
 if args.prepare_public:
  raw=(ROOT/RECEIPT).read_bytes();doc=json.loads(raw)
  if 'receipt_publication' in doc:raise ValueError('Refusing to replace an already prepared public receipt')
  backup=ROOT/'.pytest_cache/p14n-ctd-original-acquisition.json';backup.parent.mkdir(exist_ok=True)
  with backup.open('xb') as output:output.write(raw)
  for row in doc['source_files']:
   parts=urlsplit(row['response_url']);row['response_redirect_query_omitted']=bool(parts.query or parts.fragment)
   row['response_url']=urlunsplit((parts.scheme,parts.netloc,parts.path,'',''))
  doc['receipt_publication']={'generator_file':Path(__file__).relative_to(ROOT).as_posix(),'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'original_acquisition_receipt_sha256':hashlib.sha256(raw).hexdigest(),'transformation':'Response URL queries/fragments omitted from public metadata. Original source files, request URLs, acquisition time, byte counts, hashes and acquisition-producer identity unchanged. Raw custody receipt retained locally outside Git.'}
  (ROOT/RECEIPT).write_bytes((json.dumps(doc,indent=2)+'\n').encode())
 doc=verify();print('PASS public receipt; unchanged originals:',len(doc['source_files']))

if __name__=='__main__':main()
