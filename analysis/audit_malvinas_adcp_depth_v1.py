"""Bounded cloud audit of native profiles; no current-axis or bottom inference."""
import csv
import hashlib
import io
import json
import math
from collections import defaultdict
from pathlib import Path
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/malvinas-adcp-depth-audit-operator-v1.json'


def number(text):
    try:value=float(text)
    except (ValueError,TypeError):return None
    return value if math.isfinite(value) else None


def parse(raw):
    text=raw.decode('utf-8-sig')
    if '*/' not in text:raise ValueError('Missing PANGAEA metadata terminator')
    body=text.split('*/',1)[1].lstrip('\r\n')
    reader=csv.DictReader(io.StringIO(body),delimiter='\t')
    headers=reader.fieldnames
    names={}
    for key,prefix in [('date','Date/Time'),('id','ID'),('lat','Latitude'),('lon','Longitude'),('depth','Depth water [m]'),('v','Cur vel V [cm/s]'),('quality','Quality [%]')]:
        matches=[h for h in headers if h==prefix or h.startswith(prefix+' (')]
        if len(matches)!=1:raise ValueError('Missing or ambiguous native column: '+prefix)
        names[key]=matches[0]
    groups=defaultdict(list);row_count=0
    for row in reader:
        row_count+=1
        if None in row:raise ValueError('Malformed source row')
        d={key:row[names[key]] for key in names}
        for key in ['lat','lon','depth','v','quality']:d[key]=number(d[key])
        if not d['date'] or not d['id'] or any(d[k] is None for k in ['lat','lon','depth']):
            raise ValueError('Missing profile geocode')
        if not(-90<=d['lat']<=90 and -180<=d['lon']<=180 and d['depth']>=0):raise ValueError('Invalid geocode')
        if d['quality'] is not None and not 0<=d['quality']<=100:raise ValueError('Invalid PG quality')
        groups[(d['date'],d['id'])].append(d)
    return names,groups,row_count


def summarize_profile(rows,threshold):
    rows=sorted(rows,key=lambda r:r['depth'])
    if len({r['depth'] for r in rows})!=len(rows):raise ValueError('Duplicate depths in one ensemble')
    if len({(r['lat'],r['lon']) for r in rows})!=1:raise ValueError('Ensemble coordinates vary by depth')
    valid=[r for r in rows if r['v'] is not None and r['quality'] is not None and r['quality']>=threshold]
    positive=[r for r in valid if r['v']>0]
    peak=max((r['v'] for r in positive),default=None)
    peaks=[r['depth'] for r in positive if r['v']==peak] if peak is not None else []
    valid_depths=[r['depth'] for r in valid]
    return {'quality_pg_min_percent':threshold,'native_levels':len(rows),'valid_velocity_levels':len(valid),
            'valid_depth_domain_m':[min(valid_depths),max(valid_depths)] if valid else None,
            'positive_northward_velocity_max_cm_s':peak,'sampled_maximum_depths_m':peaks,
            'maximum_at_shallowest_valid_level':bool(peaks and min(peaks)==min(valid_depths)),
            'maximum_at_deepest_valid_level':bool(peaks and max(peaks)==max(valid_depths)),
            'valid_sample_depth_gaps_m':[round(b-a,6) for a,b in zip(valid_depths,valid_depths[1:])],
            'deepest_valid_northward_sample_m':max((r['depth'] for r in positive),default=None),
            'flow_boundary_depth_m':None,'physical_thickness_m':None}


def audit(raw,operator):
    names,groups,count=parse(raw)
    profiles=[]
    for (date,ensemble),rows in sorted(groups.items()):
        profiles.append({'datetime':date,'source_ensemble_id':ensemble,'longitude':rows[0]['lon'],'latitude':rows[0]['lat'],
                         'quality_scenarios':[summarize_profile(rows,t) for t in operator['quality_pg_scenarios_percent']]})
    depths=[r['depth'] for group in groups.values() for r in group]
    return {'schema':'osw.malvinas-adcp-depth-audit.v1','status':'NATIVE_PROFILE_DEPTH_DIAGNOSTICS_NOT_BRANCH_CORE_MEASUREMENTS',
            'source_url':operator['data_url'],'source_doi':operator['dataset_doi'],'license':'CC-BY-4.0',
            'source_citation':'Frey, Gladyshev, Morozov, Tarakanov, Krechik and Fofanov(2020), Shipborne Acoustic Current Profiler measurements on2020-01-12(cruise AMK79), PANGAEA, doi:10.1594/PANGAEA.925245.',
            'raw_bytes':len(raw),'raw_sha256':hashlib.sha256(raw).hexdigest(),'resolved_source_columns':names,
            'native_rows':count,'ensembles':len(profiles),'native_depth_domain_m':[min(depths),max(depths)],
            'profiles':profiles,'branch_assignment_performed':False,'paper_processing_reproduced':False,
            'tidal_correction_status':'archive_processing_not_independently_verified_no_new_tidal_correction',
            'horizontal_25km_smoothing_applied':False,'physical_boundary_inference_performed':False,
            'canonical_depth_references_added':0,'volume_estimates':0,'full_goal_complete':False}


def main():
    operator=json.loads((ROOT/OPERATOR).read_bytes())
    request=Request(operator['data_url'],headers={'User-Agent':'OSW-source-depth-audit/1.0'})
    with urlopen(request,timeout=50) as response:
        raw=response.read(operator['maximum_download_bytes']+1)
    if len(raw)>operator['maximum_download_bytes']:raise ValueError('Source exceeds bounded download')
    result=audit(raw,operator)
    result['input_sha256']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [OPERATOR,'analysis/audit_malvinas_adcp_depth_v1.py']}
    output=ROOT/'malvinas-adcp-depth-audit-v1';output.mkdir(exist_ok=True)
    (output/'audit.json').write_bytes((json.dumps(result,indent=2,ensure_ascii=False)+'\n').encode('utf8'))
    print(json.dumps({k:result[k] for k in ['native_rows','ensembles','native_depth_domain_m','raw_bytes','canonical_depth_references_added']}))


if __name__=='__main__':main()
