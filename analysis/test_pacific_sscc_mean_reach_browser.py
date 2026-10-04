"""A historical southern mean reach is neither aggregate branch length nor PV-front width."""
import hashlib
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    def read(path):
        return json.loads(Path(path).read_text(encoding='utf-8'))
    candidate=read('research/pacific-sscc-mean-reach-reference-path-candidate.json')
    audit=read('research/pacific-sscc-mean-reach-branch-width-scope-audit.json')
    catalog=read('research/ocean-current-reference-path-candidates.json')
    row=next(r for r in read('research/ocean-motion-dashboard.json')['entries'] if r['id']=='current:pacific-south-subsurface-countercurrent')
    assert candidate['candidate_comparison_group']=='osw_studied_reach_routes'
    assert 'pacific-sscc-mean-reach-reference-path-candidate' not in catalog['reference_route_length_order']
    assert audit['historical_mean_core_to_named_branch_assignment']=='not_established'
    assert audit['source_branch_topology_status']=='independent_origin_versus_split_unresolved'
    assert audit['source_front_scale']['is_whole_current_width'] is False
    assert row['capabilities']['scoped_width']==0 and row['latest_observation_date'] is None
    assert hashlib.sha256(Path('research/ocean-current-almanac.json').read_bytes()).hexdigest()==read('research/ocean-current-inventory-expansion-candidates.json')['current_ledger_sha256']
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('OSW_TEST_BROWSER',r'C:\Program Files\Google\Chrome\Application\chrome.exe'))
        page=browser.new_page(viewport={'width':1440,'height':1000});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Apacific-south-subsurface-countercurrent#route-atlas',wait_until='networkidle')
        preview=page.locator('#route-atlas-preview')
        assert preview.locator('.route-map').is_visible()
        for text in ['5,000 km','4,900–5,100','Studied reach only','250 m','160 m','primary SSCC','secondary SSCC','not current width']:
            assert text in preview.inner_text(),text
        assert preview.locator('.route-atlas-state-links li').count()==len(candidate['nominal_atlas_state_crossings'])
        page.locator('#route-atlas').screenshot(path='figures/pacific-sscc-mean-reach-reference-path-review.png')
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert preview.locator('.route-map').is_visible()
        assert row['scope_notes'][0]['summary'] in preview.inner_text()
        page.locator('#route-atlas-world').click()
        assert preview.is_hidden()
        assert not errors,errors
        browser.close()
    print('OK: historical southern mean-core card/mobile, unresolved branch assignment/topology; PV-front span not width; no aggregate rank/date; canonical unchanged')


if __name__=='__main__':
    main()
