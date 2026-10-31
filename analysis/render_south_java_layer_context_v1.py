"""Render published model definitions; never infer current thickness or width."""
import ctypes
import hashlib
import json
import os
import platform
import re
from pathlib import Path

for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name] = '1'
if os.name == 'nt':
    kernel = ctypes.windll.kernel32
    kernel.GetCurrentProcess.restype = ctypes.c_void_p
    kernel.SetProcessAffinityMask.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
    kernel.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
    assert kernel.SetProcessAffinityMask(kernel.GetCurrentProcess(), 1)
    assert kernel.SetPriorityClass(kernel.GetCurrentProcess(), 0x4000)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'research/south-java-iskandar-2006-layer-source-facts-v1.json'
OUTPUT = 'figures/south-java-iskandar-2006-layer-context-v1.svg'
MANIFEST = 'research/south-java-iskandar-2006-layer-figure-v1.json'


def main():
    raw = (ROOT / SOURCE).read_bytes()
    facts = json.loads(raw)
    assert facts['entity_id'] == 'current:south-java'
    assert facts['exclusions']['width_km'] is None
    assert facts['exclusions']['whole_current_depth_interval_m'] is None
    assert facts['exclusions']['physical_annual_depth_range_m'] is None
    bands = facts['layer_definitions']
    assert [row['classification'] for row in bands] == ['author_defined_analysis_layer_not_measured_current_thickness'] * 2
    assert bands[0]['lower_depth_m'] == 150 and bands[1]['upper_depth_m'] == 150 and bands[1]['lower_depth_m'] == 1000
    surface, cap, deep = facts['reported_model_depth_context']
    assert cap['exact_edge_depth_m'] is None and cap['velocity_threshold_relation'] == 'greater_than'
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none',
                         'svg.hashsalt':'osw-south-java-layer-context-v1'})
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 7), gridspec_kw={'width_ratios':[1,1.6]})
    fig.subplots_adjust(top=.79, bottom=.24, left=.08, right=.97, wspace=.4)
    fig.suptitle('South Java current system · model layer context', fontsize=16, y=.97)
    fig.text(.5,.91,'OFES · 1990–2003 analysis · selected mean sections at 105°, 110°, 115°, 117°E',ha='center',fontsize=10)
    fig.text(.5,.865,'Study definitions and model summaries — not measured current thickness or annual ranges',ha='center',fontsize=10)
    for ax in axes:
        ax.set_ylim(1000,0); ax.set_xlim(0,1); ax.set_xticks([])
        ax.set_ylabel('Depth below surface (m)')
        ax.set_yticks([0,150,400,600,800,1000])
        ax.grid(axis='y',color='#dce4e7',linewidth=.6)
        for side in ['top','right','bottom']: ax.spines[side].set_visible(False)
    left, right = axes
    left.set_title('Author-defined analysis bands',pad=15)
    left.axhspan(0,bands[0]['lower_depth_m'],color='#d8edf5',zorder=0)
    left.axhspan(bands[1]['upper_depth_m'],bands[1]['lower_depth_m'],color='#e8e0f2',zorder=0)
    left.axhline(150,color='#6d7180',linewidth=1)
    left.text(.5,75,'Surface coastal current (SJCC)\nsurface to 150 m',ha='center',va='center',fontsize=10)
    left.text(.5,570,'Coastal undercurrent (SJCU)\nbelow 150 m to 1000 m',ha='center',va='center',fontsize=10)
    right.set_title('Reported mean-flow depth context',pad=15)
    right.scatter([.08],[surface['reported_depth_m']],color='#146b8b',s=36,zorder=3)
    right.text(.2,40,'≈50 m: surface mean-core depth',va='center',fontsize=10)
    right.hlines(cap['depth_cap_m'],0,.15,linestyles='dashed',color='#687b84',linewidth=1.4)
    right.annotate('',xy=(.05,0),xytext=(.05,100),arrowprops={'arrowstyle':'->','color':'#687b84'})
    right.text(.2,150,'Eastward u > 5 cm/s: not below 100 m\nUpper limit; not an exact current edge',va='top',fontsize=9)
    right.scatter([.08],[deep['reported_depth_m']],color='#75549c',s=36,zorder=3)
    right.text(.2,400,'≈400 m: undercurrent mean core\nPeak eastward flow ≈3 cm/s',va='center',fontsize=10)
    fig.text(.08,.17,'Band limits classify this study’s analysis. Core dots are approximate model summaries.',fontsize=10)
    fig.text(.08,.125,'No horizontal width, physical thickness, annual envelope, uncertainty interval or state footprint is inferred.',fontsize=9)
    fig.text(.08,.075,'Source: Iskandar et al. (2006), doi:10.1029/2006JC003486 · paragraphs 6, 10–14.\nOriginal publisher prose reviewed; no source figure digitized. Schematic horizontal positions have no distance scale.',fontsize=9)
    output = ROOT / OUTPUT
    fig.savefig(output,format='svg',metadata={'Date':None,'Title':'South Java model analysis bands and mean-flow depth context',
        'Description':'Author-defined model analysis layers are distinct from approximate mean core depths and a threshold-depth upper limit. No physical width or current thickness is inferred.'})
    svg = output.read_text(encoding='utf-8')
    opening = re.search(r'<svg\b[^>]*>',svg,re.S)
    assert opening is not None
    root = opening.group()[:-1] + ' role="img" aria-labelledby="sj-layer-title sj-layer-desc">'
    labels = ('<title id="sj-layer-title">South Java model analysis bands and depth context</title>'
              '<desc id="sj-layer-desc">Left: separate author-defined surface-current and undercurrent analysis bands. '
              'Right: approximate mean core depths and an upper limit on thresholded mean-flow depth. '
              'These are model definitions and summaries, not measured current thickness, widths, or annual ranges.</desc>')
    output.write_bytes((svg[:opening.start()]+root+labels+svg[opening.end():]).encode('utf-8'))
    preview = ROOT / '.pytest_cache/south-java-layer-context-v1.png'
    preview.parent.mkdir(exist_ok=True)
    fig.savefig(preview,dpi=110)
    plt.close(fig)
    manifest = {'schema':'osw.current-layer-context-figure.v1','source_file':SOURCE,
        'source_sha256':hashlib.sha256(raw).hexdigest(),'renderer':'analysis/render_south_java_layer_context_v1.py',
        'renderer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'figure':OUTPUT,'figure_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
        'figure_bytes':output.stat().st_size,'provider_figures_reproduced':False,
        'new_scientific_values_computed':False,'physical_width_admitted':False,
        'physical_current_thickness_admitted':False,'visual_review_complete':False,
        'python_version':platform.python_version(),'matplotlib_version':matplotlib.__version__,
        'font_family':'DejaVu Sans','svg_hash_salt':'osw-south-java-layer-context-v1',
        'local_cpu_limit':1,'priority':'BelowNormal','numerical_worker_limit':1}
    (ROOT / MANIFEST).write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2))


if __name__ == '__main__':
    main()
