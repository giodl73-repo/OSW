"""Explicitly acquire one original JASADCP cruise; default verifies retained bytes."""
import argparse,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
BASE='https://uhslc.soest.hawaii.edu/sadcp/DATABASE/'
SOURCES={
 'gateway.html':BASE+'00016.html',
 'cruise-metadata.bft':BASE+'00016/00016.bft',
 'format-template.txt':BASE+'sadcp_cdl.txt',
 'hourly-vector-original.nc':BASE+'00016/00016v3.nc',
}
FOLDER=ROOT/'research/source-data/jasadcp-p14n-1993'

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--acquire',action='store_true');args=parser.parse_args()
 receipt=FOLDER/'acquisition.json'
 if args.acquire:
  if receipt.exists() or any((FOLDER/name).exists() for name in SOURCES):raise ValueError('Refusing to replace source originals or receipt')
  outputs=[]
  for name,url in SOURCES.items():
   with urllib.request.urlopen(url,timeout=40) as response:
    data=response.read(50_000_001);final=response.url
   if not data or len(data)>50_000_000:raise ValueError('Empty or oversized response: '+name)
   if name.endswith('.nc') and not data.startswith((b'CDF',b'\x89HDF')):raise ValueError('Not a NetCDF original')
   outputs.append((name,data,{'file':(FOLDER/name).relative_to(ROOT).as_posix(),'source_url':url,'response_url':final,'byte_count':len(data),'sha256':hashlib.sha256(data).hexdigest()}))
  record={'schema':'osw.source-acquisition.v1','source':'JASADCP SAC_ID00016 TT9306 P14N','acquired_at_utc':datetime.now(timezone.utc).isoformat(),'producer_file':Path(__file__).relative_to(ROOT).as_posix(),'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'source_files':[row for _,_,row in outputs],'access_note':'Public institutional archive; preserve original attribution and inspect provider metadata. No broader copyright license inferred. Acquisition does not admit a current width.'}
  FOLDER.mkdir(parents=True,exist_ok=True)
  for name,data,_ in outputs:
   with (FOLDER/name).open('xb') as output:output.write(data)
  with receipt.open('x',encoding='utf8',newline='\n') as output:json.dump(record,output,indent=2);output.write('\n')
 record=json.loads(receipt.read_bytes())
 if hashlib.sha256(Path(__file__).read_bytes()).hexdigest()!=record['producer_sha256']:raise ValueError('Changed acquisition producer')
 for row in record['source_files']:
  data=(ROOT/row['file']).read_bytes()
  if len(data)!=row['byte_count'] or hashlib.sha256(data).hexdigest()!=row['sha256']:raise ValueError('Changed original '+row['file'])
 print(json.dumps({'status':'PASS','source':record['source'],'files':len(record['source_files']),'bytes':sum(r['byte_count'] for r in record['source_files'])}))

if __name__=='__main__':main()
