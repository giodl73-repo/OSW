"""Acquire original native JASADCP products explicitly; otherwise verify offline."""
import argparse,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'research/source-data/jasadcp-p14n-1993-native'
PROTOCOL='plans/aleutian-p14n-native-source-preflight-v1.md'
SOURCES={name:'https://uhslc.soest.hawaii.edu/sadcp/DATABASE/00016/'+name for name in ['00016_short.nc','00016_long.nc']}
def sha(data):return hashlib.sha256(data).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--acquire',action='store_true');args=parser.parse_args()
    receipt=FOLDER/'acquisition.json'
    if args.acquire:
        if receipt.exists() or any((FOLDER/name).exists() for name in SOURCES):raise ValueError('Refusing to replace original native data or receipt')
        outputs=[]
        for name,url in SOURCES.items():
            with urllib.request.urlopen(url,timeout=45) as response:
                data=response.read(50_000_001);final=response.url
            if not 0<len(data)<=50_000_000 or not data.startswith((b'CDF',b'\x89HDF')):raise ValueError('Invalid native NetCDF response: '+name)
            outputs.append((name,data,{'file':(FOLDER/name).relative_to(ROOT).as_posix(),'source_url':url,'response_url':final,'byte_count':len(data),'sha256':sha(data)}))
        record={'schema':'osw.source-acquisition.v1','source':'JASADCP SAC_ID00016 TT9306 P14N native products','acquired_at_utc':datetime.now(timezone.utc).isoformat(),
                'producer_file':Path(__file__).relative_to(ROOT).as_posix(),'producer_sha256':sha(Path(__file__).read_bytes()),
                'protocol_file':PROTOCOL,'protocol_sha256':sha((ROOT/PROTOCOL).read_bytes()),'source_files':[row for _,_,row in outputs],
                'field_values_inspected':False,'new_width_record_admitted':False,'access_note':'Public institutional archive. Preserve original attribution; no broader copyright license inferred. Original hourly products remain separate.'}
        FOLDER.mkdir(parents=True,exist_ok=True)
        for name,data,_ in outputs:
            with (FOLDER/name).open('xb') as stream:stream.write(data)
        with receipt.open('x',encoding='utf8',newline='\n') as stream:json.dump(record,stream,indent=2);stream.write('\n')
    record=json.loads(receipt.read_bytes())
    if record['producer_file']!=Path(__file__).relative_to(ROOT).as_posix() or record['producer_sha256']!=sha(Path(__file__).read_bytes()):raise ValueError('Changed native acquisition producer')
    if record['protocol_file']!=PROTOCOL or record['protocol_sha256']!=sha((ROOT/PROTOCOL).read_bytes()):raise ValueError('Changed native declaration')
    if {row['source_url'] for row in record['source_files']}!=set(SOURCES.values()) or len(record['source_files'])!=2:raise ValueError('Changed source inventory')
    for row in record['source_files']:
        data=(ROOT/row['file']).read_bytes()
        if len(data)!=row['byte_count'] or sha(data)!=row['sha256']:raise ValueError('Changed native original: '+row['file'])
    print(json.dumps({'status':'PASS','files':len(record['source_files']),'bytes':sum(row['byte_count'] for row in record['source_files']),'field_values_inspected':False}))

if __name__=='__main__':main()
