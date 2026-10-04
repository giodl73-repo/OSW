"""Independent Shapely oracle for Rust topology on actual OSW source shapes."""
import json
import subprocess
from pathlib import Path
from shapely.geometry import shape
from shapely.ops import transform
from shapely.affinity import translate
from build_cartographic_current_state_join import load_states
from build_rust_query_bundle import build

ROOT=Path(__file__).resolve().parents[1]


def unwrap_geometry(geometry):
    def line(coordinates):
        result=[]
        for lon,lat in coordinates:
            if result:lon+=360*round((result[-1][0]-lon)/360)
            result.append([lon,lat])
        return result
    g=dict(geometry)
    if g['type']=='LineString':g['coordinates']=line(g['coordinates'])
    elif g['type']=='Polygon':
        rings=[line(r) for r in g['coordinates']]
        for ring in rings[1:]:
            shift=360*round((rings[0][0][0]-ring[0][0])/360)
            for p in ring:p[0]+=shift
        g['coordinates']=rings
    return shape(g)


def expected(bundle,state,code,mode,include_excluded=False):
    ids=set()
    for row in bundle['collections']['objects']:
        for feature in row['map_features']:
            point=feature['geometry']['type']=='Point'
            area=feature['geometry']['type'] in ['Polygon','MultiPolygon']
            gateway=feature['role']=='shared_regional_gateway'
            if (mode=='locator' and (not point or gateway) or mode=='gateway' and (not point or not gateway)
                    or mode=='within' and not area or mode=='intersects' and point):continue
            if not include_excluded and any(e['state_code']==code for e in feature.get('state_semantic_exclusions',[])):continue
            geo=unwrap_geometry(feature.get('spatial_geometry',feature['geometry']))
            display=transform(lambda x,y,z=None:(60+(x+180)*1480/360,90+(90-y)*740/180),geo)
            for shift in [-1480,0,1480]:
                shifted=translate(display,xoff=shift)
                if (state.intersects(shifted) if mode=='intersects' else state.covers(shifted)):
                    ids.add(row['id']);break
    return ids


def native(query):
    result=subprocess.run([str(ROOT/'rust/osw-query/target/debug/osw-query-cli.exe'),str(ROOT/'almanac/query-data.json'),'-'],
                          input=json.dumps(query),capture_output=True,text=True,encoding='utf-8')
    return json.loads(result.stdout)


def main():
    bundle=json.loads((ROOT/'almanac/query-data.json').read_text(encoding='utf-8'))
    assert build()==bundle, 'Stale or nondeterministic snapshot'
    states=load_states()
    count=0
    for code in ['NADR','KURO','CAMR','NPSW','MONS']:
        for mode in ['intersects','within','locator','gateway']:
            query={'collection':'objects','spatial':{'state_code':code,'predicate':mode},'limit':500}
            result=native(query)
            assert result['ok'],result
            actual={r['id'] for r in result['rows']}
            wanted=expected(bundle,states[code],code,mode)
            assert actual==wanted,(code,mode,'extra',actual-wanted,'missing',wanted-actual)
            assert all(r['spatial_matches'] for r in result['rows'])
            assert result['map_scene']['selected_state_code']==code
            assert result['map_scene']['state_features']
            count+=1
    for spatial in [{'state_code':'fake','predicate':'intersects'},{'state_code':'KURO','predicate':'fake'},{'state_code':'','predicate':'intersects'}]:
        assert not native({'spatial':spatial})['ok']
    assert not native({'collection':'claims','spatial':{'state_code':'KURO','predicate':'intersects'}})['ok']
    for include in [False,True]:
        query={'spatial':{'state_code':'MEDI','predicate':'intersects','include_excluded':include},'limit':500}
        result=native(query)
        assert result['ok'],result
        assert {r['id'] for r in result['rows']}==expected(bundle,states['MEDI'],'MEDI','intersects',include)
        assert ('current:black-sea-rim' in {r['id'] for r in result['rows']})==include
    print(f'PASS {count} actual-state spatial queries agree with original SVG/Shapely oracle; invalid spatial queries rejected')


if __name__=='__main__':main()
