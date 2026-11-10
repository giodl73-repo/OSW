"""Retain initial paper bytes explicitly; default checks are offline and immutable."""
import argparse
from datetime import datetime,timezone
import hashlib,json
from pathlib import Path
import urllib.request
import pymupdf
import ssl
from paper_tls import CHAIN,PIN

ROOT=Path(__file__).resolve().parents[1]
SOURCES={
 'chen-necc-2016':('https://www.soest.hawaii.edu/oceanography/bo/Chen_etal_JGR2016.pdf','10.1002/2016JC012190','countercurrent'),
 'onishi-subarctic-2001':('https://www.terrapub.co.jp/journals/JO/pdf/5701/57010079.pdf','10.1023/A:1011178821299','subarctic'),
}


def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('source',choices=SOURCES);parser.add_argument('--acquire',action='store_true');args=parser.parse_args()
 url,doi,title_word=SOURCES[args.source];folder=ROOT/'research/source-data'/args.source;pdf=folder/'journal-article.pdf';receipt=folder/'acquisition.json'
 if args.acquire:
  if pdf.exists() or receipt.exists():raise ValueError('Refusing to replace original or receipt')
  options={}
  if args.source=='chen-necc-2016':
   chain=(ROOT/CHAIN).read_bytes()
   if hashlib.sha256(chain).hexdigest()!=PIN:raise ValueError('Changed university chain link')
   context=ssl.create_default_context();context.verify_flags &= ~ssl.VERIFY_X509_PARTIAL_CHAIN
   context.load_verify_locations(cadata=chain.decode('ascii'));options={'context':context}
  with urllib.request.urlopen(url,timeout=60,**options) as response:raw=response.read(20_000_001);final_url=response.url
  if not raw.startswith(b'%PDF-') or len(raw)>20_000_000:raise ValueError('Unexpected PDF response')
  doc=pymupdf.open(stream=raw,filetype='pdf')
  if title_word not in doc[0].get_text().lower():raise ValueError('Unexpected source title')
  data={'schema':'osw.source-acquisition.v1','source_url':url,'response_url':final_url,'doi':doi,
        'acquired_at_utc':datetime.now(timezone.utc).isoformat(),'file':pdf.relative_to(ROOT).as_posix(),
        'sha256':hashlib.sha256(raw).hexdigest(),'byte_count':len(raw),'pages':len(doc),
        'source_version':'Published journal layout; original retained for local evidence inspection.',
        'access_note':'Publicly accessible primary paper; no public redistribution or license grant inferred. Original PDF remains ignored.',
        'producer_file':'analysis/acquire_pacific_width_papers.py','producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
  if args.source=='chen-necc-2016':data.update(tls_chain_file=CHAIN,tls_chain_sha256=PIN,tls_policy='Existing system root plus pinned cross-signed chain link; partial-chain trust disabled. No verification bypass or new trust anchor.')
  folder.mkdir(parents=True,exist_ok=True)
  with pdf.open('xb') as out:out.write(raw)
  with receipt.open('x',encoding='utf8',newline='\n') as out:json.dump(data,out,indent=2);out.write('\n')
 data=json.loads(receipt.read_bytes());raw=pdf.read_bytes()
 if len(raw)!=data['byte_count'] or hashlib.sha256(raw).hexdigest()!=data['sha256']:raise ValueError('Changed retained original')
 print('PASS original',args.source,data['byte_count'],data['sha256'])


if __name__=='__main__':main()
