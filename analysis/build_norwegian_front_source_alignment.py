"""Audit retained glider coordinates; never diagnose a current width or footprint."""
import argparse,hashlib,json
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
import xarray as xr
from pyproj import Geod

ROOT=Path(__file__).resolve().parents[1]
FILES={'final_sg560_MR1.nc':'ea0844e97190edffda67ef4eaf2869efcaf3d48ce7f8f4eab627eec23867c2d5','final_sg562_MR2.nc':'48c8d8c46f42a61fe9c647ba75c6d484abee698afb6b6f407905dcc4443e49a8'}
GEOD=Geod(ellps='WGS84')

def build(directory):
    missions=[]
    for name,pin in FILES.items():
        path=directory/name
        if hashlib.sha256(path.read_bytes()).hexdigest()!=pin:raise ValueError('Changed original glider source: '+name)
        with xr.open_dataset(path,decode_times=False) as d:
            for k in ['TIME','DAC_TIME']:
                if d[k].attrs['units']!='seconds since 1970-01-01T00:00:00Z':raise ValueError('Changed source time units')
            for k,standard in [('DAC_U','eastward_sea_water_velocity'),('DAC_V','northward_sea_water_velocity')]:
                if d[k].attrs['standard_name']!=standard or d[k].attrs['units']!='m/s':raise ValueError('Changed source velocity identity')
            t,x,y=[d[k].values.astype(float) for k in ['TIME','LONGITUDE','LATITUDE']]
            dt,dx,dy,u,v=[d[k].values.astype(float) for k in ['DAC_TIME','DAC_LONGITUDE','DAC_LATITUDE','DAC_U','DAC_V']]
            if not (np.all(np.isfinite(t)) and np.all(np.isfinite(x)) and np.all(np.isfinite(y)) and np.all(np.diff(t)>0) and np.all(np.abs(y)<=90) and np.all(np.abs(x)<=180)):raise ValueError('Invalid profile chronology or coordinates')
            inside=np.isfinite(dt)&np.isfinite(dx)&np.isfinite(dy)&(dt>=t[0])&(dt<=t[-1])
            offsets=GEOD.inv(dx[inside],dy[inside],np.interp(dt[inside],t,x),np.interp(dt[inside],t,y))[2]/1000
            rate=GEOD.inv(x[:-1],y[:-1],x[1:],y[1:])[2]/np.diff(t)
            positions=[{'source_epoch_seconds':float(a),'time':datetime.fromtimestamp(float(a),timezone.utc).isoformat(),'longitude':float(b),'latitude':float(c)} for a,b,c in zip(t,x,y)]
            velocity=[{'source_epoch_seconds':float(a),'time':datetime.fromtimestamp(float(a),timezone.utc).isoformat(),'longitude':float(b) if np.isfinite(b) else None,'latitude':float(c) if np.isfinite(c) else None,'source_DAC_U_m_s':float(e) if np.isfinite(e) else None,'source_DAC_V_m_s':float(f) if np.isfinite(f) else None,'vector_magnitude_m_s':float(np.hypot(e,f)) if np.isfinite(e) and np.isfinite(f) else None} for a,b,c,e,f in zip(dt,dx,dy,u,v)]
            comparisons=[{'source_epoch_seconds':float(a),'time':datetime.fromtimestamp(float(a),timezone.utc).isoformat(),'offset_km':float(b)} for a,b in zip(dt[inside],offsets)]
            missions.append({'file':name,'source_url':'https://ftp.nmdc.no/nmdc/UIB/PROVOLO/Glider/'+name,'source_sha256':pin,'source_bytes':path.stat().st_size,'source_history':d.attrs['history'],'source_creation_time':d.attrs['creation_time'],'title':d.attrs['title'],'profile_count':len(t),'DAC_count':len(dt),'complete_DAC_vectors':int(sum(np.isfinite(u)&np.isfinite(v))),'overlapping_DAC_coordinates':int(sum(inside)),'maximum_alignment_offset_km':float(np.max(offsets)),'median_alignment_offset_km':float(np.median(offsets)),'maximum_glider_position_displacement_rate_m_s':float(np.max(rate)),'variable_metadata':{k:dict(d[k].attrs) for k in ['DAC_U','DAC_V']},'profile_positions':positions,'DAC_records':velocity,'coordinate_comparisons':comparisons})
    return {'schema':'osw.glider-source-alignment-audit.v1','status':'source_alignment_preflight_not_current_measurement_admission','proposed_current_id':'norwegian-atlantic-front','data_doi':'10.21335/NMDC-980686647','attribution':'Anthony Bosse and Ilker Fer (2019), Seaglider missions in the Norwegian Sea during the PROVOLO project, University of Bergen / NMDC.','license':'CC BY 4.0','paper_doi':'10.1029/2019GL084723','paper_correction_date':'2020-09-28','alignment_operator':'Linearly interpolate profile longitude/latitude to overlapping DAC timestamps, then compute WGS84 position separation. This audits internal source alignment; it cannot independently establish true georeferencing.','interpolation_is_not_velocity_reconstruction':True,'source_metadata_conflict':'Both DAC_U long_name attributes call the component northward, while DAC_U standard_name identifies eastward. Preserve both; this audit plots direction-independent vector magnitudes. Direction validation remains open.','whole_current_length_km':None,'whole_current_width_km':None,'annual_width_range_km':None,'current_association_verified':False,'corrected_paper_reproduction_verified':False,'seasonal_width_samples':[],'missions':missions}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source-directory',type=Path,required=True);args=parser.parse_args()
    output=ROOT/'research/norwegian-front-glider-source-alignment.json'
    doc=build(args.source_directory)
    doc['generator_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    output.write_bytes((json.dumps(doc,indent=2,allow_nan=False)+'\n').encode())
    print('Built source-alignment audit; no current dimensions admitted')

if __name__=='__main__':main()
