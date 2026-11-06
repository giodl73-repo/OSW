"""Show published filtered-curve readings without inventing monthly observations."""
from pathlib import Path
import hashlib,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from build_kuroshio_filtered_width_series import ROOT,OUTPUT,verify,encoded

RECEIPT='research/kuroshio-ecs-filtered-width-time-series-figure.json'

def generate():
 report=verify();samples=report['samples']
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.hashsalt':'osw-kuroshio-filtered-width-v1'})
 fig,axes=plt.subplots(2,1,figsize=(13,11),gridspec_kw={'height_ratios':[1,1.8]})
 fig.subplots_adjust(left=.08,right=.92,top=.85,bottom=.22,hspace=.4)
 fig.suptitle('Kuroshio: readings of the published filtered width curve',x=.04,ha='left',fontsize=16,fontweight='bold')
 fig.text(.04,.94,'East China Sea 122–130°E | half-year filtered | 192 month-midpoint plot positions, not raw monthly means',fontsize=11)
 ax=axes[0];valid=[s for s in samples if s['approximate_width_km'] is not None]
 ax.errorbar([s['plot_year'] for s in valid],[s['approximate_width_km'] for s in valid],yerr=report['reading_allowance_km'],
  fmt='o',markersize=2.5,color='#125d83',ecolor='#a1c4d6',elinewidth=.7,capsize=0,label='Plot readings ±5 km graphical allowance')
 ax.set_xlim(1993,2009);ax.set_ylim(175,240);ax.set_xticks(list(range(1993,2010,2)))
 ax.set_xlabel('Published plot year; not exact observation timestamps');ax.set_ylabel('Filtered regional width (km)')
 ax.grid(alpha=.2);ax.legend(loc='upper right',frameon=False,fontsize=9)
 ax.set_title('All sampled source-curve positions; no connecting or gap-filling line',loc='left',fontsize=11)
 matrix=np.full((16,12),np.nan)
 for s in samples:
  if s['approximate_width_km'] is not None:matrix[s['plot_year_label']-1993,s['plot_month_label']-1]=s['approximate_width_km']
 ax=axes[1];cmap=plt.get_cmap('cividis').copy();cmap.set_bad('#e2e6e8')
 im=ax.imshow(matrix,aspect='auto',cmap=cmap,vmin=180,vmax=235)
 ax.set_xticks(range(12),['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
 ax.set_yticks(range(16),range(1993,2009));ax.set_xlabel('Month-midpoint label on source year axis (each reading ±5 km graphical allowance)')
 ax.set_title('Sampled positions on the filtered curve; months are not independent observations',loc='left',fontsize=11)
 for i in range(16):
  for j in range(12):
   v=matrix[i,j];ax.text(j,i,'—' if np.isnan(v) else f'{v:.0f}',ha='center',va='center',fontsize=8,color='white' if np.isfinite(v) and v<210 else '#111')
 bar=fig.colorbar(im,ax=ax,fraction=.025,pad=.02);bar.set_label('Filtered plot reading (km)')
 notes=[
  'The caption specifies half-year filtering. Kernel, alignment, endpoint treatment and detailed weights remain unresolved; the filter is not reproduced.',
  'Monthly sampling of the drawn curve adds no source resolution. Plot-coordinate allowance: ±0.05 years, not exact timestamps or filter support.',
  'The ±5 km allowance covers graphical reading/calibration/rounding. It is not source measurement uncertainty, confidence or annual physical variability.',
  'All 192 targets resolve within source segments. One native PDF stroke break is retained; no joining segment or missing source value is invented.',
  'No whole-current width, geographic boundary, annual extrema or seasonal map playback is supplied. Existing seasonal profiles and prose means are separate.',
  'Weekly surface geostrophic diagnosis excludes ageostrophic flow. Its original 1/3° grid, interpolated to0.1°, gains no independent observed resolution.',
  'Source: Liu and Gan (2012), Figure 7a, doi:10.1016/j.dsr.2011.10.008. OSW-derived plot readings; original source image is not redistributed.']
 for i,line in enumerate(notes):fig.text(.04,.16-i*.0205,line,fontsize=8.5)
 assets={}
 for suffix in ['svg','png']:
  path=ROOT/f'figures/kuroshio-ecs-filtered-width-time-series.{suffix}'
  fig.savefig(path,dpi=150,metadata={'Date':None} if suffix=='svg' else {'Software':'OSW'})
  if suffix=='svg':
   text=path.read_text(encoding='utf8');opening=text.index('>',text.index('<svg'))
   text=text[:opening+1]+'\n<title>Kuroshio published filtered width curve readings</title>\n<desc>192 month-midpoint plot samples of a half-year-filtered regional width curve, not raw monthly means. Approximate values span 190–225 km; the separate five-kilometre graphical allowance is not source uncertainty or annual extrema. A complete sixteen-by-twelve table and source links accompany these readings.</desc>'+text[opening+1:]
   path.write_text(text.replace('<svg ','<svg role="img" ',1),encoding='utf8',newline='\n')
  assets['.'+suffix]={'file':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
 plt.close(fig)
 receipt={'schema':'osw.source-figure.v1','generator_file':Path(__file__).relative_to(ROOT).as_posix(),
  'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'source_file':OUTPUT,
  'source_sha256':hashlib.sha256((ROOT/OUTPUT).read_bytes()).hexdigest(),'figures':assets,
  'sample_count':len(samples),'samples_are_raw_monthly_means':False,'graphical_allowance_km':5,
  'source_uncertainty_inferred':False,'physical_edges_rendered':False,'annual_extrema_inferred':False}
 (ROOT/RECEIPT).write_bytes(encoded(receipt));return receipt

if __name__=='__main__':print(json.dumps(generate()['figures']))
