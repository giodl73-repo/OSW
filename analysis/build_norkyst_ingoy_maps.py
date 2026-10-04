"""Render frozen model fields on their projected grid, with correctly rotated arrows."""
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from build_norkyst_ingoy_timeline import GEOD, TRANSFORM

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'research/norkyst-ingoy-2024-map-frames.json'
RULES = {'salinity_color_limits': [33.0,35.2], 'velocity_arrow_grid_stride': 5, 'velocity_arrow_scale': 0.07, 'velocity_arrow_reference_m_s': 0.5, 'coordinate_system': 'original source polar stereographic grid; relative projected kilometres', 'vector_rotation': 'True east/north velocity bearing projected using a 1 km geodesic direction probe; direction normalized, speed preserved. Arrows indicate instantaneous model velocity, not trajectories.', 'temporal_interpolation': False, 'named_current_footprint': False}


def rotated_vectors(lon, lat, eastward, northward):
    speed = np.hypot(eastward,northward)
    bearing = np.degrees(np.arctan2(eastward,northward))
    lon2,lat2,_ = GEOD.fwd(lon,lat,bearing,np.full_like(speed,1000.0))
    x,y = TRANSFORM.transform(lon,lat)
    x2,y2 = TRANSFORM.transform(lon2,lat2)
    norm = np.hypot(x2-x,y2-y)
    return (x2-x)/norm*speed, (y2-y)/norm*speed


def decoded(receipt,name):
    raw = np.asarray(receipt['packed_field_arrays'][name],float)
    packing = receipt['packing'][name]
    wet = (np.asarray(receipt['packed_field_arrays']['sea_mask']) == 1) & (raw != packing['fill'])
    return np.where(wet,raw*packing['scale']+packing['offset'],np.nan)


def main():
    acquisition_path=ROOT/'research/norkyst-ingoy-2024-monthly-sample-receipts.json'
    acquisition=json.loads(acquisition_path.read_text(encoding='utf-8'))
    if len(acquisition['observations']) != 12: raise ValueError('Incomplete map sequence')
    frames=[]
    for observation in acquisition['observations']:
        receipt_path=ROOT/observation['file']
        if hashlib.sha256(receipt_path.read_bytes()).hexdigest()!=observation['receipt_sha256']: raise ValueError('Changed map source')
        receipt=json.loads(receipt_path.read_text(encoding='utf-8'))
        arrays=receipt['packed_field_arrays']
        lon,lat=np.asarray(arrays['lon']),np.asarray(arrays['lat'])
        sal,east,north=(decoded(receipt,name) for name in ['salinity','u_eastward','v_northward'])
        u,v=rotated_vectors(lon,lat,east,north)
        ys,xs=(receipt['grid_index_slices'][k] for k in ['Y','X'])
        x=np.arange(50)*xs[1]*.8; y=np.arange(48)*ys[1]*.8
        fig,ax=plt.subplots(figsize=(10,9))
        fig.subplots_adjust(bottom=.13,top=.84,left=.12,right=.86)
        ax.set_facecolor('#e0ded6')
        image=ax.pcolormesh(x,y,sal,shading='nearest',cmap='viridis',vmin=33,vmax=35.2,rasterized=False)
        fig.colorbar(image,ax=ax,pad=.02,label='Salinity (dimensionless)',extend='both')
        latitude_contours=ax.contour(x,y,lat,levels=[71.5,72,72.5],colors='white',linewidths=.6,alpha=.7)
        ax.clabel(latitude_contours,fmt=lambda n:f'{n:g} N',fontsize=9)
        longitude_contours=ax.contour(x,y,lon,levels=[22,24,26],colors='white',linewidths=.6,alpha=.7)
        ax.clabel(longitude_contours,fmt=lambda n:f'{n:g} E',fontsize=9)
        stride=RULES['velocity_arrow_grid_stride']; sl=(slice(None,None,stride),slice(None,None,stride))
        xx,yy=np.meshgrid(x,y)
        arrows=ax.quiver(xx[sl],yy[sl],u[sl],v[sl],angles='xy',scale_units='xy',scale=RULES['velocity_arrow_scale'],color='#151f27',width=.0035,alpha=.8)
        ax.quiverkey(arrows,.1,1.025,.5,'0.5 m/s',coordinates='axes',labelpos='E')
        section_lat=np.linspace(71.1,73,191)
        sx,sy=TRANSFORM.transform(np.full(191,24.0),section_lat)
        ax.plot((sx-xs[0]*800)/1000,(sy-ys[0]*800)/1000,color='#e24c17',linewidth=2,label='Fixed 24 E profile section')
        ax.legend(loc='lower right',fontsize=9)
        ax.set(xlim=(0,x[-1]),ylim=(0,y[-1]),aspect='equal',xlabel='Source grid X from subset origin (projected km)',ylabel='Source grid Y from subset origin (projected km)')
        ax.set_title(f"Ingoy region · {observation['date']} 12:00 UTC · 10 m\nNorkyst v3 hourly hindcast; field subset, not current footprint",fontsize=13,pad=35)
        fig.text(.5,.025,'Modified MET Norway / IMR data · CC BY 4.0 · OSW rendering · hourly samples, not monthly means',ha='center',fontsize=9)
        path=ROOT/f"figures/norkyst-ingoy-map-{observation['date']}.svg"
        fig.savefig(path,metadata={'Date':None});plt.close(fig)
        frames.append({'date':observation['date'],'sample_time_utc':receipt['sample_time_utc'],'receipt_file':observation['file'],'receipt_sha256':observation['receipt_sha256'],'figure':path.relative_to(ROOT).as_posix(),'figure_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'salinity_valid_cells':int(np.isfinite(sal).sum()),'vector_valid_cells':int(np.isfinite(u[sl]).sum()),'salinity_cells_outside_color_limits':int(((sal<33)|(sal>35.2)).sum()),'geographic_bounds':{'west':float(lon.min()),'east':float(lon.max()),'south':float(lat.min()),'north':float(lat.max())},'map_role':'regional_model_field_subset_not_named_current_boundary_or_state_footprint'})
    protocol=ROOT/'plans/norkyst-ingoy-section-sampling-protocol-v1.md'
    doc={'schema':'osw.norkyst-map-frames.v1','status':'model_field_display_not_canonical_current_geometry','rules':RULES,'source_license':'CC-BY-4.0','acquisition_file':acquisition_path.relative_to(ROOT).as_posix(),'acquisition_sha256':hashlib.sha256(acquisition_path.read_bytes()).hexdigest(),'generator_file':Path(__file__).relative_to(ROOT).as_posix(),'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'protocol_file':protocol.relative_to(ROOT).as_posix(),'protocol_sha256':hashlib.sha256(protocol.read_bytes()).hexdigest(),'annual_extrema_eligible':False,'state_footprint_join_eligible':False,'frames':frames}
    helper=ROOT/'analysis/build_norkyst_ingoy_timeline.py'
    doc['projection_helper_file']=helper.relative_to(ROOT).as_posix()
    doc['projection_helper_sha256']=hashlib.sha256(helper.read_bytes()).hexdigest()
    OUTPUT.write_text(json.dumps(doc,indent=2)+'\n',encoding='utf-8')
    print('Built 12 projected field maps with rotated instantaneous velocity arrows')


if __name__=='__main__':main()
