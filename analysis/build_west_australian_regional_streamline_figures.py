"""Show supported regional lengths, failed conventions and partial trace geometry."""
import calendar
import json
import math

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np

from west_australian_regional_streamlines import ROOT, REPORT, PROTOCOL, STEPS, OFFSETS, build, encoded, digest

OPERATOR='analysis/build_west_australian_regional_streamline_figures.py'
MANIFEST='research/west-australian-regional-streamline-figures.json'


def label(anchor):return 'Source-period\nmean' if anchor['month'] is None else calendar.month_abbr[anchor['month']]


def comparison(document):
    fig,(ax,matrix)=plt.subplots(2,1,figsize=(15,10),gridspec_kw={'height_ratios':[2,2]})
    fig.subplots_adjust(left=.14,right=.98,top=.88,bottom=.23,hspace=.55)
    fig.suptitle(document.get('method_display_name','Euler baseline')+' · regional source-field streamline tests',x=.08,y=.975,ha='left',fontsize=19)
    fig.text(.08,.93,'13 mean fields × 9 seed/step conventions · OSCAR v2017.0 / nominal 15 m / 2013 source records',fontsize=12)
    colors={-1:'#287fa3',0:'#cf6821',1:'#668c32'};markers={5:'^',10:'o',20:'s'}
    statuses=np.full((13,9),-1,dtype=int);anchors=document['anchors'];counts=[]
    for x,anchor in enumerate(anchors):
        rows=[r for r in document['cases'] if r['field_id']==anchor['field_id']]
        counts.append(sum(r['status']=='both_regional_gates_reached' for r in rows))
        for row in rows:
            col=STEPS.index(row['step_km'])*3+OFFSETS.index(row['native_seed_offset'])
            if row['forward'] is not None:
                statuses[x,col]=sum(row[k]['status']=='matching_gate_reached' for k in ['backward','forward'])
            if row['conditional_regional_path_length_km'] is not None:
                ax.scatter(x+row['native_seed_offset']*.18,row['conditional_regional_path_length_km'],
                           color=colors[row['native_seed_offset']],marker=markers[row['step_km']],
                           s=75 if row['primary'] else 30,linewidth=1.5 if row['primary'] else .5,
                           edgecolors='black' if row['primary'] else 'white',zorder=3 if row['primary'] else 2)
    ax.set_xticks(range(13),[label(a)+f'\n{counts[i]}/9' for i,a in enumerate(anchors)],fontsize=9)
    ax.set_ylabel('Conditional regional path length (km)');ax.set_xlim(-.6,12.6);ax.set_ylim(bottom=0)
    ax.set_title('Only matching north/south gate pairs have a length · black outline = primary case',loc='left',fontsize=11)
    ax.grid(axis='y',alpha=.25);ax.spines[['top','right']].set_visible(False)
    matrix.imshow(statuses.T,origin='lower',aspect='auto',interpolation='nearest',vmin=-1,vmax=2,
                  cmap=ListedColormap(['#bd8abc','#d4dadd','#e4b648','#247a6c']))
    matrix.set_xticks(range(13),[label(a) for a in anchors],fontsize=9)
    matrix.set_yticks(range(9),[f'{s} km / {"west" if o<0 else "central" if o==0 else "east"} seed' for s in STEPS for o in OFFSETS],fontsize=9)
    matrix.set_title('All 117 attempts retained · number of legs reaching their matching gate',loc='left',fontsize=11)
    legend=[Patch(color='#247a6c',label='Both gates'),Patch(color='#e4b648',label='One gate'),Patch(color='#d4dadd',label='Neither gate'),
            *[Line2D([],[],color=colors[o],marker='o',linestyle='',label=('West' if o<0 else 'Central' if o==0 else 'East')+' seed') for o in OFFSETS],
            *[Line2D([],[],color='#344752',marker=markers[s],linestyle='',label=f'{s} km step') for s in STEPS]]
    fig.legend(handles=legend,loc='lower center',bbox_to_anchor=(.53,.135),ncol=5,frameon=False,fontsize=9)
    resolved=[r for r in document['cases'] if r['primary'] and r['month'] is not None and r['conditional_regional_path_length_km'] is not None]
    values='; '.join(calendar.month_abbr[r['month']]+' about '+str(r['rounded_regional_path_length_km'])+' km' for r in resolved)
    fig.text(.08,.105,'Primary monthly lengths: '+values+'. '+str(12-len(resolved))+' other months remain unresolved.',fontsize=10)
    fig.text(.08,.075,'Gates at 28/36°S and seeds are analysis conventions. Discrete mean-field paths are not observed particle trajectories or named-current axes.',fontsize=10)
    fig.text(.08,.047,'No whole-current length, annual physical range, width or eddy identity is admitted. Alternatives show seed/step sensitivity, not a confidence interval.',fontsize=10)
    fig.text(.08,.019,'Source: retained OSCAR2017.0 vectors / NOAA OceanWatch. Original clocks, masks, failed traces and exact source links accompany the data.',fontsize=9)
    return fig


def paths(document):
    primary=[r for r in document['cases'] if r['primary']]
    points=[p for r in primary for key in ['backward','forward'] if r[key] for p in r[key]['vertices_lon_lat']]
    low=max(60,min(p[0] for p in points)-1);high=min(116,max(p[0] for p in points)+1)
    fig,axes=plt.subplots(7,2,figsize=(16,14))
    fig.subplots_adjust(left=.06,right=.98,top=.9,bottom=.1,hspace=.6,wspace=.13)
    fig.suptitle(document.get('method_display_name','Euler baseline')+' · primary paths and partial failures',x=.06,y=.975,ha='left',fontsize=18)
    fig.text(.06,.94,'Central 32°S seed / nominal maximum 10 km step · fixed 28/36°S gates · common geographic scale',fontsize=11)
    names={'matching_gate_reached':'gate reached','seed_return_guard':'return guard','next_step_exceeds_distance_limit':'distance limit',
           'viewport_north_exit':'north exit','viewport_south_exit':'south exit','viewport_east_exit':'east exit','viewport_west_exit':'west exit',
           'weak_endpoint_speed_guard':'weak endpoint','gate_velocity_not_northward':'wrong gate direction','unsupported_segment_rectangle':'missing support',
           'weak_stage_speed_guard':'weak flow guard','unsupported_stage_rectangle':'missing support',
           'boundary_minimum_step_guard':'boundary guard','local_error_guard':'error control limit'}
    for ax,row in zip(axes.flat,primary):
        passed=row['status']=='both_regional_gates_reached'
        for key in ['backward','forward']:
            leg=row[key]
            if leg is None:continue
            coordinates=np.array(leg['vertices_lon_lat'])
            ax.plot(coordinates[:,0],coordinates[:,1],color='#126d70' if passed else '#737e85',linestyle='-' if passed else '--',linewidth=1)
            end=coordinates[-1];matched=leg['status']=='matching_gate_reached'
            ax.scatter([end[0]],[end[1]],color='#126d70' if matched else '#b34632',marker='o' if matched else 'x',s=22,zorder=4)
        if row['seed_lon_lat']:ax.scatter(*row['seed_lon_lat'],color='#d48121',s=18,zorder=5)
        for latitude in [-36,-28]:ax.axhline(latitude,color='#263f49',linewidth=.8,linestyle=':')
        ax.axhline(-32,color='#c98c45',linewidth=.5,linestyle=':')
        ax.set_xlim(low,high);ax.set_ylim(-36.3,-27.7);ax.set_aspect(1/math.cos(math.radians(32)))
        ax.set_yticks([-36,-32,-28]);ax.tick_params(labelsize=8);ax.grid(alpha=.18)
        month='Source-period mean' if row['month'] is None else calendar.month_name[row['month']]
        value=f"about{row['rounded_regional_path_length_km']}km" if passed else 'unresolved'
        reasons='; '.join(('backward' if key=='backward' else 'forward')+': '+names.get(row[key]['status'],row[key]['status']) for key in ['backward','forward'] if row[key])
        ax.set_title(month+' · '+value+'\n'+reasons,loc='left',fontsize=8)
    axes.flat[-1].axis('off')
    axes.flat[-1].text(.03,.8,'Solid teal: both regional gates reached\nDashed grey: failed pair; partial trace only\nOrange: seed; green endpoint: matching gate\nRed ×: last accepted point of a failed leg',transform=axes.flat[-1].transAxes,fontsize=10,va='top')
    fig.text(.06,.065,'All primary geometry is shown, including partial failures and the separate source-period mean. Polygonal paths are a numerical approximation.',fontsize=10)
    fig.text(.06,.04,'These are source-region diagnostics, not current boundaries, whole-current routes, annual physical ranges or eddy identifications. Full117case data remain available.',fontsize=10)
    fig.text(.06,.015,'Source: OSCAR2017.0 / retained2013records. Lengths sum WGS84 polygonal distances. Common longitude window includes every primary trace.',fontsize=9)
    return fig


def main():
    document=json.loads((ROOT/REPORT).read_bytes())
    if encoded(build())!=(ROOT/REPORT).read_bytes():raise ValueError('Changed regional streamline report')
    plt.rcParams.update({'font.family':'DejaVu Sans','svg.hashsalt':'osw-west-australian-regional-paths-v1'})
    assets={}
    for name,constructor,stem in [('comparison',comparison,'figures/west-australian-regional-streamlines'),('paths',paths,'figures/west-australian-regional-streamline-paths')]:
        fig=constructor(document)
        for suffix in ['svg','png']:
            path=stem+'.'+suffix
            metadata={'Date':None,'Creator':'OSW'} if suffix=='svg' else {'Software':'OSW'}
            fig.savefig(ROOT/path,dpi=130,metadata=metadata,facecolor='white')
            assets[name+'_'+suffix]={'file':path,'sha256':digest((ROOT/path).read_bytes()),'bytes':(ROOT/path).stat().st_size}
        plt.close(fig)
    manifest={'schema':'osw.west-australian-regional-streamline-figures.v1','source_file':REPORT,'source_sha256':digest((ROOT/REPORT).read_bytes()),
              'generator_file':OPERATOR,'generator_sha256':digest((ROOT/OPERATOR).read_bytes()),'figures':assets,
              'alt':f"All{len(document['cases'])}regional source-field streamline tests with{document['counts']['status_counts'].get('both_regional_gates_reached',0)}matching gate pairs. Separate maps preserve every primary partial failure and source-period mean. No named-current axis or whole-current dimension inferred.",
              'physical_current_geometry_admitted':False,'source_image_redistributed':False}
    (ROOT/MANIFEST).write_bytes((json.dumps(manifest,indent=2)+'\n').encode());print(json.dumps(assets))


if __name__=='__main__':main()
