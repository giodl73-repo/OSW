"""One reported dated jet constraint does not define the broader ASC width."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = 'research/antarctic-slope-chavanne-2010-dated-width-constraint-scope-audit.json'
PIN = 'cb1a89fd1e4475cb6682ed178e73365961abc5756054105c6c07eb0bf1bcec6e'
ID = 'antarctic-slope-chavanne-2009-02-23-jet-width-constraint'


def load():
    raw = (ROOT/AUDIT).read_bytes()
    if hashlib.sha256(raw).hexdigest() != PIN:
        raise ValueError('Changed reviewed Antarctic Slope dated jet constraint')
    return json.loads(raw)


def record():
    row = copy.deepcopy(load()['measurement'])
    row['original_regional_context'].update(audit_file=AUDIT, audit_sha256=PIN)
    return row


def validate_row(row, audit=None):
    expected = load()
    if audit is not None and audit != expected or row != record():
        raise ValueError('Antarctic Slope jet constraint differs from reviewed source or date')
    for key in ['protocol', 'previous_source_audit']:
        if hashlib.sha256((ROOT/expected[key+'_file']).read_bytes()).hexdigest() != expected[key+'_sha256']:
            raise ValueError('Changed Antarctic Slope source-review provenance')


def validate_inventory(document):
    rows = [r for r in document['measurements'] if r.get('id') == ID]
    if len(rows) != 1:
        raise ValueError('Missing or duplicated reviewed Antarctic Slope dated jet constraint')
    validate_row(rows[0])


def svg():
    load()
    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 430" role="img" aria-labelledby="title desc">
<title id="title">Antarctic Slope Current: a reported dated narrow-jet constraint</title>
<desc id="desc">Less than 28 km on 23 February 2009, in the 100 m detided LADCP context near Riiser-Larsenisen. A narrow southwestward jet within broader flow. Representative width, lower bound and error unknown. Original PDF, figure pixels and paired edges unavailable; primary publisher indexed text reviewed. No zero-to-28 interval, confidence guarantee or annual range.</desc>
<rect width="850" height="430" fill="#f7faf9"/>
<g fill="#123541" font-family="sans-serif" font-size="17">
<text x="30" y="45" font-size="22">Antarctic Slope Current · narrow-jet description</text>
<text x="30" y="79">Riiser-Larsenisen · 23 February 2009 · 100 m LADCP context</text>
<text x="30" y="154" font-size="52">&lt;28 km</text>
<text x="30" y="190">Author's reported constraint; no point width or lower bound.</text>
<text x="30" y="232">Narrow southwestward jet, embedded in broader southwestward flow.</text>
<text x="30" y="262">Peak 28 cm/s and background about 10 cm/s are not edge cutoffs.</text>
<text x="30" y="292">3000 m is bottom topography, not observation depth.</text>
<text x="30" y="322">No zero-to-28 interval, confidence guarantee, width band or annual range.</text>
<text x="30" y="359" font-size="14">Source: Chavanne et al. (2010), DOI 10.1029/2010GL043603, Observations paragraph 5.</text>
<text x="30" y="386" font-size="14">Primary publisher indexed text/captions read; original PDF and figure pixels unavailable.</text>
<text x="30" y="412" font-size="14">Independent OSW graphic; source field and paired width edges not reproduced.</text>
</g></svg>'''


if __name__ == '__main__':
    validate_inventory(json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes()))
    (ROOT/'figures/antarctic-slope-chavanne-2009-jet-width-constraint.svg').write_text(svg(), encoding='utf8')
    print('Verified dated Antarctic Slope jet constraint; independent graphic written')
