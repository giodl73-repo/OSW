"""Standalone source-aware visualization of all dated component-span outcomes."""
from datetime import datetime
import hashlib
import json
import xml.etree.ElementTree as ET
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from build_asca_component_spans import ROOT, REPORT, RAW, verify, digest

BASE = 'figures/agulhas-asca-100m-dated-component-spans'
RECEIPT = 'research/agulhas-asca-100m-dated-component-spans-figure.json'
GENERATOR = 'analysis/build_asca_component_span_figure.py'


def build():
    report = verify(); raw = json.loads((ROOT/RAW).read_bytes()); rows = report['profiles']
    fig = plt.figure(figsize=(15, 14), constrained_layout=False)
    grid = fig.add_gridspec(3, 3, left=.07, right=.97, top=.86, bottom=.22,
                           height_ratios=[1.2, 1, 1.05], hspace=.65, wspace=.28)
    fig.text(.035, .965, 'Agulhas / ASCA100m: dated fixed-array component spans', fontsize=21, weight='bold')
    fig.text(.035, .93, '931 processed source profiles • southwestward −v • 330 paired half-peak spans; 601 unresolved', fontsize=13)
    fig.text(.035, .905, 'Fixed-array section distances, not flow-normal or whole-current widths. Thresholds were declared before this calculation.', fontsize=10)
    ax = fig.add_subplot(grid[0, :])
    times = [datetime.fromisoformat(row['observed_at'].replace('Z', '+00:00')) for row in rows]
    values = [row['cases'][1]['span_km'] for row in rows]
    ax.scatter([t for t, value in zip(times, values) if value is not None],
               [value for value in values if value is not None], s=10, color='#176381', label='Resolved50% component span')
    ax.plot([t for t, value in zip(times, values) if value is None],
            [-8 for value in values if value is None], '|', ms=5, color='#a84523', label='Unresolved (below axis, not zero)')
    ax.set(ylabel='Numerical section span (km)', ylim=(-15, 200), title='All931 primary outcomes; no connecting line or missing-value filling')
    ax.grid(alpha=.2); ax.legend(fontsize=9, loc='upper right'); ax.set_xlabel('Original supplied UTC timestamps; not independent20-hour observations')
    ax = fig.add_subplot(grid[1, :])
    months = report['monthly_summaries']; matrix = np.array([[o['resolved_profiles'] for o in m['outcomes']] for m in months]).T
    im = ax.imshow(matrix, cmap='cividis', aspect='auto', vmin=0, vmax=38)
    for j, month in enumerate(months):
        for i, outcome in enumerate(month['outcomes']):
            count = outcome['resolved_profiles']; total = outcome['attempted_profiles']
            ax.text(j, i, f'{count}/{total}', ha='center', va='center', fontsize=7, color='white' if count < 18 else 'black')
    ax.set_yticks(range(3), ['40%', '50% primary', '60%'])
    ax.set_xticks(range(len(months)), [f"{m['year']}-{m['month']:02d}"+('*' if not m['complete_calendar_time_support'] else '') for m in months], rotation=65, ha='right', fontsize=8)
    ax.set_title('Resolved / attempted per calendar month and threshold: failures remain in every denominator', fontsize=11)
    ax.set_ylabel('Fraction of same peak'); fig.colorbar(im, ax=ax, fraction=.018, pad=.015, label='Resolved count')
    for column, index in enumerate([0, 465, 930]):
        ax = fig.add_subplot(grid[2, column]); source = raw['profiles'][index]; row = rows[index]
        distance = np.array(raw['coordinates']['distance_m'])/1000
        velocity = np.array([np.nan if v is None else -v for v in source['fields']['v']])
        ax.plot(distance, velocity, color='#176381', lw=1.4, label='Source−v; gaps retained')
        peak = row['peak_index']; ax.plot(distance[peak], velocity[peak], 'o', color='#212121', ms=4, label='Selected global peak')
        case = row['cases'][1]; ax.axhline(case['threshold_m_s'], color='#666666', ls=':', lw=1, label='50% threshold')
        for side in ['smaller_distance_edge', 'larger_distance_edge']:
            edge = case[side]
            if edge is not None and edge['status'] == 'resolved':
                ax.plot(edge['distance_m']/1000, case['threshold_m_s'], 'D', color='#a84523', ms=4)
        status = f"{case['span_km']:.1f}km numerical span" if case['span_km'] is not None else 'Paired span unresolved'
        ax.set(xlim=(0, 300), ylim=(-1.4, 2.5), title=f"Fixed index{index}: {row['observed_at'][:10]}\n{status}", xlabel='Source array distance (km)', ylabel='Southwestward−v (m/s)')
        ax.grid(alpha=.2)
        if column == 0: ax.legend(fontsize=7, loc='lower right')
    notes = [
        '40%/50%/60% are alternative thresholds, not uncertainty or additional observations. All2793 outcomes are retained.',
        'The601 primary failures include596 missing-barrier and5 domain-truncation side failures. A missing edge is not coast or current absence.',
        'Monthly sampled ranges condition on resolved profiles and may be biased by missing boundaries. * marks partial calendar bins; no climatology.',
        '500m output spacing is interpolation, not independent instrument resolution. Grid-bracket separation is support, not physical error or confidence.',
        '40-hour low-pass filtering and20-hour subsampling make adjacent profiles dependent. Supplied float32 timestamps are preserved.',
        'Provider product2.0 is corrected; no independent ADCP rotation repair. Full2022corrigenda remain unreviewed; no old transport values validate these spans.',
        'No geographic edges, whole-current width, annual physical range, ranking or seasonal map animation is admitted.',
        'Source: Beal Lab / University of Miami, ASCA product2.0, doi:10.5281/zenodo.20515068, CC BY4.0. Derived analysis and figure: OSW.']
    for i, note in enumerate(notes): fig.text(.035, .18-i*.019, note, fontsize=8.5)
    plt.rcParams['svg.hashsalt'] = 'osw-asca-component-spans-v1'
    outputs = {}
    for extension in ['png', 'svg']:
        path = BASE+'.'+extension
        fig.savefig(ROOT/path, dpi=150, metadata={'Date': None} if extension == 'svg' else {})
        if extension == 'svg':
            ET.register_namespace('', 'http://www.w3.org/2000/svg')
            tree = ET.parse(ROOT/path); node = tree.getroot(); node.set('role', 'img'); node.set('aria-labelledby', 'asca-title asca-description')
            title = ET.Element('{http://www.w3.org/2000/svg}title', id='asca-title'); title.text = 'ASCA100m dated southwestward component spans'
            desc = ET.Element('{http://www.w3.org/2000/svg}desc', id='asca-description'); desc.text = '330of931 half-peak section spans resolve;601remain unresolved. All outcomes and three threshold counts are shown, with three prespecified source profiles. Fixed-array component diagnostics, not current widths, geographic boundaries or annual physical ranges.'
            node.insert(0, title); node.insert(1, desc); tree.write(ROOT/path, encoding='utf-8', xml_declaration=True)
        outputs['.'+extension] = {'file': path, 'sha256': digest(path)}
    plt.close(fig)
    receipt = {'schema': 'osw.source-figure.v1', 'source_file': REPORT, 'source_sha256': digest(REPORT),
               'generator_file': GENERATOR, 'generator_sha256': digest(GENERATOR),
               'figures': outputs, 'prespecified_profile_indices': [0, 465, 930],
               'all_primary_outcomes_rendered': 931, 'physical_edges_rendered': False,
               'source_uncertainty_inferred': False, 'annual_extrema_inferred': False}
    (ROOT/RECEIPT).write_bytes((json.dumps(receipt, indent=2)+'\n').encode())
    print(json.dumps(receipt))


if __name__ == '__main__': build()
