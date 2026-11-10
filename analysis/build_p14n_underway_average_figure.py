"""Plot measured averaging footprints; unresolved sides remain unresolved."""
from pathlib import Path
import hashlib
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from build_p14n_underway_averages import ROOT, OUTPUT, verify, encoded

RECEIPT = 'research/aleutian-p14n-1993-underway-averages-figure.json'


def generate():
    report = verify()
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'svg.hashsalt': 'osw-p14n-underway-average-v1'})
    fig, axes = plt.subplots(2, 3, figsize=(13, 9), sharey='row')
    fig.subplots_adjust(left=.075, right=.97, top=.82, bottom=.25, hspace=.45, wspace=.16)
    fig.suptitle('P14N: tested averages leave branch boundaries unresolved',
                 x=.05, ha='left', fontsize=16, fontweight='bold')
    fig.text(.05, .925, 'July 1993 | 100-300 m eastward means | station stops remain barriers | no width admitted', fontsize=11)
    styles = [(1, '#8563aa', 'o'), (2, '#126b7e', 's'), (3, '#b26324', '^')]
    handles = [Line2D([], [], marker=marker, color=color, linestyle='none', label=f'>={speed} m/s ship speed')
               for speed, color, marker in styles]
    handles.append(Line2D([], [], marker='o', markerfacecolor='none', color='#666', linestyle='none', label='Hollow: <80% time coverage'))
    fig.legend(handles=handles, loc='upper left', bbox_to_anchor=(.05, .905), ncol=4, frameon=False, fontsize=9)
    for row_index, (name, window) in enumerate([('northern', [44, 46]), ('southern', [41, 43])]):
        for col_index, minutes in enumerate([30, 60, 150]):
            ax = axes[row_index, col_index]
            for speed, color, marker in styles:
                experiment = next(e for e in report['experiments'] if e['ship_speed_cutoff_m_s'] == speed and e['averaging_minutes'] == minutes)
                for run in experiment['runs']:
                    for b in run['bins']:
                        low, high = b['contributor_latitude_range']
                        # Same complete-footprint branch scope used by the boundary operator.
                        if low < window[0] or high > window[1]:
                            continue
                        x = b['mean']['latitude_degrees_north']; y = b['mean']['eastward_m_s']
                        ax.errorbar([x], [y], xerr=[[max(0., x - low)], [max(0., high - x)]],
                                    fmt=marker, ms=4 if speed == 2 else 3, color=color,
                                    markerfacecolor=color if b['boundary_eligible_coverage'] else 'none',
                                    alpha=.9 if speed == 2 else .55, lw=.7, capsize=1.5)
            ax.axhline(0, color='#aaa', lw=.6)
            ax.set(xlim=window, title=f'{name.title()} | {minutes}-minute windows', xlabel='Ensemble-end latitude (degrees north)')
            ax.grid(alpha=.15)
            if col_index == 0:
                ax.set_ylabel('Mean eastward u (m/s)')
    fig.text(.05, .185, 'All 54 relative-peak and 72 velocity-sensitivity scenarios are unresolved: no two-sided component span.', fontsize=11)
    fig.text(.05, .145, 'Horizontal bars: contributor latitude footprint, not boundary uncertainty. Points are moving-window summaries.', fontsize=10)
    fig.text(.05, .105, 'Disjoint windows start at each run; overlapping ensemble intervals count once. Incomplete final windows remain visible.', fontsize=10)
    fig.text(.05, .065, 'No lines join runs. Eastward is not flow-normal; GPS averaging context is not a calibrated width error interval.', fontsize=10)
    fig.text(.05, .025, 'Source: UH/NOAA JASADCP 00016; OSW declared exploratory operator; Chen and Firing (2006), doi:10.1029/2005JC003064.', fontsize=9)
    prefix = ROOT / 'figures/aleutian-p14n-1993-underway-averages'
    fig.savefig(prefix.with_suffix('.svg'), metadata={'Date': None, 'Title': 'P14N contiguous underway averaging footprints'})
    fig.savefig(prefix.with_suffix('.png'), dpi=150, metadata={'Software': 'OSW P14N underway averaging v1'})
    plt.close(fig)
    svg = prefix.with_suffix('.svg')
    content = svg.read_text(encoding='utf8')
    content = content.replace('<svg ', '<svg role="img" aria-labelledby="averaging-title averaging-desc" ', 1)
    content = content.replace('<title>', '<title id="averaging-title">', 1)
    content = content.replace('</title>', '</title>\n <desc id="averaging-desc">Six panels compare northern and southern branch eastward means at fixed 30, 60 and 150 minute windows for all three ship-speed cutoffs. Horizontal bars show contributor latitude footprints, not uncertainty. Hollow markers have less than 80 percent time coverage. All 126 boundary scenarios lack two resolved sides. No physical current width is admitted. Numeric bins and the complete scenario results are in research/aleutian-p14n-1993-underway-averages.json.</desc>', 1)
    svg.write_bytes(('\n'.join(line.rstrip() for line in content.splitlines()) + '\n').encode())
    receipt = {
        'schema': 'osw.source-figure.v1', 'generator_file': Path(__file__).relative_to(ROOT).as_posix(),
        'generator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'source_file': OUTPUT, 'source_sha256': hashlib.sha256((ROOT / OUTPUT).read_bytes()).hexdigest(),
        'figures': {suffix: {'file': prefix.with_suffix(suffix).relative_to(ROOT).as_posix(),
                             'sha256': hashlib.sha256(prefix.with_suffix(suffix).read_bytes()).hexdigest()}
                    for suffix in ['.svg', '.png']},
        'osw_temporal_ocean_velocity_averaging_applied': True,
        'physical_edges_rendered': False, 'horizontal_bars_are_uncertainty': False,
        'unresolved_relative_peak_scenarios': 54, 'unresolved_velocity_scenarios': 72,
    }
    (ROOT / RECEIPT).write_bytes(encoded(receipt))
    return receipt


if __name__ == '__main__':
    print(json.dumps(generate()))
