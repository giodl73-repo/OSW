"""Screen the declared Atlantic/coastal cases with the shared coarse method."""
import hashlib
import json
from shapely.geometry import LineString
from check_current_length_geography_v2 import ROOT,SOURCE,land,dense,world

ESTIMATES='research/current-length-reference-extents-v5.json'
OUTPUT='research/current-length-reference-extents-geography-v5.json'


def build():
    raw=(ROOT/ESTIMATES).read_bytes();document=json.loads(raw);_,periodic=land();records=[]
    for row in document['records']:
        checks=[]
        for number,case in enumerate(row['scenarios']):
            path=LineString([world(p) for p in dense(case['coordinates_lon_lat'])])
            contact=path.intersection(periodic)
            checks.append({'scenario_index':number,'coarse_land_clear':contact.is_empty,
                'contact_world_bounds':list(contact.bounds) if not contact.is_empty else None})
        records.append({'entity_id':row['entity_id'],'scenarios':len(checks),'coarse_land_clear':sum(x['coarse_land_clear'] for x in checks),
            'all_clear':all(x['coarse_land_clear'] for x in checks),'checks':checks})
    return {'schema':'osw.current-length-coarse-geography.v5','source_file':SOURCE,'source_sha256':hashlib.sha256((ROOT/SOURCE).read_bytes()).hexdigest(),
        'estimate_file_sha256':hashlib.sha256(raw).hexdigest(),'method':'Shared WGS84 densification at most10km and periodic coarse OSW display-land intersection. No physical-axis test.',
        'records':records,'fine_coast_checked':False,'physical_axis_verified':False}


if __name__=='__main__':
    value=build();(ROOT/OUTPUT).write_bytes((json.dumps(value,indent=2)+'\n').encode())
    print(json.dumps([{k:r[k] for k in ['entity_id','scenarios','coarse_land_clear','all_clear']} for r in value['records']]))
    if not all(r['all_clear'] for r in value['records']):raise SystemExit('Failed cases retained; no estimate admission')
