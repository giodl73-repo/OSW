"""Research calculations survive native/WASM queries and accessible current cards."""
import copy
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from urllib.parse import quote, unquote

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get('OSW_RESEARCH_EVIDENCE_BASE', 'http://127.0.0.1:8788')
CLI = ROOT / 'rust/osw-query/target/debug' / ('osw-query-cli.exe' if os.name == 'nt' else 'osw-query-cli')
REGISTRY = 'research/current-research-evidence-registry.json'


def native(query, packet=None, index=None):
    args = [str(CLI)] + (['--index', str(index)] if index else [str(packet or ROOT / 'almanac/query-data.json')]) + ['-']
    result = subprocess.run(args, input=json.dumps(query), capture_output=True, text=True, encoding='utf8')
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def corrupt(packet, kind):
    bad = copy.deepcopy(packet)
    rows = [r for r in bad['collections']['diagnostics'] if 'research_evidence' in r]
    if kind.startswith('span_'):
        row=next(r for r in rows if r['current_id']=='aleutian')
        doc=copy.deepcopy(row['document'])
        if kind=='span_value':doc['branches'][0]['boundary_choice_scenarios'][1]['endpoint_separation_km']=1
        elif kind=='span_bracket':doc['branches'][0]['boundary_choice_scenarios'][1]['before_peak']['outside']['source_time_index']=1
        elif kind=='span_sensitivity':doc['branches'][0]['velocity_sensitivity_scenarios'].pop()
        elif kind=='span_metric':doc['metric']='physical flow-normal current width'
        elif kind=='span_admission':doc['new_width_record_admitted']=True
        elif kind=='span_envelope':doc['branches'][0]['complete_boundary_choice_envelope_km']=[1,2]
        elif kind=='span_protocol':bad['manifest']['input_sha256'][doc['protocol_file']]='0'*64;return bad
        else:raise AssertionError(kind)
        raw=json.dumps(doc);pin=hashlib.sha256(raw.encode()).hexdigest()
        row.update(document=doc,source_json=raw,source_file_sha256=pin)
        bad['manifest']['input_sha256'][row['source_file']]=pin
        return bad
    if kind.startswith('observed_'):
        row=next(r for r in rows if r['current_id']=='aleutian')
        if kind=='observed_missing':bad['collections']['diagnostics'].remove(row)
        elif kind=='observed_duplicate':
            extra=copy.deepcopy(row);extra['id']+=':copy';bad['collections']['diagnostics'].append(extra)
        elif kind=='observed_original':bad['manifest']['input_sha256']['research/source-data/jasadcp-p14n-1993/hourly-vector-original.nc']='0'*64
        else:
            doc=copy.deepcopy(row['document']);hydro=doc.get('hydrography_context',doc);velocity=hydro.get('velocity_section',hydro)
            if kind=='observed_value':velocity['profiles'][0]['profile'][0]['eastward_m_s']=3
            elif kind=='observed_mask':velocity['profiles'][0]['profile'][0]['joint_valid']=False
            elif kind=='observed_units':velocity['provider_units']='centimetres per second'
            elif kind=='observed_layer':velocity['layer_bounds_m']=[0,300]
            elif kind=='observed_annual':doc['annual_width_range_km']=[1,2]
            elif kind=='observed_association':doc['current_association_verified']=True
            elif kind=='observed_reorder':velocity['profiles'].sort(key=lambda r:r['latitude_degrees_north'])
            else:raise AssertionError(kind)
            raw=json.dumps(doc);pin=hashlib.sha256(raw.encode()).hexdigest()
            row.update(document=doc,source_json=raw,source_file_sha256=pin)
            bad['manifest']['input_sha256'][row['source_file']]=pin
        return bad
    if kind.startswith('hydro_'):
        row=next(r for r in rows if r['current_id']=='aleutian')
        if kind=='hydro_original':bad['manifest']['input_sha256']['research/source-data/cchdo-p14n-1993/ctd-original.nc']='0'*64
        else:
            doc=copy.deepcopy(row['document']);hydro=doc.get('hydrography_context',doc)
            if kind=='hydro_property':hydro['casts'][0]['cells'][0]['practical_salinity_pss78']=0
            elif kind=='hydro_quality':hydro['casts'][0]['cells'][0]['salinity_qc']=7
            elif kind=='hydro_depth':hydro['casts'][0]['cells'][10]['depth_m']=hydro['casts'][0]['cells'][10]['pressure_dbar']
            elif kind=='hydro_bottom':hydro['casts'][0]['nominal_bottom_time_utc']='1993-07-13T00:00:00Z'
            elif kind=='hydro_pair_limit':hydro['matching_rules']['maximum_absolute_bottom_time_offset_hours']=9
            elif kind=='hydro_pair_offsets':hydro['candidate_pairs'][0]['position_separation_km']=0
            elif kind=='hydro_interpolation':hydro['hydrography_interpolated_to_adcp']=True
            elif kind=='hydro_correction':hydro['historical_temperature_correction_application_verified']=True
            elif kind=='hydro_units':hydro['temperature_kind']='potential_temperature'
            else:raise AssertionError(kind)
            raw=json.dumps(doc);pin=hashlib.sha256(raw.encode()).hexdigest()
            row.update(document=doc,source_json=raw,source_file_sha256=pin)
            bad['manifest']['input_sha256'][row['source_file']]=pin
        return bad
    row = next(r for r in rows if r['current_id'] == 'red-sea-saline-overflow')
    if kind.startswith('necc_'):
        target=next(r for r in rows if r['current_id']=='pacific-north-equatorial-countercurrent')
        document=copy.deepcopy(target['document'])
        field={'necc_flow_normal':'component_spans_are_flow_normal_widths','necc_independence':'same_product_columns_are_independent_validation','necc_whole_width':'whole_current_width_km'}[kind]
        document[field]=500 if kind=='necc_whole_width' else True
        raw=json.dumps(document);pin=hashlib.sha256(raw.encode()).hexdigest()
        target.update(document=document,source_json=raw,source_file_sha256=pin)
        bad['manifest']['input_sha256'][target['source_file']]=pin
        return bad
    if kind.startswith('year_'):
        row=next(r for r in rows if r['current_id']=='norwegian-coastal')
        if kind=='year_hours':
            document=copy.deepcopy(row['document']);document['calendar_hours']=12
            raw=json.dumps(document);pin=hashlib.sha256(raw.encode()).hexdigest()
            row.update(document=document,source_json=raw,source_file_sha256=pin)
            bad['manifest']['input_sha256'][row['source_file']]=pin
        elif kind=='year_figure':row['research_evidence']['additional_figures'][0]['file']='figures/wrong.svg'
        elif kind=='year_width':row['research_evidence']['annual_width_range_km']=[1,2]
        return bad
    if kind == 'rank': row['rank_eligible'] = True
    elif kind == 'owner': row['current_id'] = 'agulhas'; row['entity_id'] = 'current:agulhas'
    elif kind == 'source_json': row['source_json'] = '{}'
    elif kind == 'missing': bad['collections']['diagnostics'].remove(row)
    elif kind == 'duplicate':
        extra = copy.deepcopy(row); extra['id'] += ':copy'; bad['collections']['diagnostics'].append(extra)
    elif kind == 'owner_link':
        next(o for o in bad['collections']['objects'] if o['id'] == row['entity_id'])['research_evidence_ids'] = []
    elif kind == 'orphan':
        del bad['manifest']['input_sha256'][REGISTRY]
        owners = {r['entity_id'] for r in rows}
        bad['collections']['objects'] = [o for o in bad['collections']['objects'] if o['id'] not in owners]
    elif kind == 'original_pin':
        bad['manifest']['input_sha256']['research/source-data/ncei-redsox-2001/ladcp-ascii-originals.zip'] = '0' * 64
    elif kind in ('whole_width', 'annual', 'blinding', 'identity'):
        target = rows[0] if kind == 'identity' else row
        document = copy.deepcopy(target['document'])
        if kind == 'whole_width': document['whole_current_width_km'] = 6
        elif kind == 'annual': document['annual_width_range_km'] = [0, 6]
        elif kind == 'blinding': document['fully_blinded_before_any_selected_velocity_exposure'] = True
        else: document['current_association_verified'] = True
        raw = json.dumps(document)
        pin = hashlib.sha256(raw.encode()).hexdigest()
        target.update(document=document, source_json=raw, source_file_sha256=pin)
        bad['manifest']['input_sha256'][target['source_file']] = pin
    elif kind in ('scene_width', 'geometry', 'figure', 'primary'):
        scene = row['research_evidence']
        if kind == 'scene_width': scene['whole_current_width_km'] = 6
        elif kind == 'geometry': scene['geometry_role'] = 'physical_width_geometry'
        elif kind == 'figure': scene['figure_sha256'] = '0' * 64
        else: scene['facts'][1]['value'] = 'About 6 km'
        # Coherently change and rehash the accompanying registry too.
        registry = json.loads((ROOT / REGISTRY).read_bytes())
        registry['scenes'] = [scene if s['diagnostic_id'] == row['id'] else s for s in registry['scenes']]
        bad['manifest']['input_sha256'][REGISTRY] = hashlib.sha256(json.dumps(registry).encode()).hexdigest()
    else: raise AssertionError(kind)
    return bad


def check_source_documents(page, registry):
    """Query every new document through one loaded WASM source store."""
    page.locator('#source-query-panel details').evaluate('(node)=>node.open=true')
    for document in [REGISTRY, *registry['documents']]:
        request = {'document':document, 'pointer':'', 'limit':1}
        page.locator('#source-query-json').fill(json.dumps(request))
        page.evaluate('window.oswSourceQueryResult=null')
        page.locator('#source-query-run-json').click()
        page.wait_for_function('window.oswSourceQueryResult', timeout=90000)
        actual = page.evaluate('window.oswSourceQueryResult')
        source = json.loads((ROOT / document).read_bytes())
        key = sorted(source)[0]
        assert actual['document'] == document and actual['total'] == len(source)
        assert actual['source_sha256'] == hashlib.sha256((ROOT / document).read_bytes()).hexdigest()
        assert actual['rows'] == [{'source_key':key, 'source_pointer':'/' + key.replace('~','~0').replace('/','~1'), 'record':source[key]}]
        print('PASS source document',document,flush=True)


def main():
    output = ROOT / '.pytest_cache/current-research-evidence-browser'
    output.mkdir(parents=True, exist_ok=True)
    registry = json.loads((ROOT / REGISTRY).read_bytes())
    packet = json.loads((ROOT / 'almanac/query-data.json').read_bytes())
    cases = ['rank', 'owner', 'source_json', 'missing', 'duplicate', 'owner_link', 'orphan', 'original_pin',
             'whole_width', 'annual', 'blinding', 'identity', 'scene_width', 'geometry', 'figure', 'primary', 'year_hours', 'year_figure', 'year_width','necc_flow_normal','necc_independence','necc_whole_width']
    cases += ['observed_'+case for case in ['value','mask','units','layer','annual','association','reorder','original','missing','duplicate']]
    cases += ['hydro_'+case for case in ['property','quality','depth','bottom','pair_limit','pair_offsets','interpolation','correction','units','original']]
    cases += ['span_'+case for case in ['value','bracket','sensitivity','metric','admission','envelope','protocol']]
    with TemporaryDirectory(dir=output) as temporary, sync_playwright() as playwright:
        folder = Path(temporary)
        index = folder / 'index.json'
        index.write_bytes(gzip.decompress((ROOT / 'almanac/index-data.json.gz').read_bytes()))
        # Loading the native index verifies all catalog document bytes once.
        assert native({'document':REGISTRY, 'pointer':'', 'limit':1}, index=index)['ok']
        browser = playwright.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page = browser.new_page(viewport={'width':1280, 'height':1000})
        errors, automatic_originals = [], []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('request', lambda r: automatic_originals.append(r.url) if r.url.lower().split('?')[0].endswith(('.pdf', '.zip', '.mat','.nc')) else None)
        for scene in registry['scenes']:
            owner = scene['current_id']
            print('Checking shared views',owner,flush=True)
            page.goto(BASE + '/almanac/reference-routes.html?atlas-feature=current%3A' + owner + '#route-atlas')
            panel = page.locator('#route-atlas-preview .current-research-evidence')
            expect(panel).to_be_visible(timeout=90000)
            assert panel.locator('dd').all_text_contents() == [f['value'] for f in scene['facts']]
            assert panel.get_attribute('data-current') == owner
            assert '\u00c3' not in panel.inner_text() and '\u00c2' not in panel.inner_text()
            details = panel.locator('details')
            assert details.get_attribute('open') is None
            details.locator('summary').focus(); page.keyboard.press('Enter')
            assert details.get_attribute('open') is not None
            expect(details.locator('img')).to_be_visible()
            expect(details.locator('img')).to_have_js_property('complete', True)
            assert details.locator('img').evaluate('(img)=>img.naturalWidth>0')
            expect(details).to_contain_text('Next evidence needed:')
            if owner == 'red-sea-saline-overflow':
                expect(details).to_contain_text('no fully blinded preregistration')
                expect(details).to_contain_text('not zero width')
                link = panel.get_by_role('link', name='Inspect declaration-history qualification')
            elif owner == 'indian-south-equatorial-countercurrent':
                expect(details).to_contain_text('northern pattern peaks at the retained data edge')
                link = panel.get_by_role('link', name='Inspect declared calculation')
            elif owner == 'norwegian-coastal':
                expect(panel).to_contain_text('8,784')
                for index_choice,choice in enumerate(scene['additional_figures'],1):
                    details.get_by_label('Analysis view').select_option(str(index_choice))
                    expect(details.locator('img')).to_have_attribute('src','../'+choice['file'])
                    expect(details.locator('img')).to_have_js_property('complete',True)
                    assert details.locator('img').evaluate('(img)=>img.naturalWidth>0')
                link=panel.get_by_role('link',name='Inspect complete-year acquisition')
            elif owner == 'aleutian':
                expect(panel).to_contain_text('132 profiles')
                expect(panel).to_contain_text('4,030 / 4,092')
                expect(panel).to_contain_text('16 northward latitude steps')
                expect(panel).to_contain_text('17 casts · 84 candidate profile pairs')
                details.get_by_label('Analysis view').select_option('1')
                expect(details.locator('img')).to_have_attribute('src','../figures/aleutian-p14n-1993-hydrography-correspondence.svg')
                expect(details.locator('img')).to_have_js_property('complete',True)
                assert details.locator('img').evaluate('(img)=>img.naturalWidth>0')
                details.get_by_label('Analysis view').select_option('2')
                expect(details.locator('img')).to_have_attribute('src','../figures/aleutian-p14n-1993-component-spans.svg')
                expect(details.locator('img')).to_have_js_property('complete',True)
                assert details.locator('img').evaluate('(img)=>img.naturalWidth>0')
                expect(panel).to_contain_text('North ≈100 km · south ≈80 km')
                link=panel.get_by_role('link',name='Inspect all CTD casts and quality codes')
            else:
                expect(panel).to_contain_text('7,992')
                details.get_by_label('Analysis view').select_option('1')
                expect(details.locator('img')).to_have_attribute('src','../'+scene['additional_figures'][0]['file'])
                expect(details.locator('img')).to_have_js_property('complete',True)
                assert details.locator('img').evaluate('(img)=>img.naturalWidth>0')
                link=panel.get_by_role('link',name='Inspect paired source vectors')
            source_query = json.loads(unquote(link.get_attribute('href').split('source-q=')[1]))
            link.click()
            page.wait_for_function('window.oswSourceQueryResult', timeout=90000)
            assert page.evaluate('oswSourceQueryResult') == native(source_query, index=index)
            if owner == registry['scenes'][0]['current_id']:
                check_source_documents(page, registry)
            page.goto(BASE + '/almanac/seasons.html?current=' + owner)
            page.wait_for_function('(id)=>window.oswSeasonPlan?.current_id===id', arg=owner, timeout=90000)
            panel = page.locator('#current-width-source-review .current-research-evidence')
            expect(panel).to_be_visible()
            page.set_viewport_size({'width':320, 'height':900}); page.emulate_media(reduced_motion='reduce')
            panel.locator('summary').focus(); page.keyboard.press('Enter')
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            panel.screenshot(path=str(output / (owner + '-mobile.png')))
            page.locator('#season-current').select_option('portugal')
            assert page.locator('.current-research-evidence').count() == 0
            page.set_viewport_size({'width':1280, 'height':1000})
            query = {'collection':'diagnostics', 'filters':[{'field':'id','op':'eq','value':scene['diagnostic_id']}], 'limit':100}
            page.goto(BASE + '/almanac/query.html?q=' + quote(json.dumps(query)))
            page.wait_for_function('window.oswLastQueryResult', timeout=90000)
            assert page.evaluate('oswLastQueryResult') == native(query)
            panel = page.locator('#query-chart-panels .current-research-evidence')
            expect(panel).to_be_visible()
            assert panel.locator('details').get_attribute('open') is not None
            panel.get_by_role('button', name='Inspect research evidence record').click()
            expect(page.locator('#query-detail')).to_contain_text(scene['diagnostic_id'])
            print('PASS card/seasons/query/source/inspector/mobile',owner,flush=True)
        query = {'collection':'diagnostics', 'limit':100}
        page.goto(BASE + '/almanac/query.html?q=' + quote(json.dumps(query)))
        page.wait_for_function('window.oswLastQueryResult', timeout=90000)
        assert page.evaluate('oswLastQueryResult') == native(query)
        assert page.locator('#query-chart-panels .current-research-evidence').count() == len(registry['scenes'])
        assert page.locator('#query-chart-panels .current-width-source-review').count() == 2
        assert not automatic_originals, automatic_originals
        page.close()
        for kind in cases:
            # Release each WASM heap with its page; retaining 22 full packet
            # instances in one renderer can exhaust memory before assertions run.
            page = browser.new_page()
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.route('**/research-evidence-guard.html', lambda route: route.fulfill(body='<title>Research evidence guard</title>', content_type='text/html'))
            page.goto(BASE + '/research-evidence-guard.html')
            path = folder / 'corrupt.json'
            bad=corrupt(packet,kind)
            with path.open('w',encoding='utf8') as stream:json.dump(bad,stream)
            del bad
            result = subprocess.run([str(CLI), str(path), '-'], input='{}', capture_output=True, text=True, encoding='utf8')
            assert result.returncode == 2 and not result.stdout, (kind, result.stderr)
            result = page.evaluate('''async data=>{
              const wasm=await fetch(data.wasm);if(!wasm.ok)throw new Error('Unserved WASM');
              const {instance}=await WebAssembly.instantiate(await wasm.arrayBuffer(),{}),e=instance.exports;
              const response=await fetch(data.fixture);if(!response.ok)throw new Error(`Corruption fixture HTTP ${response.status}`);
              const b=new Uint8Array(await response.arrayBuffer()),p=e.osw_alloc(b.length);
              try{new Uint8Array(e.memory.buffer,p,b.length).set(b);e.osw_load(p,b.length);
                return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));
              }finally{e.osw_dealloc(p,b.length);}
            }''', {'wasm':BASE+'/almanac/query-engine.wasm','fixture':BASE+'/' + path.relative_to(ROOT).as_posix()})
            assert result['ok'] is False, (kind, result)
            page.close()
            print('PASS native/WASM',kind,flush=True)
        assert not errors, errors
        browser.close()
    print(f'PASS: {len(registry['scenes'])} research cards/seasons/query/source/inspector/mobile; {len(registry['documents'])+1} indexed documents; mixed diagnostics; {len(cases)} native/WASM corruption rejections; no automatic originals')


if __name__ == '__main__':
    main()
