"""Standalone source fields, uncertainty support and fixed-array geography."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import TwoSlopeNorm
import numpy as np
from acquire_eac_100m_source import ROOT,sha
from check_eac_100m_source import REPORT,load,build,times

BASE='figures/eac-csiro-v23-100m-source-fields'
RECEIPT='research/eac-csiro-v23-100m-source-fields-figure.json'
OPERATOR='analysis/build_eac_100m_source_figure.py'


def render():
    report=json.loads((ROOT/REPORT).read_bytes())
    if report!=build():raise ValueError('Stale EAC source quality report')
    receipt,header,arrays=load();dates=times(arrays['TIME']);x=mdates.date2num(dates)
    fig,axes=plt.subplots(5,2,figsize=(17,19));fig.subplots_adjust(left=.065,right=.965,top=.90,bottom=.17,hspace=.50,wspace=.25)
    fig.text(.035,.969,'East Australian Current: fixed-array source fields at100m',fontsize=21,weight='bold')
    fig.text(.035,.943,'CSIRO collection v23 / data v19 • 3,770 daily records • 124 source positions • original values and uncertainty arrays',fontsize=11.5)
    fig.text(.035,.923,'Processed, SOM-filled and spatially mapped source data; five-day filter. Source grid and daily output are not independent observations.',fontsize=10)
    labels={'UCUR':'Eastward velocity','VCUR':'Northward velocity','TEMP':'Temperature','PSAL':'Practical salinity'}
    for i,name in enumerate(['UCUR','VCUR','TEMP','PSAL']):
        for j,field in enumerate([name,name+'_uncertainty']):
            ax=axes[i,j];data=arrays[field].T
            cmap=plt.get_cmap('RdBu_r' if j==0 and name in ['UCUR','VCUR'] else 'viridis' if j==0 else 'cividis').copy();cmap.set_bad('#d6d6d6')
            kwargs={}
            if j==0 and name in ['UCUR','VCUR']:
                bound=float(np.nanmax(abs(data)));kwargs['norm']=TwoSlopeNorm(vmin=-bound,vcenter=0,vmax=bound)
            image=ax.imshow(data,origin='lower',aspect='auto',interpolation='nearest',cmap=cmap,
                extent=[x[0]-.5,x[-1]+.5,-.5,123.5],**kwargs)
            unit=header['datasets'][field]['attributes']['units']
            ax.set_title(labels[name]+(' — provider uncertainty' if j else '')+f' ({unit})',fontsize=11)
            ax.set_yticks([0,40,80,123]);ax.set_ylabel('Source position index')
            ax.xaxis_date();ax.xaxis.set_major_locator(mdates.YearLocator(2));ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            ax.set_xlabel('Original daily source timestamps (UTC)');fig.colorbar(image,ax=ax,fraction=.035,pad=.02)
    ax=axes[4,0]
    paired=np.isfinite(arrays['UCUR'])&np.isfinite(arrays['VCUR']);above=arrays['BOTTOM_DEPTH']>100
    ax.plot(dates,paired.sum(axis=1),color='#176381',lw=1.5,label='Paired velocity cells, including source bottom values')
    ax.plot(dates,paired[:,above].sum(axis=1),color='#bc572d',lw=1,ls='--',label='Paired cells strictly above source bottom')
    ax.set(ylim=(-5,130),ylabel='Available source cells',title='Missing-source support; zero available cells is not current absence')
    ax.set_xlabel('Original source timestamps (UTC)');ax.grid(alpha=.2);ax.legend(fontsize=7,loc='lower right')
    ax.xaxis.set_major_locator(mdates.YearLocator(2));ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax=axes[4,1];lon=arrays['LONGITUDE'];lat=arrays['LATITUDE'];bottom=arrays['BOTTOM_DEPTH']
    ax.plot(lon,lat,color='#455e68',lw=.8);points=ax.scatter(lon,lat,c=bottom,cmap='viridis',s=13)
    ax.scatter(lon[bottom<=100],lat[bottom<=100],marker='x',color='#bc572d',s=22,label='Source bottom at/above100m level')
    ax.set(xlabel='Longitude (°E, WGS84)',ylabel='Latitude (°N, WGS84)',title='Fixed source array: geography, not a current axis or width')
    ax.set_aspect(1/np.cos(np.deg2rad(float(lat.mean()))));ax.grid(alpha=.2);ax.legend(fontsize=7,loc='upper left')
    fig.colorbar(points,ax=ax,fraction=.035,pad=.02,label='Source bottom depth (m)')
    notes=[
        'Grey cells are source missing values. All eight fields share the retained mask:354,933 finite and112,547NaN values per field; no infinities.',
        '629 source dates have no retained paired velocity:27Aug2013–17May2015. The source clock remains daily; OSW fills no gap.',
        'Two source bottom cells at100m prescribe zero velocity and zero velocity uncertainty on all3,141 available dates; these are not observed calm-current records.',
        'The uncertainty arrays retain the provider *_standard_error names. No universal confidence level, lateral-width error or independence model is inferred.',
        'Output spacing is approximately1–2km; mooring separation is approximately10–65km. The173km source array is not a current length.',
        'File lineage and descriptor disagree about QC wording and final interpolation. Preserve both; the exact final spatial build is not independently reproduced.',
        'No current width, annual physical range, current edges or seasonal current polygons are admitted. Geographic points describe the fixed processing grid.',
        'Source: Sloyan, Cowley and Chapman / CSIRO, IMOS, NESP, Marine National Facility. doi:10.25919/sfw7-hc46, CC BY4.0. Derived figure: OSW.']
    for i,note in enumerate(notes):fig.text(.035,.137-i*.015,note,fontsize=8)
    plt.rcParams['svg.hashsalt']='osw-eac-source-v1';assets={}
    for extension in ['png','svg']:
        path=BASE+'.'+extension;fig.savefig(ROOT/path,dpi=150,metadata={'Date':None} if extension=='svg' else {})
        if extension=='svg':
            ET.register_namespace('','http://www.w3.org/2000/svg');tree=ET.parse(ROOT/path);root=tree.getroot()
            root.set('role','img');root.set('aria-labelledby','eac-source-title eac-source-description')
            title=ET.Element('{http://www.w3.org/2000/svg}title',id='eac-source-title');title.text='East Australian Current100m source fields and uncertainty support'
            desc=ET.Element('{http://www.w3.org/2000/svg}desc',id='eac-source-description');desc.text='Eight dated source-field panels preserve the2013–2015missing period; source support and fixed WGS84 array geography are shown. Source bottom zeros, SOM filling, mapping and uncertainty limitations remain explicit. No physical current dimensions are supplied.'
            root.insert(0,title);root.insert(1,desc);tree.write(ROOT/path,encoding='utf8',xml_declaration=True)
        assets['.'+extension]={'file':path,'sha256':sha(ROOT/path)}
    plt.close(fig)
    document={'schema':'osw.source-figure.v1','source_file':REPORT,'source_sha256':sha(ROOT/REPORT),
        'source_subset_file':'research/source-data/eac-csiro-v23-100m/selected-source.npz','source_subset_sha256':receipt['subset_sha256'],
        'generator_file':OPERATOR,'generator_sha256':sha(ROOT/OPERATOR),'figures':assets,
        'source_field_panels':8,'source_profiles':3770,'fixed_geometry_not_current_edges':True,
        'physical_width_admitted':False,'provider_uncertainty_reinterpreted_as_confidence_interval':False}
    (ROOT/RECEIPT).write_bytes((json.dumps(document,indent=2)+'\n').encode());print(json.dumps(document))


if __name__=='__main__':render()
