"""Small research plot of already executed primary scalar brackets, using Matplotlib."""
import argparse
import calendar
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from current_local_extent_evidence_v1 import ROOT,OUTPUT,QUANTITIES,encoded

SVG='figures/eacc-local-extent-primary-months-v1.svg'
MANIFEST='research/eacc-local-extent-primary-months-figure-v1.json'
LABELS={
    'core_to_positive_normal_threshold_extent':'Core to positive-normal edge',
    'local_two_sided_threshold_span':'Local paired span',
    'finite_paired_support_to_positive_threshold_extent':'Model support boundary to positive edge',
    'shore_reference_to_positive_threshold_extent':'Independent shore to positive edge'}


def render(bundle,svg_path,png_path):
    """Draw lower/upper bounds directly; no midpoint or interpolated annual curve."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    matplotlib.rcParams.update({'svg.fonttype':'none','svg.hashsalt':'osw-eacc-local-extents-v1',
        'font.family':'DejaVu Sans','font.size':10})
    rows=bundle['collections']['current_local_extents']
    selected=[r for r in rows if r['native_latitude_offset']==0 and r['threshold_fraction']==.5]
    if len(selected)!=96 or len({r['id'] for r in selected})!=96:
        raise ValueError('All24 primary half-peak attempts per quantity required')
    lookup={(r['quantity'],r['normal_sample_step_km'],r['month']):r for r in selected}
    if set(lookup)!={(q,s,m) for q in QUANTITIES for s in (5,10) for m in range(1,13)}:
        raise ValueError('Missing primary quantity/month/sampling identity')
    fig,axes=plt.subplots(2,2,figsize=(14,10))
    fig.subplots_adjust(left=.065,right=.98,top=.83,bottom=.23,hspace=.73,wspace=.20)
    fig.suptitle('Local extents in the EACC candidate region · 2013',fontsize=18,y=.98)
    fig.text(.5,.94,'15 m · daily 00Z sampled monthly mean fields · primary latitude · 50% threshold',ha='center',fontsize=11)
    fig.text(.5,.907,'Model diagnostics: whole-current widths, physical annual ranges and uncertainty remain unadmitted.',ha='center',fontsize=10)
    colors={5:'#164e80',10:'#a04b00'};offsets={5:-.14,10:.14};status_counts={}
    for ax,quantity in zip(axes.flat,QUANTITIES):
        supported=0
        for step in (5,10):
            for month in range(1,13):
                row=lookup[quantity,step,month];x=month+offsets[step]
                if row['source_scale_gate_passed']:
                    low,high=row['extent_bracket_km'];supported+=1
                    ax.vlines(x,low,high,color=colors[step],linewidth=2,
                        linestyles='solid' if step==5 else 'dashed')
                    ax.hlines([low,high],x-.09,x+.09,color=colors[step],linewidth=1.6)
                else:
                    ax.text(x,-.12 if step==5 else -.21,'×' if step==5 else '+',
                        transform=ax.get_xaxis_transform(),ha='center',va='center',color=colors[step],fontsize=12)
        ax.set_title(LABELS[quantity],loc='left',fontsize=12,pad=13)
        ax.set_xticks(range(1,13),[calendar.month_abbr[m] for m in range(1,13)],fontsize=9)
        ax.set_xlim(.4,12.6);ax.set_ylim(bottom=0);ax.set_ylabel('Local extent (km)')
        ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',color='#dce1e4',linewidth=.7)
        ax.set_axisbelow(True)
        if supported==0:
            ax.set_ylim(0,100)
            message=('No independent shoreline reference\nAll 24 primary attempts unresolved'
                if quantity=='shore_reference_to_positive_threshold_extent' else
                'No source-scale-supported extent\nAll 24 primary attempts unresolved or rejected')
            ax.text(.5,.55,message,
                transform=ax.transAxes,ha='center',va='center',fontsize=11)
        status_counts[quantity]={'primary_attempts':24,'source_scale_supported':supported,'unresolved_or_rejected':24-supported}
    handles=[Line2D([0],[0],color=colors[5],linewidth=2,label='5 km sampling · solid bracket / × unresolved'),
        Line2D([0],[0],color=colors[10],linewidth=2,linestyle='--',label='10 km sampling · dashed bracket / + unresolved')]
    fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.5,.105),ncol=2,frameon=False,fontsize=10)
    fig.text(.065,.073,'Vertical bars show stored lower/upper bounds; no midpoint, connecting curve or annual envelope is calculated.',fontsize=10)
    fig.text(.065,.048,'Missing/rejected attempts appear below the month axis, not as zero extents. Bounds are not confidence intervals.',fontsize=10)
    fig.text(.065,.023,'Source: HYCOM 2013 saved profiles · case 40128227569/1 · exact values and all 864 outcomes in the linked JSON bundle.',
        fontsize=9,color='#164e80',url='../research/eacc-local-extent-evidence-bundle-v1.json')
    svg_path=Path(svg_path);png_path=Path(png_path)
    svg_path.parent.mkdir(parents=True,exist_ok=True);png_path.parent.mkdir(parents=True,exist_ok=True)
    if svg_path.exists() or png_path.exists():raise ValueError('Refuse to overwrite a figure version')
    fig.savefig(svg_path,format='svg',metadata={'Date':None,'Title':'EACC candidate-region local extent evidence',
        'Description':'Primary monthly model-section sampling brackets at15m in2013; separate quantities and5/10km sampling. Every unsupported attempt remains explicit. No physical whole-current width or annual range admitted.'})
    fig.savefig(png_path,format='png',dpi=100);plt.close(fig)
    ns='http://www.w3.org/2000/svg';ET.register_namespace('',ns)
    tree=ET.parse(svg_path);root=tree.getroot();root.set('role','img');root.set('aria-labelledby','extent-title extent-description')
    title=ET.Element('{'+ns+'}title',{'id':'extent-title'});title.text='Monthly local extent evidence: EACC candidate region,2013'
    desc=ET.Element('{'+ns+'}desc',{'id':'extent-description'})
    desc.text='Four panels show distinct scalar quantities, with separate lower/upper sampling brackets for5/10km steps and explicit unresolved markers. All72 cases and864 outcomes are in the JSON alternative. These are model-local diagnostics at15m, not admitted physical whole-current widths or climatological annual ranges.'
    root.insert(0,desc);root.insert(0,title);tree.write(svg_path,encoding='utf-8',xml_declaration=True)
    ET.parse(svg_path)
    return {'schema':'osw.current-local-extent.primary-months-figure.v1','figure':SVG,
        'figure_sha256':hashlib.sha256(svg_path.read_bytes()).hexdigest(),'figure_bytes':svg_path.stat().st_size,
        'data_file':OUTPUT,'data_sha256':hashlib.sha256(encoded(bundle)).hexdigest(),
        'renderer':'analysis/render_current_local_extent_evidence_v1.py','matplotlib_version':matplotlib.__version__,
        'primary_attempts_drawn':96,'case_scope':'primary_offset0_half_peak_only; full bundle retains all72 cases/864 attempts',
        'status_counts_by_quantity':status_counts,'data_values_reestimated':False,
        'source_velocity_arrays_read':False,'midpoints_or_fitted_curves_supplied':False,
        'physical_current_width_admitted':False,'small_png_visual_inspection_required':True,
        'export_xml_roundtrip_verified':True}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--png',type=Path,required=True)
    args=parser.parse_args();raw=(ROOT/OUTPUT).read_bytes();bundle=json.loads(raw)
    if raw!=encoded(bundle):raise ValueError('Noncanonical scalar bundle')
    manifest=render(bundle,ROOT/SVG,args.png)
    manifest['input_sha256']={OUTPUT:hashlib.sha256(raw).hexdigest(),
        'analysis/render_current_local_extent_evidence_v1.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'analysis/test_render_current_local_extent_evidence_v1.py':hashlib.sha256((ROOT/'analysis/test_render_current_local_extent_evidence_v1.py').read_bytes()).hexdigest()}
    with (ROOT/MANIFEST).open('xb') as stream:stream.write(encoded(manifest))
    print(json.dumps({'figure':SVG,'figure_bytes':manifest['figure_bytes'],'primary_slots':96,
        'reestimated_values':False,'physical_width_admission':False}))
