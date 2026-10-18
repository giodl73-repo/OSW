"""Offline statistical classification experiment; never a physical width builder.

python analysis/build_indian_secc_eof_feasibility.py
The retained source originals and frozen preflight are versioned. No downloads.
"""
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from itertools import combinations, permutations
import csv,hashlib,io,json,math
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/source-data/oscar-indian-eof-1995-2016'
RESULT=ROOT/'research/indian-secc-eof-classification-feasibility.json'
PREFLIGHT_SHA='b9c19d3c1abd87bf9b1c03910d383905a07de73ba2a957f597f83ab1224587a9'
ACQUISITION_SHA='dc684f969378f2ada64a6174fa23810ade8bbe8db2f86ea77e849384b7d95fae'
METADATA_SHA='8c1f41c4e7a0f91492482345e7038c47e461c46c56852dbe57f217e40b9ec2ba'


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(path,longitude,low,high):
    reader=csv.reader(io.StringIO(path.read_bytes().decode('utf8')))
    assert next(reader)==['time','depth','latitude','longitude','u','v']
    assert next(reader)==['UTC','m','degrees_north','degrees_east','m s-1','m s-1']
    frames={}
    for row in reader:
        assert len(row)==6
        stamp=datetime.fromisoformat(row[0].replace('Z','+00:00'))
        depth,lat,lon,u,v=map(float,row[1:])
        assert stamp.utcoffset().total_seconds()==0
        assert depth==15 and abs(lon-longitude)<1e-8 and low-1e-8<=lat<=high+1e-8
        index=round(lat*3)
        assert abs(index/3-lat)<1e-8 and not math.isinf(u) and not math.isinf(v)
        cells=frames.setdefault(row[0],{})
        assert index not in cells
        cells[index]=(u if math.isfinite(u) else None,v if math.isfinite(v) else None)
    expected=list(range(round(low*3),round(high*3)+1))
    assert frames and all(sorted(cells)==expected for cells in frames.values())
    return frames


def covariance_eof(matrix):
    matrix=np.asarray(matrix,dtype=float)
    if matrix.ndim!=2 or matrix.shape[0]<2 or matrix.shape[1]<1 or not np.isfinite(matrix).all():
        raise ValueError('EOF requires a complete finite monthly matrix')
    mean=matrix.mean(axis=0);anomaly=matrix-mean
    left,singular,spatial=np.linalg.svd(anomaly,full_matrices=False)
    total=float(np.sum(singular**2))
    if total<=np.finfo(float).eps:raise ValueError('No variability available for EOF decomposition')
    pc=left*singular
    for mode in range(len(singular)):
        sign=1 if spatial[mode,np.argmax(abs(spatial[mode]))]>=0 else -1
        spatial[mode]*=sign;pc[:,mode]*=sign
    assert np.allclose(pc@spatial+mean,matrix,atol=1e-12)
    return mean,spatial,pc,singular**2/total


def retained_columns(matrix):
    return np.isfinite(matrix).all(axis=0)


def context_energy(latitude,loading,bands):
    # Point-membership convention only: shared endpoints belong to WJ.
    # These are paper classification regions, not physical current edges.
    masks={
        'WJ':(latitude>=bands['WJ'][0])&(latitude<=bands['WJ'][1]),
        'MC':(latitude>bands['MC'][0])&(latitude<=bands['MC'][1]),
        'SECC':(latitude>=bands['SECC'][0])&(latitude<bands['SECC'][1]),
    }
    assert np.max(np.sum(np.stack(list(masks.values())),axis=0))<=1
    return {name:float(np.sum(loading[mask]**2)) for name,mask in masks.items()}


def spectral_fraction(pc,cycles_per_year):
    pc=pc-pc.mean()
    time=np.arange(len(pc));omega=2*np.pi*cycles_per_year/12
    design=np.column_stack([np.cos(omega*time),np.sin(omega*time)])
    fitted=design@np.linalg.lstsq(design,pc,rcond=None)[0]
    return float(np.sum(fitted**2)/np.sum(pc**2)) if np.sum(pc**2)>0 else None


def compare_modes(a,b):
    """Match first three source modes to all five target modes on common support.

    Absolute normalized inner products compare loadings, without spatial
    demeaning. PC correlations remain signed after loading-sign alignment.
    Assignment maximizes their total; no acceptance cutoff or identity inferred.
    """
    ai={round(x*3):i for i,x in enumerate(a['latitude_degrees'])}
    bi={round(x*3):i for i,x in enumerate(b['latitude_degrees'])}
    common=sorted(ai.keys()&bi.keys())
    if len(common)<3:raise ValueError('Insufficient common spatial support')
    left=np.array([m['spatial_loading'] for m in a['modes'][:3]])[:,[ai[x] for x in common]]
    right=np.array([m['spatial_loading'] for m in b['modes']])[:,[bi[x] for x in common]]
    if left.shape[0]!=3 or right.shape[0]<3 or not np.isfinite(left).all() or not np.isfinite(right).all():
        raise ValueError('Invalid mode comparison')
    ln=np.linalg.norm(left,axis=1);rn=np.linalg.norm(right,axis=1)
    if np.any(ln==0) or np.any(rn==0):raise ValueError('Zero loading on common support')
    scores=(left/ln[:,None])@(right/rn[:,None]).T
    assignment=max(permutations(range(len(right)),3),key=lambda p:sum(abs(scores[i,j]) for i,j in enumerate(p)))
    matched=[]
    for i,j in enumerate(assignment):
        sign=1 if scores[i,j]>=0 else -1
        ap=np.array(a['modes'][i]['principal_component_m_s'])
        bp=np.array(b['modes'][j]['principal_component_m_s'])*sign
        if ap.shape!=bp.shape or ap.ndim!=1 or not np.isfinite(ap).all() or not np.isfinite(bp).all() or np.std(ap)==0 or np.std(bp)==0:
            raise ValueError('Invalid PC comparison')
        matched.append({'source_rank':i+1,'target_rank':j+1,
            'absolute_loading_cosine':float(np.clip(abs(scores[i,j]),0,1)),
            'loading_aligned_pc_correlation':float(np.corrcoef(ap,bp)[0,1])})
    if np.linalg.matrix_rank(left)<3 or np.linalg.matrix_rank(right[:3])<3:
        raise ValueError('Degenerate first-three subspace on common support')
    ql=np.linalg.qr(left.T)[0];qr=np.linalg.qr(right[:3].T)[0]
    singular=np.linalg.svd(ql.T@qr,compute_uv=False)
    return {'source':{'longitude':a['longitude'],'domain':a['domain']},
        'target':{'longitude':b['longitude'],'domain':b['domain']},
        'common_latitude_degrees':[x/3 for x in common],
        'matched_modes':matched,
        'first_three_subspace_principal_angles_degrees':np.degrees(np.arccos(np.clip(singular,0,1))).tolist()}


def build():
    if digest(OUT/'preflight.json')!=PREFLIGHT_SHA or digest(OUT/'acquisition.json')!=ACQUISITION_SHA:
        raise ValueError('Changed frozen preflight or original acquisition receipt')
    c=json.loads((OUT/'preflight.json').read_bytes())
    receipt=json.loads((OUT/'acquisition.json').read_bytes())
    assert digest(OUT/'preflight.json')==receipt['preflight_sha256']
    metadata=ROOT/'research/source-data/oscar-indian-secc-1995-2016/metadata.json'
    if digest(metadata)!=METADATA_SHA:raise ValueError('Changed original product metadata')
    attrs={(r[1],r[2]):r[4] for r in json.loads(metadata.read_bytes())['table']['rows'] if r[0]=='attribute'}
    assert attrs[('NC_GLOBAL','version')]=='2017.0' and attrs[('u','units')]=='m s-1' and attrs[('v','units')]=='m s-1'
    months=[f'{y}-{m:02d}' for y in range(1995,2017) for m in range(1,13)]
    datasets=[];fits=[]
    for index,longitude in enumerate(c['native_longitudes']):
        source=c['existing_southern_files'][index];south=ROOT/source['file'];north=OUT/f'north-{index}.csv'
        assert digest(south)==source['sha256'] and digest(north)==receipt['files'][north.name]['sha256']
        s=parse(south,longitude,-12,0);n=parse(north,longitude,0,6)
        assert s.keys()==n.keys()
        assert all(s[stamp][0]==n[stamp][0] for stamp in s),'Changed equatorial overlap'
        stamps=sorted(s);gaps=[]
        for a,b in zip(stamps,stamps[1:]):
            days=(datetime.fromisoformat(b.replace('Z','+00:00'))-datetime.fromisoformat(a.replace('Z','+00:00'))).days
            if days not in [5,6]:gaps.append({'start':a,'end':b,'days':days})
        cells=defaultdict(list);excluded=[]
        for stamp in stamps:
            date=datetime.fromisoformat(stamp.replace('Z','+00:00'))
            if not 1995<=date.year<=2016:excluded.append(stamp);continue
            joined={**s[stamp],**n[stamp]}
            for latitude,pair in joined.items():
                if all(value is not None for value in pair):cells[(stamp[:7],latitude)].append(pair)
        latitudes=list(range(-36,19));u=np.full((264,55),np.nan);v=u.copy();counts=np.zeros((264,55),dtype=int)
        for ti,month in enumerate(months):
            for li,latitude in enumerate(latitudes):
                pairs=cells[(month,latitude)];counts[ti,li]=len(pairs)
                if len(pairs)>=5:u[ti,li],v[ti,li]=np.mean(pairs,axis=0)
        datasets.append({'longitude':longitude,'source_frames':len(stamps),'excluded_times':excluded,'time_gaps':gaps,
            'overlapping_equator_rows_equal':len(stamps),'months':months,'latitude_degrees':[x/3 for x in latitudes],
            'monthly_pair_counts':counts.tolist(),
            'monthly_fields_retained_in_output':False,
            'monthly_fields_reconstructed_from_pinned_originals':True})
        for domain in [c['primary_latitude_domain'],*c['predeclared_domain_sensitivities']]:
            selection=np.array([domain[0]-1e-8<=lat/3<=domain[1]+1e-8 for lat in latitudes])
            available=retained_columns(u)&selection
            latitude=np.array(latitudes,dtype=float)[available]/3
            mean,spatial,pcs,variance=covariance_eof(u[:,available])
            modes=[]
            for mode in range(min(5,len(variance))):
                loading=spatial[mode];pc=pcs[:,mode]
                band_energy=context_energy(latitude,loading,c['context_bands'])
                modes.append({'rank':mode+1,'variance_fraction':float(variance[mode]),'spatial_loading':loading.tolist(),
                    'principal_component_m_s':pc.tolist(),'peak_absolute_loading_latitude':float(latitude[np.argmax(abs(loading))]),
                    'absolute_peak_at_retained_domain_edge':int(np.argmax(abs(loading))) in [0,len(latitude)-1],
                    'classification_band_energy_fractions':band_energy,'annual_harmonic_fraction':spectral_fraction(pc,1),
                    'semiannual_harmonic_fraction':spectral_fraction(pc,2),
                    'monthly_pc_climatology_m_s':[float(np.mean(pc[np.arange(264)%12==month])) for month in range(12)],
                    'named_current_identity_assigned':False})
            fits.append({'longitude':longitude,'domain':domain,'latitude_degrees':latitude.tolist(),
                'dropped_latitudes':[lat/3 for li,lat in enumerate(latitudes) if selection[li] and not available[li]],
                'temporal_mean_profile_m_s':mean.tolist(),'modes':modes,'first_three_variance_fraction':float(sum(variance[:3]))})
    result={'schema':'osw.indian-current-eof-classification-feasibility.v1','status':'feasibility_only_not_current_width_admission',
        'preflight_sha256':digest(OUT/'preflight.json'),'acquisition_sha256':digest(OUT/'acquisition.json'),
        'datasets':datasets,'fits':fits,'current_association_verified':False,'new_width_record_admitted':False,
        'whole_current_width_km':None,'annual_width_range_km':None,
        'width_rank_eligible':False,'annual_extrema_eligible':False,'seasonal_playback_eligible':False,
        'source_doi':c['source_doi'],
        'source_percentages_are_fit_targets':False,
        'comparison_method':'Exploratory follow-up after inspecting the primary fits: all15 fit pairs, common-support normalized loading inner products, maximum-sum one-to-one first3-to-first5 assignment; signed PC correlations after loading-sign alignment; first3 subspace angles. No cutoff or current identity admission.',
        'mode_comparisons':[compare_modes(a,b) for a,b in combinations(fits,2)],
        'incomplete_support_note':'Five northern latitudes fail the264-month completeness rule. The northern mode peaks at the retained support edge; no missing northern edge or full source-domain shape is inferred.',
        'context_band_membership_rule':'Implementation clarification: WJ includes both endpoints; MC excludes its lower endpoint; SECC excludes its upper endpoint. Shared point membership is never counted twice. These are classification contexts, not current boundaries.'}
    return result


def main():
    result=build()
    RESULT.write_bytes((json.dumps(result,indent=2,allow_nan=False)+'\n').encode())
    fits=result['fits']
    for fit in fits:
        print(json.dumps({'longitude':fit['longitude'],'domain':fit['domain'],'dropped':fit['dropped_latitudes'],
            'variance_percent':[round(100*m['variance_fraction'],2) for m in fit['modes'][:3]],
            'mode_peaks':[m['peak_absolute_loading_latitude'] for m in fit['modes'][:3]],
            'annual_fraction':[round(m['annual_harmonic_fraction'],3) for m in fit['modes'][:3]],
            'semiannual_fraction':[round(m['semiannual_harmonic_fraction'],3) for m in fit['modes'][:3]]}),flush=True)


if __name__=='__main__':main()
