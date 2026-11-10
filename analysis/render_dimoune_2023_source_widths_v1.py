"""Render a small published-value comparison; never opens ocean fields or packets."""
import hashlib
import json
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FILE='research/dimoune-2023-section-width-records-prepared-v1.json'

def render():
    for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='1'
    os.environ['MPLCONFIGDIR']=str(ROOT/'.pytest_cache/mpl-dimoune-widths-v1')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    raw=(ROOT/FILE).read_bytes();doc=json.loads(raw);rows=doc['records']
    assert len(rows)==len({r['id'] for r in rows})==14
    assert doc['counts']=={'source_rows':14,'existing_inventory_matches':5,'potential_additional_scoped_width_records':6,'unplaced_surface_current_rows':3,'records_admitted':0}
    assert all(r['width_range_km'] is None and r['annual_physical_width_range_km'] is None and r['geometry'] is None for r in rows)
    palette={'duplicate_context_only':'#879ca4','scoped_width_admission_candidate':'#008c86','taxonomy_review_before_admission':'#c68a2b'}
    labels={'NBC1':'North Brazil / HS1','NBC2':'North Brazil / HS2','rNBC2':'Retroflected NBC / HS2','NBC3':'Guiana convention / HS3','NBCR4':'NBC retroflection zone / HS4','nSEC4':'Northern SEC / HS4','nSEC5':'Northern SEC / HS5','nSEC6':'Northern SEC / HS6','cSEC6':'Central SEC / HS6','NECC5':'NECC / HS5','NECC6':'NECC / HS6','ESC4':'Equatorial surface flow / HS4','ESC5':'Equatorial surface flow / HS5','ESC6':'Equatorial surface flow / HS6'}
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'svg.fonttype':'none','svg.hashsalt':'osw-dimoune-widths-v1'})
    fig,ax=plt.subplots(figsize=(11.5,8.7));fig.subplots_adjust(left=.30,right=.94,bottom=.25,top=.81)
    for i,row in enumerate(rows):
        value=row['approximate_width_km'];ax.barh(i,value,height=.58,color=palette[row['candidate_action']])
        ax.text(value+12,i,f'~{value} km',va='center',fontsize=10)
    ax.set_yticks(range(len(rows)),[labels[r['source_flow_label']] for r in rows]);ax.invert_yaxis();ax.set_xlim(0,1060)
    ax.set_xlabel('Published approximate width of a mean current band (km)');ax.xaxis.grid(True,color='#d7e2e5');ax.set_axisbelow(True)
    for side in ['top','right','left']:ax.spines[side].set_visible(False)
    ax.tick_params(axis='y',length=0,pad=10)
    fig.text(.06,.95,'Tropical Atlantic: reported mean section widths',fontsize=19,weight='bold',color='#173e49')
    fig.text(.06,.905,'1993-2017 surface geostrophic estimates | Different sections, not a current ranking',fontsize=12)
    fig.text(.06,.865,'SOURCE TRANSCRIPTION - candidate ownership/admission audit pending',fontsize=11,weight='bold',color='#856117')
    fig.legend(handles=[Patch(color=palette['duplicate_context_only'],label='5 existing inventory matches'),Patch(color=palette['scoped_width_admission_candidate'],label='6 potential additional records'),Patch(color=palette['taxonomy_review_before_admission'],label='3 surface-current rows: identity pending')],loc='upper left',bbox_to_anchor=(.05,.165),ncol=1,frameon=False,fontsize=10)
    fig.text(.06,.061,'Zero contours of time-mean section velocities; not annual minima/maxima or whole-current widths.',fontsize=10)
    fig.text(.06,.036,'Dimoune et al. (2023), Table 1, p. 256 (prose refers to Table 2). DOI: 10.5194/os-19-251-2023. CC BY 4.0.',fontsize=9)
    fig.text(.06,.015,'Source discrepancies and unknown edge geometry are retained in the record review. Chart: OSW.',fontsize=9)
    output=ROOT/'figures/dimoune-2023-section-widths-source-review-v1.svg';output.parent.mkdir(exist_ok=True)
    fig.savefig(output,metadata={'Date':None})
    preview=ROOT/'.pytest_cache/atlantic-dimension-primary-review-v1/dimoune-2023-widths-review.png';fig.savefig(preview,dpi=125);plt.close(fig)
    return {'source_file':FILE,'source_sha256':hashlib.sha256(raw).hexdigest(),'figure_file':output.relative_to(ROOT).as_posix(),'figure_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'preview_png':str(preview),'records_admitted':0,'ocean_field_processing':False}

if __name__=='__main__':print(json.dumps(render()))
