"""Compare two frozen reported model-core spans without inventing a width cycle."""
import argparse,hashlib,json
from pathlib import Path
from html import escape

ROOT=Path(__file__).resolve().parents[1]
RECORD=ROOT/'research/azores-carracedo-2014-climatological-core-width-record.json'
RECORD_SHA='a692447701908505b1e59824c932e2f3a1d9eb4d59922f6a3cd0019fc1d213f4'
FIGURE=ROOT/'figures/azores-carracedo-2014-climatological-core-widths.svg'

def load():
    raw=RECORD.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=RECORD_SHA:raise ValueError('Changed reviewed seasonal model-width record')
    return json.loads(raw)

def validate(document):
    if document!=load():raise ValueError('Seasonal model-width extraction differs from reviewed record')

def verify_originals(document):
    validate(document)
    for receipt in [document,document['season_convention']]:
        raw=(ROOT/receipt['source_document_file']).read_bytes()
        if len(raw)!=receipt['source_document_bytes'] or hashlib.sha256(raw).hexdigest()!=receipt['source_document_sha256']:raise ValueError('Changed source original')

def svg(document):
    validate(document)
    rows=document['measurements'];parts=[]
    for i,r in enumerate(rows):
        y=175+i*90;x=250+r['approximate_width_km']*.9
        parts.append(f'<text x="35" y="{y+5}" font-size="17">{escape(r["source_season_label"].title())}</text><text x="35" y="{y+27}" font-size="13">'+('April-June' if i==0 else 'October-December')+f'</text><circle cx="{x}" cy="{y}" r="7" fill="#087a91"/><text x="{x+14}" y="{y+5}" font-size="17">about {r["approximate_width_km"]} km</text>')
    ticks=''.join(f'<line x1="{250+n*.9}" y1="125" x2="{250+n*.9}" y2="295" stroke="#d5e1e4"/><text x="{250+n*.9}" y="320" text-anchor="middle" font-size="13">{n}</text>' for n in [0,100,200,300,400,500])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 560" role="img" aria-labelledby="azores-title azores-desc">
<title id="azores-title">Azores Current: two reported seasonal model-core spans</title>
<desc id="azores-desc">About 240 km in WOA09 spring (April to June), about 400 km in autumn (October to December), on a regional inverse-model section at 19.5 W using a 2 cm/s velocity criterion. Width uncertainty, winter/summer values and annual physical ranges remain unknown. Points are independent source summaries and are not interpolated.</desc>
<rect width="880" height="560" fill="#f7faf9"/>
<g font-family="Arial,sans-serif" fill="#183b46">
<text x="35" y="45" font-size="23">Azores Current / reported seasonal model core</text>
<text x="35" y="77" font-size="16">19.5 W regional section / velocities greater than 2 cm/s</text>
{ticks}{''.join(parts)}
<text x="480" y="355" text-anchor="middle" font-size="15">Reported model-core span (km)</text>
<text x="35" y="405" font-size="15">WOA09 seasons: April-June and October-December. Native hydrographic grid: 1 degree.</text>
<text x="35" y="435" font-size="15">No width error supplied. Winter/summer widths, full-current dimensions and annual ranges unknown.</text>
<text x="35" y="465" font-size="15">Mixed historical climatological support; no monthly interpolation or mapped width footprint.</text>
<text x="35" y="505" font-size="13">Source: Carracedo et al. (2014), Progress in Oceanography 122, p.122 / doi:10.1016/j.pocean.2013.12.005.</text>
<text x="35" y="530" font-size="13">Season definitions: NOAA World Ocean Atlas 2009, Volume 1, p.1. OSW comparison; scientific admission pending.</text>
</g></svg>
'''

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--verify-originals',action='store_true');args=parser.parse_args()
    document=load()
    if args.verify_originals:verify_originals(document)
    FIGURE.write_bytes(svg(document).encode());print(FIGURE.relative_to(ROOT))

if __name__=='__main__':main()
