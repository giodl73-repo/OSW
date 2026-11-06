"""Acquire the licensed publisher originals once, or verify them offline."""
import argparse,datetime,hashlib,json,urllib.request
from pathlib import Path
import agulhas_reported_dimensions as a

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--verify-only',action='store_true');args=parser.parse_args()
    root=a.ROOT/a.DIRECTORY;receipt=root/'acquisition.json'
    if receipt.exists() or args.verify_only:
        a.original();print('Verified original2021 publication PDF/XML and acquisition receipt.');return
    root.mkdir(parents=True,exist_ok=True)
    if any((root/name).exists() for name in a.PINS):raise SystemExit('Partial originals exist; preserve them and recover their acquisition receipt before retrying.')
    rows=[]
    for name,pin in a.PINS.items():
        suffix=Path(name).suffix;url='https://bg.copernicus.org/articles/18/5967/2021/bg-18-5967-2021'+suffix
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'OSW scientific source audit'}),timeout=60) as response:
            raw=response.read();kind=response.headers.get_content_type();final=response.url
        if hashlib.sha256(raw).hexdigest()!=pin:raise ValueError('Publisher original changed; review a new source edition before replacing anything.')
        (root/name).write_bytes(raw)
        rows.append({'path':a.DIRECTORY+name,'request_url':url,'final_url':final,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'content_type':kind,'bytes':len(raw),'sha256':pin})
    receipt.write_bytes(a.encoded({'schema':'osw.original-publication-acquisition.v1','doi':'10.5194/bg-18-5967-2021','files':rows,
        'license':'CC BY 4.0','license_url':'https://creativecommons.org/licenses/by/4.0/','publisher_url':a.URL}))
    a.original();print('Acquired and verified licensed originals; subsequent runs preserve them.')

if __name__=='__main__':main()
