"""Verify the retained public-domain source; network acquisition requires --acquire."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,io,json,urllib.request,zipfile

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY='research/source-data/natural-earth-land-10m-5.1.1/'
FILE=DIRECTORY+'ne_10m_land.zip'
RECEIPT=DIRECTORY+'acquisition.json'
URL='https://naturalearth.s3.amazonaws.com/10m_physical/ne_10m_land.zip'
SHA256='e547d749445eaa0964aba76738090ec88f5e63c4585122170f98c67a7ea922dc'

def archive_metadata(data):
    if hashlib.sha256(data).hexdigest()!=SHA256:raise ValueError('Original land archive checksum changed; preserve it for review')
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        if archive.read('ne_10m_land.VERSION.txt').decode().strip()!='5.1.1':raise ValueError('Unexpected land edition')
        return {name:{'bytes':len(archive.read(name)),'sha256':hashlib.sha256(archive.read(name)).hexdigest()}
            for name in archive.namelist() if not name.endswith('/')}

def verify(root=ROOT):
    data=(root/FILE).read_bytes();receipt=json.loads((root/RECEIPT).read_bytes())
    members=archive_metadata(data)
    if receipt['sha256']!=SHA256 or receipt['bytes']!=len(data) or receipt['package_version']!='5.1.1' or receipt['members']!=members:
        raise ValueError('Land acquisition receipt differs from retained original')
    return {'status':'VERIFIED','package_version':'5.1.1','bytes':len(data),'sha256':SHA256}

def acquire(root=ROOT):
    if (root/FILE).exists() and (root/RECEIPT).exists():return verify(root)
    if (root/FILE).exists():archive_metadata((root/FILE).read_bytes())
    request=urllib.request.Request(URL,headers={'User-Agent':'OSW explicit public-data acquisition'})
    with urllib.request.urlopen(request,timeout=60) as response:data=response.read();final_url=response.url
    members=archive_metadata(data);(root/DIRECTORY).mkdir(parents=True,exist_ok=True)
    if not (root/FILE).exists():(root/FILE).write_bytes(data)
    if not (root/RECEIPT).exists():
        receipt={'schema':'osw.natural-earth-land-acquisition.v1','source_url':URL,'final_url':final_url,
            'retrieved_utc':datetime.now(timezone.utc).isoformat(),'package_version':'5.1.1','advertised_scale':'1:10 million',
            'file':FILE,'bytes':len(data),'sha256':SHA256,
            'product_url':'https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-land/',
            'license':'Public domain','license_url':'https://www.naturalearthdata.com/about/terms-of-use/',
            'crs':'WGS84 geographic degrees; retained .prj member supplies exact CRS declaration','members':members}
        (root/RECEIPT).write_bytes((json.dumps(receipt,indent=2)+'\n').encode())
    return verify(root)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--acquire',action='store_true');parser.add_argument('--check',action='store_true')
    arguments=parser.parse_args();print(json.dumps(acquire() if arguments.acquire else verify()))
