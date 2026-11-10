"""Acquire official P14N hydrography explicitly; verify retained originals offline."""
import argparse,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'research/source-data/cchdo-p14n-1993'
PROTOCOL='plans/aleutian-p14n-1993-hydrography-join-preflight-v1.md'
SOURCES={
 'cruise-page.html':'https://cchdo.ucsd.edu/cruise/325023_1',
 'ctd-original.nc':'https://cchdo.ucsd.edu/data/40783/325023_1_ctd.nc',
 'cruise-summary-original.txt':'https://cchdo.ucsd.edu/data/9343/p14nsu.txt',
 'cruise-report-original.txt':'https://cchdo.ucsd.edu/data/11174/p14ndo.txt',
}

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--acquire',action='store_true');args=parser.parse_args();receipt=FOLDER/'acquisition.json'
 if args.acquire:
  if receipt.exists() or any((FOLDER/name).exists() for name in SOURCES):raise ValueError('Refusing to replace source originals or receipt')
  protocol_sha=hashlib.sha256((ROOT/PROTOCOL).read_bytes()).hexdigest();outputs=[]
  for name,url in SOURCES.items():
   with urllib.request.urlopen(url,timeout=40) as response:data=response.read(25_000_001);final=response.url
   if not data or len(data)>25_000_000:raise ValueError('Empty or oversized source')
   if name.endswith('.nc') and not data.startswith((b'CDF',b'\x89HDF')):raise ValueError('Not a NetCDF original')
   outputs.append((name,data,{'file':(FOLDER/name).relative_to(ROOT).as_posix(),'source_url':url,'response_url':final,'byte_count':len(data),'sha256':hashlib.sha256(data).hexdigest()}))
  record={'schema':'osw.source-acquisition.v1','source':'CCHDO325023_1 P14N CTD and original documentation','acquired_at_utc':datetime.now(timezone.utc).isoformat(),'producer_file':Path(__file__).relative_to(ROOT).as_posix(),'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'protocol_file':PROTOCOL,'protocol_sha256':protocol_sha,'source_files':[row for _,_,row in outputs],'scope':'Follow-up to previously viewed July1993 SADCP velocities. Acquisition alone does not establish paired measurement support, current association, physical width or annual variability.'}
  FOLDER.mkdir(parents=True,exist_ok=True)
  for name,data,_ in outputs:
   with (FOLDER/name).open('xb') as output:output.write(data)
  with receipt.open('x',encoding='utf8',newline='\n') as output:json.dump(record,output,indent=2);output.write('\n')
 record=json.loads(receipt.read_bytes())
 for name,pin in [(record['producer_file'],record['producer_sha256']),(record['protocol_file'],record['protocol_sha256'])]:
  if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=pin:raise ValueError('Changed acquisition or declaration')
 for row in record['source_files']:
  data=(ROOT/row['file']).read_bytes()
  if len(data)!=row['byte_count'] or hashlib.sha256(data).hexdigest()!=row['sha256']:raise ValueError('Changed original '+row['file'])
 print(json.dumps({'status':'PASS','source':record['source'],'files':len(record['source_files']),'bytes':sum(row['byte_count'] for row in record['source_files'])}))

if __name__=='__main__':main()
