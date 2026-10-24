"""Explicit initial acquisition; default operation only verifies retained bytes."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'research/source-data/cainzos-antilles-2023'
URL='https://os.copernicus.org/articles/19/1009/2023/os-19-1009-2023.pdf'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--acquire',action='store_true')
    args=parser.parse_args()
    path=DIRECTORY/'journal-article.pdf';receipt=DIRECTORY/'acquisition.json'
    if args.acquire:
        if path.exists() or receipt.exists():raise ValueError('Refusing to replace retained source or receipt')
        with urllib.request.urlopen(URL,timeout=90) as response:
            raw=response.read(20_000_001);final_url=response.url
        if not raw.startswith(b'%PDF-') or len(raw)>20_000_000:raise ValueError('Unexpected article response')
        DIRECTORY.mkdir(parents=True,exist_ok=True)
        data={'schema':'osw.published-article-acquisition.v1','retrieved_utc':datetime.now(timezone.utc).isoformat(),
              'source_url':URL,'response_url':final_url,'file':path.relative_to(ROOT).as_posix(),
              'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
              'doi':'10.5194/os-19-1009-2023','license':'CC-BY-4.0',
              'license_url':'https://creativecommons.org/licenses/by/4.0/',
              'citation':'Cainzos et al. (2023), Consistent picture of the horizontal circulation of the Atlantic Ocean over 3 decades, Ocean Science19,1009-1045.',
              'acquirer_file':'analysis/acquire_antilles_cainzos_article.py',
              'acquirer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
        with path.open('xb') as out:out.write(raw)
        with receipt.open('x',encoding='utf8',newline='\n') as out:json.dump(data,out,indent=2);out.write('\n')
    data=json.loads(receipt.read_bytes());raw=path.read_bytes()
    if len(raw)!=data['bytes'] or hashlib.sha256(raw).hexdigest()!=data['sha256']:raise ValueError('Changed original article')
    print('PASS retained publisher article',data['bytes'],data['sha256'])


if __name__=='__main__':main()
