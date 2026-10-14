"""Show section positions and their difference without inventing a current width."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'research/azores-countercurrent-posaf-coordinate-meaning-audit.json'
SOURCE_SHA='7be42893016b7e8d895b5d978d4812058830d1a8556de93db6d855178f47cf43'

def load():
    raw=SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:raise ValueError('Changed reviewed coordinate-meaning audit')
    return json.loads(raw)

def validate(doc):
    if doc!=load():raise ValueError('Coordinate interpretation differs from reviewed primary passage')

def svg(doc):
    validate(doc);a=doc['coordinate_arithmetic'];lo=a['lower_section_coordinate_km'];hi=a['upper_section_coordinate_km']
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 490" role="img" aria-labelledby="azcc-title azcc-desc">
<title id="azcc-title">Azores Countercurrent: section positions versus width</title>
<desc id="azcc-desc">Primary indexed text describes positions about {lo} and {hi} km along a POSAF section. Their arithmetic difference is {hi-lo} km. The later 100 to 250 km width-range wording is a different interpretation. A current width or geographic boundary is not verified. Full primary figure and methods remain unreviewed.</desc>
<rect width="850" height="490" fill="#f7faf9"/><g font-family="Arial,sans-serif" fill="#183b46">
<text x="30" y="42" font-size="24">Azores Countercurrent / what the numbers locate</text>
<text x="30" y="76" font-size="16">POSAF temporal mean, February-June 1999 / 500-1200 dbar context</text>
<line x1="80" y1="155" x2="730" y2="155" stroke="#526c77"/>
<text x="80" y="185" text-anchor="middle">0</text><text x="730" y="185" text-anchor="middle">300</text>
<circle cx="297" cy="155" r="7" fill="#087a91"/><circle cx="622" cy="155" r="7" fill="#087a91"/>
<text x="297" y="127" text-anchor="middle">about {lo} km position</text><text x="622" y="127" text-anchor="middle">about {hi} km position</text>
<text x="405" y="219" text-anchor="middle">Section-distance coordinate (km); origin and geographic mapping unreviewed</text>
<line x1="297" y1="266" x2="622" y2="266" stroke="#c47418" stroke-width="3"/>
<text x="460" y="299" text-anchor="middle" font-size="20">Coordinate difference: {hi-lo} km</text>
<text x="30" y="348" font-size="16">The primary passage describes the mean westward maximum's section positions.</text>
<text x="30" y="378" font-size="16">Physical width and width error remain unknown; no velocity boundaries or annual range admitted.</text>
<text x="30" y="411" font-size="14">Primary: Alves et al. (2002), indexed discussion / Fig.9 caption; full original unreviewed.</text>
<text x="30" y="441" font-size="14">Secondary: Carracedo et al. (2012), pp.278-279. OSW source-meaning comparison, no curve digitization.</text>
</g></svg>
'''

if __name__=='__main__':
    target=ROOT/'figures/azores-countercurrent-posaf-coordinate-meaning.svg'
    target.write_bytes(svg(load()).encode());print(target.relative_to(ROOT))
