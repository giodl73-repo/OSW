"""Calendar distributions of diagnosed depths; never cross an averaged profile."""
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/source-data/agulhas-chandler-seasonal-depth-v1/candidate.json'
OUTPUT='research/agulhas-chandler-individual-depth-distributions-v1.json'


def quantile(values,p):
    if not values or not 0<=p<=1:raise ValueError('Invalid quantile request')
    ordered=sorted(values);position=(len(ordered)-1)*p;i=math.floor(position);j=math.ceil(position)
    return ordered[i]+(ordered[j]-ordered[i])*(position-i)


def summarize(records,month,threshold):
    rows=[r for r in records if r['calendar_month']==month]
    years=[int(r['date'][:4]) for r in rows]
    if len(rows)!=16 or sorted(years)!=list(range(2004,2020)):raise ValueError('Need exactly one matching month per source year')
    if any(int(r['date'][5:7])!=month for r in rows):raise ValueError('Calendar label/date mismatch')
    samples=[]
    for r in rows:
        diagnosis=r.get('derived',{}).get('crossings',{}).get(threshold,{'status':'unknown_no_supported_axis','depth_m':None})
        value=diagnosis['depth_m']
        if diagnosis['status']=='resolved_adjacent_level_crossing' and (not isinstance(value,(float,int)) or not math.isfinite(value) or value<0):raise ValueError('Invalid resolved depth')
        samples.append({'year':int(r['date'][:4]),'diagnosis':diagnosis['status'],'depth_m':value,'axis_longitude':r.get('longitude'),'axis_latitude':r.get('latitude')})
    resolved=[r['depth_m'] for r in samples if r['diagnosis']=='resolved_adjacent_level_crossing']
    full=len(resolved)==16
    statistics=None
    if full:
        statistics={'median_m':quantile(resolved,.5),'arithmetic_mean_m':sum(resolved)/16,
                    'minimum_m':min(resolved),'maximum_m':max(resolved),'q25_m':quantile(resolved,.25),'q75_m':quantile(resolved,.75)}
    return {'calendar_month':month,'poleward_velocity_threshold_m_s':float(threshold),
            'status':'complete16_year_individual_depth_distribution' if full else 'unknown_incomplete16_year_crossing_support',
            'source_years':[2004,2019],'source_year_count':16,'resolved_year_count':len(resolved),
            'diagnosis_counts':dict(Counter(r['diagnosis'] for r in samples)),'year_samples':samples,'statistics':statistics,
            'statistics_are_confidence_bounds':False,'physical_depth_uncertainty_m':None,'volume_eligible':False}


def build(root=ROOT):
    source=json.loads((root/SOURCE).read_bytes())
    if source['entity_id']!='current:agulhas':raise ValueError('Wrong current identity')
    records=[summarize(source['records'],month,threshold) for month in range(1,13) for threshold in ['0.0','0.05','0.1']]
    return {'schema':'osw.agulhas-individual-depth-distributions.v1','status':'COMPLETE_SUPPORT_STATISTICS_SEPARATE_FROM_MEAN_PROFILE_CROSSINGS',
            'entity_id':'current:agulhas','input_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in [SOURCE,'analysis/build_agulhas_individual_depth_distributions_v1.py']},
            'records':records,'quantile_method':'linear_order_statistic_at_index_n_minus1_times_p',
            'interpretation':'Statistics of16 reconstructed year-specific diagnosed depths per calendar month. Incomplete zero/5cm/s crossing groups retain samples and statuses but no complete-case summary. Interannual sample spread is not physical uncertainty, confidence bounds, annual extrema or the crossing of a calendar-mean velocity profile.',
            'new_independent_observations':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0,'full_goal_complete':False}


if __name__=='__main__':
    output=ROOT/'agulhas-individual-depth-distributions-v1';output.mkdir(exist_ok=True)
    d=build();(output/'distribution.json').write_bytes((json.dumps(d,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode('utf8'))
    print(json.dumps([{'month':r['calendar_month'],'statistics':r['statistics']} for r in d['records'] if r['poleward_velocity_threshold_m_s']==.1]))
