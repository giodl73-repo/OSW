"""Keep M6 observations separate from mooring spacing and current width."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/antarctic-slope-darelius-2024-scope-audit.json'
PAPER='research/source-data/darelius-asc-2024/journal-article.pdf'
SHA='acd1fd9be2546c270a6f2f26ed7d1ecb0bb6923be68298def3e6591e0bc38ab7'


def validate(audit,inventory):
    if audit['current_id']!='antarctic-slope' or audit['source_pdf_file']!=PAPER or audit['source_pdf_sha256']!=SHA:
        raise ValueError('Changed Antarctic Slope primary source identity')
    if hashlib.sha256((ROOT/PAPER).read_bytes()).hexdigest()!=SHA:
        raise ValueError('Changed Antarctic Slope original paper')
    if audit['map_buffer_eligible'] is not False or any(audit[k] is not None for k in ['whole_current_width_km','annual_width_range_km']):
        raise ValueError('Mooring scales promoted to current dimensions')
    if audit['excluded_dimensions']!=[
        {'value_km':5,'meaning':'M530–M740 mooring spacing','locator':'PDF p4, section 2.1'},
        {'value_km':80,'meaning':'M2570–M740 mooring separation','locator':'PDF p4, section 2.1'},
        {'value_km':10,'meaning':'Dynamical length scale, and separate approximate radius of curvature','locator':'PDF p13, section 4'}]:
        raise ValueError('Changed excluded Antarctic Slope dimension meaning')
    reviews=[r for r in inventory['review_assessments'] if r['current_id']=='antarctic-slope']
    review=audit['width_review']
    if review['decision']!='sources_reviewed_no_comparable_numeric_current_width' or any(review[k] is not None for k in ['whole_current_width_km','annual_width_range_km']):
        raise ValueError('Antarctic Slope review promoted to numeric width')
    if reviews!=[audit['width_review']] or any(r['current_id']=='antarctic-slope' for r in inventory['measurements']):
        raise ValueError('Antarctic Slope source review or unknown width changed')
    if hashlib.sha256((ROOT/audit['velocity_series_file']).read_bytes()).hexdigest()!=audit['velocity_series_sha256']:
        raise ValueError('Changed M6 velocity source binding')


if __name__=='__main__':
    validate(json.loads((ROOT/AUDIT).read_bytes()),json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes()))
    print('PASS: Antarctic Slope local velocity and excluded scales retain unknown current width')
