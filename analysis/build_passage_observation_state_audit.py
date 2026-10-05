"""Independent point-location audit; never infer passage/current containment."""
import hashlib
import json
from pathlib import Path
from shapely.geometry import Point,shape
from shapely.affinity import translate

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'research/indonesian-throughflow-observation-state-audit.json'

def build():
    bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    states=sorted([{'code':r['code'],'geometry':r['display_geometry']} for r in bundle['collections']['states'] if 'display_geometry' in r],key=lambda r:r['code'])
    polygons={r['code']:shape(r['geometry']) for r in states}
    rows=[]
    for record in bundle['collections']['passage_samples']:
        for index,site in enumerate(record['moorings']):
            point=Point(site['coordinates_lon_lat']);matches=[]
            for code,polygon in polygons.items():
                for shift in [-360,0,360]:
                    candidate=translate(point,xoff=shift)
                    if polygon.covers(candidate):
                        matches.append({'state_code':code,'boundary_touch_only':polygon.touches(candidate)})
                        break
            rows.append({'record_id':record['id'],'feature_index':index,'mooring_label':site['label'],
                         'coordinates_lon_lat':site['coordinates_lon_lat'],'deployment_start':site['deployment_start'],
                         'deployment_end':site['deployment_end'],'matches':matches,
                         'relation_kind':'published_first_deployment_point_locator_covered_by_display_state'})
    return {'schema':'osw.passage-observation-state-audit.v1','entity_id':'current:indonesian-throughflow',
        'source_file':'research/indonesian-throughflow-network-input.json',
        'source_sha256':hashlib.sha256((ROOT/'research/indonesian-throughflow-network-input.json').read_bytes()).hexdigest(),
        'state_geometry_sha256':hashlib.sha256(json.dumps(states,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        'state_count':len(states),'observation_site_count':len(rows),'rows':rows,
        'canonical_admission':False,'whole_current_containment':None,
        'method':'Shapely planar covers/touches on existing geographic OSW display polygons, retaining longitude shifts and boundary contact.',
        'scope':'Published first-deployment sites, not persistent positions throughout deployment, exact redeployment locations, current axes, passage footprints or whole-current containment. Coarse display-state geometry is not an independently validated physical boundary. No-match is not absence of the current.',
        'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}

if __name__=='__main__':
    document=build();OUTPUT.write_text(json.dumps(document,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Audited',document['observation_site_count'],'sites against',document['state_count'],'states')
