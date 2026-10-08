"""Every atlas source geometry uses native/WASM cartography with scoped omissions."""
import json,os,re,subprocess
from playwright.sync_api import sync_playwright,expect
from test_rust_query_browser import ROOT,CLI
BASE='http://127.0.0.1:8788/almanac/reference-routes.html#route-atlas'

def native(request):
    result=subprocess.run([str(CLI),'--cartography'],input=json.dumps(request),capture_output=True,text=True,encoding='utf-8')
    assert result.returncode==0,result.stderr
    return json.loads(result.stdout)

def main():
    snapshot=json.loads((ROOT/'research/ocean-motion-dashboard.json').read_bytes())
    catalog=json.loads((ROOT/'research/ocean-current-reference-path-candidates.json').read_bytes())
    requests=[{'op':'fit','coordinates':[]}]
    for row in snapshot['entries']:
        for feature in row['map_features']:
            geometry=feature['geometry'];coords=geometry['coordinates'];kind=geometry['type']
            if kind=='Point':requests.append({'op':'project','coordinates':coords});points=[coords]
            elif kind=='LineString':requests.append({'op':'path','coordinates':coords});points=coords
            elif kind=='Polygon':
                requests.extend({'op':'path','coordinates':ring,'closed':True} for ring in coords);points=[p for ring in coords for p in ring]
            else:raise AssertionError(kind)
            requests.append({'op':'fit','coordinates':points})
    for row in catalog['candidates']:
        coords=json.loads((ROOT/row['candidate_file']).read_bytes())['coordinates_lon_lat']
        requests.extend([{'op':'path','coordinates':coords},{'op':'fit','coordinates':coords}])
    requests=list({json.dumps(r,sort_keys=True):r for r in requests}.values())
    expected=[native(r) for r in requests]
    for request,result in zip(requests,expected):
        coordinates=request['coordinates']
        if request['op']=='project':
            lon,lat=coordinates;assert abs(result['point'][0]-(60+(lon+180)/360*1480))<1e-9
            assert abs(result['point'][1]-(90+(90-lat)/180*740))<1e-9
        elif request['op']=='path':
            points=[tuple(map(float,p)) for p in re.findall(r'[ML]\s*([^,\s]+),([^\sZ]+)',result['d'])]
            assert len(points)==len(coordinates)
            for (x,y),(lon,lat) in zip(points,coordinates):
                assert abs(x-(60+(lon+180)/360*1480))<1e-9 and abs(y-(90+(90-lat)/180*740))<1e-9
            assert result['d'].count('M')==1+sum(abs(a[0]-b[0])>180 for a,b in zip(coordinates,coordinates[1:]))
        elif coordinates:
            xs=[60+(p[0]+180)/360*1480 for p in coordinates];ys=[90+(90-p[1])/180*740 for p in coordinates]
            width=min(1480,max(160 if len(coordinates)==1 else 16,(max(xs)-min(xs))*1.4,(max(ys)-min(ys))*2.8))
            oracle=[max(60,min(1540-width,(min(xs)+max(xs))/2-width/2)),max(90,min(830-width/2,(min(ys)+max(ys))/2-width/4)),width,width/2]
            assert all(abs(a-b)<1e-9 for a,b in zip(result['view_box'],oracle))
    invalid=[{'op':'project','coordinates':[0,91]},{'op':'path','closed':True,'coordinates':[[179,0],[-179,0],[-179,1],[179,0]]},
             {'op':'fit','coordinates':[[181,0]]},{'op':'unknown','coordinates':[]},{'op':'fit','coordinates':[],'extra':True}]
    for request in invalid:
        result=subprocess.run([str(CLI),'--cartography'],input=json.dumps(request),capture_output=True,text=True)
        assert result.returncode==2 and not result.stdout and result.stderr
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(BASE);expect(page.locator('#route-atlas-select option')).to_have_count(101,timeout=90000)
        actual=page.evaluate('(requests)=>requests.map(r=>window.oswCartography(r))',requests)
        assert actual==expected
        failures=page.evaluate('(requests)=>requests.map(r=>{try{window.oswCartography(r);return null}catch(e){return e.message}})',invalid)
        assert all(failures)
        assert not errors,errors;browser.close()
    print(f'PASS: {len(requests)} unique source geometry requests covering 63 reports and all atlas features; independent projection/fit, native/WASM equality, seam breaks and five invalid requests')

if __name__=='__main__':main()
