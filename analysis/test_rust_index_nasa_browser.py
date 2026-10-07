"""Exact source NASA object joins, media/evidence parity and filtered navigation."""
import gzip
import json
import os
from pathlib import Path
import subprocess
import tempfile
from playwright.sync_api import sync_playwright
from test_rust_query_browser import ROOT, CLI


def main():
    def read(name): return json.loads((ROOT/'research'/name).read_bytes())
    data=read('nasa-perpetual-ocean-objects.json')
    crosswalk=read('nasa-ocean-object-state-crosswalk.json')['objects']
    forms=read('nasa-perpetual-ocean-motion-forms.json')
    objects={r['id']:r for r in data['objects']}
    releases={r['id']:r for r in data['releases']}
    currents={r['id']:r for r in read('ocean-current-almanac.json')['entries']}
    assets={r['id']:r for r in read('nasa-perpetual-ocean-object-media.json')['assets']}
    catalog={r['id']:r for r in read('nasa-perpetual-ocean-atlas-catalog.json')['records']}
    crops=read('nasa-current-cartographic-crop-join.json')
    crop_rows={r['nasa_object_id']:r for r in crops['records']}
    movies=read('nasa-object-movie-variant-join.json')
    def oracle(text=''):
        rows=[]
        for ordinal,item in enumerate(data['objects']):
            id=item['id'];form=forms['objects'][id];relation=crosswalk[id]
            haystack=' '.join([item['name'],item['support'],form,item['description']]).lower()
            if text.strip().lower() not in haystack: continue
            variants=[{'movie':movie,'relation':edge,'release':releases[movie['release_id']]}
                      for movie in movies['entries'] for edge in movie['direct_object_relations'] if edge['object_id']==id]
            rows.append({'record':item,'source_pointer':f'/objects/{ordinal}','form':form,'crosswalk':relation,
                         'parent':objects.get(item.get('parent_id')),
                         'external_currents':[{'relation':r,'record':currents[r['current_id']]} for r in relation['external_current_context']],
                         'examples':[objects[k] for k in relation['example_object_ids']],
                         'systems':[{'relation':r,'record':objects[r['system_id']]} for r in relation['system_context']],
                         'class_parent':objects[relation['class_parent']['parent_id']] if relation.get('class_parent') else None,
                         'class_children':[{'relation':r,'record':objects[r['child_id']]} for r in relation['class_children']],
                         'catalog':catalog[id],'cartographic_crops':crop_rows.get(id),
                         'releases':[{'record':releases[k],'evidence':relation['release_evidence'][k]} for k in item['nasa_sources']],
                         'feature_media':[assets[k] for k in relation['feature_media_ids']],
                         'variants':variants,'narrated_release':releases['po2-narrated'] if item.get('narrated_start_s') is not None else None})
        return rows
    selections=[{}, {'text':'kuroshio'}, {'text':'eddies'}, {'text':'overflow'}]
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as directory:
        packet=Path(directory)/'index.json'
        packet.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        native_views=[]
        for selection in selections:
            result=subprocess.run([str(CLI),'--index',str(packet),'--nasa','-'],input=json.dumps(selection),
                                  capture_output=True,text=True,encoding='utf-8')
            assert result.returncode==0,result.stderr
            view=json.loads(result.stdout)
            assert view['rows']==oracle(selection.get('text','')),selection
            assert view['total']==len(data['objects'])
            assert view['form_definitions']==forms['forms']
            assert view['class_relation_rule']==forms['class_relation_rule']
            assert view['crop_claim_limit']==crops['claim_limit']
            assert view['movie_variant_rule']==movies['rule']
            assert view['release_evidence_count']==sum(len(r['release_evidence']) for r in crosswalk.values())
            native_views.append(view)
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
            page=browser.new_page(viewport={'width':1440,'height':1000})
            errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto('http://127.0.0.1:8788/almanac/index.html')
            page.wait_for_function('window.oswIndexPageReady',timeout=90000)
            assert page.evaluate('oswIndexNasaView')==native_views[0]
            for selection,expected in zip(selections,native_views):
                page.locator('#nasa-search').fill(selection.get('text',''))
                page.locator('#nasa-search').dispatch_event('input')
                page.wait_for_function('text=>oswIndexNasaView.text===text',arg=selection.get('text',''))
                assert page.evaluate('oswIndexNasaView')==expected
                assert page.locator('#nasa-rows tr').evaluate_all('(rows)=>rows.map(r=>r.id)')==[
                    'nasa-'+r['record']['id'] for r in expected['rows']]
            # Find every original object through its literal name and preserve its joins.
            for item in data['objects']:
                actual=page.evaluate('text=>oswIndexNasa({text})',item['name'])
                assert actual['rows']==oracle(item['name'])
                assert any(r['record']['id']==item['id'] for r in actual['rows'])
            assert page.evaluate('oswIndexNasa({extra:true}).then(()=>false,()=>true)')
            page.locator('#nasa-search').fill('kuroshio')
            page.wait_for_function("oswIndexNasaView.text==='kuroshio'")
            for group in ['376521','376522','376523']:
                assert page.locator(f'#nasa-kuroshio a[href="https://svs.gsfc.nasa.gov/5425#media_group_{group}"]').count()==1
            # Parent, class and current links reveal targets hidden by active searches.
            child=next(item for item in data['objects'] if item.get('parent_id') and not item.get('almanac_current_id') and not item.get('atlas_feature_id'))
            page.locator('#nasa-search').fill(child['name'])
            page.wait_for_function('text=>oswIndexNasaView.text===text',arg=child['name'])
            page.locator(f'#nasa-{child["id"]} a[href="#nasa-{child["parent_id"]}"]').first.click()
            page.wait_for_function('hash=>location.hash===hash && oswIndexNasaView.text===\'\'',arg='#nasa-'+child['parent_id'])
            page.locator('#current-search').fill('Agulhas')
            page.locator('#nasa-search').fill('Kuroshio')
            page.wait_for_function("oswIndexNasaView.text==='Kuroshio'")
            page.locator('#nasa-kuroshio a[href="#current-kuroshio"]').first.click()
            page.wait_for_function("location.hash==='#current-kuroshio' && oswIndexCurrentView.rows.length===100")
            # An external map marker can restore a NASA object excluded by search.
            target=next(r for r in data['objects'] if r.get('locator') and not r.get('almanac_current_id') and r['id']!=child['parent_id'])
            marker=page.locator(f'#motion-markers a[data-record="{target["id"]}"]')
            marker.focus();marker.press('Enter')
            page.wait_for_function('hash=>location.hash===hash && oswIndexNasaView.text===\'\'',arg='#nasa-'+target['id'])
            page.locator('#nasa-search').fill('eddies');page.locator('#nasa-search').fill('overflow');page.locator('#nasa-search').fill('gulf stream')
            page.wait_for_function("oswIndexNasaView.text==='gulf stream'")
            assert page.evaluate('oswIndexNasaView.rows')==oracle('gulf stream')
            page.set_viewport_size({'width':320,'height':800})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            assert not errors,errors
            browser.close()
    print(f'PASS: {len(data["objects"])} exact NASA objects and every original source/media/context join; four native/WASM views, all names, filtered links, rapid search and mobile layout')


if __name__=='__main__': main()
