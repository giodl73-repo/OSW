"""Compare retained hourly snapshots with continuous monthly model support."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'research/source-data/norkyst-ingoy-months-2024'


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--all-months',action='store_true');args=parser.parse_args()
    phase='year' if args.all_months else 'pilot'
    report=json.loads((SOURCE/('section-diagnostic-'+phase+'.json')).read_bytes())
    if phase=='year':raise ValueError('Year figure layout must be reviewed separately; do not silently omit ten months')
    if report['completed_months']!=[1,7]:raise ValueError('Expected the declared January/July comparison')
    from norkyst_continuous_source import sha
    asset=ROOT/report['bulk_asset']['file']
    if sha(asset.read_bytes())!=report['bulk_asset']['sha256']:raise ValueError('Changed hourly profile asset')
    plt.rcParams.update({'font.size':9,'svg.hashsalt':'osw-norkyst-continuous-pilot-v1','axes.spines.top':False,'axes.spines.right':False})
    with np.load(asset,allow_pickle=False) as data:
        distance=data['distance_km'];months=[1,7]
        limit=max(float(np.nanmax(np.abs(data[f'month_{m:02d}_{kind}_u_eastward']))) for m in months for kind in ['raw','lowpass'])
        limit=max(.1,float(np.ceil(limit*10)/10))
        fig,axes=plt.subplots(4,2,figsize=(12,13),layout='constrained')
        images=[]
        for column,month in enumerate(months):
            stem=f'month_{month:02d}_';name='January' if month==1 else 'July';summary=report['months'][column]
            for row,kind in enumerate(['raw','lowpass']):
                values=data[stem+kind+'_u_eastward']
                image=axes[row,column].imshow(values.T,origin='lower',aspect='auto',
                    extent=(0,len(values)/24,float(distance[0]),float(distance[-1])),cmap='RdBu_r',vmin=-limit,vmax=limit,interpolation='nearest')
                images.append(image)
                axes[row,column].axvline(14.5,color='#222',lw=.9,ls='--')
                axes[row,column].set(title=f'{name} 2024: '+('total model flow' if kind=='raw' else '71-hour low-pass flow'),
                    xlabel='Days since first UTC hour of month',ylabel='Distance from selected southern limit (km)')
            raw=data[stem+'raw_u_eastward'];filtered=data[stem+'lowpass_u_eastward']
            u=summary['summary']['u_eastward'];s=summary['summary']['salinity']
            profile=axes[2,column]
            profile.fill_between(distance,np.asarray(u['lowpass']['p05'],dtype=float),np.asarray(u['lowpass']['p95'],dtype=float),color='#9cc6d3',alpha=.55,label='5th–95th hourly sample quantiles (low-pass)')
            profile.plot(distance,raw[14*24+12],color='#777',ls='--',lw=1,label='Earlier single noon snapshot, day 15')
            profile.plot(distance,u['raw']['mean'],color='#c35d18',lw=1.5,label='Complete-month total-flow mean')
            profile.plot(distance,u['lowpass']['mean'],color='#11627c',lw=1.5,label='Complete-month low-pass mean')
            profile.axhline(0,color='#555',lw=.7)
            profile.set(title=f'{name}: eastward profile comparison',xlabel='Distance along fixed section (km)',ylabel='Eastward model velocity (m/s)',ylim=(-limit,limit))
            profile.legend(fontsize=7,loc='best')
            sal=axes[3,column]
            sal.fill_between(distance,np.asarray(s['lowpass']['p05'],dtype=float),np.asarray(s['lowpass']['p95'],dtype=float),color='#bfd7b1',alpha=.6,label='5th–95th hourly sample quantiles (low-pass)')
            sal.plot(distance,s['raw']['mean'],color='#c35d18',label='Complete-month total-field mean')
            sal.plot(distance,s['lowpass']['mean'],color='#3e682d',label='Complete-month low-pass mean')
            sal.set(title=f'{name}: model salinity',xlabel='Distance along fixed section (km)',ylabel='Salinity (source units: 1)')
            sal.legend(fontsize=7,loc='best')
            for row in range(4):axes[row,column].grid(alpha=.16)
        axes[3,0].sharey(axes[3,1])
        fig.colorbar(images[0],ax=list(axes[:2,:].ravel()),label='Eastward model velocity at 10 m (m/s)',shrink=.85)
        fig.suptitle('Continuous Norkyst model sections: January and July 2024\n24°E, 71.10–73.00°N, 10 m; no physical current boundaries or widths inferred',fontsize=13)
        fig.supxlabel('Dashed heatmap line: the earlier day-15 noon reading. Quantiles describe temporal variation, not confidence intervals.\n3.2 km retained grid spacing; interpolated section points add no resolution. Low-pass filtering also alters non-tidal variability.\nModified Norkyst v3 hindcast: MET Norway / Institute of Marine Research, CC BY 4.0; Christensen et al. (2026), doi:10.5194/gmd-19-2785-2026.',fontsize=8)
        target=ROOT/'figures/norkyst-ingoy-continuous-months'
        fig.savefig(target.with_suffix('.svg'),metadata={'Date':None})
        svg=target.with_suffix('.svg').read_bytes();position=svg.index(b'>',svg.index(b'<svg '))
        description=(b'<title id="norkyst-monthly-title">January and July 2024 continuous model sections</title>'
                     b'<desc id="norkyst-monthly-description">Eastward total and low-pass model flow at a fixed offshore section, with complete-month velocity and salinity profiles. The older single hourly reading is shown separately. All hourly samples, support counts and statistics are retained in the accompanying section report and numeric asset. Quantiles describe temporal variability, not confidence intervals. No physical current edges, widths, seasonal width range or annual extrema are inferred.</desc>')
        svg=svg[:position]+b' role="img" aria-labelledby="norkyst-monthly-title norkyst-monthly-description">'+description+svg[position+1:]
        target.with_suffix('.svg').write_bytes(b'\n'.join(line.rstrip() for line in svg.splitlines())+b'\n')
        fig.savefig(target.with_suffix('.png'),dpi=140)
        plt.close(fig)
    provenance={'schema':'osw.norkyst-continuous-figure.v1','report_file':str((SOURCE/('section-diagnostic-'+phase+'.json')).relative_to(ROOT)),
                'report_sha256':sha((SOURCE/('section-diagnostic-'+phase+'.json')).read_bytes()),
                'generator_file':'analysis/build_norkyst_continuous_figure.py','generator_sha256':sha(Path(__file__).read_bytes()),
                'svg_file':target.with_suffix('.svg').relative_to(ROOT).as_posix(),'svg_sha256':sha(target.with_suffix('.svg').read_bytes()),
                'png_file':target.with_suffix('.png').relative_to(ROOT).as_posix(),'png_sha256':sha(target.with_suffix('.png').read_bytes()),
                'heatmap_symmetric_limit_m_s':limit,'missing_rendering':'Unfilled/transparent missing cells; no substitution with zero',
                'quantity':'Eastward component, not speed or current width','physical_geometry_admitted':False}
    (SOURCE/('figure-'+phase+'.json')).write_bytes((json.dumps(provenance,indent=2)+'\n').encode())
    print('Rendered January/July continuous model support; no width or physical footprint admission')


if __name__=='__main__':main()
