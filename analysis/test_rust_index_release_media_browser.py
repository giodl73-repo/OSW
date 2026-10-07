"""Release catalog/source credit/object evidence joins and exact media inventory."""
import gzip
import json
import os
from pathlib import Path
import subprocess
import tempfile
from playwright.sync_api import sync_playwright
from test_rust_query_browser import ROOT, CLI


def main():
    def read(path):return json.loads((ROOT/path).read_bytes())
    catalog=read('research/nasa-perpetual-ocean-release-media.json')
    audit={r['id']:r for r in read('research/nasa-perpetual-ocean-source-audit.json')['releases']}
    objects={r['id']:r for r in read('research/nasa-perpetual-ocean-objects.json')['objects']}
    crosswalk=read('research/nasa-ocean-object-state-crosswalk.json')['objects']
    registry={r['url']:r for r in read('almanac/release/v0.1.0/sources.json') if r.get('url')}
    rows=[{'record':release,'source_pointer':f'/releases/{ordinal}',
           'audit':audit[release['release_id']],'source':registry[release['source_page']],
           'objects':[{'record':objects[id],'evidence':crosswalk[id]['release_evidence'][release['release_id']]}
                      for id in audit[release['release_id']]['object_ids']]}
          for ordinal,release in enumerate(catalog['releases'])]
    assert len(rows)==catalog['release_count']==7
    assert sum(len(row['record']['movies']) for row in rows)==catalog['movie_listing_count']==55
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as directory:
        packet=Path(directory)/'index.json'
        packet.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        run=subprocess.run([str(CLI),'--index',str(packet),'--release-media','-'],input='{}',
                           capture_output=True,text=True,encoding='utf-8')
        assert run.returncode==0,run.stderr
        expected=json.loads(run.stdout)
        assert expected['rows']==rows
        assert expected['method']==catalog['method']
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
            page=browser.new_page(viewport={'width':1440,'height':1000})
            errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto('http://127.0.0.1:8788/almanac/index.html')
            page.wait_for_function('window.oswIndexPageReady',timeout=90000)
            assert page.evaluate('oswIndexReleaseMediaView')==expected
            assert page.evaluate('oswIndexReleaseMedia()')==expected
            panels=page.locator('#nasa-media-releases > details')
            assert panels.count()==7
            for index,row in enumerate(rows):
                panel=panels.nth(index)
                panel.evaluate('el=>el.open=true')
                assert panel.locator('summary').inner_text()==f'{row["record"]["title"]} · {len(row["objects"])} identified records · {len(row["record"]["movies"])} movie files'
                citation=panel.locator('.source-review-note')
                assert citation.locator('cite').inner_text()==row['source']['preferred_citation']
                assert row['source']['credit_text'] in citation.inner_text()
                assert panel.locator('.nasa-release-objects a').evaluate_all('(nodes)=>nodes.map(n=>n.getAttribute("href"))')==[
                    href for obj in row['objects'] for href in ['#nasa-'+obj['record']['id'],obj['evidence']['source_url']]]
                assert panel.locator('ul').last.locator('a').evaluate_all('(nodes)=>nodes.map(n=>n.getAttribute("href"))')==[m['url'] for m in row['record']['movies']]
                for movie,link in zip(row['record']['movies'],panel.locator('ul').last.locator('a').all()):
                    assert link.inner_text()==movie['filename']+' ↗'
                    assert link.get_attribute('title')==(movie.get('group_title') or movie.get('group_description') or None)
            # Release navigation resets NASA search before jumping to an object.
            page.locator('#nasa-search').fill('overflow')
            page.wait_for_function("oswIndexNasaView.text==='overflow'")
            row=next(r for r in rows if r['objects'])
            target=row['objects'][0]['record']['id']
            page.locator(f'#nasa-media-releases .nasa-release-objects a[href="#nasa-{target}"]').first.click()
            page.wait_for_function('hash=>location.hash===hash && oswIndexNasaView.text===\'\'',arg='#nasa-'+target)
            assert page.locator('#nasa-media-count').inner_text()=='7 releases · 55 movie files'
            page.set_viewport_size({'width':320,'height':800})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            assert not errors,errors
            browser.close()
    print('PASS: seven original releases, 55 exact media listings, all source credits/citations and object passage joins, native/WASM parity, filtered navigation and mobile layout')


if __name__=='__main__':main()
