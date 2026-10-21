"""Refined traces and an explicit overlay of the retained Euler baseline."""
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from build_west_australian_regional_streamline_figures import comparison, paths, OPERATOR as SUPPORT
from west_australian_regional_streamlines_rk4 import ROOT, REPORT, build, encoded, digest

OPERATOR='analysis/build_west_australian_regional_streamline_rk4_figures.py'
MANIFEST='research/west-australian-regional-streamline-rk4-figures.json'


def main():
    document=json.loads((ROOT/REPORT).read_bytes())
    if encoded(build())!=(ROOT/REPORT).read_bytes():raise ValueError('Changed refined report')
    original=json.loads((ROOT/document['euler_baseline_file']).read_bytes())
    plt.rcParams.update({'font.family':'DejaVu Sans','svg.hashsalt':'osw-west-australian-regional-rk4-v2'})
    assets={}
    for name,constructor,stem in [('comparison',comparison,'figures/west-australian-regional-streamlines-rk4'),('paths',paths,'figures/west-australian-regional-streamline-paths-rk4')]:
        fig=constructor(document)
        if name=='comparison':
            ax=fig.axes[0];maximum=0
            for i,anchor in enumerate(document['anchors']):
                for row in original['cases']:
                    if row['field_id']==anchor['field_id'] and row['conditional_regional_path_length_km'] is not None:
                        value=row['conditional_regional_path_length_km'];maximum=max(maximum,value)
                        ax.scatter(i+row['native_seed_offset']*.18,value,marker='x',color='#a7afb3',s=22,zorder=1)
            values=[r['conditional_regional_path_length_km'] for r in document['cases'] if r['conditional_regional_path_length_km'] is not None]
            ax.set_ylim(0,max([maximum,*values])*1.08)
            ax.set_title('Colored: refined results · grey ×: Euler baseline · black outline: primary refined case',loc='left',fontsize=11)
        for suffix in ['svg','png']:
            path=stem+'.'+suffix;metadata={'Date':None,'Creator':'OSW'} if suffix=='svg' else {'Software':'OSW'}
            fig.savefig(ROOT/path,dpi=130,metadata=metadata,facecolor='white')
            assets[name+'_'+suffix]={'file':path,'sha256':digest((ROOT/path).read_bytes()),'bytes':(ROOT/path).stat().st_size}
        plt.close(fig)
    manifest={'schema':'osw.west-australian-regional-streamline-rk4-figures.v2','source_file':REPORT,
        'source_sha256':digest((ROOT/REPORT).read_bytes()),'generator_file':OPERATOR,'generator_sha256':digest((ROOT/OPERATOR).read_bytes()),
        'supporting_generator_file':SUPPORT,'supporting_generator_sha256':digest((ROOT/SUPPORT).read_bytes()),'figures':assets,
        'alt':f"Adaptive RK4 retains all117cases: {document['counts']['status_counts'].get('both_regional_gates_reached',0)}regional gate pairs match. The Euler baseline remains visible; failed and successful primary paths are mapped separately. No named-current axis or whole-current length inferred.",
        'physical_current_geometry_admitted':False,'source_image_redistributed':False}
    (ROOT/MANIFEST).write_bytes((json.dumps(manifest,indent=2)+'\n').encode());print(json.dumps(assets))


if __name__=='__main__':main()
