"""Publication figures for complete monthly sections and regional model means."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from build_norkyst_ingoy_maps import rotated_vectors
from build_norkyst_ingoy_timeline import TRANSFORM
import norkyst_continuous_source as source

ROOT=source.ROOT
FOLDER=ROOT/source.SOURCE
MONTHS=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']


def save(fig,name,title,description):
    base=ROOT/'figures'/name
    svg=base.with_suffix('.svg');png=base.with_suffix('.png')
    fig.savefig(svg,metadata={'Date':None});fig.savefig(png,dpi=140)
    raw=svg.read_bytes();position=raw.index(b'>',raw.index(b'<svg '))
    import xml.sax.saxutils
    identity=name+'-title';detail=name+'-description'
    tags=f'<title id="{identity}">{xml.sax.saxutils.escape(title)}</title><desc id="{detail}">{xml.sax.saxutils.escape(description)}</desc>'.encode()
    raw=raw[:position]+f' role="img" aria-labelledby="{identity} {detail}">'.encode()+tags+raw[position+1:]
    svg.write_bytes(b'\n'.join(line.rstrip() for line in raw.splitlines())+b'\n')
    plt.close(fig)
    return {'svg_file':svg.relative_to(ROOT).as_posix(),'svg_sha256':source.sha(svg.read_bytes()),
            'png_file':png.relative_to(ROOT).as_posix(),'png_sha256':source.sha(png.read_bytes())}


def profiles(report,variability=False):
    distances=np.asarray(report['section_distances_km'])
    fig,axes=plt.subplots(3,2,figsize=(13,11),layout=None if variability else 'constrained')
    if variability:fig.subplots_adjust(left=.085,right=.9,bottom=.12,top=.90,hspace=.38,wspace=.24)
    for row,(variable,label,unit) in enumerate([('u_eastward','Eastward velocity','m/s'),('v_northward','Northward velocity','m/s'),('salinity','Salinity','source units: 1')]):
        statistic='standard_deviation' if variability else 'mean'
        matrices=[np.asarray([month['summary'][variable][kind][statistic] for month in report['months']],dtype=float) for kind in ['raw','lowpass']]
        if variability:
            low=0;high=max(.01,float(np.ceil(max(np.nanmax(a) for a in matrices)*100)/100));cmap='magma'
        elif row<2:
            limit=max(.05,float(np.ceil(max(np.nanmax(np.abs(a)) for a in matrices)*20)/20))
            low,high,cmap=-limit,limit,'RdBu_r'
        else:low,high,cmap=33,35.2,'viridis'
        palette=plt.get_cmap(cmap).copy();palette.set_bad('#c7c7c7')
        images=[]
        labels=['Total-field standard deviation','Low-pass standard deviation'] if variability else ['Total-field mean','Low-pass mean']
        for column,(kind,matrix) in enumerate(zip(labels,matrices)):
            ax=axes[row,column]
            image=ax.imshow(matrix,origin='lower',aspect='auto',interpolation='nearest',
                extent=(float(distances[0]),float(distances[-1]),.5,12.5),cmap=palette,vmin=low,vmax=high)
            images.append(image)
            ax.set(title=f'{label}: {kind}',xlabel='Distance along selected 24°E section (km)',ylabel='2024 calendar month')
            ax.set_yticks(range(1,13),MONTHS)
        fig.colorbar(images[0],ax=list(axes[row]),label=f'{label} ({unit})',shrink=.9,
                     extend='both' if row==2 and not variability else 'neither')
    if variability:
        fig.suptitle('2024 within-month model variability · Norkyst v3 · 10 m\nPopulation standard deviations of hourly fields at the fixed 24°E section',fontsize=13)
        fig.supxlabel('These are temporal variations in model fields, not measurement uncertainty, confidence intervals or current-width ranges.\nComplete calendar months; population convention ddof=0. Serial dependence remains. Gray means incomplete required support.\nModified MET Norway / Institute of Marine Research data · CC BY 4.0 · Christensen et al. (2026), doi:10.5194/gmd-19-2785-2026.',fontsize=8)
        return save(fig,'norkyst-ingoy-complete-year-variability',
                    'Within-month model variability across2024',
                    'Population standard deviations of total and low-pass hourly eastward velocity, northward velocity and salinity. Each row represents a complete calendar month. These describe serially dependent model temporal variation, not confidence intervals, measurement uncertainty or physical current-width ranges. Missing support remains gray. Numeric statistics and all hourly section fields accompany this figure.')
    fig.suptitle('Complete 2024 monthly model sections · Norkyst v3 · 10 m\n24°E, 71.10–73.00°N; no physical current widths or annual width extrema inferred',fontsize=13)
    fig.supxlabel('Each row is a complete UTC calendar-month mean, not an interpolated current trajectory or a climatology. Gray means incomplete required support.\nLow-pass means use the same71-point 24/24/25-hour kernel; filtering also alters non-tidal variability. 3.2 km retained grid spacing.\nModified MET Norway / Institute of Marine Research data · CC BY 4.0 · Christensen et al. (2026), doi:10.5194/gmd-19-2785-2026.',fontsize=8)
    return save(fig,'norkyst-ingoy-complete-year-sections',
                'Complete 2024 monthly model section means',
                'Twelve calendar-month means of eastward and northward velocity and salinity, each shown before and after low-pass filtering. Missing required support remains gray. Numeric support and all section means are retained in the accompanying year report. This model section does not establish physical current boundaries, widths, annual physical width extrema or a climatology.')


def maps(document):
    longitude=np.asarray(document['longitude']);latitude=np.asarray(document['latitude'])
    x=np.arange(50)*3.2;y=np.arange(48)*3.2;xx,yy=np.meshgrid(x,y)
    section_lat=np.asarray([round(71.1+i*.01,2) for i in range(191)])
    sx,sy=TRANSFORM.transform(np.full(191,24.),section_lat)
    section_x=(sx-source.X[0]*800)/1000;section_y=(sy-source.Y[0]*800)/1000
    palette=plt.get_cmap('viridis').copy();palette.set_bad('#c7c7c7')
    fig,axes=plt.subplots(4,3,figsize=(13,16),layout='constrained');images=[]
    for entry,ax in zip(document['months'],axes.flat):
        values=entry['lowpass']['mean'];sal=np.asarray(values['salinity'],dtype=float)
        east=np.asarray(values['u_eastward'],dtype=float);north=np.asarray(values['v_northward'],dtype=float)
        u,v=rotated_vectors(longitude,latitude,east,north)
        image=ax.pcolormesh(x,y,sal,shading='nearest',cmap=palette,vmin=33,vmax=35.2,rasterized=True);images.append(image)
        contour=ax.contour(x,y,latitude,levels=[71.5,72,72.5],colors='white',alpha=.7,linewidths=.5)
        ax.clabel(contour,fmt=lambda n:f'{n:g}°N',fontsize=6)
        contour=ax.contour(x,y,longitude,levels=[22,24,26],colors='white',alpha=.7,linewidths=.5)
        ax.clabel(contour,fmt=lambda n:f'{n:g}°E',fontsize=6)
        sl=(slice(None,None,5),slice(None,None,5))
        arrows=ax.quiver(xx[sl],yy[sl],u[sl],v[sl],angles='xy',scale_units='xy',scale=.07,color='#161c24',width=.004)
        key=ax.quiverkey(arrows,.10,.94,.5,'0.5 m/s',coordinates='axes',labelpos='E',fontproperties={'size':7})
        key.text.set_bbox({'facecolor':'white','alpha':.85,'edgecolor':'none','pad':1})
        ax.plot(section_x,section_y,color='#e24c17',lw=.8)
        ax.set(xlim=(0,x[-1]),ylim=(0,y[-1]),aspect='equal',title=f"{MONTHS[entry['month']-1]} 2024 · low-pass monthly mean",
               xlabel='Source X from patch origin (projected km)',ylabel='Source Y from patch origin (projected km)')
        ax.tick_params(labelsize=7)
    fig.colorbar(images[0],ax=list(axes.flat),label='Model salinity (source units: 1)',extend='both',shrink=.75)
    fig.suptitle('2024 monthly regional model means · Norkyst v3 · 10 m\nSalinity and mean-velocity arrows; fixed offshore patch, no coastline or physical current footprint',fontsize=13)
    fig.supxlabel('Original polar stereographic grid; equal projected X/Y scale. Orange line: fixed 24°E section, not a current axis or boundary.\nAll panels share salinity and vector scales. Gray indicates incomplete required support. Arrow bearings rotate true east/north into the map plane.\nModified MET Norway / Institute of Marine Research data · CC BY 4.0 · Christensen et al. (2026), doi:10.5194/gmd-19-2785-2026.',fontsize=8)
    return save(fig,'norkyst-ingoy-complete-year-maps',
                'Twelve monthly regional model field maps for2024',
                'Twelve complete-calendar low-pass mean salinity maps with correctly rotated mean velocity arrows. Geographic contours locate the fixed offshore source patch. The orange line identifies the section. These are model fields, not the Norwegian Coastal Current occupied footprint or physical width. Data support, source-cell means and raw means are retained in the accompanying regional map document.')


def main():
    path=FOLDER/'section-diagnostic-year.json';report=json.loads(path.read_bytes())
    if report['completed_months']!=list(range(1,13)) or report['calendar_hours']!=8784 or report['complete_annual_timestamp_coverage'] is not True:
        raise ValueError('Complete twelve-month source support required for year figures')
    region=ROOT/report['regional_maps']['file']
    if source.sha(region.read_bytes())!=report['regional_maps']['sha256']:raise ValueError('Changed monthly regional means')
    document=json.loads(region.read_bytes())
    if [m['month'] for m in document['months']]!=list(range(1,13)):raise ValueError('Missing or reordered monthly maps')
    plt.rcParams.update({'font.size':9,'svg.hashsalt':'osw-norkyst-complete-year-v1'})
    figures={'sections':profiles(report),'variability':profiles(report,variability=True),'regional_maps':maps(document)}
    provenance={'schema':'osw.norkyst-continuous-year-figures.v1','report_file':path.relative_to(ROOT).as_posix(),
                'report_sha256':source.sha(path.read_bytes()),'regional_map_file':region.relative_to(ROOT).as_posix(),
                'regional_map_sha256':source.sha(region.read_bytes()),'generator_file':Path(__file__).relative_to(ROOT).as_posix(),
                'generator_sha256':source.sha(Path(__file__).read_bytes()),'figures':figures,'physical_geometry_admitted':False,'new_width_record_admitted':False}
    provenance['input_sha256']={file:source.sha((ROOT/file).read_bytes()) for file in
                               ['analysis/build_norkyst_ingoy_maps.py','analysis/build_norkyst_ingoy_timeline.py']}
    (FOLDER/'figure-year.json').write_bytes((json.dumps(provenance,indent=2)+'\n').encode())
    print('Rendered complete2024 monthly sections and regional field maps; no width admission')


if __name__=='__main__':main()
